from src.helpers.helpers import chunkify


class DataPreparation:
    @staticmethod
    def prepare_players(all_matches, chunk_size=25):
        all_players = []
        for match in all_matches:
            for pl in match['home_team_starters']:
                all_players.append(pl)
            for pl in match['away_team_starters']:
                all_players.append(pl)
            for pl in match['home_team_subs']:
                all_players.append(pl)
            for pl in match['away_team_subs']:
                all_players.append(pl)
        cured_players_list, used_licences = [], []
        for pl in all_players:
            if not pl['licence_number'] in used_licences:
                used_licences.append(pl['licence_number'])
                cured_players_list.append(pl)
        chunked_all_players = chunkify(cured_players_list, chunk_size=chunk_size)
        return chunked_all_players

    @staticmethod
    def prepare_teams(all_matches):
        all_teams = []
        for match in all_matches:
            all_teams.append({"name": match['home_team'], "season": match['season_name'], "league_code": match['league_code']})
            all_teams.append({"name": match['away_team'], "season": match['season_name'], "league_code": match['league_code']})
        cured_teams_list, used_names = [], []
        for pl in all_teams:
            if not pl['name'] in used_names:
                used_names.append(pl['name'])
                cured_teams_list.append(pl)
        return cured_teams_list

    @staticmethod
    def prepare_venues(all_matches):
        all_venues = []
        for match in all_matches:
            all_venues.append({"name": match['venue']})
        cured_venues_list, used_names = [], []
        for pl in all_venues:
            if not pl['name'] in used_names:
                used_names.append(pl['name'])
                cured_venues_list.append(pl)
        return cured_venues_list



    @staticmethod
    def prepare_matches(journee):
        cured_matches_list = []
        selected_keys = ['home_team', 'away_team', 'score', 'home_team_score', 'away_team_score', 'venue', 'date_str',
                         'date', 'season_name', 'league_name', 'league_code', 'stage', 'match_day_str', 'match_day']
        for m in journee:
            selected = {key: m.get(key) for key in selected_keys}
            cured_matches_list.append(selected)
        return cured_matches_list

    @staticmethod
    def prepare_starters(match_data):
        cured_player_list = []
        for k, team in zip(['home_team_starters', 'away_team_starters'], ['home_team', 'away_team']):
            for pl in match_data[k]:
                pl['team'] = match_data[team]
                pl['match_date'] = match_data['date']
                pl['season_name'] = match_data['season_name']
                pl['league_code'] = match_data['league_code']
                pl['stage'] = match_data['stage']
                pl['match_day'] = match_data['match_day']
                # print(pl.keys())
                cured_player_list.append(pl)
        return cured_player_list

    @staticmethod
    def prepare_substitutes(match_data):
        cured_player_list = []
        for k, team in zip(['home_team_subs', 'away_team_subs'], ['home_team', 'away_team']):
            for pl in match_data[k]:
                pl['team'] = match_data[team]
                pl['match_date'] = match_data['date']
                pl['season_name'] = match_data['season_name']
                pl['league_code'] = match_data['league_code']
                pl['stage'] = match_data['stage']
                pl['match_day'] = match_data['match_day']
                cured_player_list.append(pl)
        return cured_player_list

    @staticmethod
    def prepare_substitutions(match_data):
        substitutions = []
        for sub in match_data["substitutions"]:
            sub['match_date'] = match_data['date']
            sub['season_name'] = match_data['season_name']
            sub['league_code'] = match_data['league_code']
            sub['stage'] = match_data['stage']
            sub['match_day'] = match_data['match_day']
            substitutions.append(sub)
        return substitutions

    @staticmethod
    def prepare_yellow_cards(match_data):
        yellow_cards = []
        for card in match_data["yellow_cards"]:
            card['date'] = match_data['date']
            card['season_name'] = match_data['season_name']
            card['league_code'] = match_data['league_code']
            card['stage'] = match_data['stage']
            card['match_day'] = match_data['match_day']
            yellow_cards.append(card)
        return yellow_cards

    @staticmethod
    def prepare_referees(match_data):
        referees = []
        for card in match_data["referees"]:
            card['match_date'] = match_data['date']
            card['season_name'] = match_data['season_name']
            card['league_code'] = match_data['league_code']
            card['stage'] = match_data['stage']
            card['match_day'] = match_data['match_day']
            referees.append(card)
        return referees
