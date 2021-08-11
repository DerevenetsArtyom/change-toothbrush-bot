import os
from datetime import time

import pytz
import sentry_sdk
from telegram.ext import Updater

from handlers.main import setup_dispatcher
from jobs import check_events_for_expiration, check_events_for_notification
from models import create_tables


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if telegram_token is None:
        raise Exception("Please setup the .env variable TELEGRAM_TOKEN.")

    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    job_queue.run_daily(check_events_for_notification, time(hour=9, tzinfo=pytz.timezone("Europe/Kiev")))
    job_queue.run_daily(check_events_for_expiration, time(hour=9, minute=10, tzinfo=pytz.timezone("Europe/Kiev")))

    setup_dispatcher(dispatcher)

    HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")

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
        PORT = int(os.getenv("PORT", "5000"))
        DOMAIN_NAME = os.getenv("DOMAIN_NAME")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            # url_path=telegram_token,
            # webhook_url=f"https://{HEROKU_APP_NAME}.{DOMAIN_NAME}/{telegram_token}",
            webhook_url=f"https://{HEROKU_APP_NAME}.{DOMAIN_NAME}",
        )

        updater.idle()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    create_tables()
    main()
