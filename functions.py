from datetime import datetime
from liquipediapy import dota
import json
import logging
import pyjson5
import requests
import urllib.parse
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import text
from data_model import engine, League, Game, leagues_table, games_table

mapper(Game, games_table)
mapper(League, leagues_table)

def get_leagues():
    # os.environ['STEAM_API_KEY']
    # os.environ['TOKEN']
    stratz_req = requests.get("https://api.stratz.com/api/v1/league")
    stratz_data = json.loads(stratz_req.text)
    stratz_data.sort(key=lambda z: z["endDateTime"])
    return stratz_data


def get_current_leagues():
    Session = sessionmaker(bind=engine)
    session = Session()
    leagues = []
    for league in session.query(League):
        if check_end_league(league.dates):
            leagues.append(
                (league.name, league.icon_url, league.prize_pool, league.dates)
            )
    session.commit()
    return leagues


def get_league_id(league):
    response = requests.get(
        f"https://api.opendota.com/api/explorer/?sql=select leagueid from leagues where name = '{urllib.parse.quote(league)}'"
    )
    league_id = json.loads(response.text)
    if league_id:
        if league_id["rows"]:
            return league_id["rows"][0]["leagueid"]
    else:
        return None


def check_end_league(period):
    now = datetime.now()
    try:
        p_end_year = period.split(",")[-1].strip()
        p_end_day = period.split(",")[-2].split()[-1]
        
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

        # Проблема с текущей датой
        if now <= parsed_period:
            return True
        else:
            return False

    except IndexError:
        logging.exception("не хватает данных")
    except ValueError:
        logging.exception("это неправильный формат периода")


def get_games_current_league(league):
    Session = sessionmaker(bind=engine)
    session = Session()
    games = []
    for game in session.query(Game).filter(Game.league_name==text(league)): # сортировка по дате 
        games.append((game.league_name, game.team1, game.team2, game.game_format, game.start_time, game.game_id))
    session.commit()
    return games


def sync_current_leagues():
    dota_liquipedi = dota("appname")
    mapper(League, leagues_table)  # non_primary=True
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        major = dota_liquipedi.get_tournaments("Major")
        major_json = pyjson5.loads(str(major))
        for item in major_json:
            if check_end_league(item["dates"]):
                my_data = League(
                    (get_league_id(item["name"].strip())),
                    item["tier"],
                    item["name"].strip(),
                    item["icon"],
                    item["dates"],
                    item["prize_pool"],
                    item["teams"],
                    item["host_location"],
                    item["event_location"],
                    # item["links"],
                )
            session.add(my_data)
            session.commit()
    except AttributeError:
        logging.warning("Not found data in API for Major")
    try:
        minor = dota_liquipedi.get_tournaments("Minor")
        minor_json = pyjson5.loads(str(minor))
        for item in minor_json:
            if check_end_league(item["dates"]):
                my_data = League(
                    (get_league_id(item["name"].strip())),
                    item["tier"],
                    item["name"].strip(),
                    item["icon"],
                    item["dates"],
                    item["prize_pool"],
                    item["teams"],
                    item["host_location"],
                    item["event_location"],
                    # item["links"],
                )
            session.add(my_data)
            session.commit()
    except AttributeError:
        logging.warning("Not found data in API for Minor")
    try:
        premier = dota_liquipedi.get_tournaments("Premier")
        premier_json = pyjson5.loads(str(premier))
        for item in premier_json:
            if check_end_league(item["dates"]):
                my_data = League(
                    (get_league_id(item["name"].strip())),
                    item["tier"],
                    item["name"].strip(),
                    item["icon"],
                    item["dates"],
                    item["prize_pool"],
                    item["teams"],
                    item["host_location"],
                    item["event_location"],
                    # item["links"],
                )
            session.add(my_data)
            session.commit()
    except AttributeError:
        logging.warning("Not found data in API for Premier")


def sync_game_current_league():
    dota_liquipedi = dota("appname")
    mapper(Game, games_table)
    Session = sessionmaker(bind=engine)
    session = Session()
    games = dota_liquipedi.get_upcoming_and_ongoing_games()
    games_json = pyjson5.loads(str(games).replace("None", "'None'"))
    print(games_json)
    for item in games_json:
        my_data = Game(
            None,
            get_league_id(item["tournament"]),
            item["tournament"],
            item["team1"],
            item["team2"],
            item["format"],
            datetime.strptime(item["start_time"][0:-4], "%B %d, %Y - %H:%M"),
            item["twitch_channel"],
        )
        session.add(my_data)
        session.commit()
