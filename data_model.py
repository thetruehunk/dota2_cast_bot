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
    Binary,
    DateTime,
    MetaData,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import generic_repr
import typing

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(
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
    team_name = Column(String)
    team_logo = Column(String)


@generic_repr
class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    geme_id = Column(Integer)


# If db is new - create struct
if not engine.dialect.has_table(engine, "league"):
    Base.metadata.create_all(engine)
