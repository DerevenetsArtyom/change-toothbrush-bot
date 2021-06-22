from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from models import complete_event, get_expired_events, get_pending_events
from utils import prettify_date


def show_pending(update: Update, _: CallbackContext) -> None:
    """User should be able to request from bot all his pending events (that are waiting its notification time)."""

    user_events = get_pending_events(update.effective_user.id)

    if user_events.count() == 0:
        update.message.reply_text("You don't have entries yet (")
        return

    update.message.reply_text("All entries you have:")
    for event in user_events:
        keyboard = [[InlineKeyboardButton(text="Click to archive!", callback_data=f"event:{event.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            text=f"Subject: {event.subject}\n"
            f"Notification date: {prettify_date(event.notification_date)}\n"
            f"Expiration date: {prettify_date(event.expiration_date)}\n",
            reply_markup=reply_markup,
        )

    update.message.reply_text("After taking some actions, don't forget to call /list again!")


def show_expired(update: Update, _: CallbackContext) -> None:
    """User should be able to request from bot all his expired events. Together with pending events - it's all events"""

    user_events = get_expired_events(update.effective_user.id)

    if user_events.count() == 0:
        update.message.reply_text("You don't have entries yet (")
        return

    update.message.reply_text("All entries you had before:")
    for event in user_events:
        update.message.reply_text(
            text=f"Subject: {event.subject}\n"
            f"Notification date: {prettify_date(event.notification_date)}\n"
            f"Expiration date: {prettify_date(event.expiration_date)}\n",
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
