import datetime
from datetime import timedelta

import pytest

from constants import CONFIRMATION, EXPIRATION_DATE, NOTIFICATION_DATE


def test_add_notification_date_manually_handler(bot_app, update, context):
    # fill data in 'context.user_data' to be able to show correct output to the user
    context.user_data["entry"] = None
    context.user_data["expiration_date"] = datetime.date(2021, 12, 12)

    update.message.text = "01-12-2021"  # emulate user input of correct date format

    return_value = bot_app.call("add_notification_date_manually", update, context)

    assert "You've added notification date" in update.message.reply_text.call_args[0][0]

    assert str(context.user_data["notification_date"]) == "2021-12-01"  # DB keeps dates in slightly different format

    # Correct step is returned for correct conversation flow
    assert return_value == CONFIRMATION


def test_add_notification_date_manually_confirmation_message(bot_app, update, context):
    user_entry = "Change a toothbrush"

    context.user_data = {"entry": user_entry, "expiration_date": datetime.date(2021, 12, 12)}

    update.message.text = "01-12-2021"  # emulate user input of correct date format

    bot_app.call("add_notification_date_manually", update, context)

    confirmation_message = (
        f"You've added notification date! Confirm the data below:\n\n"
        f'Subject - "{user_entry}"\n'
        f'Notification date - "01 December 2021"\n'
        f'Expiration date - "12 December 2021"\n\n'
        f"If everything is correct, please enter /done command.\n"
        f"If not, enter /cancel command and start again."
    )

    assert update.message.reply_text.call_args[0][0] == confirmation_message


@pytest.mark.parametrize("invalid_input", ["invalid notification date", "42", ""])
def test_add_notification_date_manually_handler_invalid_date(bot_app, update, context, invalid_input):
    update.message.text = invalid_input

    return_value = bot_app.call("add_notification_date_manually", update, context)

    assert "The date format is wrong" in update.message.reply_text.call_args[0][0]

    # Invalid 'notification_date' was not stored in 'user_data'
    assert "notification_date" not in context.user_data

    # Correct step is returned for correct conversation flow
    assert return_value == NOTIFICATION_DATE


@pytest.mark.parametrize("user_notification_choice", ["week", "month", "3month"])
def test_add_notification_date_from_choice(bot_app, update, context, user_notification_choice):
    expiration_date = datetime.date(2021, 12, 12)
    notification_date = None

    update.callback_query.data = f"notification_date:{user_notification_choice}"  # emulate user's correct choice

    # fill data in 'context.user_data' to be able to show correct output to the user
    context.user_data["entry"] = None
    context.user_data["expiration_date"] = expiration_date

    return_value = bot_app.call("add_notification_date_from_choice", update, context)

    if user_notification_choice == "week":
        notification_date = expiration_date - timedelta(weeks=1)
    elif user_notification_choice == "month":
        notification_date = expiration_date - timedelta(days=30)
    elif user_notification_choice == "3month":
        notification_date = expiration_date - timedelta(days=92)

    assert context.user_data["notification_date"] == notification_date
    assert "You've added notification date" in update.callback_query.message.reply_text.call_args[0][0]

    # Correct step is returned for correct conversation flow
    assert return_value == CONFIRMATION


def test_add_notification_date_from_choice_invalid_choice(bot_app, update, context):
    update.callback_query.data = "invalid-choice-user-somehow-put"

    return_value = bot_app.call("add_notification_date_from_choice", update, context)

    # Invalid 'notification_date' was not stored in 'user_data'
    assert "notification_date" not in context.user_data

    # We print warning and abort the flow
    assert update.callback_query.message.reply_text.call_args[0][0] == "Something went wrong. Don't know your choice"
    assert return_value is None


def test_add_notification_date_from_choice_missing_data(bot_app, update, context):
    update.callback_query.data = "notification_date:does-not-matter-now"

    # emulate missing (somehow) entering "expiration date" on previous step
    context.user_data["expiration_date"] = None

    return_value = bot_app.call("add_notification_date_from_choice", update, context)

    # Invalid 'notification_date' was not stored in 'user_data'
    assert "notification_date" not in context.user_data

    warning_message = "You have not set an 'expiration date'. Please do manually"
    assert warning_message in update.callback_query.message.reply_text.call_args[0][0]
    assert return_value == EXPIRATION_DATE
