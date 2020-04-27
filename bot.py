"""
Здесь находится все для инициализации и старта  бота
"""

import logging

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Dispatcher,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)
from telegram.ext import messagequeue as mq

from functions import sync_current_leagues, sync_game_current_league
from handlers import (
    get_game_start_twitch,
    get_tournament_info,
    help_me,
    ikb_subscribe,
    inlinequery,
    set_alarm,
    start,
)

from settings import PROXY, TOKEN

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log",
)

subscribers = set()


def main():
    # Создаем бота
    bot = Updater(TOKEN, use_context=True, request_kwargs=PROXY)
    
    # Создаем диспетчер
    dp = bot.dispatcher

    bot.job_queue.run_once(get_game_start_twitch, 2)

    # bot.job_queue.run_repeating(send_updates, 5)
    # bot.job_queue.run_repeating(send_updates, 5)

    # Ставим в очередь задачи по синхронизации БД
    # bot.job_queue.run_repeating(sync_current_leagues(), 20)
    # bot.job_queue.run_repeating(sync_game_current_league(), 120)

    # выполняем синхронизацию БД с API
    # sync_current_leagues()
    # sync_game_current_league()
    # Делаем запись в лог
    logging.info("bot запускается")

    # Создаем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_me))
    dp.add_handler(
        MessageHandler(Filters.regex("OK, ищу информацию по (.*)"), get_tournament_info)
    )
    dp.add_handler(CallbackQueryHandler(ikb_subscribe))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(
        CommandHandler("alarm", set_alarm, pass_args=True, pass_job_queue=True)
    )
    # Запускаем бота
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()
