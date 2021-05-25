class ScheduledEvent:
    def __init__(self):
        self.subject = None  # what user has done and subject of notification in the future
        self.created = None  # DateField, should be something like auto_now_add
        self.author = None  # FK or ID of user
        self.notification_date = None  # DateField, when user notified first time (about 2/3 of expiration date)
        self.expiration_date = None  # DateField, when user notified second (last) time (action should be already taken)
        self.completed = None  # flag whether the event goes off or not yet
