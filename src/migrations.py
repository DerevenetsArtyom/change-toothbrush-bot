import os

import playhouse.migrate

from models import database

if os.getenv("DATABASE_URL"):  # it's remote Postgres most likely
    migrator = playhouse.migrate.PostgresqlMigrator(database)
else:
    migrator = playhouse.migrate.SqliteMigrator(database)

print("Current migrator is", migrator)

with database.atomic():
    print("Going to migrate...")
    playhouse.migrate.migrate(
        migrator.drop_not_null("event", "notification_date"),
    )
    print("Migration done!")
