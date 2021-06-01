import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

from models import User, create_tables, Event
from utils import error_logger, logger

load_dotenv()

"""
It should look like:

1. Add topic/subject of notification
2. Add expiration date - when event should expire and you should be notified
3. Add intermediate notification date (optional) - when user should be notified first time and take some action
4. Confirmation! (user should verify and approve collected data from his input)
"""

# TODO: add datepickers for dates input and shorthands (in one week, in one month, in three months etc)


SUBJECT, EXPIRATION_TIME, NOTIFICATION_TIME, CONFIRMATION = range(4)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    # TODO: add nice introductory text with list of commands

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

    update.message.reply_text(f'You\'ve added an entry - "{user_text}"! Now add expiration time')

    return EXPIRATION_TIME


def expiration_time(update: Update, context: CallbackContext) -> int:
    # TODO: add validation for date/time to be in the future only

    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    context.user_data["expiration_time"] = update.message.text

    update.message.reply_text("You've added expiration time! Now add notification time")

    return NOTIFICATION_TIME


def notification_time(update: Update, context: CallbackContext) -> int:
    # TODO: add validation for date/time to be in the future only
    # TODO: 'notification_date could be optional for input, if nothing is passed - calculate automatically

    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data before %s", context.user_data)

    context.user_data["notification_time"] = update.message.text

    logger.info("context.user_data after %s", context.user_data)

    update.message.reply_text(
        f"You've added notification time! Confirm tha data below:\n\n"
        f'Subject - "{context.user_data["entry"]}"\n'
        f'Expiration time - "{context.user_data["expiration_time"]}"\n'
        f'Notification time - "{context.user_data["notification_time"]}"\n\n'
        f"If everything is correct, please enter /done command. "
        f"If not, enter /cancel command."
    )

    return CONFIRMATION


def confirmation(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    expiration_date = datetime.strptime(context.user_data["expiration_time"], '%d-%m-%y')
    notification_date = datetime.strptime(context.user_data["notification_time"], '%d-%m-%y')

    current_user_id = User.get(user_id=context.user_data["user_id"]).id
    Event.create(
        author=current_user_id,
        subject=context.user_data["entry"],
        expiration_date=expiration_date,
        notification_date=notification_date,
    )

    update.message.reply_text(
        "Great! The entry has been created!\n"
        "Use /add command if you want to add more."
    )

    # TODO: show to user newly created data from DB record

    return ConversationHandler.END


def show_pending(update: Update, context: CallbackContext) -> None:
    """
    User should be able to request from bot all his pending events (that are waiting its notification time).

    TODO: Improvement - not just plain list, but list of entries with action buttons: remove, prolong etc.
    """

    update.message.reply_text("Soon we'll show you all your pending entries")


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
    # dispatcher.add_handler(CommandHandler("add_new", add_new_entry))
    # dispatcher.add_handler(CommandHandler("list", show_pending))
    # dispatcher.add_handler(CommandHandler("list_old", show_archived))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_creating_entry)],
        states={
            SUBJECT: [MessageHandler(Filters.text, add_new_entry)],
            EXPIRATION_TIME: [MessageHandler(Filters.text, expiration_time)],
            NOTIFICATION_TIME: [MessageHandler(Filters.text, notification_time)],
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

    dispatcher.add_handler(conv_handler)

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
