import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from utils import error_logger

load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


# function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()}\!')


def add_new_entry(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('You are going to add a new entry!')


def show_pending(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Soon we\'ll show you all your pending entries')


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    # Handlers for main commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_new", add_new_entry))
    dispatcher.add_handler(CommandHandler("list", show_pending))

    # add an handler for normal text (not commands)
    # dispatcher.add_handler(MessageHandler(Filters.text, text))

    # add an handler for errors
    dispatcher.add_error_handler(error_logger)

    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
