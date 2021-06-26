from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler

from handlers.conversation import (
    CONFIRMATION,
    EXPIRATION_DATE,
    NOTIFICATION_DATE,
    SUBJECT,
    add_expiration_date_custom,
    add_expiration_date_from_choice,
    add_new_entry,
    add_notification_date_custom,
    add_notification_date_from_choice,
    confirmation,
    start_creating_entry,
)
from handlers.list import complete_event_handler, show_expired, show_pending
from handlers.others import cancel, help_handler, start
from utils import error_logger


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_handler))
    dispatcher.add_handler(CommandHandler("list", show_pending))
    dispatcher.add_handler(CommandHandler("list_expired", show_expired))

    dispatcher.add_handler(CallbackQueryHandler(complete_event_handler, pattern="^event-complete:"))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_creating_entry)],
        states={
            SUBJECT: [MessageHandler(Filters.text & ~Filters.command, add_new_entry)],
            EXPIRATION_DATE: [
                MessageHandler(Filters.text & ~Filters.command, add_expiration_date_custom),
                CallbackQueryHandler(add_expiration_date_from_choice, pattern="^expiration_date"),
            ],
            NOTIFICATION_DATE: [
                MessageHandler(Filters.text & ~Filters.command, add_notification_date_custom),
                CallbackQueryHandler(add_notification_date_from_choice, pattern="^notification_date"),
            ],
            CONFIRMATION: [CommandHandler("done", confirmation)],
            # GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            # PHOTO: [
            #     MessageHandler(Filters.photo, photo),
            #     CommandHandler('skip', skip_photo)
            # ],
            # LOCATION: [
            #     MessageHandler(Filters.location, location),
            #     CommandHandler('skip', skip_location),
            # ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conversation_handler)

    # add an handler for errors
    dispatcher.add_error_handler(error_logger)
