from telegram.ext import CallbackContext

from models import User, complete_event, get_events_for_expiration, get_events_for_notification
from utils import prettify_date


def check_events_for_notification(context: CallbackContext):
    """Fetch user events that should be notified today and send messages to the user"""

    for user in User.select():
        today_events_to_notify = get_events_for_notification(user.user_id)

        for event in today_events_to_notify:
            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"You wanted me to notify you about:"
                f"Subject: {event.subject}\n"
                f"Notification date: {prettify_date(event.notification_date)}\n"
                f"Expiration date: {prettify_date(event.expiration_date)}\n",
            )


def check_events_for_expiration(context: CallbackContext):
    """Fetch user events that should expired today and send messages to the user"""

    for user in User.select():
        today_events_to_expire = get_events_for_expiration(user.user_id)

        for event in today_events_to_expire:
            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"This event is expired today:"
                f"Subject: {event.subject}\n"
                f"Expiration date: {prettify_date(event.expiration_date)}\n"
                f"(you were notified on: {prettify_date(event.notification_date)})\n",
            )

            complete_event(event.id)
