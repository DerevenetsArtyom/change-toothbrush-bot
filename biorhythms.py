import datetime
import math
import os

from dotenv import load_dotenv
from telegram.ext import MessageHandler, Filters, Updater, CommandHandler

load_dotenv()

STATE = None

BIRTH_YEAR = 1
BIRTH_MONTH = 2
BIRTH_DAY = 3


# function to handle the /start command
def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f'Hi, {first_name}, nice to meet yaa!!!')
    start_getting_birthday_info(update, context)


def start_getting_birthday_info(update, context):
    global STATE
    STATE = BIRTH_YEAR
    update.message.reply_text(f"I would need to know your birthday, so tell me what year did you born in...")


def received_birth_year(update, context):
    global STATE

    try:
        today = datetime.date.today()
        year = int(update.message.text)

        if year > today.year:
            raise ValueError("invalid value")

        context.user_data['birth_year'] = year
        update.message.reply_text(f"ok, now I need to know the month (in numerical form)...")
        STATE = BIRTH_MONTH
    except:
        update.message.reply_text("it's funny but it doesn't seem to be correct...")


def received_birth_month(update, context):
    global STATE

    try:
        month = int(update.message.text)

        if month > 12 or month < 1:
            raise ValueError("invalid value")

        context.user_data['birth_month'] = month
        update.message.reply_text(f"great! And now, the day...")
        STATE = BIRTH_DAY
    except:
        update.message.reply_text("it's funny but it doesn't seem to be correct...")


def received_birth_day(update, context):
    global STATE

    try:
        today = datetime.date.today()
        dd = int(update.message.text)
        yyyy = context.user_data['birth_year']
        mm = context.user_data['birth_month']
        birthday = datetime.date(year=yyyy, month=mm, day=dd)

        if today - birthday < datetime.timedelta(days=0):
            raise ValueError("invalid value")

        context.user_data['birthday'] = birthday
        STATE = None
        update.message.reply_text(f'ok, you born on {birthday}')

    except:
        update.message.reply_text("it's funny but it doesn't seem to be correct...")


# function to handle the /help command
def help(update, context):
    update.message.reply_text('help command received')


# function to handle normal text
def text(update, context):
    global STATE

    if STATE == BIRTH_YEAR:
        return received_birth_year(update, context)

    if STATE == BIRTH_MONTH:
        return received_birth_month(update, context)

    if STATE == BIRTH_DAY:
        return received_birth_day(update, context)


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('an error occurred')


# This function is called when the /biorhythm command is issued
def get_biorhythm(update, context):
    user_biorhythm = calculate_biorhythm(context.user_data['birthday'])

    update.message.reply_text(f"Physical: {user_biorhythm['physical']}")
    update.message.reply_text(f"Emotional: {user_biorhythm['emotional']}")
    update.message.reply_text(f"Intellectual: {user_biorhythm['intellectual']}")


def calculate_biorhythm(birthday_date):
    today = datetime.date.today()
    delta = today - birthday_date
    days = delta.days

    physical = math.sin(2 * math.pi * (days / 23))
    emotional = math.sin(2 * math.pi * (days / 28))
    intellectual = math.sin(2 * math.pi * (days / 33))

    biorhythm = {}
    biorhythm['physical'] = int(physical * 10000) / 100
    biorhythm['emotional'] = int(emotional * 10000) / 100
    biorhythm['intellectual'] = int(intellectual * 10000) / 100

    biorhythm['physical_critical_day'] = (physical == 0)
    biorhythm['emotional_critical_day'] = (emotional == 0)
    biorhythm['intellectual_critical_day'] = (intellectual == 0)

    return biorhythm


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    # create the updater, that will automatically create also a dispatcher and a queue to make them dialog
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    # add handlers for /start and /help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))

    # add an handler for our biorhythm command
    dispatcher.add_handler(CommandHandler("biorhythm", get_biorhythm))

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
