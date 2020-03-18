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
            "НАЙТИ " + magnifying_glass + "", switch_inline_query_current_chat=""
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
    else:
        pass
