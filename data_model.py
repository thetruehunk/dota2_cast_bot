""" Здесь лежат описания таблиц и классы для взаимодействия ними"""


from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData
# from sqlalchemy.orm import mapper, sessionmaker
# from sqlalchemy.sql import text
from datetime import datetime
import os

# получаем путь к текущему каталогу
basedir = os.path.abspath(os.path.dirname(__file__))
# подключаемся к БД
engine = create_engine("sqlite:///" + os.path.join(basedir, "dota.db3"), echo=True,)

metadata = MetaData()
# описываем структуру БД
leagues_table = Table(
    "leagues",
    metadata,
    Column("id", Integer, primary_key=True),  # sqlite_autoincrement=True
    Column("league_id", Integer),
    Column("tier", String),
    Column("name", String),
    Column("icon_url", String),
    Column("dates", String),  # timezone=False
    Column("prize_pool", Integer),
    Column("teams", Integer),
    Column("host_location", String),
    Column("event_location", String),
    # Column("links", String),
)
games_table = Table(
    "games",
    metadata,
    Column("game_id", Integer, primary_key=True),
    Column("league_id", Integer),  # ForeignKey('leagues_table.league_id')
    Column("league_name", String),
    Column("team1", String),
    Column("team2", String),
    Column("game_format", String),
    Column("start_time", DateTime),
    Column("twitch_channel", String),
)
teams_table = Table(
    "teams",
    metadata,
    Column("team_id", Integer, primary_key=True),
    Column("team_name", String),
    Column("team_logo", String),
)
users_table = Table("users", metadata, Column("id", Integer, primary_key=True), Column("user_id", Integer), Column("game_id", Integer))

# создаем обьекты для взаимодействия с БД
class League(object):
    def __init__(
        self,
        league_id,
        tier,
        name,
        icon_url,
        dates,
        prize_pool,
        teams,
        host_location,
        event_location,
        # links,
    ):
        self.league_id = league_id
        self.tier = tier
        self.name = name
        self.icon_url = icon_url
        self.dates = dates
        self.prize_pool = prize_pool
        self.teams = teams
        self.host_location = host_location
        self.event_location = event_location
        # self.links = links


class Game(object):
    def __init__(
        self, game_id, league_id, league_name, team1, team2, game_format, start_time, twitch_channel,
    ):
        self.game_id = game_id
        self.league_id = league_id
        self.league_name = league_name
        self.team1 = team1
        self.team2 = team2
        self.game_format = game_format
        self.start_time = start_time
        self.twitch_channel = twitch_channel


class Team(object):
    def __init__(
        self, team_id, team_name, team_logo,
    ):
        self.team_id = team_id
        self.team_name = team_name
        self.team_logo = team_logo


class User(object):
    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id
