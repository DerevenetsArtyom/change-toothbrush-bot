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
    """
    User should be able to request from bot all his pending events (that are waiting its notification time).

    #TODO: Improvement - not just plain list, but list of entries with action buttons: remove, prolong etc.
    """

    update.message.reply_text('Soon we\'ll show you all your pending entries')


def show_archived(update: Update, context: CallbackContext) -> None:
    """
    User should be able to request from bot all his archived events (it's "completed" events actually).

    """

    update.message.reply_text('Soon we\'ll show you all your archived entries')


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    # Handlers for main commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_new", add_new_entry))
    dispatcher.add_handler(CommandHandler("list", show_pending))
    dispatcher.add_handler(CommandHandler("list_old", show_archived))

    # add an handler for normal text (not commands)
    # dispatcher.add_handler(MessageHandler(Filters.text, text))

    # add an handler for errors
    dispatcher.add_error_handler(error_logger)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
