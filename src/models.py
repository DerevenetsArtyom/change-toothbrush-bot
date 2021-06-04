import datetime
import os

import peewee as pw
from dotenv import load_dotenv
from playhouse.db_url import connect

load_dotenv()

database = connect(os.getenv("DATABASE_URL", default="sqlite:///db.sqlite3"))


class ScheduledEvent:
    def __init__(self, author, subject, expiration_date, notification_date=None):
        # FK (or ID at least) of user who created event
        self.author = author

        # what user has done and subject of notification in the future ("started use new toothbrush")
        self.subject = subject

        # DateField, when user should be notified second (last) time (action should be already taken)
        self.expiration_date = expiration_date

        # DateField, when user wants to be notified first time - beforehand
        # might be calculated automatically - about 2/3 of expiration date, 2 weeks before or so
        self.notification_date = notification_date

        # DateField, should be something like auto_now_add (automatically set, no need to pass)
        self.created = None

        # flag whether the event is done or not yet. Set when notification goes off at self.notification_date
        self.completed = False


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
    subject = pw.CharField()
    expiration_date = pw.DateField()
    notification_date = pw.DateField()
    created = pw.DateField(default=datetime.datetime.now)
    completed = pw.BooleanField(default=False)

    class Meta:
        database = database


def get_pending_events():
    """Returns all pending events (that are waiting its notification time)."""


def get_expired_events():
    """Returns all archived / expires events (that have been completed already)."""


def create_event(user_data):
    """Creates event from data passed by user"""

    expiration_date = datetime.datetime.strptime(user_data["expiration_date"], "%d-%m-%y")
    notification_date = datetime.datetime.strptime(user_data["notification_date"], "%d-%m-%y")

    current_user_id = User.get(user_id=user_data["user_id"]).id
    Event.create(
        author=current_user_id,
        subject=user_data["entry"],
        expiration_date=expiration_date,
        notification_date=notification_date,
    )


def create_tables():
    with database:
        database.create_tables([Event, User])
