import os

from dotenv import load_dotenv
from telegram.ext import MessageHandler, Filters, Updater, CommandHandler

load_dotenv()


# function to handle the /start command
def start(update, context):
    update.message.reply_text('start command received')


# function to handle the /help command
def help(update, context):
    update.message.reply_text('help command received')


# function to handle normal text
def text(update, context):
    text_received = update.message.text
    update.message.reply_text(f'did you said "{text_received}" ?')


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('an error occurred')


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    # add handlers for /start and /help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))

    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
