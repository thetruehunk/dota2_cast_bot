"""
Здесь находится все для инициализации и старта  бота
"""

from telegram.ext import (
    Updater,
    Dispatcher,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    )

import logging
from handlers import *
from settings import *

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log",
)


def main():
    # Создаем бота
    bot = Updater(TOKEN, use_context = True, request_kwargs = PROXY)
    
    # Создаем диспетчер
    dp = bot.dispatcher
    
    # Делаем запись в лог
    logging.info('bot запускается')

    # Создаем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CallbackQueryHandler(help, "help"))
    dp.add_handler(InlineQueryHandler(inlinequery))


    # Запускаем бота
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()