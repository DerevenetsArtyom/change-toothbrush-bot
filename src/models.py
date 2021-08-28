import datetime
import os

import peewee as pw
from dotenv import load_dotenv
from playhouse.db_url import connect

load_dotenv()

database = connect(os.getenv("DATABASE_URL", default="sqlite:///db.sqlite3"))


class User(pw.Model):
    user_id = pw.IntegerField(unique=True)
    chat_id = pw.IntegerField()
    first_name = pw.CharField()
    last_name = pw.CharField(null=True)
    username = pw.CharField(null=True)

    class Meta:
        database = database


class Event(pw.Model):
    author = pw.ForeignKeyField(User, backref="events")

    # what user has done and subject of notification in the future ("started use new toothbrush")
    subject = pw.CharField()

    # when user should be notified second (last) time (action should be already taken)
    expiration_date = pw.DateField()

    # when user wants to be notified first time - beforehand
    notification_date = pw.DateField()

    created = pw.DateField(default=datetime.datetime.now)

    # flag whether the event is done or not yet. Set when notification goes off at self.notification_date
    completed = pw.BooleanField(default=False)

    class Meta:
        database = database

    @classmethod
    def create_event(cls, user_data: dict) -> None:
        """Create event from data passed by user"""

        expiration_date = user_data["expiration_date"]
        notification_date = user_data["notification_date"]
        current_user_id = User.get(user_id=user_data["user_id"])

        cls.create(
            author=current_user_id,
            subject=user_data["entry"],
            expiration_date=expiration_date,
            notification_date=notification_date,
        )


def create_tables():
    with database:
        database.create_tables([Event, User])


def get_pending_events(user_id):
    """Return all pending events (that are waiting its notification time)."""

    current_user_id = User.get(user_id=user_id).id

    user_events = Event.select().where(Event.author == current_user_id, Event.completed == False)  # noqa: E712
    return user_events.order_by(Event.expiration_date)


def get_expired_events(user_id):
    """Return all archived / expired events (that have been completed already)."""

    current_user_id = User.get(user_id=user_id).id

    user_events = Event.select().where(Event.author == current_user_id, Event.completed == True)  # noqa: E712
    return user_events.order_by(Event.expiration_date)


def complete_event(event_id: int) -> None:
    event = Event.get(Event.id == event_id)
    event.completed = True
    event.save()


def delete_event(event_id: int) -> None:
    event = Event.get(Event.id == event_id)
    event.delete_instance()


def get_events_for_notification(user_id: int):
    """Return events for which notification should go off today."""

    today_date = datetime.datetime.now().date()
    user = User.get(user_id=user_id)

    return user.events.select().where(Event.notification_date == today_date, Event.completed == False)  # noqa: E712


def get_events_for_expiration(user_id: int):
    """Return events that expire today."""

    today_date = datetime.datetime.now().date()
    user = User.get(user_id=user_id)

    return user.events.select().where(Event.expiration_date == today_date, Event.completed == False)  # noqa: E712


def is_user_exists(tg_user) -> bool:
    """Check if user with given ID exists in the DB."""

    return User.select().where(User.user_id == tg_user.id)


def create_user(user_data, chat_id: int) -> None:
    """Create user in DB from data obtained from TG user."""

    User.create(
        user_id=user_data.id,
        chat_id=chat_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
    )
