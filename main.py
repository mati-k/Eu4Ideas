import json
import re
from Idea import Idea

def load_idea_file(idea_path, ideas):
    file = open(idea_path, 'r', encoding='cp1252', errors='ignore')
    lines = file.readlines()
    file.close()

    bracket_level = 0
    is_in_idea = False
    current_stack = []
    key = None

    for line in lines:
        line = line.strip().replace('=', ' ')
        has_comment = False

        words = line.split()
        for word in words:
            if has_comment:
                break

            for index, character in enumerate(word):
                if character == '#':
                    word = word[:index]
                    has_comment = True
                    break

            if word.strip() == '':
                continue

            # ignore free = yes
            if word == 'free':
                break

            if not is_in_idea:
                ideas.append(Idea(word))
                is_in_idea = True
                continue

            if word == '{':
                bracket_level += 1
                if bracket_level > 2:
                    current_stack[-1].append((key, []))
                    current_stack.append(current_stack[-1][-1][1])
                    key = None
            elif word == '}':
                bracket_level -= 1
                if bracket_level == 0:
                    is_in_idea = False
                if len(current_stack) > 0:
                    current_stack.pop()
            elif bracket_level == 1:
                if word == 'start':
                    current_stack.append(ideas[-1].start)
                elif word == 'bonus':
                    current_stack.append(ideas[-1].bonus)
                elif word == 'trigger':
                    current_stack.append(ideas[-1].trigger)
                else:
                    ideas[-1].ideas.append(word)
                    ideas[-1].modifiers.append([])
                    current_stack.append(ideas[-1].modifiers[-1])
            else:
                if key is None:
                    key = word.lower()
                else:
                    current_stack[-1].append((key, word))
                    key = None


def load_ideas(idea_files):
    ideas = []
    for file in idea_files:
        load_idea_file(file, ideas)
    return ideas


def create_new_modifier_file(ideas):
    used_modifiers = set()

    for idea in ideas:
        for modifier in idea.start:
            used_modifiers.add(modifier[0])
        for modifier in idea.bonus:
            used_modifiers.add(modifier[0])
        for modifier_list in idea.modifiers:
            for modifier in modifier_list:
                used_modifiers.add(modifier[0])

    output_json = {}
    for modifier in used_modifiers:
        # Ignore estate loyalty and influence, will be handled genericaly
        if 'loyalty_modifier' in modifier:
            continue

        if 'influence_modifier' in modifier and modifier != 'all_estate_influence_modifier':
            continue

        if 'privilege_slots' in modifier:
            continue

        output_json[modifier] = {
            "text": "",
            "multiplier": 1,
            "percent": False
        }
    with open("new_modifiers.json", "w") as file:
        json.dump(output_json, file, indent=2)


def load_localisation_file(localisation_path, localisation_keys):
    with open(localisation_path, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
        for line in lines:
            if not line.startswith(' '):
                continue
            line = line.strip()

            if line.startswith('#') or line == '':
                continue

            space_position = line.index(' ')
            key = line[:space_position]
            key = re.sub(r':\d*', '', line[:space_position])
            if key in localisation_keys:
                continue

            text = line[space_position:].strip().strip('"')
            localisation_keys[key] = text
    return localisation_keys


def load_localisations(localisation_files):
    localisation_keys = {}
    for file in localisation_files:
        load_localisation_file(file, localisation_keys)
    return localisation_keys


def create_customizable_localization(ideas):
    text = 'defined_text = {\n'\
            '\tname = national_ideas_custom_loc\n'\
            '\trandom = no\n'

    for idea in ideas:
        text += '\ttext = {\n' \
                f'\t\tlocalisation_key = national_ideas_{idea.name}\n' \
                f'{idea.get_trigger_text()}' \
                '\t}\n'

    text += '\ttext = {\n'\
            '\t\tlocalisation_key = national_ideas_blank\n'\
            '\t\ttrigger = { always = yes }\n'\
            '\t}\n'\
            '}'

    with open('out/customizable_localization/national_ideas_customizable_loc.txt', 'w', encoding='cp1252') as file:
        file.write(text)


def create_localisation_file(ideas, localisation_keys, modifier_map, text_warnings, modifier_warnings, add_icons):
    text = 'l_english:\n'\
            ' national_ideas_blank:0 ""\n'
    for idea in ideas:
        text += idea.get_localisation(localisation_keys, modifier_map, text_warnings, modifier_warnings, add_icons)

    with open('out/localisation/national_ideas_loc_l_english.yml', 'w', encoding='utf-8-sig') as file:
        file.write(text)


def load_json_file(file):
    data = {}
    with open(file, 'r') as file:
        data = json.load(file)
    return data


paths_data = load_json_file('paths.json')
ideas = load_ideas(paths_data['idea_files'])
localisation_keys = load_localisations(paths_data['localisation_files'])
modifier_map = load_json_file('modifiers.json')
create_customizable_localization(ideas)
create_localisation_file(ideas, localisation_keys, modifier_map, text_warnings=False, modifier_warnings=False, add_icons=False)
# create_new_modifier_file(ideas)
