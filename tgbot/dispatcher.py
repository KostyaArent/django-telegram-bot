"""
    Telegram event handlers
"""
import sys
import logging
from typing import Dict


import telegram.error
from telegram import Bot, Update, BotCommand
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler
)

from dtb.celery import app  # event processing in async mode
from dtb.settings import TELEGRAM_TOKEN, DEBUG

from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.wpassist import handlers as wpassist_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.onboarding.manage_data import WP_ASSIST
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # admin commands
    dp.add_handler(CommandHandler("admin", admin_handlers.admin))
    dp.add_handler(CommandHandler("stats", admin_handlers.stats))
    dp.add_handler(CommandHandler('export_users', admin_handlers.export_users))

    # location
    dp.add_handler(CommandHandler("ask_location", location_handlers.ask_for_location))
    dp.add_handler(MessageHandler(Filters.location, location_handlers.location_handler))

    # wpassist
    dp.add_handler(MessageHandler(Filters.regex('^Remove me from search$'), wpassist_handlers.in_search_off))
    dp.add_handler(MessageHandler(Filters.regex('^Add me to search$'), wpassist_handlers.in_search_on))
    dp.add_handler(MessageHandler(Filters.regex('^Начать$'), wpassist_handlers.go))
    dp.add_handler(CommandHandler("go", wpassist_handlers.go))
    dp.add_handler(wpassist_handlers.find_handler)
    dp.add_handler(wpassist_handlers.profile_handler)

    # wp assist main menu button
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.wp_assist, pattern=f"^{WP_ASSIST}"))

    # broadcast message
    dp.add_handler(
        MessageHandler(Filters.regex(rf'^{broadcast_command}(/s)?.*'), broadcast_handlers.broadcast_command_with_message)
    )
    dp.add_handler(
        CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler, pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    )

    # files
    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
    ))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'start': 'Start bot 🚀',
            # 'stats': 'Statistics of bot 📊',
            # 'admin': 'Show admin info ℹ️',
            # 'ask_location': 'Send location 📍',
            #'go': 'WP Assist 👥',
            # 'broadcast': 'Broadcast message 📨',
            'export_users': 'Export users.csv 👥',
        },
        'es': {
            'start': 'Iniciar el bot de 🚀',
            # 'stats': 'Estadísticas de bot 📊',
            # 'admin': 'Mostrar información de administrador ℹ️',
            # 'ask_location': 'Enviar ubicación 📍',
            #'go': 'WP Asistir 👥',
            # 'broadcast': 'Mensaje de difusión 📨',
            'export_users': 'Exportar users.csv 👥',
        },
        'fr': {
            'start': 'Démarrer le bot 🚀',
            # 'stats': 'Statistiques du bot 📊',
            # 'admin': "Afficher les informations d'administrateur ℹ️",
            # 'ask_location': 'Envoyer emplacement 📍',
            #'go': 'WP Aider 👥',
            # 'broadcast': 'Message de diffusion 📨',
            "export_users": 'Exporter users.csv 👥',
        },
        'ru': {
            'start': 'Запустить бота 🚀',
            # 'stats': 'Статистика бота 📊',
            # 'admin': 'Показать информацию для админов ℹ️',
            # 'broadcast': 'Отправить сообщение 📨',
            # 'ask_location': 'Отправить локацию 📍',
            #'go': 'WP Ассистент 👥',
            'export_users': 'Экспорт users.csv 👥',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


bot = telegram.Bot(token=TELEGRAM_TOKEN)
# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
# set_up_commands(bot)

# Global variable - best way I found to init Telegram bot
dispatcher = setup_dispatcher(Dispatcher(bot, None, workers=0, use_context=True))
TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
