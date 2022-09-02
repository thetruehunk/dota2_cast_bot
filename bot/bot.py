""" bot initialization """

import logging

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    # Dispatcher,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)
from telegram.ext import messagequeue as mq

from functions import sync_current_leagues, sync_game_current_league, sync_league_baner, sync_teams 
from handlers import (
    get_game_info,
    get_game_start_twitch,
    view_league_info,
    view_game_info,
    help_me,
    inlinequery,
    # set_alarm,
    start,
    subs_video,
    subs_text,
)
from settings import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="logs/bot.log",
)


def main():
    # creating bot
    bot = Updater(TOKEN, use_context=True)

    # creating dispatcher
    dp = bot.dispatcher

    # creating job for regular sync database
    #bot.job_queue.run_repeating(callback=sync_current_leagues, interval=3600, first=10)
    #bot.job_queue.run_repeating(callback=sync_game_current_league, interval=3600, first=10)
    #bot.job_queue.run_repeating(callback=sync_teams, interval=3600, first=10)
    #bot.job_queue.run_repeating(callback=sync_league_baner, interval=3600, first=40)
    # TODO get_baner

    # creating write in log about start bot
    logging.info("Bot is run")

    # creating handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_me))
    dp.add_handler(MessageHandler(Filters.regex("OK, search informations about(.*)"),view_league_info))
    dp.add_handler(CallbackQueryHandler(view_game_info, pattern="^view_game_info \d+$"))
    dp.add_handler(CallbackQueryHandler(subs_video, pattern="^subs_video \d+$"))
    dp.add_handler(CallbackQueryHandler(subs_text, pattern="^subs_text \d+$"))
    dp.add_handler(InlineQueryHandler(inlinequery))
    # dp.add_handler(CommandHandler("alarm", set_alarm, pass_args=True, pass_job_queue=True))
    # run bot
    bot.start_polling()
    bot.idle()


if __name__ == "__main__":
    main()
