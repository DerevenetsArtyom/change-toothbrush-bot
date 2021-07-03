from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from models import Event
from utils import logger, prettify_date

SUBJECT, EXPIRATION_DATE, NOTIFICATION_DATE, CONFIRMATION = [0, 1, 2, 3]

USER_INPUT_DATE_FORMAT = "%d-%m-%Y"


#####################
# SUBJECT step (№1) #
#####################


def start_creating_entry(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Enter your subject or event below:")

    # Duplicate adding user_id to context here (if '/start' command was skipped)
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
        f"You've added an entry \- *_{user_text}_*\n"
        f"Now select an __expiration date__ from list or add it manually \(dd\-mm\-yyyy\):",
        reply_markup=markup,
        parse_mode="MarkdownV2",
    )

    return EXPIRATION_DATE


#############################
# EXPIRATION_DATE step (№2) #
#############################


def add_expiration_date_custom(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    try:
        # TODO: add validation for date to be in the future only
        context.user_data["expiration_date"] = datetime.strptime(update.message.text, USER_INPUT_DATE_FORMAT).date()
    except ValueError:
        logger.info("wrong input date format - %s", update.message.text)
        update.message.reply_text("The date format is wrong. Try again, please. Example: 21-12-2021")
        return EXPIRATION_DATE

    keyboard = [
        [InlineKeyboardButton(text="A week beforehand!", callback_data="notification_date:week")],
        [InlineKeyboardButton(text="A month beforehand!", callback_data="notification_date:month")],
        [InlineKeyboardButton(text="3 months beforehand!", callback_data="notification_date:3month")],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "You've added an expiration date\! \n"
        "Now select a __notification date__ from list or add it manually \(dd\-mm\-yyyy\):",
        reply_markup=markup,
        parse_mode="MarkdownV2",
    )

    return NOTIFICATION_DATE


def add_expiration_date_from_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    desired_time_period = query.data.split(":")[-1]

    expiration_date = None
    now = datetime.now().date()

    if desired_time_period == "week":
        expiration_date = now + timedelta(weeks=1)
    elif desired_time_period == "month":
        expiration_date = now + timedelta(days=30)
    elif desired_time_period == "3month":
        expiration_date = now + timedelta(days=92)

    context.user_data["expiration_date"] = expiration_date

    # TODO: this code snippet duplicates the one in 'expiration_date' ('update' -> 'query')
    keyboard = [
        [InlineKeyboardButton(text="A week beforehand!", callback_data="notification_date:week")],
        [InlineKeyboardButton(text="A month beforehand!", callback_data="notification_date:month")],
        [InlineKeyboardButton(text="3 months beforehand!", callback_data="notification_date:3month")],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(
        "You've added an expiration date\! \n"
        "Now select a __notification date__ from list or add it manually \(dd\-mm\-yyyy\):",
        reply_markup=markup,
        parse_mode="MarkdownV2",
    )

    return NOTIFICATION_DATE


###############################
# NOTIFICATION_DATE step (№3) #
###############################


def add_notification_date_custom(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data before %s", context.user_data)

    try:
        # TODO: add validation for date to be in the future only and SHOULD BE BEFORE EXPIRATION DATE
        context.user_data["notification_date"] = datetime.strptime(update.message.text, USER_INPUT_DATE_FORMAT).date()
    except ValueError:
        logger.info("wrong input date format - %s", update.message.text)
        update.message.reply_text("The date format is wrong. Try again, please. Example: 21-12-2021")
        return NOTIFICATION_DATE

    update.message.reply_text(
        f"You've added notification date! Confirm the data below:\n\n"
        f'Subject - "{context.user_data["entry"]}"\n'
        f'Notification date - "{prettify_date(context.user_data["notification_date"])}"\n'
        f'Expiration date - "{prettify_date(context.user_data["expiration_date"])}"\n\n'
        f"If everything is correct, please enter /done command. "
        f"If not, enter /cancel command and start again."
    )

    return CONFIRMATION


def add_notification_date_from_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    desired_time_period = query.data.split(":")[-1]

    expiration_date = context.user_data["expiration_date"]
    notification_date = None

    if desired_time_period == "week":
        notification_date = expiration_date - timedelta(weeks=1)
    elif desired_time_period == "month":
        notification_date = expiration_date - timedelta(days=30)
    elif desired_time_period == "3month":
        notification_date = expiration_date - timedelta(days=92)

    context.user_data["notification_date"] = notification_date

    # TODO: this code snippet duplicates the one in 'notification_date' ('update' -> 'query')
    query.message.reply_text(
        f"You've added notification date! Confirm the data below:\n\n"
        f'Subject - "{context.user_data["entry"]}"\n'
        f'Notification date - "{prettify_date(context.user_data["notification_date"])}"\n'
        f'Expiration date - "{prettify_date(context.user_data["expiration_date"])}"\n\n'
        f"If everything is correct, please enter /done command. "
        f"If not, enter /cancel command and start again."
    )

    return CONFIRMATION


##########################
# CONFIRMATION step (№4) #
##########################


def confirmation(update: Update, context: CallbackContext) -> int:
    logger.info("context.user_data %s", context.user_data)

    Event.create_event(context.user_data)

    update.message.reply_text("Great! The entry has been created!\n Use /add command if you want to add more.")

    # TODO: show to user newly created data from DB record

    return ConversationHandler.END
