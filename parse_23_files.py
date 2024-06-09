import os
from pprint import pprint
from src.parsers.parser_23 import Parser
from src.helpers.helpers import jsonify, save_json, extract_competition_info

files_base = "C:/Users/Administrator/PycharmProjects/tn-football-db/match_files/raw/22-23/l1/"
files = os.listdir(files_base)

target_base = "C:/Users/Administrator/PycharmProjects/tn-football-db/match_files/parsed/22-23/l1/"
p = Parser()

season_name = "22/23"
league_name = "Championnat de Tunisie"
league_code = "l1"

for f in files:
    file_path = files_base + f
    # print("file_path: ", f)
    json_name = f[:-3]+"json"
    stage, match_day_str, match_day = extract_competition_info(f)
    doc = p.parser_re(file_path)
    for match in doc:
        print(match['home_team'], match['score'], match['away_team'],
              match['venue'], match['date'])
        match['season_name'] = season_name
        match['league_name'] = league_name
        match['league_code'] = league_code
        match['stage'] = stage
        match['match_day_str'] = match_day_str
        match['match_day'] = match_day
        # print(match.keys())
        print("**************************************************************************************************")
        # print("////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
        # print("////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
    doc = jsonify(doc)
    save_json(doc, target_base+json_name)