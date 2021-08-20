import gettext
from functools import wraps
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "locale"

lang_pt = gettext.translation("messages", localedir=LOCALES_DIR, languages=["ru_RU"])


# Default implementation
def _(msg):
    return msg


def user_language(func):
    @wraps(func)
    def wrapped(update, context):
        # TODO: fetch language from user profile
        lang = b"ru_RU"

        global _

        if lang == b"ru_RU":
            _ = lang_pt.gettext
        else:

            def _(msg):
                return msg

        result = func(update, context)
        return result

    return wrapped
