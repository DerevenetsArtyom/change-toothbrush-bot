import datetime

import peewee as pw

database = pw.SqliteDatabase(None)


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


class Event(pw.Model):
    author = pw.CharField(unique=True)
    subject = pw.CharField()
    expiration_date = pw.DateField()
    notification_date = pw.DateField()
    created = pw.DateField(default=datetime.datetime.now)
    completed = pw.BooleanField(default=False)

    class Meta:
        database = database
