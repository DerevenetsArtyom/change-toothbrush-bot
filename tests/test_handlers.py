import pytest


def test_start_handler(bot_app, update, context, mocker):
    mocker.patch("src.handlers.main.is_user_exists")
    mocker.patch("src.handlers.main.create_user")

    bot_app.call("start", update, context)

    current_user = update.effective_user

    # We say 'hello' to the user using his first and last name
    assert current_user.first_name in update.message.reply_markdown_v2.call_args[0][0]
    assert current_user.last_name in update.message.reply_markdown_v2.call_args[0][0]

    # We store 'user_id' in 'user_data' for the future reference
    assert context.user_data["user_id"] == current_user.id

    assert "The available commands" in update.message.reply_text.call_args[0][0]


@pytest.mark.parametrize("is_user_exist", [True, False])
def test_new_user_creation_in_start_handler(bot_app, update, context, mocker, is_user_exist):
    is_user_exists_mock = mocker.patch("src.handlers.main.is_user_exists", return_value=is_user_exist)
    create_user_mock = mocker.patch("src.handlers.main.create_user")

    bot_app.call("start", update, context)

    # 'is_user_exists' check itself is called indeed, but 'create_user' function should not
    if is_user_exist is True:
        is_user_exists_mock.assert_called()
        create_user_mock.assert_not_called()

    # 'is_user_exists' check is called and returned False - so, call 'create_user' afterwards
    if is_user_exist is False:
        is_user_exists_mock.assert_called()
        create_user_mock.assert_called()
