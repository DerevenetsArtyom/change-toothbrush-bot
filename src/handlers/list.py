from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from models import complete_event, delete_event, get_expired_events, get_pending_events
from utils import prettify_date


def show_pending(update: Update, context: CallbackContext) -> None:
    """Show all pending events for the user (that are waiting for it's notification time)"""

    user_events = get_pending_events(update.effective_user.id)

    if user_events.count() == 0:
        update.message.reply_text("You don't have entries yet (")
        return

    update.message.reply_text("All entries you have:")
    for event in user_events:
        keyboard = [[InlineKeyboardButton(text="Click to archive!", callback_data=f"event-complete:{event.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            text=f"Subject: {event.subject}\n"
            f"Notification date: {prettify_date(event.notification_date)}\n"
            f"Expiration date: {prettify_date(event.expiration_date)}\n",
            reply_markup=reply_markup,
        )

    update.message.reply_text("After taking some actions, don't forget to call /list again!")


def show_expired(update: Update, _: CallbackContext) -> None:
    """Show all expired events for the user. Together with pending events - there are all events"""

    user_events = get_expired_events(update.effective_user.id)

    if user_events.count() == 0:
        update.message.reply_text("You don't have entries yet (")
        return

    update.message.reply_text("All entries you had before:")
    for event in user_events:
        keyboard = [[InlineKeyboardButton(text="Click to delete!", callback_data=f"event-delete:{event.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            text=f"Subject: {event.subject}\n"
            f"Notification date: {prettify_date(event.notification_date)}\n"
            f"Expiration date: {prettify_date(event.expiration_date)}\n",
            reply_markup=reply_markup,
        )


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
