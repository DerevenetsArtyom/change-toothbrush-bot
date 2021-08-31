import datetime

from constants import CONFIRMATION, NOTIFICATION_DATE

# TODO: add test for correct output of final message in 'add_notification_date_custom' (or in integrations tests?)
# TODO: add test for 'add_notification_date_from_choice'


def test_add_notification_date_custom_handler(bot_app, update, context):
    # fill data in 'context.user_data' to be able to show correct output to the user
    context.user_data["entry"] = None
    context.user_data["expiration_date"] = datetime.date(2021, 12, 12)

    update.message.text = "01-12-2021"  # emulate user input of correct date format

    return_value = bot_app.call("add_notification_date_custom", update, context)

    assert "You've added notification date" in update.message.reply_text.call_args[0][0]

    # We store 'notification_date' to 'user_data' for the future reference
    assert str(context.user_data["notification_date"]) == "2021-12-01"  # DB keeps dates in slightly different format

    # Correct step is returned for correct conversation flow
    assert return_value == CONFIRMATION


def test_add_notification_date_custom_handler_invalid_date(bot_app, update, context):
    update.message.text = "I've entered an invalid notification date"  # emulate user input of incorrect date format

    return_value = bot_app.call("add_notification_date_custom", update, context)

    assert "The date format is wrong" in update.message.reply_text.call_args[0][0]

    # Invalid 'expiration_date' was not stored in 'user_data'
    assert "notification_date" not in context.user_data

    # Correct step is returned for correct conversation flow
    assert return_value == NOTIFICATION_DATE
