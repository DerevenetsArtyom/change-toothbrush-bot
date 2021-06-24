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


def get_pending_events(user_id):
    """Returns all pending events (that are waiting its notification time)."""

    current_user_id = User.get(user_id=user_id).id
    return Event.select().where(Event.author == current_user_id, Event.completed == False)  # noqa: E712


def get_expired_events(user_id):
    """Returns all archived / expires events (that have been completed already)."""

    current_user_id = User.get(user_id=user_id).id
    return Event.select().where(Event.author == current_user_id, Event.completed == True)  # noqa: E712


def create_event(user_data: dict) -> None:
    """Creates event from data passed by user"""

    expiration_date = user_data["expiration_date"]
    notification_date = user_data["notification_date"]

    current_user_id = User.get(user_id=user_data["user_id"]).id
    Event.create(
        author=current_user_id,
        subject=user_data["entry"],
        expiration_date=expiration_date,
        notification_date=notification_date,
    )


def complete_event(event_id: int) -> None:
    event = Event.get(Event.id == event_id)
    event.completed = True
    event.save()


def get_events_for_notification(user_id: int):
    """Returns events for which notification should go off today"""

    today_date = datetime.datetime.now().date()
    user = User.get(user_id=user_id)

    return user.events.select().where(Event.notification_date == today_date, Event.completed == False)  # noqa: E712


def create_tables():
    with database:
        database.create_tables([Event, User])
