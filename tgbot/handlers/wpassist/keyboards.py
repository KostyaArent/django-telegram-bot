from telegram import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.wpassist.static_text import edit_profile
from tgbot.models import Game


def send_wpassist_keyboard() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=edit_profile)]],
        resize_keyboard=True
    )
