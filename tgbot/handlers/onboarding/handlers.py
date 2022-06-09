import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User
from tgbot.handlers.onboarding.keyboards import (
    make_keyboard_for_start_command, send_go_keyboard,
    make_keyboard_for_wp_assist_start
    )
from tgbot.handlers.wpassist.keyboards import send_wpassist_create_keyboard
from tgbot.models import User, Profile


def command_start(update: Update, context: CallbackContext) -> None:
    user, us_create = User.get_user_and_created(update, context)
    profile, pr_created = Profile.objects.get_or_create(user=user)
    if us_create:
        print(profile)
        profile.change_status('1')
        text = static_text.start_created.format(first_name=user.first_name)
    else:
        text = static_text.start_not_created.format(first_name=user.first_name)
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command()
        )


def wp_assist(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = extract_user_data_from_update(update)['user_id']
    bot = context.bot
    bot.answer_callback_query(query.id)
    bot.editMessageReplyMarkup(user_id, query.message.message_id)
    # bot.send_message(user_id, 'Отлично! Давайте начнем интервью?', reply_markup=send_go_keyboard())
    bot.send_message(user_id, 'Отлично! Давайте начнем интервью?', reply_markup=send_wpassist_create_keyboard())
