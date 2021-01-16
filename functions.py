#############################
#      support functions    #
#############################

import json
import logging
import urllib.parse
from datetime import datetime
import time

import pyjson5
from PIL import Image, ImageFilter
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from liquipediapy import dota

from data_model import Game, League, engine
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import exists, text


def leagues_search(query):
    leagues_list = get_current_leagues()
    result = []
    for league in leagues_list:
        if query in league[0]:
            result.append(league)
    return result


def get_current_leagues():
    Session = sessionmaker(bind=engine)
    session = Session()
    leagues = []
    for league in session.query(League):
        if check_end_league(league.dates):
            leagues.append(
                (
                    league.name,
                    league.icon_url,
                    league.page_url,
                    league.prize_pool,
                    league.dates,
                )
            )
    session.commit()
    return leagues


def get_league_info(league):
    Session = sessionmaker(bind=engine)
    session = Session()
    response = (
        session.query(
            League.name,
            League.tier,
            League.baner_url,
            League.page_url,
            League.dates,
            League.prize_pool,
            League.host_location,
        )
        .filter(League.name == text(league))
        .first()
    )
    session.commit()
    return response


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
        Game.league_name == text(league),
        Game.start_time >= datetime.now(),
    ).order_by(Game.start_time):
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


def get_game_info(game_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    responce = (
        session.query(
            Game.league_name,
            Game.team1,
            Game.team2,
            Game.game_format,
            Game.start_time,
            Game.twitch_channel,
        )
        .filter(Game.game_id == game_id)
        .all()[0]
    )
    session.commit()
    return responce


def add_leagues_to_database(leagues_by_tier):
    Session = sessionmaker(bind=engine)
    session = Session()
    for league in leagues_by_tier:
        if session.query(League).filter(League.name == league["name"].strip()).scalar():
            logging.info("Такой турнир уже существует")
        else:
            if check_end_league(league["dates"]):
                try:
                    new_league = League(
                        league_id=(get_league_id(league["name"].strip())),
                        tier=league["tier"],
                        name=league["name"].strip(),
                        icon_url=league["icon"],
                        page_url=league["page"],
                        baner_url=None,
                        dates=league["dates"],
                        prize_pool=league["prize_pool"],
                        teams=league["teams"],
                        host_location=league["host_location"],
                        # TODO winner': 'TBD', 'runner_up': 'TBD'}
                    )
                    session.add(new_league)
                except KeyError as error:
                    logging.warning(f"Can't create object for league {error}")
            session.commit()


def sync_current_leagues(context):
    dota_liquipedi = dota("appname")
    try:
        tournaments = dota_liquipedi.get_tournaments()
        tournaments_json = pyjson5.loads(str(tournaments))
        add_leagues_to_database(tournaments_json)
    except AttributeError:
        logging.warning("Not found data in API")


def sync_game_current_league(context):
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
                game_id=None,
                league_id=get_league_id(game["tournament"]),
                league_name=game["tournament"],
                league_short_name=game["tournament_short_name"],
                team1=game["team1"],
                team2=game["team2"],
                game_format=game["format"],
                start_time=datetime.strptime(
                    game["start_time"][0:-4], "%B %d, %Y - %H:%M"
                ),
                twitch_channel=game["twitch_channel"],
            )
            session.add(new_game)
        session.commit()


def sync_league_baner(context):
    dota_liquipedi = dota("appname")
    leagues = get_current_leagues()
    try:
        for league in leagues:
            Session = sessionmaker(bind=engine)
            session = Session()
            row = session.query(League).filter(League.name == league[0]).first()
            if row.baner_url == None:
                logging.info(f"Search baner for '{league[0]}'")
                baner_url = dota_liquipedi.get_tournament_baner(league[2])
                row.baner_url = baner_url
            session.commit()
            time.sleep(30)

    except KeyError as err:
        logging.info(err)
    except json.decoder.JSONDecodeError:
        logging.info('api request is block, try "https://liquipedia.net"')


def make_game_baner(baner_url, team1, team2):
    raw_background = requests.get(baner_url, stream=True).raw
    background = Image.open(raw_background)
    blured_background = background.filter(ImageFilter.GaussianBlur(10))
    bufer = BytesIO()
    blured_background.save(bufer, format = 'png')
    # TODO add teams logo
    bufer.seek(0)

    return bufer

