import os
from datetime import time

import pytz
from dotenv import load_dotenv
from telegram.ext import CallbackContext, Updater

from handlers.main import setup_dispatcher
from models import User, complete_event, create_tables, get_events_for_expiration, get_events_for_notification
from utils import prettify_date

load_dotenv()


def check_events_for_notification(context: CallbackContext):
    for user in User.select():
        today_events_to_notify = get_events_for_notification(user.id)

        for event in today_events_to_notify:
            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"You wanted me to notify you about:"
                f"Subject: {event.subject}\n"
                f"Notification date: {prettify_date(event.notification_date)}\n"
                f"Expiration date: {prettify_date(event.expiration_date)}\n",
            )


def check_events_for_expiration(context: CallbackContext):
    for user in User.select():
        today_events_to_expire = get_events_for_expiration(user.id)

        for event in today_events_to_expire:
            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"This event is expired today:"
                f"Subject: {event.subject}\n"
                f"Expiration date: {prettify_date(event.expiration_date)}\n"
                f"(you were notified on: {prettify_date(event.notification_date)})\n",
            )

            complete_event(event.id)


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if telegram_token is None:
        raise Exception("Please setup the .env variable TELEGRAM_TOKEN.")

    PORT = int(os.getenv("PORT", "8443"))
    HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    job_queue.run_daily(check_events_for_notification, time(hour=9, tzinfo=pytz.timezone("Europe/Kiev")))
    job_queue.run_daily(check_events_for_expiration, time(hour=9, minute=10, tzinfo=pytz.timezone("Europe/Kiev")))

    setup_dispatcher(dispatcher)

    if HEROKU_APP_NAME is None:  # pooling mode, local development
        print("Can't detect 'HEROKU_APP_NAME' env. Running bot in pooling mode.")
        print("Note: this is not a great way to deploy the bot in Heroku.")

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
        # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    else:  # webhook mode, production-like Heroku setup
        print(
            f"Running bot in webhook mode. Make sure that this url is correct: https://{HEROKU_APP_NAME}.herokuapp.com/"
        )
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/"
            # url_path=TELEGRAM_TOKEN,
            # webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{TELEGRAM_TOKEN}"
        )

        updater.idle()


if __name__ == "__main__":
    create_tables()
    main()
