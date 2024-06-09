import os
from pprint import pprint

import requests

from src.exporter.data_prep import DataPreparation
from src.helpers.helpers import read_json

prep = DataPreparation()


def post_data(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


files_path = "C:/Users/Administrator/PycharmProjects/tn-football-db/match_files/parsed/22-23/l1/"

base = "http://127.0.0.1:8000"

leagues_url = f"{base}/api_v0/leagues-ftf/"
teams_url = f"{base}/api_v0/teams-ftf/"
venues_url = f"{base}/api_v0/venues-ftf/"
players_url = f"{base}/api_v0/players-ftf/"
matches_url = f"{base}/api_v0/matches-ftf/"
starters_url = f"{base}/api_v0/starters-ftf/"
substitutes_url = f"{base}/api_v0/substitutes-ftf/"
substitutions_url = f"{base}/api_v0/substitutions-ftf/"
referees_url = f"{base}/api_v0/referees-ftf/"


all_matches = []
files = os.listdir(files_path)
for f in files:
    journee = read_json(files_path + f)

    for match in journee:
        all_matches.append(match)

#         starters = prep.prepare_starters(match)
#         post_data(starters_url, starters)
#
#         substitutes = prep.prepare_substitutes(match)
#         post_data(substitutes_url, substitutes)
#
#         substitutions = prep.prepare_substitutions(match)
#         post_data(substitutions_url, substitutions)
#
#         referees = prep.prepare_referees(match)
#         post_data(referees_url, referees)
#
#         # yellow_cards = prep.prepare_yellow_cards(match)
#         # post_data(yellow_cards_url, yellow_cards)
#
#     matches = prep.prepare_matches(journee)
#     post_data(matches_url, matches)
#     # print('******************************************************************************************************************************************')
#
#
# teams = prep.prepare_teams(all_matches)
# post_data(teams_url, teams)
#
# venues = prep.prepare_venues(all_matches)
# post_data(venues_url, venues)

players = prep.prepare_players(all_matches)
for ch in players:
    post_data(players_url, ch)

