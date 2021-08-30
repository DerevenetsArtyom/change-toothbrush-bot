"""
The general approach for testing and mocking especially
was stolen from Fedor Borshev: https://github.com/f213/selfmailbot/blob/master/conftest.py

Thanks for that! I have not found other appropriate approaches for that in open source.

"""
from random import randint
from unittest.mock import MagicMock

import peewee
import pytest


@pytest.fixture
def test_db():
    return peewee.SqliteDatabase(":memory:")


@pytest.fixture(autouse=True)
def models(test_db):
    """
    Emulate the transaction -- create a new db before each test and flush it after.
    Also, return the app.models module
    """

    from src import models

    app_models = [models.User, models.Event]

    test_db.bind(app_models, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(app_models)
    yield models

    test_db.drop_tables(app_models)
    test_db.close()


@pytest.fixture
def mixer():
    from mixer.backend.peewee import mixer

    return mixer


def factory(class_name: str = None, **kwargs):
    """Simple factory to create a class with attributes from kwargs"""

    class FactoryGeneratedClass:
        pass

    rewrite = {
        "__randint": lambda *args: randint(100_000_000, 999_999_999),
    }

    for key, value in kwargs.items():
        if value in rewrite:
            value = rewrite[value](value)

        setattr(FactoryGeneratedClass, key, value)

    if class_name is not None:
        FactoryGeneratedClass.__qualname__ = class_name
        FactoryGeneratedClass.__name__ = class_name

    return FactoryGeneratedClass


@pytest.fixture
def context():
    """telegram.CallbackContext"""

    class CallbackContext(factory("CallbackContext")):
        user_data = {}

    return CallbackContext()


@pytest.fixture
def bot_app(update, context):
    """Our bot app, adds the magic curring `call` method to call it with fake bot"""

    import sys

    sys.path.append("src")

    from src.handlers import main

    main.call = lambda method, *args: getattr(main, method)(update, context)

    return main


@pytest.fixture
def bot(message):
    """Mocked instance of the bot"""

    class Bot:
        send_message = MagicMock()

    return Bot()


@pytest.fixture
def tg_user(mixer):
    """telegram.User"""

    class User(
        factory(
            "User",
            id="__randint",
            is_bot=False,
            first_name="Poligraph",
            last_name="Sharikov",
            username="Creature",
        )
    ):
        def mention_markdown_v2(self):
            """Simplified version of markdown formatted input"""

            return f"{self.first_name} {self.last_name}"

    return User()


# TODO: Maybe is not needed
@pytest.fixture
def db_user(models):
    return lambda **kwargs: models.User.create(
        **{
            **dict(
                user_id=randint(100_000_000, 999_999_999),
                chat_id=randint(100_000_000, 999_999_999),
                first_name="Poligraph",
                last_name="Sharikov",
            ),
            **kwargs,
        }
    )


@pytest.fixture
def message():
    """telegram.Message"""

    return lambda **kwargs: factory(
        "Message",
        chat_id="__randint",
        reply_text=MagicMock(return_value=factory(message_id=100800)()),  # always 100800 as the replied message id
        reply_markdown_v2=MagicMock(),
        **kwargs,
    )()


@pytest.fixture
def update(message, tg_user):
    """telegram.Update"""

    return factory(
        "Update",
        update_id="__randint",
        message=message(from_user=tg_user),
        effective_user=tg_user,
        callback_query=MagicMock(),
    )()
