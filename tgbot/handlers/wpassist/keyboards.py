from telegram import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
    )

from tgbot.handlers.wpassist.static_text import edit_profile
from tgbot.models import Game


def build_keyboard(query, name_key, date_key) -> InlineKeyboardMarkup:
    """Helper function to build the next inline keyboard."""
    return InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(item[name_key], callback_data=str(item[date_key]), title=item[name_key], number=item[date_key]) for item in query]
    )


def send_wpassist_keyboard(status: bool) -> ReplyKeyboardMarkup:
    search_action = 'Remove me from search' if status else 'Add me to search'
    keys = [['Edit profile', 'Find teammate', search_action]]
    return ReplyKeyboardMarkup(
        keys,
        one_time_keyboard=True,
        resize_keyboard=True
    )


def send_wpassist_create_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [['Edit profile']],
        one_time_keyboard=True,
        resize_keyboard=True
    )


def send_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [['Confirm', 'Restart', 'Cancel']],
        one_time_keyboard=True,
        resize_keyboard=True
    )


def send_find_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [['Send', 'Next', 'Cancel']],
        one_time_keyboard=True,
        resize_keyboard=True
    )
