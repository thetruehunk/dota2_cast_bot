import json
import logging
import urllib.parse
from datetime import datetime

import pyjson5
import requests
from liquipediapy import dota

from data_model import Game, League, engine, games_table, leagues_table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import exists, text

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
    try:
        response = requests.get(
            f"https://api.opendota.com/api/explorer/?sql=select leagueid from leagues where name = '{urllib.parse.quote(league)}'"
        )
        league_id = json.loads(response.text)
        if league_id:
            if league_id["rows"]:
                return league_id["rows"][0]["leagueid"]
        else:
            return None
    except KeyError:
        logging.info(f"Отсутствуют данные по: {league}")
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
    for game in session.query(Game).filter(
        Game.league_name == text(league)
    ):  # сортировка по дате
        games.append(
            (
                game.league_name,
                game.team1,
                game.team2,
                game.game_format,
                game.start_time,
                game.game_id,
            )
        )
    session.commit()
    return games


def add_leagues_to_database(leagues_by_tier):
    Session = sessionmaker(bind=engine)
    session = Session()
    for league in leagues_by_tier:
        if (
            session.query(League)
            .filter(
                League.name == league["name"].strip(), League.dates == league["dates"]
            )
            .scalar()
        ):
            logging.info("Такой турнир уже существует")
        else:
            if check_end_league(league["dates"]):
                print(league)
                try:
                    new_league = League(
                        (get_league_id(league["name"].strip())),
                        league["tier"],
                        league["name"].strip(),
                        league["icon"],
                        league["dates"],
                        league["prize_pool"],
                        league["teams"],
                        league["host_location"],
                        league["event_location"],
                        str(league["links"]),
                    )
                    session.add(new_league)
                except KeyError:
                    new_league = League(
                        (get_league_id(league["name"].strip())),
                        league["tier"],
                        league["name"].strip(),
                        league["icon"],
                        league["dates"],
                        league["prize_pool"],
                        league["teams"],
                        league["host_location"],
                        league["event_location"],
                        None,
                    )
                    session.add(new_league)
            session.commit()


def sync_current_leagues():
    dota_liquipedi = dota("appname")
    try:
        tournaments = dota_liquipedi.get_tournaments()
        tournaments_json = pyjson5.loads(str(tournaments))
        add_leagues_to_database(tournaments_json)
    except AttributeError:
        logging.warning("Not found data in API")


def sync_game_current_league():
    dota_liquipedi = dota("appname")
    Session = sessionmaker(bind=engine)
    session = Session()
    games = dota_liquipedi.get_upcoming_and_ongoing_games()
    games_json = pyjson5.loads(str(games).replace("None", "'None'"))
    for game in games_json:
        if (
            session.query(Game)
            .filter(
                Game.league_name == game["tournament"],
                Game.start_time
                == datetime.strptime(game["start_time"][0:-4], "%B %d, %Y - %H:%M"),
            )
            .scalar()
        ):
            logging.info("Такая игра существует")
        else:
            new_game = Game(
                None,
                get_league_id(game["tournament"]),
                game["tournament"],
                game["team1"],
                game["team2"],
                game["format"],
                datetime.strptime(game["start_time"][0:-4], "%B %d, %Y - %H:%M"),
                game["twitch_channel"],
            )
            session.add(new_game)
        session.commit()
