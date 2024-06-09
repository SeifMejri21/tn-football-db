import re
from datetime import date, datetime

import fitz

from src.helpers.helpers import chunkify


class Parser(object):
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        text = ""
        pdf_document = fitz.open(pdf_path)
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text += page.get_text()
        return text, pdf_document

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

    def concatenate_consecutive_alphabetic_elements(self, lst):
        res = []
        last_concatted = False
        for st1, st2 in zip(lst[:-1], lst[1:]):
            if last_concatted:
                last_concatted = False
            else:
                if self.is_alpha_space(st1) and self.is_alpha_space(st2):
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
    def search_for_string_in_pages(word, pages):
        coords = []
        for page in pages:
            text_instances = page.search_for(word)
            for inst in text_instances:
                x0, y0, x1, y1 = inst
                avg_x, avg_y = (x0 + x1) / 2, (y0 + y1) / 2
                coords.append((avg_x, avg_y))
        return coords

    def assign_team_by_position_in_page(self, parsed_list, assign_key, picked_coord, pages, diff_axis=250):
        home, away = [], []
        for el in parsed_list:
            coords = self.search_for_string_in_pages(' ' + el[assign_key], pages)
            if coords[picked_coord][0] < diff_axis:
                home.append(el)
            else:
                away.append(el)
        return home, away

    def parse_single_match(self, pdf_text, pdf_document):
        parsed_match_report = {}
        # match info
        match_into_match = re.search(r"([\s\S]*?)Titulaires", pdf_text)
        match_into_text = match_into_match.group(1)
        split_text = match_into_text.split('\n')
        split_text = [s for s in split_text if s]
        parsed_match_report['home_team'] = split_text[0]
        parsed_match_report['away_team'] = split_text[4]
        parsed_match_report['score'] = split_text[3]
        parsed_match_report['home_team_score'] = int(split_text[3].split('-')[0])
        parsed_match_report['away_team_score'] = int(split_text[3].split('-')[1])
        parsed_match_report['venue'] = split_text[1]
        parsed_match_report['date_str'] = split_text[2]
        parsed_match_report['date'] = datetime.strptime(split_text[2], "%d/%m/%Y %H:%M")
        # print(parsed_match_report['home_team'], parsed_match_report['score'], parsed_match_report['away_team'],
        #       parsed_match_report['venue'], parsed_match_report['date'])

        # Titulaires
        titulaires_match = re.search(r"Titulaires([\s\S]*?)Remplacants", pdf_text)
        if titulaires_match:
            titulaires_text = titulaires_match.group(1)
            titulaires_split_text = titulaires_text.split('\n')
            titulaires_split_text = self.remove_empty_edges(titulaires_split_text)
            titulaires_split_text = [el for el in titulaires_split_text if
                                     el not in ['N° Nom et prénom', 'Licence', 'N°', 'Nom et prénom', ]]
            titulaires_split_text = self.split_mixed_elements(titulaires_split_text)
            titulaires_split_text = self.concatenate_consecutive_alphabetic_elements(titulaires_split_text)
            chunked_titulaires = chunkify(titulaires_split_text, 3)
            titulaires = [
                {"shirt_number": int(ch[0]), "licence_number": ch[2], "player_name": ch[1], 'date_of_birth': self.licence_parser(ch[2])}
                for ch in chunked_titulaires]
            home_team_starters, away_team_starters = self.assign_team_by_position_in_page(titulaires, "player_name", 0,
                                                                                          pdf_document,
                                                                                          diff_axis=250)
            parsed_match_report['home_team_starters'] = home_team_starters
            parsed_match_report['away_team_starters'] = away_team_starters

        # Remplaçants
        remplacants_match = re.search(r"Remplacants([\s\S]*?)Staff", pdf_text)
        if remplacants_match:
            remplacants_text = remplacants_match.group(1)
            remplacants_split_text = remplacants_text.split('\n')
            remplacants_split_text = self.remove_empty_edges(remplacants_split_text)
            remplacants_split_text = [el for el in remplacants_split_text if
                                      el not in ['N° Nom et prénom', 'Licence', 'N°', 'Nom et prénom', ]]
            remplacants_split_text = self.split_mixed_elements(remplacants_split_text)
            remplacants_split_text = self.concatenate_consecutive_alphabetic_elements(remplacants_split_text)
            chunked_remplacants = chunkify(remplacants_split_text, 3)
            remplacants = [
                {"shirt_number": int(ch[0]), "licence_number": ch[2], "player_name": ch[1], 'date_of_birth': self.licence_parser(ch[2])}
                for ch in chunked_remplacants]
            home_team_subs, away_team_subs = self.assign_team_by_position_in_page(remplacants, "player_name", 0, pdf_document,
                                                                                  diff_axis=250)
            # print(f"home_team_subs: {len(home_team_subs)}, away_team_subs: {len(away_team_subs)}")
            parsed_match_report['home_team_subs'] = home_team_subs
            parsed_match_report['away_team_subs'] = away_team_subs

        # #Staff
        # staff_match = re.search(r"Staff([\s\S]*?)REMPLACEMENTS", pdf_text)
        # if staff_match:
        #     staff_text = staff_match.group(1)
        #     staff_split_text = staff_text.split('\n')
        #     staff_split_text = self.remove_empty_edges(staff_split_text)
        #     staff_split_text = [el for el in staff_split_text if
        #                         el not in ['N° Nom et prénom', 'Licence', 'N°', 'Nom et prénom', ]]
        #     staff_split_text = self.split_mixed_elements(staff_split_text)
        #     staff_split_text = self.concatenate_consecutive_alphabetic_elements(staff_split_text)
        #     chunked_staff = chunkify(staff_split_text, 2)
        #     for s in chunked_staff:
        #         print(s)
        #     staff = [{"licence": ch[1], "name": ch[0]} for ch in chunked_staff]
        #     home_team_staff, away_team_staff = self.assign_team_by_position_in_page(staff, "name", 0, pdf_document,
        #                                                                           diff_axis=200)
        #     parsed_match_report['home_team_staff'] = home_team_staff
        #     parsed_match_report['away_team_staff'] = away_team_staff

        # REMPLACEMENTS
        replacements_match = re.search(r"REMPLACEMENTS([\s\S]*?)OFFICIELS DU MATCH", pdf_text)
        if replacements_match:
            replacements_text = replacements_match.group(1)
            replacements_split_text = replacements_text.split('\n')
            replacements_split_text = self.remove_empty_edges(replacements_split_text)
            replacements_split_text = [el for el in replacements_split_text if
                                       el not in ['Equipe', 'Min', 'Joueur Entrant', 'Joueur Sortant',
                                                  'Equipe Min Joueur Entrant', 'Min Joueur Entrant']]
            if replacements_split_text:
                replacements_split_text = self.concatenate_long_names(replacements_split_text)
            chunked_replacements = chunkify(replacements_split_text, 4)
            remplacements = []
            for ch in chunked_replacements:
                if len(ch) == 4:
                    remplacements.append(
                        {"team": ch[0], "minute": int(re.sub('"', '', ch[1])), "player_in": ch[2].split('-')[-1][1:],
                         'player_out': ch[3].split('-')[-1][1:]})
                elif len(ch) == 3:
                    remplacements.append(
                        {"team": ch[0], "minute": int(re.sub('"', '', ch[1])), "player_in": ch[2].split('-')[-2][1:],
                         'player_out': ch[2].split('-')[-1][1:]})
                else:
                    print('len(ch): ', len(ch), ch)
            parsed_match_report['substitutions'] = remplacements

        # OFFICIELS DU MATCH
        officiels_match = re.search(r"OFFICIELS DU MATCH([\s\S]*?)JOUEURS AVERTIS", pdf_text)
        if officiels_match:
            officiels_text = officiels_match.group(1)
            officiels_split_text = officiels_text.split('\n')
            officiels_split_text = self.remove_empty_edges(officiels_split_text)
            officiels_split_text = [el for el in officiels_split_text if
                                    el not in ['Poste', 'Nom et prénom']]
            chunked_officiels = chunkify(officiels_split_text, 2)
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
            if repr(expulses_text) != repr('\nNom et prénom\nN° Licence\nClub\nMin\nMotif\n'):
                expulses_split_text = expulses_text.split('\n')
                expulses_split_text = self.remove_empty_edges_smartly(expulses_split_text)
                expulses_split_text = [el for el in expulses_split_text[1:] if
                                       not el in ['Nom et prénom', 'N° Licence', 'Club', 'Min', 'Motif',
                                                  'Club Min Motif', 'Licence', 'N°', 'N° Licence Club Min Motif', ]]
                chunked_expulses = chunkify(expulses_split_text, 5)
                parsed_match_report['red_cards'] = chunked_expulses

        # JOUEURS BLESSÉS
        blesses_match = re.search(
            r"JOUEURS BLESSÉS([\s\S]*?)",
            pdf_text)
        if blesses_match:
            blesses_text = blesses_match.group(1)
            injured_players = self.parse_cartons(blesses_text, carton_type='injury')
            parsed_match_report['injuries'] = injured_players
        return parsed_match_report

    def parser_re(self, file_path):
        doc, pdf_document = self.extract_text_from_pdf(file_path)
        matches_text = doc.split('FEUILLE DE MATCH INFORMATISÉE')
        matches_text = [mt for mt in matches_text if mt]
        parsed_matches = [self.parse_single_match(m, pdf_document) for m in matches_text]
        return parsed_matches

# file_path = "C:/Users/Administrator/PycharmProjects/tn-football-db/match_files/22-23/l1/regular_season_j6.pdf"
# file_base = "C:/Users/Administrator/PycharmProjects/tn-football-db/match_files/22-23/l1/"
# files = os.listdir(file_base)
#
# p = Parser()
#
# # for f in files[1:2]:
# for f in files[:1]:
# # for f in files:
#     file_path = file_base + f
#     print("file_path: ", f)
#     # text = p.extract_text_from_pdf(file_path)
#     doc = p.parser_re(file_path)
#     for match in doc:
#         pprint(match)
#         print("////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
#         print("////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
#         print("////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
#     # pprint(doc[0])
#     # keyz = ["home_team", "away_team", "score", "home_team_score", "away_team_score", "venue", "date"]
#     # for mtch in doc:
#     #     pprint(doc)
#     # for k in keyz:
#     #     print(k, mtch[k])
#     # print(
#     #     "************************************************************************************************************************************")
#
#     # matches_text = doc.split('FEUILLE DE MATCH INFORMATISÉE')
#     # matches_text = [mt for mt in matches_text if mt]
#     # titulaires = 0
#     # blessures = 0
#     # for l in tables_lines:
#     #     if len(l) == 1:
#     #         # print(l)
#     #         if 'Titulaires' in l:
#     #             titulaires += 1
#     #         if 'JOUEURS BLESSÉS' in l:
#     #             blessures += 1
#     #
#     # # print(titulaires)
#     # # print(blessures)
#     # print(f"number of matches: {len(matches_text)}, titulaires: {titulaires}, blessures: {blessures}")
#     # print('**************************************************************************************************')
#     # print('**************************************************************************************************')
