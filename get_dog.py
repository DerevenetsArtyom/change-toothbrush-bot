import logging
import os

import requests
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler

load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def bop(update, context):
    url = get_url()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    updater = Updater(telegram_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('bop', bop))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
