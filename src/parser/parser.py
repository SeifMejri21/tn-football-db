import os
import re
from pprint import pprint

import fitz


class Parser(object):

    @staticmethod
    def pdf_reader(file_path):
        return 1

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        text = ""
        tables_lines = []
        with fitz.open(pdf_path) as pdf_document:
            num_pages = pdf_document.page_count
            for page_number in range(num_pages):
                page = pdf_document[page_number]
                # tables = page.find_tables()
                # for t in tables:
                #     for line in t.extract():  # print cell text for each row
                #         tables_lines.append(line)
                text += page.get_text()
        return text, tables_lines

    @staticmethod
    def titulaires_parser(text):
        return

    @staticmethod
    def rect_formatter(text):
        # try:
        #     print(text)
            rect = re.sub('\n', ' ', text)
            rect_splitted = rect.split(' ')
            rect_splitted = [t for t in rect_splitted if t]
        # except Exception as e:
        #     rect_splitted = []
        #     print(text)
        #     print(e)
            return rect_splitted

    def parse_titulaires(self, titulaires_text):
        players_list = []
        rect_splitted = self.rect_formatter(titulaires_text)
        player_info = {"shirt_number": None, "licence": None, "name": ''}
        for r in rect_splitted[5:]:
            try:
                nb = int(r)
                if nb < 100:
                    shirt_number = nb
                    player_info['shirt_number'] = shirt_number
                if nb >= 100:
                    licence = nb
                    player_info['licence'] = licence
                    players_list.append(player_info)
                    player_info = {"shirt_number": None, "licence": None, "name": ''}
            except ValueError as ve:
                if r not in ["N°", "Nom", "et", "prénom", "Licence"]:
                    name = r
                    player_info['name'] += name + " "
        print("len(players_list): ", len(players_list))
        if len(players_list) != 22:
            print(f"we_are_fucked, found: {len(players_list)}")
        return players_list[:11], players_list[11:]

    def parse_staff(self, staff_text):
        rect_splitted = self.rect_formatter(staff_text)
        staff_info = {"licence": None, "name": ''}
        staff_list = []
        for r in rect_splitted[5:]:
            try:
                nb = int(r)
                if nb >= 100:
                    licence = nb
                    staff_info['licence'] = licence
                    staff_list.append(staff_info)
                    staff_info = {"licence": None, "name": ''}
            except ValueError as ve:
                if r not in ["Nom", "et", "prénom", "Licence"]:
                    name = r
                    staff_info['name'] += name + " "
        print("len(staff_list): ", len(staff_list))
        return staff_list

    def parse_officiels(self, officiels_text):
        rect_splitted = self.rect_formatter(officiels_text)

        officiel_info = {"licence": None, "name": ''}
        officiels_list = []
        for r in rect_splitted[5:]:
            if r:
                if r not in ["Poste", "et", "prénom"]:
                    if r in ['ARBITRE', '1ER_ASSISTANT', '2EME_ASSISTANT', '4eme_ARBITRE', 'COMMISSAIRE']:
                        poste = r
                        officiel_info['poste'] = poste
                    else:
                        name = r
                        officiel_info['name'] += name + " "
        print("len(officiels_list): ", len(officiels_list))
        return officiels_list

    def parse_cartons(self, cartons_text, carton_type='yellow'):
        rect_splitted = self.rect_formatter(cartons_text)
        carton_info = {"licence": None, "name": '', 'team': '', 'minute': None}
        cartons_list = []
        last_numeric_label = 'minute'
        for r in rect_splitted[5:]:
            try:
                nb = int(r)
                if nb < 130:
                    shirt_number = nb
                    carton_info['minute'] = shirt_number
                    last_numeric_label = 'minute'
                    cartons_list.append(carton_info)
                    carton_info['type'] = carton_type
                    carton_info = {"licence": None, "name": '', 'team': '', 'minute': None}
                if nb >= 130:
                    licence = nb
                    carton_info['licence'] = licence
                    last_numeric_label = 'licence'
            except ValueError as ve:
                if r not in ["N°", "Nom", "et", "prénom", "Licence", 'Club', 'min', 'Motif']:
                    name = r
                    if last_numeric_label == 'licence':
                        carton_info['team'] += name
                    elif last_numeric_label == 'minute':
                        carton_info['name'] += name + " "
        print("len(cartons_list): ", len(cartons_list))
        return cartons_list


    def parse_single_match(self, pdf_text):
        parsed_match_report = {}

        # Titulaires
        titulaires_match = re.search(r"Titulaires([\s\S]*?)Remplacants", pdf_text)
        if titulaires_match:
            titulaires_text = titulaires_match.group(1)
            home_team_players, away_team_players = self.parse_titulaires(titulaires_text)

        # Remplacants
        remplacants_match = re.search(r"Remplacants([\s\S]*?)Staff", pdf_text)
        if remplacants_match:
            remplacants_text = remplacants_match.group(1)
            # self.parse_titulaires(remplacants_text)

        # Staff
        staff_match = re.search(r"Staff([\s\S]*?)REMPLACEMENTS", pdf_text)
        if staff_match:
            staff_text = staff_match.group(1)
            staff_list = self.parse_staff(staff_text)

        # REMPLACEMENTS
        replacements_match = re.search(r"REMPLACEMENTS([\s\S]*?)OFFICIELS DU MATCH", pdf_text)
        if replacements_match:
            replacements_text = replacements_match.group(1)


        # OFFICIELS DU MATCH
        officiels_match = re.search(r"OFFICIELS DU MATCH([\s\S]*?)JOUEURS AVERTIS", pdf_text)
        if officiels_match:
            officiels_text = officiels_match.group(1)
            officiels = self.parse_officiels(officiels_text)


        # JOUEURS AVERTIS
        avertis_match = re.search(r"JOUEURS AVERTIS([\s\S]*?)JOUEURS EXPULSÉS", pdf_text)
        if avertis_match:
            avertis_text = avertis_match.group(1)
            yellow_cards = self.parse_cartons(avertis_text, carton_type='yellow')
            for c in yellow_cards:
                print(c)


        # JOUEURS EXPULSÉS
        expulses_match = re.search(r"JOUEURS EXPULSÉS([\s\S]*?)JOUEURS BLESSÉS", pdf_text)
        if expulses_match:
            expulses_text = expulses_match.group(1)
            red_cards = self.parse_cartons(expulses_text, carton_type='red')
            for c in red_cards:
                print(c)


        # JOUEURS BLESSÉS
        blesses_match = re.search(
            r"JOUEURS BLESSÉS([\s\S]*?)xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            pdf_text)
        if blesses_match:
            blesses_text = blesses_match.group(1)
            injured_players = self.parse_cartons(blesses_text, carton_type='injury')
            for c in injured_players:
                print(c)
        return parsed_match_report



    def match_parser(self, match_text):
        parsed_match = []
        for match in match_text:
            if match:
                pprint(match)
                self.parse_single_match(match)
                print("-----------------------------------------------------------------------------------------------")
        return parsed_match

    def parser(self, file_path):
        doc, tables_lines = self.extract_text_from_pdf(file_path)
        return doc, tables_lines

    def parser_re(self, file_path):
        doc, tables_lines = self.extract_text_from_pdf(file_path)
        # print(doc[:200])
        matches_text = doc.split('FEUILLE DE MATCH INFORMATISÉE')
        matches_text = [mt for mt in matches_text if mt]
        print("len(matches_text): ", len(matches_text))
        # print(matches_text[0])
        print("////////////////////////////////////////////////////////////////////////////////////////////")
        self.parse_single_match(matches_text[0])
        return doc


file_path = "C:/Users/Administrator/PycharmProjects/tn-football-db/pdf_files/22-23/l1/regular_season_j6.pdf"
file_base = "C:/Users/Administrator/PycharmProjects/tn-football-db/pdf_files/22-23/l1/"
files = os.listdir(file_base)

p = Parser()

for f in files:
    file_path = file_base + f
    print("file_path: ", f)
    # text = p.extract_text_from_pdf(file_path)
    doc = p.parser_re(file_path)

    # matches_text = doc.split('FEUILLE DE MATCH INFORMATISÉE')
    # matches_text = [mt for mt in matches_text if mt]
    # titulaires = 0
    # blessures = 0
    # for l in tables_lines:
    #     if len(l) == 1:
    #         # print(l)
    #         if 'Titulaires' in l:
    #             titulaires += 1
    #         if 'JOUEURS BLESSÉS' in l:
    #             blessures += 1
    #
    # # print(titulaires)
    # # print(blessures)
    # print(f"number of matches: {len(matches_text)}, titulaires: {titulaires}, blessures: {blessures}")
    print('**************************************************************************************************')
    print('**************************************************************************************************')
