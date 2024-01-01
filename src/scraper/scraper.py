import os

import requests as req


class UrlBase(object):
    @staticmethod
    def url_formatter(league, season, tournament_type, match_day):
        url = ""
        if season == "22-23" and league == "l1":
            if tournament_type == "regular_season":
                if match_day == 1:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2023/02/1e%CC%80re-Journe%CC%81e-Ligue-I-%E2%80%93-Feuilles-de-Matchs-1.pdf"
                elif match_day in range(2, 14):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2023/02/{match_day}e%CC%80me-Journe%CC%81e-Ligue-I-%E2%80%93-Feuilles-de-Matchs-1.pdf"
            elif tournament_type == "play_off":
                if match_day in range(1, 8):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2023/06/PLAY-OFF-0{match_day}.pdf"
            elif tournament_type == "play_out":
                if match_day in range(1, 10):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2023/06/PLAY-OUT-0{match_day}.pdf"
                elif match_day == 10:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2023/06/PLAY-OUT-{match_day}.pdf"
        elif season == "21-22" and league == "l1":
            if tournament_type == "regular_season":
                if match_day in range(1, 11):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2022/03/Ligue-I-J{match_day}-2122.pdf"
        elif season == "20-21" and league == "l1":
            if tournament_type == "regular_season":
                if match_day in range(1, 12) or match_day == 13:
                    if match_day in [6, 10, 11, 13]:
                        url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2021/02/J{match_day}_L1_2020-2021.pdf"
                    else:
                        url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2021/01/J{match_day}_L1_2020-2021.pdf"
                elif match_day == 12:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2021/05/J12-2020-2021.pdf"
                elif match_day in range(14, 21):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2021/03/J{match_day}.pdf"
                elif match_day in [21, 23]:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2014/12/J{match_day}-2020-2021.pdf"
                elif match_day in [22, 24]:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2021/05/J{match_day}-2020-2021.pdf"
                elif match_day == 25:
                    url = "https://www.ftf.org.tn/fr/wp-content/uploads/2021/06/J25-LIGUE-I.pdf"
                elif match_day == 26:
                    url = "https://www.ftf.org.tn/fr/wp-content/uploads/2021/05/LIGUE-I-J26.pdf"
        elif season == "19-20":
            if league == "l1" and tournament_type == "regular_season":
                if match_day == 1:
                    url = "https://www.ftf.org.tn/fr/wp-content/uploads/2019/11/1e%CC%80re-Journe%CC%81e-Ligue-I-%E2%80%93-Feuilles-de-Matchs.pdf"
                elif match_day in [2, 5, 6, 8, 9]:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2019/11/{match_day}e%CC%80me-Journe%CC%81e-Ligue-I-%E2%80%93-Feuilles-de-Matchs.pdf"
                elif match_day in [3, 4, 7]:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2020/05/Ligue-I-Journe%CC%81e-0{match_day}-20192020.pdf"
                elif match_day in range(10, 17):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2020/05/Ligue-I-Journe%CC%81e-{match_day}-20192020.pdf"
                elif match_day in [17, 18, 19, 20]:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2020/08/{match_day}e%CC%80me-Journe%CC%81e-Ligue-I-%E2%80%93-Feuilles-de-Matchs.pdf"
                elif match_day in range(21, 25):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2020/10/Ligue-I-20192020-J{match_day}.pdf"
                elif match_day in [25, 26]:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2014/12/{match_day}e%CC%80me-Journe%CC%81e-Ligue-I-%E2%80%93-Feuilles-de-Matchs.pdf"
            if league == "l2" and tournament_type == "regular_season":
                if match_day == 1:
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2020/07/LIGUE-II-1e%CC%80re-Journe%CC%81e-20192020.pdf"
                elif match_day in range(2, 11):
                    url = f"https://www.ftf.org.tn/fr/wp-content/uploads/2020/07/LIGUE-II-{match_day}e%CC%80me-Journe%CC%81e-20192020.pdf"

        return url

    @staticmethod
    def save_path_formatter(league, season, tournament_type, match_day):
        base_path = "C:/Users/Administrator/PycharmProjects/tn-football-db/pdf_files/"
        file_save_path = f"{base_path}{season}/{league}/{tournament_type}_j{match_day}.pdf"
        return file_save_path


class Scraper(object):
    def __init__(self):
        self.ub = UrlBase()

    @staticmethod
    def download_pdf(url, save_path):
        response = req.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded: {url} -> {save_path}")
        else:
            print(f"Failed to download: {url} (Status code: {response.status_code})")

    def save_match_file(self, league, season, tournament_type, match_day):
        """
        :param league: (str) l1, l2, l3 ...
        :param season: (str) 22-23, 21-22, ...
        :param tournament_type: (str) regular_season, play_off, play_out
        :param match_day: (int) like 1,2,3,...
        :return:
        """
        url = self.ub.url_formatter(league=league, season=season, tournament_type=tournament_type, match_day=match_day)
        if url:
            save_path = self.ub.save_path_formatter(league=league, season=season, tournament_type=tournament_type,
                                                    match_day=match_day)
            if os.path.exists(save_path):
                print(f"{save_path}   already exists")
            else:
                self.download_pdf(url=url, save_path=save_path)
        else:
            print("No URL was received")

    def save_22_23_season_games(self):
        season = '22-23'
        league = 'l1'
        for tournament_type in ['regular_season', 'play_off', 'play_out']:
            if tournament_type == "regular_season":
                for match_day in range(1, 14):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)
            elif tournament_type == "play_off":
                for match_day in range(1, 8):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)
            elif tournament_type == "play_out":
                for match_day in range(1, 11):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)

    def save_21_22_season_games(self):
        season = '21-22'
        league = 'l1'
        for tournament_type in ['regular_season']:
            if tournament_type == "regular_season":
                for match_day in range(1, 11):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)

    def save_20_21_season_games(self):
        season = '20-21'
        league = 'l1'
        for tournament_type in ['regular_season']:
            if tournament_type == "regular_season":
                for match_day in range(1, 27):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)

    def save_19_20_season_games(self):
        season = '19-20'
        tournament_type = 'regular_season'
        for league in ['l1', 'l2']:
            if league == 'l1':
                for match_day in range(1, 27):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)
            if league == 'l2':
                for match_day in range(1, 11):
                    self.save_match_file(league=league, season=season, tournament_type=tournament_type,
                                         match_day=match_day)


scr = Scraper()
scr.save_19_20_season_games()
