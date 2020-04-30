import json

import requests


def get_bet_koef(team1, team2, start_date):
    responce = requests.get("https://api.egamersworld.com/dota2/bets")
    r_json = json.loads(responce.text)
    for element in r_json["recentMatches"]:
        if element["status"] == "upcoming":
            if (
                (
                    element["home_team_name"] == team1
                    and element["away_team_name"] == team2
                )
                and element["start_date"] >= start_date
            ) or (
                (
                    element["home_team_name"] == team2
                    and element["away_team_name"] == team1
                )
                and element["start_date"] >= start_date
            ):
                for bet in element["odds"]:
                    if bet["bookmaker_name"] == "Parimatch":
                        return f'{element["home_team_name"]}: {bet["koef"]["k1"]}, {element["away_team_name"]}: {bet["koef"]["k2"]}'
