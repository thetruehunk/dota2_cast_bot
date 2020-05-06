# https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails#Barracks_Status

# barracks state:
#    ┌─┬───────────── Not used.
#    │ │ ┌─────────── Bottom Ranged
#    │ │ │ ┌───────── Bottom Melee
#    │ │ │ │ ┌─────── Middle Ranged
#    │ │ │ │ │ ┌───── Middle Melee
#    │ │ │ │ │ │ ┌─── Top Ranged
#    │ │ │ │ │ │ │ ┌─ Top Melee
#    │ │ │ │ │ │ │ │
#    0 0 0 0 0 0 0 0

#    ┌─┬─┬─┬─┬─────────────────────── Not used.ß
#    │ │ │ │ │ ┌───────────────────── Ancient Bottom
#    │ │ │ │ │ │ ┌─────────────────── Ancient Top
#    │ │ │ │ │ │ │ ┌───────────────── Bottom Tier 3
#    │ │ │ │ │ │ │ │ ┌─────────────── Bottom Tier 2
#    │ │ │ │ │ │ │ │ │ ┌───────────── Bottom Tier 1
#    │ │ │ │ │ │ │ │ │ │ ┌─────────── Middle Tier 3
#    │ │ │ │ │ │ │ │ │ │ │ ┌───────── Middle Tier 2
#    │ │ │ │ │ │ │ │ │ │ │ │ ┌─────── Middle Tier 1
#    │ │ │ │ │ │ │ │ │ │ │ │ │ ┌───── Top Tier 3
#    │ │ │ │ │ │ │ │ │ │ │ │ │ │ ┌─── Top Tier 2
#    │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ ┌─ Top Tier 1
#    │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
#    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

import json

import requests


def get_match_id(team1, team2):
    responce = requests.get("https://api.opendota.com/api/live")
    responce_json = json.loads(responce.text)
    for element in responce_json:
        try:
            if ((element["team_name_radiant"] == team1 and element["team_name_dire"] == team2) and element["deactivate_time"] == 0) or ((element["team_name_radiant"] == team2 and element["team_name_dire"] == team1) and element["deactivate_time"] == 0):
                return element["match_id"]
        except KeyError:
            pass # for not pro matches


def get_match_state(match_id):
    responce = requests.get("https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v001?key=FB73DF3B5529D699D2AC8CBE7F861B72")
    responce_json = json.loads(responce.text)
    for element in responce_json["result"]["games"]:
        if element["match_id"] == match_id:
            print(f'{element["scoreboard"]["dire"]["barracks_state"]:08b}', f'{element["scoreboard"]["dire"]["tower_state"]:08b}')
            print(f'{element["scoreboard"]["radiant"]["barracks_state"]:08b}', f'{element["scoreboard"]["radiant"]["tower_state"]:08b}')




# get_match_id("TEAM Ethereal", "Panda Gaming")

get_match_state(5389788640)

# можно получить данные лога матча тут
# https://api.opendota.com/api/explorer/?sql=select * from match_logs where match_id = 5389409751