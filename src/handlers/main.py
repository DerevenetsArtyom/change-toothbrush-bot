from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from handlers.conversation import (
    CONFIRMATION,
    EXPIRATION_DATE,
    NOTIFICATION_DATE,
    SUBJECT,
    add_expiration_date_custom,
    add_expiration_date_from_choice,
    add_new_entry,
    add_notification_date_custom,
    add_notification_date_from_choice,
    confirmation,
    start_creating_entry,
)
from handlers.list import complete_event_handler, delete_event_handler, show_expired, show_pending
from models import create_user, is_user_exists
from utils import get_description, logger


def help_handler(update: Update, _: CallbackContext) -> None:
    division_by_zero = 1 / 0
    print(division_by_zero)

    update.message.reply_text(f"Supported commands:\n{get_description()}")


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("The data you've entered previously is gone. Start again!")

    context.user_data.clear()

    return ConversationHandler.END


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    current_user = update.effective_user
    chat_id = update.message.chat_id

    update.message.reply_markdown_v2(fr"Hi {current_user.mention_markdown_v2()}\!")

    if not is_user_exists(current_user):
        create_user(current_user, chat_id)

    # Save "user_id" for future linking with new event
    context.user_data["user_id"] = current_user.id

    reply_keyboard = [
        ["/add", "/list"],
        ["/list_expired", "/help"],
    ]

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    update.message.reply_text(f"The available commands for now:\n{get_description()}", reply_markup=markup)


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_handler))
    dispatcher.add_handler(CommandHandler("list", show_pending))
    dispatcher.add_handler(CommandHandler("list_expired", show_expired))

    dispatcher.add_handler(CallbackQueryHandler(complete_event_handler, pattern="^event-complete:"))
    dispatcher.add_handler(CallbackQueryHandler(delete_event_handler, pattern="^event-delete:"))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_creating_entry)],
        states={
            SUBJECT: [MessageHandler(Filters.text & ~Filters.command, add_new_entry)],
            EXPIRATION_DATE: [
                MessageHandler(Filters.text & ~Filters.command, add_expiration_date_custom),
                CallbackQueryHandler(add_expiration_date_from_choice, pattern="^expiration_date"),
            ],
            NOTIFICATION_DATE: [
                MessageHandler(Filters.text & ~Filters.command, add_notification_date_custom),
                CallbackQueryHandler(add_notification_date_from_choice, pattern="^notification_date"),
            ],
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
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conversation_handler)

    # add an handler for errors
    # dispatcher.add_error_handler(error_logger)
