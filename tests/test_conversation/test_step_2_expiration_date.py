import datetime
from datetime import timedelta

import pytest

from constants import EXPIRATION_DATE, NOTIFICATION_DATE


def test_add_expiration_date_custom_handler(bot_app, update, context):
    update.message.text = "12-12-2021"  # emulate user input of correct date format

    return_value = bot_app.call("add_expiration_date_custom", update, context)

    assert "You've added an expiration date" in update.message.reply_text.call_args[0][0]

    # We store 'expiration_date' in 'user_data' for the future reference
    assert str(context.user_data["expiration_date"]) == "2021-12-12"  # DB keeps dates in slightly different format

    # Correct step is returned for correct conversation flow
    assert return_value == NOTIFICATION_DATE


def test_add_expiration_date_custom_handler_invalid_date(bot_app, update, context):
    update.message.text = "I've entered an invalid expiration date"  # emulate user input of incorrect date format

    return_value = bot_app.call("add_expiration_date_custom", update, context)

    assert "The date format is wrong" in update.message.reply_text.call_args[0][0]

    # Invalid 'expiration_date' was not stored in 'user_data'
    assert "expiration_date" not in context.user_data

    # Correct step is returned for correct conversation flow
    assert return_value == EXPIRATION_DATE


@pytest.mark.parametrize("user_expiration_choice", ["week", "month", "3month"])
def test_add_expiration_date_from_choice(bot_app, update, context, user_expiration_choice):
    update.callback_query.data = f"expiration_date:{user_expiration_choice}"  # emulate user's correct choice

    return_value = bot_app.call("add_expiration_date_from_choice", update, context)

    expiration_date = None
    now = datetime.datetime.now().date()

    if user_expiration_choice == "week":
        expiration_date = now + timedelta(weeks=1)
    elif user_expiration_choice == "month":
        expiration_date = now + timedelta(days=30)
    elif user_expiration_choice == "3month":
        expiration_date = now + timedelta(days=92)

    assert context.user_data["expiration_date"] == expiration_date
    assert "You've added an expiration date" in update.callback_query.message.reply_text.call_args[0][0]

    # Correct step is returned for correct conversation flow
    assert return_value == NOTIFICATION_DATE


def test_add_expiration_date_from_choice_invalid_choice(bot_app, update, context):
    update.callback_query.data = "invalid-choice-user-somehow-put"

    return_value = bot_app.call("add_expiration_date_from_choice", update, context)

    # Invalid 'expiration_date' was not stored in 'user_data'
    assert "expiration_date" not in context.user_data

    # We print warning and abort the flow
    assert update.callback_query.message.reply_text.call_args[0][0] == "Something went wrong. Don't know your choice"
    assert return_value is None
