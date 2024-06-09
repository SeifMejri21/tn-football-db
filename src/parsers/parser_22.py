import os
import re
from datetime import date, datetime
from pprint import pprint

import fitz

from src.helpers.helpers import chunkify


class Parser(object):
    # @staticmethod
    # def extract_text_from_pdf(pdf_path):
    #     text = ""
    #     pages = []
    #     with fitz.open(pdf_path) as pdf_document:
    #         for page_number in range(pdf_document.page_count):
    #             page = pdf_document[page_number]
    #             pages.append(page)
    #             text += page.get_text()
    #     return text, pages
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        text = ""
        pages = []
        pdf_document = fitz.open(pdf_path)
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            pages.append(page)
            text += page.get_text()
        return text, pages, pdf_document

    @staticmethod
    def can_be_integer(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def rect_formatter(text):
        rect = re.sub('\n', ' ', text)
        rect_splitted = rect.split(' ')
        rect_splitted = [t for t in rect_splitted if t]
        return rect_splitted

    @staticmethod
    def parse_match_date(date_str):
        month_mapping = {
            'janv.': '01',
            'févr.': '02',
            'mars': '03',
            'avr.': '04',
            'mai': '05',
            'juin.': '06',
            'juil.': '07',
            'août': '08',
            'sept.': '09',
            'oct.': '10',
            'nov.': '11',
            'déc.': '12'
        }

        for french_month, month_num in month_mapping.items():
            if french_month in date_str:
                date_str = date_str.replace(french_month, month_num)
                break
        return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

    @staticmethod
    def licence_parser(licence_txt):
        if len(licence_txt) >= 6:
            year = int(licence_txt[:2])
            month = int(licence_txt[2:4])
            day = int(licence_txt[4:6])
            if year < 10:
                year = 2000 + int(licence_txt[:2])
            else:
                year = 1900 + int(licence_txt[:2])
            try:
                bd = date(year=year, month=month, day=day)
                return bd
            except Exception as e:
                pass
                # print(licence_txt, e)

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
                if r not in ["N°", "Nom", "et", "prénom", "Licence", 'Club', 'Min', 'min', 'Motif', 'Carton jaune ']:
                    name = r
                    if last_numeric_label == 'licence':
                        carton_info['team'] += name
                    elif last_numeric_label == 'minute':
                        carton_info['name'] += name + " "
        # print("len(cartons_list): ", len(cartons_list))
        return cartons_list

    @staticmethod
    def remove_empty_edges(lst):
        if lst and lst[0] == '':
            lst = lst[1:]
        if lst and lst[-1] == '':
            lst = lst[:-1]
        return lst

    def remove_empty_edges_smartly(self, lst):
        if lst and lst[0] == '':
            lst = lst[1:]
        if lst and lst[-1] == '' and not self.can_be_integer(lst[-2]):
            lst = lst[:-1]
        return lst

    @staticmethod
    def split_mixed_elements(lst):
        result = []
        for element in lst:
            if re.search(r'\d', element) and re.search(r'[a-zA-Z]', element):
                match = re.search(r'[a-zA-Z]', element)
                if match:
                    pos = match.start()
                    numeric_part = element[:pos].strip()
                    character_part = element[pos:].strip()
                    result.append(numeric_part)
                    result.append(character_part)
            else:
                result.append(element)
        return result

    @staticmethod
    def is_alpha_space(s):
        # return bool(re.match(r'^[A-Za-z\s]+$', s))
        return not bool(re.search(r'\d', s))

    @staticmethod
    def is_alpha_space_mine(s):
        integers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        is_alpha = True
        for char in s:
            if char in integers:
                is_alpha = False
        return is_alpha

        return not bool(re.search(r'\d', s))

    def concatenate_consecutive_alphabetic_elements(self, lst):
        # print("lst: ",lst)
        res = []
        last_concatted = False
        for st1, st2 in zip(lst[:-1], lst[1:]):
            if last_concatted:
                last_concatted = False
            else:
                if self.is_alpha_space(st1) and self.is_alpha_space(st2):
                    # if self.is_alpha_space_mine(st1) and self.is_alpha_space_mine(st2):
                    concatenated_element = st1 + ' ' + st2
                    res.append(concatenated_element)
                    last_concatted = True
                else:
                    res.append(st1)
                    last_concatted = False
        if not last_concatted:
            res.append(lst[-1])
        return res

    @staticmethod
    def concatenate_long_names(lst):
        res = []
        last_concatted = False
        for st1, st2 in zip(lst[:-1], lst[1:]):
            if last_concatted:
                last_concatted = False
            else:
                if re.search('EL JOURNI MOHAMED HOUCINE', st1) and re.search('MOHAMED', st2) \
                        or re.search('ASSALE BOSSO MARC-ANDY', st1) and re.search('JUNIOR', st2) \
                        or re.search('NGUEMA OBONO JESUS', st1) and re.search('MANSOGO', st2):
                    concatenated_element = st1 + ' ' + st2
                    res.append(concatenated_element)
                    last_concatted = True
                else:
                    res.append(st1)
                    last_concatted = False
        if not last_concatted:
            res.append(lst[-1])
        return res

    @staticmethod
    def arrange_avertis(lst, keyz_list, actual_keyz_nb, other_keyz_nb):
        if len(lst) % (actual_keyz_nb) == 0:
            lst_lst = chunkify(lst, actual_keyz_nb)
        else:
            lst_lst = chunkify(lst, other_keyz_nb)
            for l in lst_lst:
                l.append('')
        try:
            return [{keyz_list[i]: l[i] for i in range(len(keyz_list))} for l in lst_lst]
        except:
            pass

    @staticmethod
    def correct_goals(names_list):
        concatenated_list = []
        buffer = ""
        for name in names_list:
            if name[0].isdigit():
                if buffer:
                    concatenated_list[-1] += " " + buffer
                    buffer = ""
                concatenated_list.append(name)
            else:
                buffer = name
        if buffer:
            concatenated_list[-1] += " " + buffer

        return concatenated_list

    def extract_complex_match_info(self, match_info_split_list):
        short_list = match_info_split_list[2:-1]
        if len(short_list) == 3:
            home_team, match_day, score, goals = short_list[0], short_list[1], short_list[2], \
                                                 {'home_team_goals': [], 'away_team_goals': []}
        else:
            score_pattern = re.compile(r'^\d+ - \d+$')  # Pattern to match scores like 'X - X'
            score_index = None
            for i, s in enumerate(short_list):
                if score_pattern.match(s):
                    score_index = i
                    break
            if score_index is None:
                raise ValueError("No score found in the list")
            home_team_goals = short_list[:score_index - 2]
            away_team_goals = short_list[score_index + 1:]
            home_team_goals = self.correct_goals(home_team_goals)
            away_team_goals = self.correct_goals(away_team_goals)
            home_team, match_day, score, goals = short_list[score_index - 2], short_list[score_index - 1], short_list[
                score_index], \
                                                 {'home_team_goals': home_team_goals,
                                                  'away_team_goals': away_team_goals}
            for g in home_team_goals:
                if not g[0].isdigit():
                    # print("short_list: ", short_list)
                    print('home_team_goals: ', home_team_goals)
            for g in away_team_goals:
                if not g[0].isdigit():
                    print('away_team_goals: ', away_team_goals)
        return home_team, match_day, score, goals

    @staticmethod
    def search_for_string_in_pages(word, pages):
        coords = []
        for page in pages:
            text_instances = page.search_for(word)
            for inst in text_instances:
                x0, y0, x1, y1 = inst
                # print(f"text bounding box coordinates: x0:{x0}, y0:{y0}, x1:{x1}, y1:{y1}")
                avg_x, avg_y = (x0 + x1) / 2, (y0 + y1) / 2
                coords.append((avg_x,avg_y))
        return coords

    def assign_team_by_position_in_page(self, parsed_list, assign_key, picked_coord,pages, diff_axis=250):
        home, away = [], []
        for el in parsed_list:
            coords = self.search_for_string_in_pages(el[assign_key], pages)
            # print(f'{el[assign_key]}: coords:', coords)
            if coords[picked_coord][0] < diff_axis:
                home.append(el)
            else:
                away.append(el)
        return home, away

    def parse_single_match(self, pdf_text, pages):
        parsed_match_report = {}

        # match info
        match_into_match = re.search(r"([\s\S]*?)TITULAIRES", pdf_text)
        match_into_text = match_into_match.group(1)
        split_text = match_into_text.split('\n')
        split_text = [s for s in split_text if s]
        # print("split_text: ",split_text[2:-1])
        # print(split_text)
        home_team, match_day, score, goals = self.extract_complex_match_info(split_text)
        parsed_match_report['home_team'] = home_team
        parsed_match_report['away_team'] = split_text[-1]
        parsed_match_report['score'] = score
        parsed_match_report['home_team_score'] = int(score.split('-')[0])
        parsed_match_report['away_team_score'] = int(score.split('-')[1])
        parsed_match_report['venue'] = split_text[0]
        parsed_match_report['date_str'] = split_text[1]
        parsed_match_report['date'] = self.parse_match_date(split_text[1])
        parsed_match_report['match_day_str'] = match_day
        parsed_match_report['match_day'] = int(match_day[8:])
        parsed_match_report['goals'] = goals
        # print(home_team, score, parsed_match_report['away_team'], parsed_match_report['date'], parsed_match_report['venue'])
        # pprint(parsed_match_report)

        # Titulaires
        titulaires_match = re.search(r"TITULAIRES([\s\S]*?)REMPLACANTS", pdf_text)
        if titulaires_match:
            titulaires_text = titulaires_match.group(1)
            titulaires_split_text = titulaires_text.split('\n')
            titulaires_split_text = self.remove_empty_edges(titulaires_split_text)
            titulaires_split_text = [el for el in titulaires_split_text if not
            el in ['Club recevant Club visiteur', 'N° Nom', 'Licence N°', 'Nom Licence', 'Nom', 'Licence', 'Nom'
                                                                                                           'Club recevant Club visiteur',
                   'N° Nom', 'Licence N°', 'Club recevant', 'Club visiteur', 'N°']]
            titulaires_split_text = self.split_mixed_elements(titulaires_split_text)
            # for t in titulaires_split_text:
            #     self.search_for_string_in_pages(t,pages)
            if titulaires_split_text:
                titulaires_split_text = self.concatenate_consecutive_alphabetic_elements(titulaires_split_text)
                titulaires_split_text = self.concatenate_consecutive_alphabetic_elements(titulaires_split_text)
                chunked_titulaires = chunkify(titulaires_split_text, 3)
                titulaires = []
                for ch in chunked_titulaires:
                    try:
                        titulaires.append({"shirt_number": int(ch[0]), "licence": ch[2], "name": ch[1],
                                           'birthday': self.licence_parser(ch[2])})
                    except Exception as e:
                        print("Exception: ", e)
                        print(ch)
                        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                home_team_starters, away_team_starters = self.assign_team_by_position_in_page(titulaires, "name", 0,pages, diff_axis=250)
                parsed_match_report['home_team_starters'] = home_team_starters
                parsed_match_report['away_team_starters'] = away_team_starters
                # print(f"away_team_starters: {len(away_team_starters)}, away_team_starters: {len(away_team_starters)}")
            else:
                parsed_match_report['home_team_starters'] = []
                parsed_match_report['away_team_starters'] = []

        # Remplaçants
        remplacants_match = re.search(r"REMPLACANTS([\s\S]*?)STAFF", pdf_text)
        if remplacants_match:
            remplacants_text = remplacants_match.group(1)
            remplacants_split_text = remplacants_text.split('\n')
            remplacants_split_text = self.remove_empty_edges(remplacants_split_text)
            remplacants_split_text = [el for el in remplacants_split_text if
                                      el not in ['Club recevant Club visiteur', 'N° Nom', 'Licence N°', 'Nom Licence',
                                                 'Nom', 'Licence', 'Nom'
                                                                   'Club recevant Club visiteur', 'N° Nom',
                                                 'Licence N°', 'Club recevant', 'Club visiteur', 'N°']]
            remplacants_split_text = self.split_mixed_elements(remplacants_split_text)
            if remplacants_split_text:
                remplacants_split_text = self.concatenate_consecutive_alphabetic_elements(remplacants_split_text)
                remplacants_split_text = self.concatenate_consecutive_alphabetic_elements(remplacants_split_text)
                chunked_remplacants = chunkify(remplacants_split_text, 3)

                remplacants = [
                    {"shirt_number": int(ch[0]), "licence": ch[2], "name": ch[1],
                     'birthday': self.licence_parser(ch[2])}
                    for ch in chunked_remplacants]

                home_team_subs, away_team_subs = self.assign_team_by_position_in_page(remplacants, "name", 0,pages, diff_axis=250)
                # print(f"home_team_subs: {len(home_team_subs)}, away_team_subs: {len(away_team_subs)}")
                parsed_match_report['home_team_subs'] = home_team_subs
                parsed_match_report['away_team_subs'] = away_team_subs
            else:
                parsed_match_report['home_team_subs'] = []
                parsed_match_report['away_team_subs'] = []

        #Staff
        staff_match = re.search(r"STAFF([\s\S]*?)REMPLACEMENTS", pdf_text)
        if staff_match:
            staff_text = staff_match.group(1)
            staff_split_text = staff_text.split('\n')
            staff_split_text = self.remove_empty_edges(staff_split_text)
            staff_split_text = [el for el in staff_split_text if
                                el not in ['Club recevant', 'Club visiteur', 'Nom', 'Licence / CIN', 'Nom', 'Licence / CIN']]
            # print(staff_split_text)
            chunked_staff = chunkify(staff_split_text, 2)
            staff = [{'name': ch[0], 'licence': ch[1]} for ch in chunked_staff]
            home_team_staff, away_team_staff = self.assign_team_by_position_in_page(staff, "name", 0, pages,
                                                                                  diff_axis=200)
            # print(f"home_team_staff: {len(home_team_staff)}, away_team_staff: {len(away_team_staff)}")
            parsed_match_report['home_team_staff'] = home_team_staff
            parsed_match_report['away_team_staff'] = away_team_staff

        # REMPLACEMENTS
        replacements_match = re.search(r"REMPLACEMENTS([\s\S]*?)OFFICIELS DU MATCH", pdf_text)
        if replacements_match:
            replacements_text = replacements_match.group(1)
            replacements_split_text = replacements_text.split('\n')
            replacements_split_text = self.remove_empty_edges(replacements_split_text)
            replacements_split_text = [el for el in replacements_split_text if
                                       el not in ['Club recevant', 'Club visiteur', 'N°', 'Entrée',
                                                  'Sortie', 'Sortie', ]]
            if replacements_split_text:
                replacements_split_text = self.concatenate_long_names(replacements_split_text)
            if replacements_split_text:
                replacements_split_text = self.concatenate_consecutive_alphabetic_elements(replacements_split_text)
                replacements_split_text = self.concatenate_consecutive_alphabetic_elements(replacements_split_text)
                chunked_replacements = chunkify(replacements_split_text, 4)
                remplacements = []
                for ch in chunked_replacements:
                    if len(ch) == 4:
                        try:
                            remplacements.append(
                                {"in_number": int(ch[0]), "in": ch[1], "out_number": int(ch[2]), 'out': ch[3]})
                        except Exception as e:
                            print('Exception: ', e)
                            print(ch)
                            print("********************************************************************************")
                    else:
                        print('len(ch): ', len(ch), ch)
                parsed_match_report['substitutions'] = remplacements
            else:
                parsed_match_report['substitutions'] = []

        # OFFICIELS DU MATCH
        officiels_match = re.search(r"OFFICIELS DU MATCH([\s\S]*?)JOUEURS AVERTIS", pdf_text)
        if officiels_match:
            officiels_text = officiels_match.group(1)
            officiels_split_text = officiels_text.split('\n')
            officiels_split_text = self.remove_empty_edges(officiels_split_text)
            officiels_split_text = [el for el in officiels_split_text if
                                    el not in ['Poste', 'Nom et prénom', 'Nom', ]]
            chunked_officiels = chunkify(officiels_split_text, 2)
            # for ch in chunked_officiels:
            #     print(ch)
            officials = [{'name': ch[1], 'role': ch[0]} for ch in chunked_officiels]
            parsed_match_report['referees'] = officials

        # JOUEURS AVERTIS
        avertis_match = re.search(r"JOUEURS AVERTIS([\s\S]*?)JOUEURS EXPULSÉS", pdf_text)
        if avertis_match:
            avertis_text = avertis_match.group(1)
            avertis_split_text = avertis_text.split('\n')
            avertis_split_text = self.remove_empty_edges(avertis_split_text)
            avertis = self.arrange_avertis(avertis_split_text[5:], ['name', 'licence', 'club', 'min', 'reason'], 5, 4)
            parsed_match_report['yellow_cards'] = avertis

        # JOUEURS EXPULSÉS
        expulses_match = re.search(r"JOUEURS EXPULSÉS([\s\S]*?)JOUEURS BLESSÉS", pdf_text)
        parsed_match_report['red_cards'] = []
        if expulses_match:
            expulses_text = expulses_match.group(1)
            # print('expulses_text', repr(expulses_text))
            if repr(expulses_text) != repr('\nNom et prénom\nN° Licence\nClub\nMin\nMotif\n'):
                expulses_split_text = expulses_text.split('\n')
                expulses_split_text = self.remove_empty_edges_smartly(expulses_split_text)
                expulses_split_text = [el for el in expulses_split_text[1:] if
                                       not el in ['Nom et prénom', 'N° Licence', 'Club', 'Min', 'Motif',
                                                  'Club Min Motif', 'Licence', 'N°', 'N° Licence Club Min Motif', ]]
                chunked_expulses = chunkify(expulses_split_text, 5)
                # print('expulses_split_text: ')
                # for ch in chunked_expulses:
                #     print(ch)
                parsed_match_report['red_cards'] = chunked_expulses

        # JOUEURS BLESSÉS
        blesses_match = re.search(
            r"JOUEURS BLESSÉS([\s\S]*?)RÉSUMÉ DU MATCH",
            pdf_text)
        if blesses_match:
            blesses_text = blesses_match.group(1)
            # print("blesses_text: ", repr(blesses_text))
            injured_players = self.parse_cartons(blesses_text, carton_type='injury')
            parsed_match_report['injuries'] = injured_players

        return parsed_match_report

    def parser_re(self, file_path):
        doc, pages, pdf_document = self.extract_text_from_pdf(file_path)
        matches_text = doc.split('FEUILLE DE MATCH INFORMATISEE')
        matches_text = [mt for mt in matches_text if mt]
        parsed_matches = [self.parse_single_match(m, pages) for m in matches_text]
        # print("len(parsed_matches): ", len(parsed_matches))
        return parsed_matches


file_path = "/match_files/21-22/l1/regular_season_j6.pdf"
file_base = "/match_files/21-22/l1/"
file_base = "/match_files/20-21/l1/"
files = os.listdir(file_base)

p = Parser()

# for f in files[1:2]:
for f in files:
    file_path = file_base + f
    # print("file_path: ", f)
    # text = p.extract_text_from_pdf(file_path)
    doc = p.parser_re(file_path)

    # keyz = ["home_team", "away_team", "score", "home_team_score", "away_team_score", "venue", "date"]
    for mtch in doc:
        # pprint(mtch)
        print(mtch['match_day'], mtch['match_day_str'])
        # print(mtch['date'], mtch['date_str'])
        # print("/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
    # for k in keyz:
    #     print(k, mtch[k])
    # print(
    #     "************************************************************************************************************************************")

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
    # print('******************************************************************************************************************************************************************************************************************************************************************************************************')
    # print('******************************************************************************************************************************************************************************************************************************************************************************************************')
    # print('******************************************************************************************************************************************************************************************************************************************************************************************************')
    # print('******************************************************************************************************************************************************************************************************************************************************************************************************')
