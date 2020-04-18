"""
Здесь мы обрабатываем вызываемые функции
"""
from datetime import datetime, timedelta
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ParseMode
)

from uuid import uuid4
from functions import get_current_leagues, get_games_current_league
import emoji
import logging
import time
# from bot import subscribers
from data_model import *
from sqlalchemy.orm import sessionmaker, mapper


""" Emoji """
trophy = emoji.emojize(":trophy:")
magnifying_glass = emoji.emojize(":magnifying_glass_tilted_right:")
open_book = emoji.emojize(":open_book:")
party_popper = emoji.emojize(":party_popper:")

""" Mapper """
mapper(User, users_table)


""" Клавиатуры """
reply_start_kb = [
    [
        InlineKeyboardButton(
            f"ТУРНИРЫ {trophy}", switch_inline_query_current_chat="current"
        )
    ],
    [
        InlineKeyboardButton(
            f"НАЙТИ {magnifying_glass}", switch_inline_query_current_chat="search"
        )
    ],
    [InlineKeyboardButton(f"ПОМОЩЬ {open_book}", callback_data="help")],
]

markup = InlineKeyboardMarkup(reply_start_kb)


def start(update, context):
    logging.info("Вызвана функция старт")
    reply_text = "Привет! Мы рады, что ты с нами! " + party_popper + ""
    update.message.reply_text(reply_text, reply_markup=markup)


def help(update, context):
    logging.info("Вызвана функция help")
    update.effective_message.reply_text(
        "Мы умеем: /help - показать справку, @'Bot_Name' + leage_name - найти турнир"
    )


def get_tournament_info(update, context):
    message = update.message.text
    reply_games_kb = []
    games = get_games_current_league(message.split("по ")[1])
    for game in games:
        reply_games_kb.append([InlineKeyboardButton(f"🔹{game[1]} ⚔️ 🔹{game[2]}   Format: {game[3]}  🕔 {game[4]}", callback_data=game[5], parse_mode=ParseMode.MARKDOWN)])
    markup = InlineKeyboardMarkup(reply_games_kb)
    update.message.reply_text(f'*{message.split("по ")[1]}*', reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


def leagues_search(query):
    leagues_list = get_current_leagues()
    result = []
    for league in leagues_list:
        if query in league["name"]:
            result.append(league)
    return result


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
                        f"OK, ищу информацию по '{item[0].strip()}'"
                    ),
                )
            )
        update.inline_query.answer(result)
    elif query == "search":
        result = []
        user_text = update.message.text.split()[1:].strip()
        result_search = leagues_search(user_text)
        for item in result_search:
            result.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item[0],
                    description=f"Period: {item[3]}, prize: ${item[2]}",
                    thumb_url=item[1],
                    input_message_content=InputTextMessageContent(
                        "OK, нужно доработать"
                    ),
                )
            )
        update.inline_query.answer(result)

"""
def get_or_create_user(update, context):
    mapper(User, users_table)
    Session = sessionmaker(blind=engine)
    session = Session()
    user_id = update.message.chat_id
    user_json = pyjson5.loads(str(user))
    for item in user_json:
        my_data = User(
            item["user_id"],
            item["game_id"],
        )
    session.add(my_data)
    session.commit()
"""    


# подписка на игру
def ikb_subscribe(update, context):
    ikb_query = update.callback_query
    print(update.message)
    user_choice = ikb_query.data
    Session = sessionmaker(bind=engine)
    session = Session()
    game = session.query(Game).filter(Game.game_id==user_choice).first()
    text = f"Вы подписались на уведомления по игре {game.team1} vs {game.team2}"
    context.bot.edit_message_text(text=text, chat_id=ikb_query.message.chat.id,
            message_id=ikb_query.message.message_id)
    ikb_newUser = User(int(ikb_query.message.chat.id), int(ikb_query.data))
    session.add(ikb_newUser)
    session.commit()
    get_game_start_twitch(context)


def callback_alarm(context, chat_id, team1, team2, twitch_channel):
    context.bot.send_message(chat_id=chat_id, text=f'Скоро начинается игра {team1} vs {team2} на канале https://www.twitch.tv/{twitch_channel}')


# вызов из базы юзера с подпиской, сравнение с games и получение времени 
# начала игры + ссылка на твич канал
def get_game_start_twitch(context):
    Session = sessionmaker(bind=engine)
    session = Session()
    notification_30 = datetime.now() + timedelta(hours=5) #когда будет готово удалить
    print(notification_30)    
    for game_id, start_time, team1, team2, twitch_channel in session.query(Game.game_id, Game.start_time, Game.team1, Game.team2, Game.twitch_channel).filter(Game.start_time <= notification_30, Game.start_time >= datetime.now()):
        if game_id:
            for user_id, game_id in session.query(User.user_id, User.game_id).filter(User.game_id == game_id):
                game_timer = int((start_time - datetime.now()).total_seconds())                
                context.job_queue.run_once(callback_alarm(context, user_id, team1, team2, twitch_channel), 5)                    
    session.commit()


# переделать на увдомления по подписке
"""def send_updates(context, job):
        subscrubeJob = updater.job_queue
    context.job_morning = subscrubeJob.run_once()"""


def set_alarm(update, context):
    try:
        seconds = abs(int(context.args[0]))
        context.job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except (IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")


def alarm(context):
    context.bot.send_message(chat_id=context.job.context, text="Сработал будильник!")
