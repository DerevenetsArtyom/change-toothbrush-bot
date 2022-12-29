from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from handlers.callback_handlers import complete_event_handler, delete_event_handler
from handlers.conversation import (
    CONFIRMATION,
    EXPIRATION_DATE,
    NOTIFICATION_DATE,
    SUBJECT,
    add_expiration_date_from_choice,
    add_expiration_date_manually,
    add_new_entry,
    add_notification_date_from_choice,
    add_notification_date_manually,
    confirmation,
    skip_notification_date,
    start_creating_entry,
)
from handlers.list import show_expired, show_pending
from models import create_user, database, is_user_exists
from utils import get_description, logger


def help_handler(update: Update, _: CallbackContext) -> None:
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

    update.message.reply_markdown_v2(rf"Hi {current_user.mention_markdown_v2()}\!")

    with database:
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
                MessageHandler(Filters.text & ~Filters.command, add_expiration_date_manually),
                CallbackQueryHandler(add_expiration_date_from_choice, pattern="^expiration_date"),
            ],
            NOTIFICATION_DATE: [
                MessageHandler(Filters.text & ~Filters.command, add_notification_date_manually),
                CallbackQueryHandler(add_notification_date_from_choice, pattern="^notification_date"),
                CommandHandler("skip", skip_notification_date),
            ],
            CONFIRMATION: [CommandHandler("done", confirmation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conversation_handler)
