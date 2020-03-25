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
)
from liquipediapy import dota
from uuid import uuid4
import emoji
import os
import requests
import logging
import json
import pyjson5

from functions import *

""" Инициализация liquipediapy """
dota_obj = dota("appname")

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


def get_leagues():
    # os.environ['STEAM_API_KEY']
    # os.environ['TOKEN']
    stratz_req = requests.get("https://api.stratz.com/api/v1/league")
    stratz_data = json.loads(stratz_req.text)
    stratz_data.sort(key=lambda z: z["endDateTime"])
    return stratz_data


def get_current_leagues():
    dota_liquipedi = dota("appname")

    leagues = []

    major = dota_liquipedi.get_tournaments("Major")
    minor = dota_liquipedi.get_tournaments("Minor")
    premier = dota_liquipedi.get_tournaments("Premier")

    major_json = pyjson5.loads(str(major))
    minor_json = pyjson5.loads(str(minor))
    premier_json = pyjson5.loads(str(premier))

    for item in major_json:
        if check_end_league(item["dates"]):
            leagues.append(
                (item["name"], item["icon"], item["prize_pool"], item["dates"])
            )
    for item in minor_json:
        if check_end_league(item["dates"]):
            leagues.append(
                (item["name"], item["icon"], item["prize_pool"], item["dates"])
            )
    for item in premier_json:
        if check_end_league(item["dates"]):
            leagues.append(
                (item["name"], item["icon"], item["prize_pool"], item["dates"])
            )

    return leagues

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
                    title=item[0],
                    description= f"Period: {item[3]}, prize: ${item[2]}",
                    thumb_url=item[1],
                    input_message_content=InputTextMessageContent(
                        "OK, нужно доработать"
                    ),
                )
            )
        update.inline_query.answer(result)
    elif query == "search":
        result = []
        user_text = (update.message.text.split()[1:].strip())
        result_search = leagues_search(user_text)
        for item in result_search:
            result.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=item[0],
                    description= f"Period: {item[3]}, prize: ${item[2]}",
                    thumb_url=item[1],
                    input_message_content=InputTextMessageContent(
                        "OK, нужно доработать"
                    ),
                )
            )
        update.inline_query.answer(result)
            

        

        
        


        




