def test_start_handler(bot_app, update, context, mocker):
    mocker.patch("src.handlers.main.is_user_exists")
    mocker.patch("src.handlers.main.create_user")

    bot_app.call("start", update, context)

    current_user = update.effective_user

    # We say 'hello' to the user using his first and last name
    assert current_user.first_name in update.message.reply_markdown_v2.call_args[0][0]
    assert current_user.last_name in update.message.reply_markdown_v2.call_args[0][0]

    # We store 'user_id' to 'user_data' for the future reference
    assert context.user_data["user_id"] == current_user.id

    assert "The available commands" in update.message.reply_text.call_args[0][0]


def test_start_creating_entry_handler(bot_app, update, context):
    return_value = bot_app.call("start_creating_entry", update, context)

    assert "Enter subject / entry below" in update.message.reply_text.call_args[0][0]

    # We store 'user_id' to 'user_data' for the future reference
    assert context.user_data["user_id"] == update.effective_user.id

    assert return_value == 0  # Correct step is returned for correct conversation flow
