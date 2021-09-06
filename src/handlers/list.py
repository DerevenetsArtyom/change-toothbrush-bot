from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from models import get_expired_events, get_pending_events
from utils import prettify_date


def get_event_message(event):
    """Constructing message for single event based on event data to be displayed in the list of events"""

    notification_date_line = ""
    if event.notification_date:
        notification_date_line = f"Notification date: {prettify_date(event.notification_date)}\n"

    return (
        f"Subject: {event.subject}\n"
        f"{notification_date_line}"
        f"Expiration date: {prettify_date(event.expiration_date)}\n"
    )


def show_pending(update: Update, _: CallbackContext) -> None:
    """Show all pending events for the user (that are waiting for it's notification time)"""

    user_events = get_pending_events(update.effective_user.id)

    if user_events.count() == 0:
        update.message.reply_text("You don't have entries yet (")
        return

    update.message.reply_text("All entries you have:")
    for event in user_events:
        keyboard = [[InlineKeyboardButton(text="Click to archive!", callback_data=f"event-complete:{event.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(text=get_event_message(event), reply_markup=reply_markup)

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

        update.message.reply_text(text=get_event_message(event), reply_markup=reply_markup)
