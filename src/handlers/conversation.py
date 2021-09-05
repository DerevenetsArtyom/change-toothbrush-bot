from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from telegram.utils.helpers import escape_markdown

from constants import CONFIRMATION, EXPIRATION_DATE, NOTIFICATION_DATE, SUBJECT, USER_INPUT_DATE_FORMAT
from models import Event
from utils import logger, prettify_date

expiration_date_keyboard = [
    [InlineKeyboardButton(text="In a week!", callback_data="expiration_date:week")],
    [InlineKeyboardButton(text="In a month!", callback_data="expiration_date:month")],
    [InlineKeyboardButton(text="In a 3 month!", callback_data="expiration_date:3month")],
]

expiration_date_keyboard_markup = InlineKeyboardMarkup(expiration_date_keyboard)

notification_date_keyboard = [
    [InlineKeyboardButton(text="A week beforehand!", callback_data="notification_date:week")],
    [InlineKeyboardButton(text="A month beforehand!", callback_data="notification_date:month")],
    [InlineKeyboardButton(text="3 months beforehand!", callback_data="notification_date:3month")],
]

notification_date_keyboard_markup = InlineKeyboardMarkup(notification_date_keyboard)


def get_confirmation_message(user_data):
    notification_date = user_data["notification_date"]

    first_line = "You've added notification date! Confirm the data below:"
    notification_line = ""

    if not notification_date:
        first_line = "Confirm the data below:"

    if notification_date:
        notification_line = f'Notification date - "{prettify_date(user_data["notification_date"])}"\n'

    return (
        f"{first_line}\n\n"
        f'Subject - "{user_data["entry"]}"\n'
        f"{notification_line}"
        f'Expiration date - "{prettify_date(user_data["expiration_date"])}"\n\n'
        f"If everything is correct, please enter /done command.\n"
        f"If not, enter /cancel command and start again."
    )


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

    update.message.reply_text(
        f"You've added an entry \- *_{escape_markdown(user_text, version=2)}_*\n"
        f"Now select an __expiration date__ from the list or add it manually \(dd\-mm\-yyyy\):",
        reply_markup=expiration_date_keyboard_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return EXPIRATION_DATE


#############################
# EXPIRATION_DATE step (№2) #
#############################


def add_expiration_date_manually(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data %s", context.user_data)

    try:
        context.user_data["expiration_date"] = datetime.strptime(update.message.text, USER_INPUT_DATE_FORMAT).date()
    except ValueError:
        logger.warning("wrong input date format - %s", update.message.text)
        update.message.reply_text("The date format is wrong. Try again, please. Example: 21-12-2021")
        return EXPIRATION_DATE

    update.message.reply_text(
        "You've added an expiration date\! \n"
        "Now select a __notification date__ from the list or add it manually \(dd\-mm\-yyyy\): \n"
        "If you don't want to set it \- send /skip",
        reply_markup=notification_date_keyboard_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return NOTIFICATION_DATE


def add_expiration_date_from_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    desired_time_period = query.data.split(":")[-1]

    expiration_date = None
    now = datetime.now().date()

    # TODO: move to helper function (and reuse in tests) ?
    if desired_time_period == "week":
        expiration_date = now + timedelta(weeks=1)
    elif desired_time_period == "month":
        expiration_date = now + timedelta(days=30)
    elif desired_time_period == "3month":
        expiration_date = now + timedelta(days=92)

    context.user_data["expiration_date"] = expiration_date

    query.message.reply_text(
        "You've added an expiration date\! \n"
        "Now select a __notification date__ from list or add it manually \(dd\-mm\-yyyy\): \n"
        "If you don't want to set it \- send /skip",
        reply_markup=notification_date_keyboard_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return NOTIFICATION_DATE


###############################
# NOTIFICATION_DATE step (№3) #
###############################


def add_notification_date_manually(update: Update, context: CallbackContext) -> int:
    logger.info("update.message.text %s", update.message.text)
    logger.info("context.user_data before %s", context.user_data)

    try:
        context.user_data["notification_date"] = datetime.strptime(update.message.text, USER_INPUT_DATE_FORMAT).date()
    except ValueError:
        logger.warning("wrong input date format - %s", update.message.text)
        update.message.reply_text("The date format is wrong. Try again, please. Example: 21-12-2021")
        return NOTIFICATION_DATE

    update.message.reply_text(get_confirmation_message(context.user_data))

    return CONFIRMATION


def add_notification_date_from_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if ":" not in query.data:
        query.message.reply_text("Something went wrong. Don't know your choice")
        return

    desired_time_period = query.data.split(":")[-1]

    expiration_date = context.user_data.get("expiration_date")
    if not expiration_date:
        logger.warning("User 'expiration date' is not set. Present user data - %s", context.user_data)
        query.message.reply_text("Something went wrong. You have not set an 'expiration date'. Please do manually:")
        return EXPIRATION_DATE

    notification_date = None

    if desired_time_period == "week":
        notification_date = expiration_date - timedelta(weeks=1)
    elif desired_time_period == "month":
        notification_date = expiration_date - timedelta(days=30)
    elif desired_time_period == "3month":
        notification_date = expiration_date - timedelta(days=92)

    context.user_data["notification_date"] = notification_date

    query.message.reply_text(get_confirmation_message(context.user_data))

    return CONFIRMATION


def skip_notification_date(update: Update, context: CallbackContext) -> int:
    logger.info("User %s did not set notification date", update.message.from_user.first_name)

    context.user_data["notification_date"] = None
    update.message.reply_text(get_confirmation_message(context.user_data))

    return CONFIRMATION


##########################
# CONFIRMATION step (№4) #
##########################


def confirmation(update: Update, context: CallbackContext) -> int:
    logger.info("context.user_data %s", context.user_data)

    Event.create_event(context.user_data)

    update.message.reply_text(
        "Great! The entry has been created!\n"
        "Use /add command if you want to add more or /list to check all your events"
    )

    # TODO: show to user newly created data from DB record

    return ConversationHandler.END
