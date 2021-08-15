import logging

from constants import HUMAN_READABLE_OUTPUT_DATE_FORMAT

# Enable logging
logging.basicConfig(
    format="[%(filename)s:%(lineno)s - %(funcName)20s() ] - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def get_description() -> str:
    return """
/help - Show help
/add - Start the process of adding a new event
/list - Show all pending events
/list_expired - Show all expired events
"""


def prettify_date(date_object) -> str:
    """Format datetime object to human-friendly format"""

    return date_object.strftime(HUMAN_READABLE_OUTPUT_DATE_FORMAT)
