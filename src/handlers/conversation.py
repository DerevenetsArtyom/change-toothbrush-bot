from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from models import create_event
from utils import logger

SUBJECT, EXPIRATION_DATE, NOTIFICATION_DATE, CONFIRMATION = [0, 1, 2, 3]


#####################
# SUBJECT step (№1) #
#####################


def start_creating_entry(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Enter subject / entry below")

    # Duplicate it here, if '/start' command was skipped
    context.user_data["user_id"] = update.effective_user.id

    return SUBJECT


def add_new_entry(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    logger.info("update.message.text %s", user_text)

    context.user_data["entry"] = user_text

    keyboard = [
        [InlineKeyboardButton(text="In a week!", callback_data="expiration_date:week")],
        [InlineKeyboardButton(text="In a month!", callback_data="expiration_date:month")],
        [InlineKeyboardButton(text="In a 3 month!", callback_data="expiration_date:3month")],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"You've added an entry - '{user_text}'!\n" f"Now select from list or add expiration date manually:",
        reply_markup=markup,
    )

    return EXPIRATION_DATE


#############################
# EXPIRATION_DATE step (№2) #
#############################


def add_expiration_date_custom(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    context.user_data["expiration_date"] = update.message.text

    keyboard = [
        [InlineKeyboardButton(text="A week beforehand!", callback_data="notification_date:week")],
        [InlineKeyboardButton(text="A month beforehand!", callback_data="notification_date:month")],
        [InlineKeyboardButton(text="3 month beforehand!", callback_data="notification_date:3month")],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "You've added expiration time!\n" "Now select from list or add notification time manually:", reply_markup=markup
    )

    return NOTIFICATION_DATE


def add_expiration_date_from_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    # TODO: calculate expiration date based on user choice and put it to context.user_data["expiration_date"] here

    context.user_data["expiration_date"] = query.data.split(":")[-1]

    # TODO: this code snippet duplicates the one in 'expiration_date' ('update' -> 'query')
    keyboard = [
        [InlineKeyboardButton(text="A week beforehand!", callback_data="notification_date:week")],
        [InlineKeyboardButton(text="A month beforehand!", callback_data="notification_date:month")],
        [InlineKeyboardButton(text="3 month beforehand!", callback_data="notification_date:3month")],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(
        "You've added expiration time! \nNow select from list or add notification time manually:", reply_markup=markup
    )

    return NOTIFICATION_DATE


###############################
# NOTIFICATION_DATE step (№3) #
###############################


def add_notification_date_custom(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data before %s", context.user_data)

    context.user_data["notification_date"] = update.message.text

    logger.info("context.user_data after %s", context.user_data)

    update.message.reply_text(
        f"You've added notification time! Confirm tha data below:\n\n"
        f'Subject - "{context.user_data["entry"]}"\n'
        f'Expiration time - "{context.user_data["expiration_date"]}"\n'
        f'Notification time - "{context.user_data["notification_date"]}"\n\n'
        f"If everything is correct, please enter /done command. "
        f"If not, enter /cancel command."
    )

    return CONFIRMATION


def add_notification_date_from_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    # TODO: calculate notification date based on user choice and put it to context.user_data["notification_date"] here
    context.user_data["notification_date"] = query.data.split(":")[-1]

    # TODO: this code snippet duplicates the one in 'notification_date' ('update' -> 'query')
    query.message.reply_text(
        f"You've added notification time! Confirm tha data below:\n\n"
        f'Subject - "{context.user_data["entry"]}"\n'
        f'Expiration time - "{context.user_data["expiration_date"]}"\n'
        f'Notification time - "{context.user_data["notification_date"]}"\n\n'
        f"If everything is correct, please enter /done command. "
        f"If not, enter /cancel command."
    )

    return CONFIRMATION


##########################
# CONFIRMATION step (№4) #
##########################


def confirmation(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    create_event(context.user_data)

    update.message.reply_text("Great! The entry has been created!\n Use /add command if you want to add more.")

    # TODO: show to user newly created data from DB record

    return ConversationHandler.END
