import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from models import Event, User, create_event, create_tables
from utils import error_logger, logger

load_dotenv()

"""
It should look like:

1. Add topic/subject of notification
2. Add expiration date - when event should expire and you should be notified
3. Add intermediate notification date (optional) - when user should be notified first time and take some action
4. Confirmation! (user should verify and approve collected data from his input)
"""

SUBJECT, EXPIRATION_DATE, NOTIFICATION_DATE, CONFIRMATION = [0, 1, 2, 3]


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    current_user = update.effective_user
    chat_id = update.message.chat_id

    update.message.reply_markdown_v2(fr"Hi {current_user.mention_markdown_v2()}\!")

    if not User.select().where(User.user_id == current_user.id):
        User.create(
            user_id=current_user.id,
            chat_id=chat_id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            username=current_user.username,
        )

    # Save "user_id" for future linking with new event
    context.user_data["user_id"] = current_user.id

    update.message.reply_text("The available commands for now: /add")


def start_creating_entry(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Enter subject / entry below")

    # Duplicate it here, if '/start' command was skipped
    context.user_data["user_id"] = update.effective_user.id

    return SUBJECT


def add_new_entry(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    logger.info("update.message.text %s", user_text)

    context.user_data["entry"] = user_text

    update.message.reply_text(f"You've added an entry - '{user_text}'! Now add expiration date")

    return EXPIRATION_DATE


def expiration_date(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    context.user_data["expiration_date"] = update.message.text

    update.message.reply_text("You've added expiration time! Now add notification time")

    return NOTIFICATION_DATE


def notification_date(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data before %s", context.user_data)

    context.user_data["notification_date"] = update.message.text

    logger.info("context.user_data after %s", context.user_data)

    update.message.reply_text(
        f"You've added notification time! Confirm tha data below:\n\n"
        f'Subject - "{context.user_data["entry"]}"\n'
        f'Expiration time - "{context.user_data["expiration_date"]}"\n'
        f'Notification time - "{context.user_data["notification_date"]}"\n\n'
        f"If everything is correct, please enter /done command. "
        f"If not, enter /cancel command."
    )

    return CONFIRMATION


def confirmation(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    create_event(context.user_data)

    update.message.reply_text("Great! The entry has been created!\n Use /add command if you want to add more.")

    # TODO: show to user newly created data from DB record

    return ConversationHandler.END


def show_pending(update: Update, context: CallbackContext) -> None:
    """
    User should be able to request from bot all his pending events (that are waiting its notification time).
    """

    current_user_id = User.get(user_id=update.effective_user.id).id
    user_events = Event.select().where(Event.author == current_user_id, Event.completed == False)  # noqa: E712

    if user_events.count() == 0:
        update.message.reply_text("You don't have entries yet (")
        return

    update.message.reply_text("All entries you have:")
    for event in user_events:
        keyboard = [[InlineKeyboardButton(text="Click to archive!", callback_data=f"event:{event.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            text=f"Subject: {event.subject}\n"
            f"Expiration date: {event.expiration_date}\n"
            f"Notification date: {event.notification_date}\n",
            reply_markup=reply_markup,
        )

    update.message.reply_text("After taking some actions, don't forget to call /list again!")


def complete_event_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    event_id = query.data.split(":")[-1]
    event = Event.get(Event.id == event_id)
    event.completed = True
    event.save()

    query.message.reply_text(f"Event '{event.subject}' was completed and archived! ")


def show_archived(update: Update, context: CallbackContext) -> None:
    """
    User should be able to request from bot all his archived events (it's "completed" events actually).

    """

    update.message.reply_text("Soon we'll show you all your archived entries")


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("Bye! I hope we can talk again some day.")

    # TODO: flush "context.user_data" is user canceled the thing

    return ConversationHandler.END


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    # Handlers for main commands

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("list", show_pending))
    # dispatcher.add_handler(CommandHandler("list_old", show_archived))

    dispatcher.add_handler(CallbackQueryHandler(complete_event_handler))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_creating_entry)],
        states={
            SUBJECT: [MessageHandler(Filters.text, add_new_entry)],
            EXPIRATION_DATE: [MessageHandler(Filters.text, expiration_date)],
            NOTIFICATION_DATE: [MessageHandler(Filters.text, notification_date)],
            CONFIRMATION: [CommandHandler("done", confirmation)],
            # GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            # PHOTO: [
            #     MessageHandler(Filters.photo, photo),
            #     CommandHandler('skip', skip_photo)
            # ],
            # LOCATION: [
            #     MessageHandler(Filters.location, location),
            #     CommandHandler('skip', skip_location),
            # ],
            # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conversation_handler)

    # add an handler for errors
    dispatcher.add_error_handler(error_logger)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    create_tables()
    main()
