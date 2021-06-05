import os

from dotenv import load_dotenv
from telegram.ext import (
    Updater,
)

from handlers import setup_dispatcher
from models import create_tables

load_dotenv()


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if telegram_token is None:
        raise Exception("Please setup the .env variable TELEGRAM_TOKEN.")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    setup_dispatcher(dispatcher)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    create_tables()
    main()
