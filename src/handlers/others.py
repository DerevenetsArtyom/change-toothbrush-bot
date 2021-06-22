from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from models import User
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

    reply_keyboard = [
        ["/add", "/list"],
        ["/list_expired", "/help"],
    ]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(f"The available commands for now:\n{get_description()}", reply_markup=markup)
