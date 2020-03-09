"""
Здесь мы обрабатываем вызываемые функции
"""

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
)

import emoji
from uuid import uuid4

# import requests
import logging

""" Emoji """
trophy = emoji.emojize(":trophy:")
magnifying_glass = emoji.emojize(":magnifying_glass_tilted_right:")
open_book = emoji.emojize(":open_book:")
party_popper = emoji.emojize(":party_popper:")


""" Клавиатуры """
reply_start_kb = [
    [
        InlineKeyboardButton(
            "ТУРНИРЫ " + trophy + "", switch_inline_query_current_chat="find top 10"
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
    reply_text = "Привет! Мы рады, что ты с нами! "+party_popper+""
    update.message.reply_text(reply_text, reply_markup=markup)


def help(update, context):
    logging.info("Вызвана функция help")
    update.effective_message.reply_text(
        "Мы умеем: /help - показать справку, @'Bot_Name' + leage_name - найти турнир"
    )


def get_leagues(update, context):
    pass


def inlinequery(update, context):
    """ ЗДЕСЬ НАХОДИТСЯ ШАБЛОННЫЙ КОД, ЕГО НУЖНО ЗАМЕНИТЬ """
    query = update.inline_query.query
    result = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="The International 2019",
            description="Турнир 19 года",
            # url = 'https://i1.pngguru.com/preview/835/152/984/marei-icon-theme-dota-2-logo.jpg',
            thumb_url="https://gamewelcome.ru/upload/par/kanobu/parsing/images/7a8e1d6f-bb2e-4e58-b446-0c7a04225004.jpg",
            input_message_content=InputTextMessageContent("OK, нужно доработать"),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="ESL One",
            description="Тут описание",
            # url = 'https://i1.pngguru.com/preview/835/152/984/marei-icon-theme-dota-2-logo.jpg',
            thumb_url="https://jpimg.com.br/uploads/2018/06/esl-one-belo-horizonte-1024x525.png",
            input_message_content=InputTextMessageContent("OK, нужно доработать"),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="The International",
            description="Описание",
            # url = 'https://i1.pngguru.com/preview/835/152/984/marei-icon-theme-dota-2-logo.jpg',
            thumb_url="http://www.dota2.com/international/overview/",
            input_message_content=InputTextMessageContent("OK, нужно доработать"),
        ),
    ]

    update.inline_query.answer(result)
