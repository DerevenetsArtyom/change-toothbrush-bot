import os
import socket
import urllib.request

from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from models import User, complete_event, get_events_for_expiration, get_events_for_notification
from utils import prettify_date


def check_events_for_notification(context: CallbackContext):
    """Fetch user events that should be notified today and send messages to the user"""

    for user in User.select():
        today_events_to_notify = get_events_for_notification(user.user_id)

        for event in today_events_to_notify:
            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"You wanted me to notify you about:\n"
                f"*__{escape_markdown(event.subject, version=2)}__*\n"
                f"Notification date: _{prettify_date(event.notification_date)}_\n"
                f"Expiration date:   _{prettify_date(event.expiration_date)}_\n",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    HEALTHCHECKS_NOTIFICATION_UUID = os.getenv("HEALTHCHECKS_NOTIFICATION_UUID")
    if HEALTHCHECKS_NOTIFICATION_UUID:
        try:
            urllib.request.urlopen(f"https://hc-ping.com/{HEALTHCHECKS_NOTIFICATION_UUID}", timeout=10)
        except socket.error as e:
            print("Ping failed: %s" % e)


def check_events_for_expiration(context: CallbackContext):
    """Fetch user events that expire today and send messages to the user"""

    for user in User.select():
        today_events_to_expire = get_events_for_expiration(user.user_id)

        for event in today_events_to_expire:
            notification_date_line = ""
            if event.notification_date:
                notification_date_line = f"(you were notified on: {prettify_date(event.notification_date)})\n"

            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"This event is expired today:"
                f"Subject: {event.subject}\n"
                f"Expiration date: {prettify_date(event.expiration_date)}\n"
                f"{notification_date_line}",
            )

            complete_event(event.id)

    HEALTHCHECKS_EXPIRATION_UUID = os.getenv("HEALTHCHECKS_EXPIRATION_UUID")
    if HEALTHCHECKS_EXPIRATION_UUID:
        try:
            urllib.request.urlopen(f"https://hc-ping.com/{HEALTHCHECKS_EXPIRATION_UUID}", timeout=10)
        except socket.error as e:
            print("Ping failed: %s" % e)
