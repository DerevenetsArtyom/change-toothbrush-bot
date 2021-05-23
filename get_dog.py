import logging
import os
import re

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


def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def bop(update, context):
    url = get_image_url()
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
