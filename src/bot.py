import os
from datetime import datetime, time

import pytz
from dotenv import load_dotenv
from telegram.ext import CallbackContext, Updater

from handlers.main import setup_dispatcher
from models import Event, User, create_tables
from utils import prettify_date

load_dotenv()


def check_database(context: CallbackContext):
    # chat_id = "348029891"
    # context.bot.send_message(chat_id=chat_id, text="JOB EXECUTED!!!")

    today = datetime.now().date()

    for user in User.select():
        today_events = user.events.select().where(Event.notification_date == today)

        for event in today_events:
            context.bot.send_message(
                chat_id=user.chat_id,
                text=f"You wanted me to notify you about today:"
                f"Subject: {event.subject}\n"
                f"Notification date: {prettify_date(event.notification_date)}\n"
                f"Expiration date: {prettify_date(event.expiration_date)}\n",
            )


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

    job_queue.run_daily(check_database, time(hour=9, tzinfo=pytz.timezone("Europe/Kiev")))

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
