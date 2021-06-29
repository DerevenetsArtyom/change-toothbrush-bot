import datetime

from telegram.ext import ConversationHandler


def test_start_creating_entry_handler(bot_app, update, context):
    return_value = bot_app.call("start_creating_entry", update, context)

    assert "Enter subject / entry below" in update.message.reply_text.call_args[0][0]

    # We store 'user_id' to 'user_data' for the future reference
    assert context.user_data["user_id"] == update.effective_user.id

    # Correct step (SUBJECT) is returned for correct conversation flow
    assert return_value == 0


def test_add_new_entry_handler(bot_app, update, context):
    # emulate user input of subject
    user_input_text = "Buy new socks!"
    update.message.text = user_input_text

    return_value = bot_app.call("add_new_entry", update, context)

    assert user_input_text in update.message.reply_text.call_args[0][0]

    # We store 'entry' to 'user_data' for the future reference
    assert context.user_data["entry"] == user_input_text

    # Correct step (EXPIRATION_DATE) is returned for correct conversation flow
    assert return_value == 1


def test_add_expiration_date_custom_handler_invalid_date(bot_app, update, context):
    # emulate user input of incorrect date format
    update.message.text = "I've entered an invalid expiration date"

    return_value = bot_app.call("add_expiration_date_custom", update, context)

    assert "The date format is wrong" in update.message.reply_text.call_args[0][0]

    # Invalid 'expiration_date' was not stored in 'user_data'
    assert "expiration_date" not in context.user_data

    # Correct step (EXPIRATION_DATE) is returned for correct conversation flow
    assert return_value == 1


def test_add_expiration_date_custom_handler(bot_app, update, context):
    # emulate user input of correct date format
    update.message.text = "12-12-2021"

    return_value = bot_app.call("add_expiration_date_custom", update, context)

    assert "You've added an expiration date" in update.message.reply_text.call_args[0][0]

    # We store 'expiration_date' to 'user_data' for the future reference
    assert str(context.user_data["expiration_date"]) == "2021-12-12"  # DB keeps dates in slightly different format

    # Correct step (NOTIFICATION_DATE) is returned for correct conversation flow
    assert return_value == 2


# TODO: add test for 'add_expiration_date_from_choice'


def test_add_notification_date_custom_handler_invalid_date(bot_app, update, context):
    # emulate user input of incorrect date format
    update.message.text = "I've entered an invalid notification date"

    return_value = bot_app.call("add_notification_date_custom", update, context)

    assert "The date format is wrong" in update.message.reply_text.call_args[0][0]

    # Invalid 'expiration_date' was not stored in 'user_data'
    assert "notification_date" not in context.user_data

    # Correct step (NOTIFICATION_DATE) is returned for correct conversation flow
    assert return_value == 2


def test_add_notification_date_custom_handler(bot_app, update, context):
    # fill data in 'context.user_data' to be able to show correct output to the user
    context.user_data["entry"] = None
    context.user_data["expiration_date"] = datetime.date(2021, 12, 12)

    # emulate user input of correct date format
    update.message.text = "01-12-2021"

    return_value = bot_app.call("add_notification_date_custom", update, context)

    assert "You've added notification date" in update.message.reply_text.call_args[0][0]

    # We store 'notification_date' to 'user_data' for the future reference
    assert str(context.user_data["notification_date"]) == "2021-12-01"  # DB keeps dates in slightly different format

    # Correct step (CONFIRMATION) is returned for correct conversation flow
    assert return_value == 3


# TODO: add test for correct output of final message in 'add_notification_date_custom' (or in integrations tests?)
# TODO: add test for 'add_notification_date_from_choice'


def test_confirmation_handler(bot_app, update, context, mocker):
    # TODO: I can't patch 'create_event' for some reasons ((
    mocker.patch("src.handlers.conversation.create_event")

    return_value = bot_app.call("confirmation", update, context)

    assert "Great! The entry has been created" in update.message.reply_text.call_args[0][0]
    assert return_value == ConversationHandler.END
