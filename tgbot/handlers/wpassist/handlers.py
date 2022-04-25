import telegram
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.wpassist.static_text import edit_profile, find_teammate, go
from tgbot.handlers.wpassist.keyboards import send_wpassist_keyboard
from tgbot.models import User, Profile


def go(update: Update, context: CallbackContext) -> None:
    """ Entered /go command"""
    u = User.get_user(update, context)
    text = go if Profile.objects.filter(user=u).first() else edit_profile
    context.bot.send_message(
        chat_id=u.user_id,
        text=text,
        reply_markup=send_wpassist_keyboard()
    )


def edit(update: Update, context: CallbackContext) -> None:
    # receiving user's location
    u = User.get_user(update, context)
    # lat, lon = update.message.location.latitude, update.message.location.longitude
    # Location.objects.create(user=u, latitude=lat, longitude=lon)

    update.message.reply_text(
        edit_profile,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
