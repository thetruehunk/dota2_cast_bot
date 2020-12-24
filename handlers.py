#######################################
#      core functions for handlers    #
#######################################

import logging
from datetime import datetime, timedelta
from time import strftime
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    KeyboardButton,
    ParseMode,
)

from bet import get_bet_koef
from data_model import (
    Game,
    League,
    User,
    engine,
    games_table,
    leagues_table,
    users_table,
)
from functions import (
    leagues_search,
    get_current_leagues,
    get_games_current_league,
    get_league_info,
    get_game_info,
)
from keyboards import start_kb_markup
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import text

""" Mapper """
mapper(User, users_table)


def start(update, context):
    logging.info("Start function called")
    reply_text = "Hello! Choose a league or use the search! 🎉"
    update.message.reply_text(reply_text, reply_markup=start_kb_markup)


def help_me(update, context):
    logging.info("Help function called")
    update.effective_message.reply_text(
        """Это бот для отслеживания событий киберспортивной дисциплины - DOTA2
С его помощью можно получить список текущих и предстоящих турниров и игр,
для каждой игры можно подписаться на уведомление о начале, получить доступ
к видео или текстовой трансляции.Команда /start - вызывает клавиатуру, 
отображающую текущие турниры и предоставляющую поиск по названию.
Для турнира будет выведен список игр, нажав на кнопку с игрой можно подписаться
на трансляцию. За некоторое время до начала игры вам придёт уведомление."""
    )


def view_league_info(update, context):
    league_name = update.message.text.split("about ")[1]
    reply_games_kb = []
    games = get_games_current_league(league_name)
    for game in games:
        reply_games_kb.append(
            [
                InlineKeyboardButton(
                    f'🔹{game[1]} ⚔️ 🔹{game[2]}  🕔{game[4].strftime("%b-%d %H:%M")}',
                    callback_data=f"view_game_info {game[5]}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            ]
        )
    markup = InlineKeyboardMarkup(reply_games_kb)
    league_info = get_league_info(league_name)
    # link = league_info[7].split(",")[0].strip("[}{'").split("': '")
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=league_info[2],
        caption=(
            # f"*{league_info[0]}*\n" 
            # f"Tier: *{league_info[1]}*\n"
            # f'Organizer: *{"Twitch account"}*\n'
            # f"Location📍: *{league_info[5]}*\n"
            # f"Dates📅: *{league_info[3]}*\n" f"Prize pool💰: *{league_info[4]}$*\n"
            # f'Link🔗: {f"[{link[0]}]({link[1]})" if league_info[7] else None}\n'
            # if reply_games_kb
            # else f"*No found games for:\n{league_info[0]}*"
        ),
        reply_markup=markup if reply_games_kb else None,
        parse_mode=ParseMode.MARKDOWN,
    )


def view_game_info(update, context):
    game_id = update.callback_query.data.split(" ")[1]
    print(game_id)
    game_info = get_game_info(game_id)
    reply_subscribe_kb = [
        [InlineKeyboardButton(f"text stream", callback_data=f"subs_text {game_id}")],
        [InlineKeyboardButton(f"video stream", callback_data=f"subs_video {game_id}")],
        [InlineKeyboardButton(f"back", switch_inline_query_current_chat="13")],
    ]
    subscribe_kb_markup = InlineKeyboardMarkup(reply_subscribe_kb)
    context.bot.send_photo(
        chat_id=update.callback_query.message.chat_id,
        photo=open("VS.png", "rb"),
        caption=(
            f"League🏆: *{game_info[0]}*\n"
            f"Start time🕑: *{game_info[4]}*\n"
            f"Game format🎲: *{game_info[3]}*\n"
            f"Bookmaker odds📊: *{get_bet_koef(game_info[1], game_info[2], game_info[4])}*\n"
            f"Bookmaker link🔗: [Parimatch](https://parimatch.ru)\n"
            f"#dota2 #parimatch #team1 #team2\n"
        ),
        reply_markup=subscribe_kb_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


def inlinequery(update, context):
    query = update.inline_query.query
    if query == "current":
        result = []
        current_leagues = get_current_leagues()
        for item in current_leagues:
            result.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item[0].strip(),
                    description=f"Period: {item[3]}, prize: ${item[2]}",
                    thumb_url=item[1],
                    input_message_content=InputTextMessageContent(
                        f'OK, search informations about "{item[0].strip()}"'
                    ),
                )
            )
        update.inline_query.answer(result)
    else:
        result = []
        user_text = update.inline_query.query
        result_search = leagues_search(user_text)
        for item in result_search:
            result.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item[0],
                    description=f"Period: {item[3]}, prize: ${item[2]}",
                    thumb_url=item[1],
                    input_message_content=InputTextMessageContent(
                        f'OK, search informations about "{item[0].strip()}"'
                    ),
                )
            )
        update.inline_query.answer(result)


def subs_video(update, context):
    game_id = update.callback_query.data.split(" ")[1]
    Session = sessionmaker(bind=engine)
    session = Session()
    game = session.query(Game).filter(Game.game_id == game_id).first()
    text = f"Вы подписались на уведомления по игре {game.team1} vs {game.team2}"
    context.bot.send_message(text=text, chat_id=update.callback_query.message.chat.id)
    subscription = User(int(update.callback_query.message.chat.id), int(game_id))
    session.add(subscription)
    session.commit()
    get_game_start_twitch(context)


def subs_text(update, context):
    print(update.callback_query.data)


def callback_alarm(context, chat_id, team1, team2, twitch_channel):
    context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"Скоро начинается игра {team1} vs {team2} на канале"
            f" https://www.twitch.tv/{twitch_channel}"
        ),
    )


# вызов из базы юзера с подпиской, сравнение с games и получение времени
# начала игры + ссылка на твич канал
def get_game_start_twitch(context):
    Session = sessionmaker(bind=engine)
    session = Session()
    notification_30 = datetime.now() + timedelta(hours=60)  # когда будет готово удалить
    print(notification_30)
    for game_id, start_time, team1, team2, twitch_channel in session.query(
        Game.game_id, Game.start_time, Game.team1, Game.team2, Game.twitch_channel
    ).filter(Game.start_time <= notification_30, Game.start_time >= datetime.now()):
        if game_id:
            for user_id, game_id in session.query(User.user_id, User.game_id).filter(
                User.game_id == game_id
            ):
                game_timer = int((start_time - datetime.now()).total_seconds())
                context.job_queue.run_once(
                    callback_alarm(context, user_id, team1, team2, twitch_channel), 5
                )
    session.commit()


# переделать на увдомления по подписке
"""def send_updates(context, job):
        subscrubeJob = updater.job_queue
    context.job_morning = subscrubeJob.run_once()"""


# def set_alarm(update, context):
#     try:
#         seconds = abs(int(context.args[0]))
#         context.job_queue.run_once(alarm, seconds, context=update.message.chat_id)
#     except (IndexError, ValueError):
#         update.message.reply_text("Введите число секунд после команды /alarm")


# def alarm(context):
#     context.bot.send_message(chat_id=context.job.context, text="Сработал будильник!")
