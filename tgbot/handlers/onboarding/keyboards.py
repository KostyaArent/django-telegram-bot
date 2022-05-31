from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import WP_ASSIST
from tgbot.handlers.onboarding.static_text import github_button_text, wp_assist_button_text


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(github_button_text, url="https://kazan.1cbit.ru"),
        InlineKeyboardButton(wp_assist_button_text, callback_data=f'{WP_ASSIST}')
    ]]

    return InlineKeyboardMarkup(buttons)


def send_go_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [['Начать']],
        one_time_keyboard=True,
        resize_keyboard=True
    )

def make_keyboard_for_wp_assist_start() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton('Начать', callback_data=f'/edit')
    ]]

    return InlineKeyboardMarkup(buttons)
