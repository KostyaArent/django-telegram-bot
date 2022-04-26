import random
import telegram
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler
)

from typing import Callable, List

from tgbot.handlers.wpassist.static_text import (
    edit_profile, find_teammate,
    go, nick_name, primary_game,
    excluded, included, choose_action,
    lets_edit, choose_game, bye,
    open_username, no_body
    )

from tgbot.handlers.wpassist.keyboards import (
    send_wpassist_keyboard, build_keyboard,
    send_confirm_keyboard, send_find_keyboard,
    send_wpassist_create_keyboard
    )
from tgbot.models import User, Profile, Game

NICKNAME, GAME, CONFIRMATION, NEXT, TEAMMATE_GAME, SEND = range(6)


def go(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    profile = Profile.objects.filter(user=user).first()
    if profile is not None:
        update.message.reply_text(choose_action, reply_markup=send_wpassist_keyboard(profile.in_search))
    else:
        update.message.reply_text(lets_edit, reply_markup=send_wpassist_create_keyboard())


def in_search_off(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    profile = Profile.objects.get(user=user)
    profile.in_search = False
    profile.save()
    update.message.reply_text(
        excluded,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


def in_search_on(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    profile = Profile.objects.get(user=user)
    profile.in_search = True
    profile.save()
    update.message.reply_text(
        included,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


# Profile_handler start
def edit(update: Update, context: CallbackContext) -> Callable:
    u = User.get_user(update, context)
    update.message.reply_text(
        nick_name,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
    return NICKNAME


def nickname(update: Update, context: CallbackContext) -> Callable:
    u = User.get_user(update, context)
    chat_id = update.message.chat_id
    user_data = context.user_data
    user_data['nickname'] = update.message.text
    prof, _ = Profile.objects.get_or_create(user=u)
    prof.steam_nickname = update.message.text
    prof.save()
    games = Game.objects.values('id', 'title')
    update.message.reply_text(
        primary_game,
        reply_markup=build_keyboard(games, 'title', 'id')
        )
    return GAME


def game(update: Update, context: CallbackContext) -> Callable:
    query = update.callback_query
    bot = context.bot
    user_data = context.user_data
    user_data['game'] = query.data
    user = User.get_user(update, context)
    user_game = Game.objects.get(id=int(query.data))
    prof, _ = Profile.objects.get_or_create(
        user=user,
    )
    prof.game = user_game
    prof.save()
    bot.answer_callback_query(query.id)
    bot.editMessageReplyMarkup(user.user_id, query.message.message_id)
    bot.send_message(user.user_id, f'Your profile looks like:\n\
    Steam nickname: {prof.steam_nickname}\nFavorite game: {user_game.title}')
    bot.send_message(user.user_id, f'Confirm your participation in the\
 selection',reply_markup=send_confirm_keyboard())
    return CONFIRMATION


def confirmation(update: Update, context: CallbackContext) -> Callable:
    user = User.get_user(update, context)
    prof, _ = Profile.objects.get_or_create(
        user=user,
    )
    prof.in_search = True
    prof.save()
    update.message.reply_text(fine + " " choose_action, reply_markup=send_wpassist_create_keyboard())
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> Callable:
    update.message.reply_text(bye,
                              reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


profile_handler = \
ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^Edit profile$'),
                              edit)
            ],
        states={
            NICKNAME: [MessageHandler(Filters.text, nickname)],
            GAME: [CallbackQueryHandler(game)],
            CONFIRMATION: [
                MessageHandler(Filters.regex('^Confirm$'),
                                  confirmation),
                MessageHandler(Filters.regex('^Restart$'),
                                  edit),
                MessageHandler(Filters.regex('^Cancel$'),
                                  cancel)
                                  ],
            },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.regex('^Edit profile$'),
                              edit),
            ]
        )
# profile_handler end


# find_handler start
def find(update: Update, context: CallbackContext) -> Callable:
    if update.message.from_user.username is not None:
        games = Game.objects.values('id', 'title')
        update.message.reply_text(
            choose_game,
            reply_markup=build_keyboard(
                games, 'title', 'id'
                ))
        return TEAMMATE_GAME
    else:
        update.message.reply_text(
            open_username,
            reply_markup=telegram.ReplyKeyboardRemove()
            )
        return ConversationHandler.END

def teammate_game(update: Update, context: CallbackContext) -> Callable:
    query = update.callback_query
    user = User.get_user(update, context)
    bot = context.bot
    bot.answer_callback_query(query.id)
    bot.editMessageReplyMarkup(query.message.chat.id, query.message.message_id)
    user_data = context.user_data
    category = 'teammate_game'
    user_data[category] = query.data
    teammate_game = Game.objects.get(id=int(query.data))
    profiles = Profile.objects.filter(game=teammate_game, in_search=True).exclude(user=user).values('pk', 'steam_nickname')
    if profiles.count() > 0:
        teammate = random.choice(profiles)
        user_data['teammate'] = teammate
        user_data['teammates'] = profiles
        bot.send_message(user.user_id, f'You teammate for {teammate_game.title}:\n{teammate.get("steam_nickname")}', reply_markup=send_find_keyboard())
        return NEXT
    else:
        bot.send_message(user.user_id, no_body')
        return ConversationHandler.END


def next(update: Update, context: CallbackContext) -> Callable:
    user_data = context.user_data
    user = User.get_user(update, context)
    bot = context.bot
    if update.callback_query:
        query = update.callback_query
        teammate_game = Game.objects.get(id=int(query.data))
        profiles = Profile.objects.filter(game=teammate_game, in_search=True).exclude(user=user).values('pk', 'steam_nickname')
        if profiles.count() > 0:
            teammate = random.choice(profiles)
            user_data['teammate'] = teammate.pk
            user_data['teammates'] = profiles
            update.message.reply_text(f'{teammate.steam_nickname}', reply_markup=send_find_keyboard())
            return SEND
        else:
            update.message.reply_text(no_body)
            return ConversationHandler.END
    else:
        teammate_game = Game.objects.get(id=int(user_data['teammate_game']))
        teammate = random.choice(user_data['teammates'])
        bot.send_message(update.message.chat.id, f'You teammate for {teammate_game.title}:\n{teammate.get("steam_nickname")}', reply_markup=send_find_keyboard())
        return NEXT


def send(update: Update, context: CallbackContext) -> Callable:
    user_data = context.user_data
    user = User.get_user(update, context)
    bot = context.bot
    username = update.message.chat.username
    teammate_id = user_data['teammate']['pk']
    # teammate = Profile.objects.get(external_id=teammate_id)
    bot.send_message(teammate_id, f'@{username} invited you to play! Send him\
 :)')
    update.message.reply_text(f'Will send to {teammate_id}!', reply_markup=\
    telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


find_handler = \
        ConversationHandler(
            entry_points=[
                MessageHandler(Filters.regex('^Find teammate$'),
                                  find)
                ],
            states={
                TEAMMATE_GAME: [CallbackQueryHandler(teammate_game)],
                NEXT: [
                    MessageHandler(Filters.regex('^Send$'),
                                      send),
                    MessageHandler(Filters.regex('^Next$'),
                                      next),
                       ],
                },
            fallbacks=[
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.regex('^Find teammate$'),
                                  find)
                ])
# find_handler end
