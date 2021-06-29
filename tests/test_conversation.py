def test_start_creating_entry_handler(bot_app, update, context):
    return_value = bot_app.call("start_creating_entry", update, context)

    assert "Enter subject / entry below" in update.message.reply_text.call_args[0][0]

    # We store 'user_id' to 'user_data' for the future reference
    assert context.user_data["user_id"] == update.effective_user.id

    assert return_value == 0  # Correct step is returned for correct conversation flow
