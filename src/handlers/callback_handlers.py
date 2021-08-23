from telegram import Update
from telegram.ext import CallbackContext

from models import complete_event, delete_event


def complete_event_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    event_id = query.data.split(":")[-1]
    complete_event(event_id)

    query.message.reply_text("Event was completed and archived!")


def delete_event_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    event_id = query.data.split(":")[-1]
    delete_event(event_id)

    query.message.reply_text("Event was deleted!")


def set_language_code(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    language_code = query.data.split(":")[-1]
    context.user_data["language_code"] = language_code

    query.message.reply_text(f"Your language was set to '{language_code}' !")
