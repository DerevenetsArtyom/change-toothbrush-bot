import logging

# Enable logging
logging.basicConfig(
    format='[%(filename)s:%(lineno)s - %(funcName)20s() ] - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def error_logger(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
