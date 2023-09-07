class Idea:
    def __init__(self, name):
        self.name = name
        self.trigger = []
        self.start = []
        self.bonus = []
        self.ideas = []
        self.modifiers = []

    def get_trigger_text(self):
        trigger_text = '\t\ttrigger = {\n'
        trigger_text = self.__get_trigger_text_recursive(3, self.trigger, trigger_text)
        trigger_text += '\t\t}\n'

        return trigger_text

    def __get_trigger_text_recursive(self, tab_offset, array, trigger_text):
        tab = '\t' * tab_offset
        for entry in array:
            if isinstance(entry[1], list):
                trigger_text += f'{tab}{entry[0]} = {{\n'
                trigger_text = self.__get_trigger_text_recursive(tab_offset+1, entry[1], trigger_text)
                trigger_text += f'{tab}}}\n'
            else:
                trigger_text += f'{tab}{entry[0]} = {entry[1]}\n'
        return trigger_text

    def try_get_loc(self, key, localization_keys):
        if key in localization_keys:
            return localization_keys[key]
        else:
            print("Localization key not found: ", key)
            return

    def format_modifier(self, modifier, modifier_map, text_warnings, modifier_warnings, add_icons):
        modifier_text = ''
        modifier_entry = {
            "text": '',
            "multiplier": 1,
            "percent": False
        }

        if modifier[0] in modifier_map:
            modifier_entry = modifier_map[modifier[0]]
        elif 'influence_modifier' in modifier[0] or 'loyalty_modifier' in modifier[0]:
            modifier_entry['multiplier'] = 100
            modifier_entry['percent'] = True
        elif 'possible_privileges' in modifier[0]:
            pass
        elif modifier_warnings:
            print("Modifier not found in json file: ", modifier[0])

        if modifier[1].lower() != 'yes':
            value = float(modifier[1])
            modifier_text += '§G'
            if value > 0:
                modifier_text += '+'

            modifier_text += f'{(value * modifier_entry["multiplier"]):g}'
            if modifier_entry["percent"]:
                modifier_text += '%'
            modifier_text += '§! '

        if modifier_entry['text'] != '':
            modifier_text += modifier_entry["text"]
        elif 'loyalty_modifier' in modifier[0]:
            estate_name = modifier[0].replace('_loyalty_modifier', '').capitalize()
            modifier_text += f'[Root.Get{estate_name}Name] Loyalty Equilibrium'
        elif 'influence_modifier' in modifier[0] and modifier[0] != 'all_estate_influence_modifier':
            estate_name = modifier[0].replace('_influence_modifier', '').capitalize()
            modifier_text += f'[Root.Get{estate_name}Name] Influence'
        elif 'privilege_slots' in modifier[0]:
            estate_name = modifier[0].replace('_privilege_slots', '').capitalize()
            modifier_text += f'[Root.Get{estate_name}Name] Max Privileges'
        else:
            modifier_text += modifier[0]
            if text_warnings:
                print(f"Modifier {modifier[1]} has no text set")

        return f'{modifier_text}\\n'

    def get_localisation(self, localization_keys, modifier_map):
        ideas_text = "\\nNew National Ideas\\n\\n"
        ideas_text += "Traditions:\\n"
        for modifier in self.start:
            ideas_text += self.format_modifier(modifier, modifier_map)
        ideas_text += '\\n'

        for modifier_index in range(len(self.modifiers)):
            ideas_text += f'{self.try_get_loc(self.ideas[modifier_index], localization_keys)}\\n'
            for modifier in self.modifiers[modifier_index]:
                ideas_text += self.format_modifier(modifier, modifier_map)

        ideas_text += '\\n'
        ideas_text += "Ambition:\\n"
        for modifier in self.bonus:
            ideas_text += self.format_modifier(modifier, modifier_map)

        return f' national_ideas_{self.name}:0 "{ideas_text}"\n'
