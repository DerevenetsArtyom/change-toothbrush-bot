from datetime import date, datetime, timedelta

import pytest


@pytest.fixture
def user(models, mixer):
    return models.User.create(
        user_id=1,
        chat_id=1,
        first_name=mixer.faker.first_name(),
        last_name=mixer.faker.last_name(),
    )


@pytest.fixture
def another_user(models, mixer):
    return models.User.create(
        user_id=2,
        chat_id=2,
        first_name=mixer.faker.first_name(),
        last_name=mixer.faker.last_name(),
    )


def test_create_event(models, user):
    user_data = {
        "expiration_date": date(year=2021, month=12, day=1),
        "notification_date": date(year=2021, month=10, day=1),
        "user_id": user.id,
        "entry": "This is test entry",
    }

    models.Event.create_event(user_data)

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


def test_get_expired_events(models, user, mixer):
    expired_events_amount = 5

    for i in range(expired_events_amount):
        mixer.blend(models.Event, author=user, subject=mixer.faker.text(35), completed=True)

    assert models.get_expired_events(user.id).count() == expired_events_amount


def test_get_expired_events_for_different_user(models, user, another_user, mixer):
    expired_events_amount = 3

    for i in range(expired_events_amount):
        mixer.blend(models.Event, author=another_user, subject=mixer.faker.text(35), completed=True)

    assert not models.get_expired_events(user.id)  # all events are bind to 'another_user'


def test_get_expired_events_ordering(models, user, mixer):
    expired_events_amount = 10
    now = datetime.now()

    for i in range(expired_events_amount):
        mixer.blend(
            models.Event,
            author=user,
            subject=mixer.faker.text(35),
            completed=True,
            expiration_date=now - timedelta(days=i),
        )

    events_list = models.get_expired_events(user.id)

    for i in range(len(events_list) - 1):
        assert events_list[i].expiration_date < events_list[i + 1].expiration_date


def test_get_pending_events(models, user, mixer):
    pending_events_amount = 5

    for i in range(pending_events_amount):
        mixer.blend(models.Event, author=user, subject=mixer.faker.text(35))

    assert models.get_pending_events(user.id).count() == pending_events_amount


def test_get_pending_events_for_different_user(models, user, another_user, mixer):
    pending_events_amount = 3

    for i in range(pending_events_amount):
        mixer.blend(models.Event, author=another_user, subject=mixer.faker.text(35))

    assert not models.get_pending_events(user.id)  # all events are bind to 'another_user'


def test_get_pending_events_ordering(models, user, mixer):
    pending_events_amount = 10
    now = datetime.now()

    for i in range(pending_events_amount):
        mixer.blend(models.Event, author=user, subject=mixer.faker.text(35), expiration_date=now - timedelta(days=i))

    events_list = models.get_pending_events(user.id)

    for i in range(len(events_list) - 1):
        assert events_list[i].expiration_date < events_list[i + 1].expiration_date


def test_complete_event(models, mixer):
    mixer_event = mixer.blend(models.Event)
    event = models.Event.get(models.Event.id == mixer_event.id)

    assert event.completed is False  # check that 'completed' after creation is False

    models.complete_event(event.id)

    # Fetch updated Event from DB
    event = models.Event.get(models.Event.id == mixer_event.id)

    assert event.completed is True


def test_delete_event(models, mixer):
    for i in range(3):
        mixer.blend(models.Event)

    assert models.Event.select().count() == 3

    models.delete_event(models.Event.get())

    assert models.Event.select().count() == 2


def test_get_events_for_notification(models, user, mixer):
    events_for_notification_amount = 8

    for i in range(events_for_notification_amount):
        mixer.blend(models.Event, author=user, notification_date=datetime.now().date())

    assert models.get_events_for_notification(user.id).count() == events_for_notification_amount


def test_get_events_for_notification_for_different_user(models, user, another_user, mixer):
    events_for_notification_amount = 3

    for i in range(events_for_notification_amount):
        mixer.blend(models.Event, author=another_user, notification_date=datetime.now().date())

    assert not models.get_events_for_notification(user.id)


def test_get_events_for_notification_date_is_empty(models, user, mixer):
    events_for_notification_amount = 3

    for i in range(events_for_notification_amount):
        mixer.blend(models.Event, author=user)  # 'notification_date' is missing

    assert models.get_events_for_notification(user.id).count() == 0


def test_get_events_for_expiration(models, user, mixer):
    events_for_expiration_amount = 3

    for i in range(events_for_expiration_amount):
        mixer.blend(models.Event, author=user, expiration_date=datetime.now().date())

    assert models.get_events_for_expiration(user.id).count() == events_for_expiration_amount


def test_get_events_for_expiration_for_different_user(models, user, another_user, mixer):
    events_for_expiration_amount = 3

    for i in range(events_for_expiration_amount):
        mixer.blend(models.Event, author=another_user, expiration_date=datetime.now().date())

    assert not models.get_events_for_expiration(user.id)
