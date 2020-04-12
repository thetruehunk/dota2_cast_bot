"""
Здесь находится все для инициализации и старта  бота
"""

from telegram.ext import (
    Updater,
    Dispatcher,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CommandHandler,
    InlineQueryHandler,
)
from telegram.ext import messagequeue as mq
from sqlalchemy.orm import mapper
import logging
from handlers import start, help, subscribe, unsubscribe, set_alarm, inlinequery, get_tournament_info
from functions import (
    sync_current_leagues,
    sync_game_current_league,
)
from settings import TOKEN, PROXY

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log",
)

subscribers = set()


def main():
    # Создаем бота
    bot = Updater(TOKEN, use_context=True, request_kwargs=PROXY)
    bot.bot._msg_queue = mq.MessageQueue()
    bot.bot._is_messages_queued_default = True

    # Создаем диспетчер
    dp = bot.dispatcher

    # bot.job_queue.run_repeating(send_updates, 5)

    # Ставим в очередь задачи по синхронизации БД
    # bot.job_queue.run_repeating(sync_current_leagues, 3600)
    # bot.job_queue.run_repeating(sync_game_current_league, 3600)

    # выполняем синхронизацию БД с API
    sync_current_leagues()
    sync_game_current_league()
    # Делаем запись в лог
    logging.info("bot запускается")

    # Создаем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(
        MessageHandler(Filters.regex("OK, ищу информацию по (.*)"), get_tournament_info)
    )
    dp.add_handler(CallbackQueryHandler(ikb_subscribe))
    # dp.add_handler(CallbackQueryHandler(subscribe, "subscribe"))
    # dp.add_handler(CallbackQueryHandler(help, "help"))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dp.add_handler(
        CommandHandler("alarm", set_alarm, pass_args=True, pass_job_queue=True)
    )
    # Запускаем бота
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()
