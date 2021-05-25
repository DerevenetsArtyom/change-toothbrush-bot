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

"""
It should look like:

1. Add topic/subject of notification
2. Add expiration date - when event should expire and you should be notified
3. Add intermediate notification date (optional) - when user should be notified first time and take some action
4. Confirmation! (user should verify and approve collected data from his input)
"""


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()}\!')


def add_new_entry(update: Update, context: CallbackContext) -> None:
    """
    Should look like: /add_new [action/verb] [thing/subject] -> /add_new купил фильтр для воды
    """

    action = context.args[0]
    thing = " ".join(context.args[1:])

    update.message.reply_text(f'You are going to add a new entry - action: {action}, thing: {thing}')


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
