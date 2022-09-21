import random
import telegram
import re
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
    open_username, no_body, fine,
    send_phone, exp_question, exp_period,
    story, em_val_select, salary_question,
    more_val, custom_emp_val, end, new_work,
    status_question, in_progress
    )

from tgbot.handlers.wpassist.keyboards import (
    send_wpassist_keyboard, build_keyboard,
    send_confirm_keyboard, send_find_keyboard,
    send_wpassist_create_keyboard,
    exp_select_keyboard
    )
from tgbot.models import User, Profile, Vacancy, Experience, EmployeeValues

NICKNAME, VACANCY, CONFIRMATION, NEXT, TEAMMATE_GAME, SEND, PHONE, EXPERIENCE, WORK_STATUS, EMP_VALUES, SELF_WORK, UNIQ_VALUE, SALARY, WORK_STORY = range(14)


def go(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    profile = Profile.objects.filter(user=user).first()
    # if profile is not None:
    #     update.message.reply_text(choose_action, reply_markup=send_wpassist_keyboard(True))
    # else:
    update.message.reply_text(lets_edit, reply_markup=send_wpassist_create_keyboard())


def in_search_off(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    profile = Profile.objects.get(user=user)
    profile.working = 'Yes'
    profile.save()
    update.message.reply_text(
        excluded,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


def in_search_on(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    profile = Profile.objects.get(user=user)
    profile.working = 'yes'
    profile.save()
    update.message.reply_text(
        included,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


# Profile_handler start
def edit(update: Update, context: CallbackContext) -> Callable:
    user = User.get_user(update, context)
    profile = Profile.objects.get(user=user)
    if profile.stage.id != 1:
        update.message.reply_text(
        in_progress,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
        return ConversationHandler.END
    update.message.reply_text(
        nick_name,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
    return NICKNAME


def nickname(update: Update, context: CallbackContext) -> Callable:
    u = User.get_user(update, context)
    user_data = context.user_data
    user_data['nickname'] = update.message.text
    prof, _ = Profile.objects.get_or_create(user=u)
    prof.name_family = update.message.text
    prof.save()    
    update.message.reply_text(
        send_phone,
        reply_markup=telegram.ReplyKeyboardRemove(),
        )
    return PHONE


def phone(update: Update, context: CallbackContext) -> Callable:
    num = ''.join(re.split('\D+', update.message.text))
    if 9<len(str(num))<12:
        u = User.get_user(update, context)
        user_data = context.user_data
        user_data['phone'] = num
        prof, _ = Profile.objects.get_or_create(user=u)
        prof.phone = user_data['phone']
        prof.save()
        vacancy = Vacancy.objects.values('id', 'title')
        update.message.reply_text(
            primary_game,
            reply_markup=build_keyboard(vacancy, 'title', 'id')
            )
        return VACANCY
    update.message.reply_text(
        'Некорректный номер телефона, вводите в международном формате',
        reply_markup=telegram.ReplyKeyboardRemove(),
        )
    return PHONE


def vacancy(update: Update, context: CallbackContext) -> Callable:
    query = update.callback_query
    user = User.get_user(update, context)
    bot = context.bot
    user_data = context.user_data
    user_data['vacancy'] = query.data
    bot.send_message(user.user_id, exp_question, reply_markup=exp_select_keyboard())
    
    return EXPERIENCE


def experience(update: Update, context: CallbackContext) -> Callable:
    user_data = context.user_data
    user = User.get_user(update, context)
    if update.message.text == 'Да':
        experience = [{'id': exp[0], 'title':exp[1]} for exp in Experience.CHOICES]
        update.message.reply_text(
            exp_period,
            reply_markup=build_keyboard(experience, 'title', 'id')
            )
        return WORK_STATUS
    elif update.message.text == 'Нет':
        user_vacancy = Vacancy.objects.get(id=int(user_data['vacancy']))
        exp, _ = Experience.objects.get_or_create(user=user, vacancy=user_vacancy)
        exp.standing = None
        exp.save()
        vals = EmployeeValues.objects.filter(is_base=True).values('id', 'title')
        update.message.reply_text(
            em_val_select,
            reply_markup=build_keyboard(vals, 'title', 'id')
            )
        return EMP_VALUES
    else:
        return VACANCY


def work_status(update: Update, context: CallbackContext) -> Callable:
    query = update.callback_query
    user_data = context.user_data
    user_vacancy = Vacancy.objects.get(id=int(user_data['vacancy']))
    user = User.get_user(update, context)
    exp, _ = Experience.objects.get_or_create(user=user, vacancy=user_vacancy)
    exp.standing = query.data
    exp.save()
    bot = context.bot
    bot.send_message(user.user_id, new_work, reply_markup=exp_select_keyboard())
    return SELF_WORK


def self_work(update: Update, context: CallbackContext):
    bot = context.bot
    user = User.get_user(update, context)
    if update.message.text == 'Да':
        update.message.reply_text(
            status_question,
            reply_markup=telegram.ReplyKeyboardRemove(),
        )
        return WORK_STORY
    elif update.message.text == 'Нет':
        prof, _ = Profile.objects.get_or_create(user=user)
        prof.working = "Безработный"
        prof.save()
        vals = list(EmployeeValues.objects.filter(is_base=True).values('id', 'title'))
        vals.append({'id':'Другое', 'title':'Другое'})
        bot.send_message(user.user_id, em_val_select, reply_markup=build_keyboard(vals, 'title', 'id'))
        return EMP_VALUES
    else:
        bot.send_message(user.user_id, new_work, reply_markup=exp_select_keyboard())
        return SELF_WORK


def work_story(update: Update, context: CallbackContext):
    bot = context.bot
    user = User.get_user(update, context)
    prof, _ = Profile.objects.get_or_create(user=user)
    prof.working = update.message.text
    prof.save()
    vals = list(EmployeeValues.objects.filter(is_base=True).values('id', 'title'))
    vals.append({'id':'Другое', 'title':'Другое'})
    bot.send_message(user.user_id, em_val_select, reply_markup=build_keyboard(vals, 'title', 'id'))
    return EMP_VALUES


def emp_values(update: Update, context: CallbackContext):
    query = update.callback_query
    user = User.get_user(update, context)
    bot = context.bot
    bot.answer_callback_query(query.id)
    bot.editMessageReplyMarkup(user.user_id, query.message.message_id)
    vals = list(EmployeeValues.objects.filter(is_base=True).exclude(users__pk=user.user_id).values('id', 'title'))
    vals.append({'id':'Другое', 'title':'Другое'})
    if EmployeeValues.objects.filter(users__pk=user.user_id).count() < 3 and query.data != 'Другое':
        emval = EmployeeValues.objects.get(id=int(query.data))
        emval.users.add(user)
        emval.save()
        bot.send_message(user.user_id, more_val, reply_markup=build_keyboard(vals, 'title', 'id'))
        return EMP_VALUES
    elif EmployeeValues.objects.filter(users__pk=user.user_id).count() < 3 and query.data == 'Другое':
        bot.send_message(user.user_id, custom_emp_val, reply_markup=telegram.ReplyKeyboardRemove())
        return UNIQ_VALUE
    else:                
        #Enouth
        bot.send_message(user.user_id, salary_question, reply_markup=telegram.ReplyKeyboardRemove())
        return SALARY


def uniq_value(update: Update, context: CallbackContext) -> Callable:
    user = User.get_user(update, context)
    custom_val = EmployeeValues.objects.create(title=update.message.text)
    custom_val.users.add(user)
    custom_val.save()
    bot = context.bot
    if EmployeeValues.objects.filter(users__pk=user.user_id).count() < 3:
        vals = list(EmployeeValues.objects.filter(is_base=True).exclude(users__pk=user.user_id).values('id', 'title'))
        vals.append({'id':'Другое', 'title':'Другое'})
        bot.send_message(user.user_id, more_val, reply_markup=build_keyboard(vals, 'title', 'id'))
        return EMP_VALUES
    else:
        bot.send_message(user.user_id, salary_question, reply_markup=telegram.ReplyKeyboardRemove())
        return SALARY


def salary(update: Update, context: CallbackContext) -> Callable:
    user = User.get_user(update, context)
    prof, _ = Profile.objects.get_or_create(user=user)
    prof.salary_await = update.message.text
    prof.save()
    prof.change_status('2')
    bot = context.bot
    bot.send_message(chat_id=user.user_id, text=end)
    return ConversationHandler.END


def confirmation(update: Update, context: CallbackContext) -> Callable:
    user = User.get_user(update, context)
    prof, _ = Profile.objects.get_or_create(
        user=user,
    )
    prof.working = 'True'
    prof.save()
    update.message.reply_text(fine + " " + choose_action, reply_markup=send_wpassist_keyboard(True))
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> Callable:
    update.message.reply_text(bye,
                              reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


profile_handler = \
ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^Заполнить анкету$'),
                              edit)
            ],
        states={
            NICKNAME: [MessageHandler(Filters.text, nickname)],
            PHONE: [MessageHandler(Filters.text, phone)],
            VACANCY: [CallbackQueryHandler(vacancy)],
            EXPERIENCE: [MessageHandler(Filters.text, experience)],
            WORK_STATUS: [CallbackQueryHandler(work_status)],
            SELF_WORK: [MessageHandler(Filters.text, self_work)],
            WORK_STORY: [MessageHandler(Filters.text, work_story)],
            EMP_VALUES: [CallbackQueryHandler(emp_values)],
            UNIQ_VALUE: [MessageHandler(Filters.text, uniq_value)],
            SALARY: [MessageHandler(Filters.text, salary)],
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
        vacancies = Vacancy.objects.values('id', 'title')
        update.message.reply_text(
            choose_game,
            reply_markup=build_keyboard(
                vacancies, 'title', 'id'
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
    teammate_game = Vacancy.objects.get(id=int(query.data))
    profiles = Profile.objects.filter(game=teammate_game, in_search=True).exclude(user=user).values('pk', 'name_family')
    if profiles.count() > 0:
        teammate = random.choice(profiles)
        user_data['teammate'] = teammate
        user_data['teammates'] = profiles
        bot.send_message(user.user_id, f'You teammate for {teammate_game.title}:\n{teammate.get("name_family")}', reply_markup=send_find_keyboard())
        return NEXT
    else:
        bot.send_message(user.user_id, no_body)
        return ConversationHandler.END


def next(update: Update, context: CallbackContext) -> Callable:
    user_data = context.user_data
    user = User.get_user(update, context)
    bot = context.bot
    if update.callback_query:
        query = update.callback_query
        teammate_game = Vacancy.objects.get(id=int(query.data))
        profiles = Profile.objects.filter(vacancy=teammate_game, in_search=True).exclude(user=user).values('pk', 'name_family')
        if profiles.count() > 0:
            teammate = random.choice(profiles)
            user_data['teammate'] = teammate.pk
            user_data['teammates'] = profiles
            update.message.reply_text(f'{teammate.vacancy}', reply_markup=send_find_keyboard())
            return SEND
        else:
            update.message.reply_text(no_body)
            return ConversationHandler.END
    else:
        teammate_game = Vacancy.objects.get(id=int(user_data['teammate_game']))
        teammate = random.choice(user_data['teammates'])
        bot.send_message(update.message.chat.id, f'You teammate for {teammate_game.title}:\n{teammate.get("name_family")}', reply_markup=send_find_keyboard())
        return NEXT


def send(update: Update, context: CallbackContext) -> Callable:
    user_data = context.user_data
    user = User.get_user(update, context)
    bot = context.bot
    username = update.message.chat.username
    teammate_id = user_data['teammate']['pk']
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
