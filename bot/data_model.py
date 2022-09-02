# This is model for save data
# leagues, games, other informations
# about matchup and users

import os
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    #Binary,
    DateTime,
    MetaData,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import generic_repr
import typing

basedir = os.path.abspath("data/")
engine = create_engine(
    #"sqlite:///" + os.path.join(basedir, "dota.db3"),
    "sqlite:///" + os.path.join(basedir, "dota.db3"),
    echo=False,
)
Base = declarative_base()


@generic_repr
class League(Base):
    __tablename__ = "league"

    id = Column(Integer, primary_key=True)
    league_id = Column(Integer)
    tier = Column(String)
    name = Column(String)
    icon_url = Column(String)
    page_url = Column(String)
    baner_url = Column(String)
    dates = Column(String)
    prize_pool = Column(Integer)
    teams = Column(Integer)
    host_location = Column(String)


@generic_repr
class Game(Base):
    __tablename__ = "game"

    game_id = Column(Integer, primary_key=True)
    league_id = Column(Integer)
    league_name = Column(String)
    league_short_name = Column(String)
    team1 = Column(String)
    team2 = Column(String)
    game_format = Column(String)
    start_time = Column(DateTime)
    twitch_channel = Column(String)


@generic_repr
class Team(Base):
    __tablename__ = "team"

    team_id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    last_match_time = Column(Integer)
    name = Column(String)
    tag = Column(String)
    logo_url = Column(String)


@generic_repr
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    is_bot = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)

# If db is new - create struct
#TODO  please use ``inspect(some_engine).has_table(<tablename>>)`` for public API use
#if not engine.dialect.has_table(engine, "league"):
#    Base.metadata.create_all(engine)
