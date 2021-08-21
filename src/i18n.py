import gettext
from functools import wraps
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "locale"

lang_ru = gettext.translation("messages", localedir=LOCALES_DIR, languages=["ru_RU"])


# Default implementation
def _(msg):
    return msg


def user_locale(func):
    @wraps(func)
    def wrapped(update, context):

        global _

        # TODO: fetch language from user profile (or even DB data)
        preferred_language = context.user_data.get("language_code") or update.effective_user.language_code

        if preferred_language == "ru":
            _ = lang_ru.gettext
        else:

            def _(msg):
                return msg

        result = func(update, context)
        return result

    return wrapped
