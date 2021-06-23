import pytest
import peewee


@pytest.fixture
def db():
    return peewee.SqliteDatabase(':memory:')


@pytest.fixture(autouse=True)
def models(db):
    """
    Emulate the transaction -- create a new db before each test and flush it after.
    Also, return the app.models module
    """

    from src import models
    app_models = [models.User, models.Event]

    db.bind(app_models, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(app_models)

    yield models

    db.drop_tables(app_models)
    db.close()


@pytest.fixture
def mixer():
    from mixer.backend.peewee import mixer
    return mixer
