"""
Здесь мы обрабатываем вызываемые функции
"""
from datetime import datetime
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ParseMode
)
from telegram.ext import messagequeue as mq

from uuid import uuid4
from functions import get_current_leagues, get_games_current_league
import emoji
import logging
# from bot import subscribers

""" Emoji """
trophy = emoji.emojize(":trophy:")
magnifying_glass = emoji.emojize(":magnifying_glass_tilted_right:")
open_book = emoji.emojize(":open_book:")
party_popper = emoji.emojize(":party_popper:")


""" Клавиатуры """
reply_start_kb = [
    [
        InlineKeyboardButton(
            "ТУРНИРЫ " + trophy + "", switch_inline_query_current_chat="current"
        )
    ],
    [
        InlineKeyboardButton(
            "НАЙТИ " + magnifying_glass + "", switch_inline_query_current_chat="search"
        )
    ],
    [InlineKeyboardButton("ПОМОЩЬ " + open_book + "", callback_data="help")],
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
        reply_games_kb.append([InlineKeyboardButton(f"🔹{game[1]} ⚔️ 🔹{game[2]}   Format: {game[3]}  🕔 {game[4]}", callback_data="subscribe", parse_mode=ParseMode.MARKDOWN)])
    markup = InlineKeyboardMarkup(reply_games_kb)
    update.message.reply_text(f'*{message.split("по ")[1]}*', reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

def leagues_search(query):
    leagues_list = get_current_leagues()
    result = []
    for league in leagues_list:
        if query in league["name"]:
            result.append(league)
    return result


"""
#список всех турниров
def get_tournaments(tournamentType=None):
		tournaments = []
		if tournamentType is None:
			page_val = 'Portal:Tournaments'
		else:
			page_val = tournamentType.capitalize()+'_Tournaments'				
		soup,__ = self.liquipedia.parse(page_val)
		div_rows = soup.find_all('div',class_='divRow')
		for row in div_rows:
			tournament = {}

			values = row.find('div',class_="Tournament").get_text().split('\n')
			tournament['tier'] = re.sub('\W+',' ',values[0]).strip()
			tournament['name'] = values[1]

			try:
				tournament['icon'] = self.__image_base_url+row.find('div',class_="Tournament").find('img').get('src')
			except AttributeError:
				pass	

			tournament['dates'] = row.find('div',class_="Date").get_text()

			try:
				tournament['prize_pool'] = int(row.find('div',class_="Prize").get_text().rstrip().replace('$','').replace(',',''))
			except (AttributeError,ValueError):
				tournament['prize_pool'] = 0

			tournament['teams'] = re.sub('[A-Za-z]','',row.find('div',class_="PlayerNumber").get_text()).rstrip()	
			location_list= unicodedata.normalize("NFKD",row.find('div',class_="Location").get_text().rstrip()).split(',')	
			tournament['host_location'] = location_list[0]

			try:
				tournament['event_location'] = location_list[1]
			except IndexError:
				pass	
		
			if len(row) < 15:
				links_a = row.find('div',class_="SecondPlace").find_all('a')
				tournament['links'] = []
				for link in links_a:
					link_list = link.get('href').split('.')
					site_name = link_list[-2].replace('https://','')
					tournament['links'].append({site_name:link.get('href')})
			else:
				tournament['winner'] = 	unicodedata.normalize("NFKD",row.find('div',class_="FirstPlace").get_text().rstrip())	
				tournament['runner_up'] = 	unicodedata.normalize("NFKD",row.find('div',class_="SecondPlace").get_text().rstrip())	

			tournaments.append(tournament)

		return tournaments
"""


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
    

def subscribe(update, context):
    subscribers.add(update.message.chat_id)
    update.message.reply_text("Вы подписались") #переделать, чтобы подписаться на конкретный турнир/игру
    print(subscribers)


def send_updates(context, job):
    for chat_id in subscribers:
        context.bot.sendMessage(
            chat_id=chat_id,
            text="Тут будет инфа по турниру на который подписался пользователь",
        )


def unsubscribe(update, context):
    if update.message.chat_id in subscribers:
        subscribers.remove(update.message.chat_id)
        update.message.reply_text("Вы отпиcались от уведомлений")
    else:
        update.message.reply_text(
            "Вы не подписаны на уведомления, наберите /subscribe чтобы подписаться"
        )


def set_alarm(update, context):
    try:
        seconds = abs(int(context.args[0]))
        context.job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except (IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")


def alarm(context):
    context.bot.send_message(chat_id=context.job.context, text="Сработал будильник!")
