#######################################
#         keyboards for bot           #
#######################################
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

reply_start_kb = [
    [InlineKeyboardButton(f"LEAGUES 🏆", switch_inline_query_current_chat="current")],
    [InlineKeyboardButton(f"SEARCH 🔎", switch_inline_query_current_chat="")],
]

reply_subscribe_kb = [
    [InlineKeyboardButton(f"text stream", switch_inline_query_current_chat='123')],
    [InlineKeyboardButton(f"video stream", switch_inline_query_current_chat="13")],
    [InlineKeyboardButton(f"back", switch_inline_query_current_chat="13")],
]

start_kb_markup = InlineKeyboardMarkup(reply_start_kb)
subscribe_kb_markup = InlineKeyboardMarkup(reply_subscribe_kb)

