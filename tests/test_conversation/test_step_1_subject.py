from constants import EXPIRATION_DATE, SUBJECT


def test_start_creating_entry_handler(bot_app, update, context):
    return_value = bot_app.call("start_creating_entry", update, context)

    assert "Enter your subject or event below" in update.message.reply_text.call_args[0][0]

    # We store 'user_id' in 'user_data' for the future reference
    assert context.user_data["user_id"] == update.effective_user.id

    # Correct step is returned for correct conversation flow
    assert return_value == SUBJECT


def test_add_new_entry_handler(bot_app, update, context):
    user_input_text = "Buy new socks"
    update.message.text = user_input_text  # emulate user input of subject

    return_value = bot_app.call("add_new_entry", update, context)

    assert user_input_text in update.message.reply_text.call_args[0][0]

    # We store 'entry' in 'user_data' for the future reference
    assert context.user_data["entry"] == user_input_text

    # Correct step is returned for correct conversation flow
    assert return_value == EXPIRATION_DATE
