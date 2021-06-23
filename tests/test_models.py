import pytest
from datetime import datetime, date


@pytest.fixture
def user(models):
    return models.User.create(
        user_id=1,
        chat_id=1,
        first_name="First Name",
        last_name="Last Name",
        username="Username",
    )


def test_create_event(models, user):
    expiration_date = date(year=2021, month=12, day=1)
    notification_date = date(year=2021, month=10, day=1)

    user_data = {
        "expiration_date": expiration_date,
        "notification_date": notification_date,
        "user_id": user.id,
        "entry": "This is test entry",
    }

    models.create_event(user_data)

    created_event = models.Event.get_by_id(1)

    # Check that event was created with correct data
    assert created_event.subject == user_data["entry"]
    assert created_event.expiration_date == user_data["expiration_date"]
    assert created_event.notification_date == user_data["notification_date"]
    assert created_event.created == datetime.now().date()
    assert created_event.completed is False

    # Check that event was assigned to correct user
    assert created_event.author.first_name == user.first_name
    assert created_event.author.id == user.id
