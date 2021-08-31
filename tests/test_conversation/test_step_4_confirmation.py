from telegram.ext import ConversationHandler


def test_confirmation_handler(bot_app, update, context, mocker):
    # I was not able to patch "create_event" as regular function for some reasons:
    # neither `mocker.patch("src.handlers.conversation.create_event")`
    # nor `@patch("src.handlers.conversation.create_event")` worked 🙄.
    # So, I had to move this method to "Event" model and patch it here.
    # Another strange point - that test (as well as the tests above) uses real DB if patching is not present.

    user_data = {"entry": "This is test entry", "user_id": 1}
    context.user_data = user_data

    create_event_patch = mocker.patch("src.handlers.conversation.Event.create_event")

    return_value = bot_app.call("confirmation", update, context)

    create_event_patch.assert_called_with(user_data)

    assert "Great! The entry has been created" in update.message.reply_text.call_args[0][0]
    assert return_value == ConversationHandler.END
