from datetime import datetime
from liquipediapy import dota
import json
import logging
import pyjson5
import requests


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
    try:
        major = dota_liquipedi.get_tournaments("Major")
        major_json = pyjson5.loads(str(major))
        for item in major_json:
            if check_end_league(item["dates"]):
                leagues.append(
                    (item["name"], item["icon"], item["prize_pool"], item["dates"])
                )
    except AttributeError:
        logging.warning("Not found data in API for Major")
    try:
        minor = dota_liquipedi.get_tournaments("Minor")
        minor_json = pyjson5.loads(str(minor))
        for item in minor_json:
            if check_end_league(item["dates"]):
                leagues.append(
                    (item["name"], item["icon"], item["prize_pool"], item["dates"])
                )
    except AttributeError:
        logging.warning("Not found data in API for Minor")
    try:
        premier = dota_liquipedi.get_tournaments("Premier")
        premier_json = pyjson5.loads(str(premier))
        for item in premier_json:
            if check_end_league(item["dates"]):
                leagues.append(
                    (item["name"], item["icon"], item["prize_pool"], item["dates"])
                )
    except AttributeError:
        logging.warning("Not found data in API for Premier")

    return leagues


def check_end_league(period):
    now = datetime.now()
    try:
        p_end_year = period.split(",")[-1].strip()
        p_end_day = period.split(",")[-2].split()[-1]
        p_end_month = ""

        if (
            "-" in period.split(",")[-2]
            and len(period.split(",")[-2].split("-")[-1].split()) == 2
        ):
            p_end_month = period.split(",")[-2].split("-")[-1].split()[0]
        elif (
            "-" in period.split(",")[-2]
            and len(period.split(",")[-2].split("-")[-1].split()) == 1
        ):
            p_end_month = period.split("-")[0].strip().split()[0]
        else:
            p_end_month = period.split(",")[-2].split()[0]

        parsed_period = datetime.strptime(
            "23:59:59 " + " " + p_end_month + " " + p_end_day + " " + p_end_year,
            "%H:%M:%S %b %d %Y",
        )

        """ Проблема с текущей датой"""
        if now <= parsed_period:
            return True
        else:
            return False

    except IndexError:
        logging.exception("не хватает данных")
    except ValueError:
        logging.exception("это неправильный формат периода")


def get_games_current_league(league):
    league_game = []
    dota_liquipedi = dota("appname")
    games = dota_liquipedi.get_upcoming_and_ongoing_games()
    games_json = pyjson5.loads(str(games).replace("None", "'None'"))
    for item in games_json:
        if item["tournament"] == league:
            league_game.append(item)
    print(league_game)
    return league_game
