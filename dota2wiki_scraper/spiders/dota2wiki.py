# -*- coding: utf-8 -*-
import scrapy

from prettytable import PrettyTable

from dota2wiki_scraper.items import Hero


class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'

    def __init__(self, domain=None, *args, **kwargs):
        super(Dota2wikiSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://dota2.gamepedia.com/%s' % kwargs.get('hero')]

    def parse(self, response):

        # Defines hero as Hero item defined in items.py
        hero = Hero()

        # Uses defined static parse methods to fill Hero fields
        hero['title'] = self.parse_title(response)
        hero['lore'] = self.parse_lore(response)
        hero['stat_gain'] = self.parse_stat_gain(response)
        hero['data'] = self.parse_data(response)
        hero['misc_data'] = self.parse_misc_data(response)
        hero['abilities'] = self.parse_abilities(response)
        hero['talent_tree'] = self.parse_talent_tree(response)

        print(hero['data'])

    @staticmethod
    def parse_title(response):

        # Hero title without leading and trailing spaces
        title = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//tr'
                               '[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//th'
                               '/text()').extract()[1].strip()

        return title

    @staticmethod
    def parse_lore(response):

        # Hero lore
        lore_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//tr[(((count'
                                  '(preceding-sibling::*) + 1) = 4) and parent::*)]//td | //*[contains(concat( " ", '
                                  '@class, " " ), concat( " ", "biobox", " " ))]//p/text()').extract()

        # Retrieves necessary lore data
        lore_raw = lore_raw[0]

        lore = []
        index = 0

        # Removes HTML tags from raw lore data
        while index < len(lore_raw):
            # Removes values inside and including HTML brackets
            if lore_raw[index] == '<':
                while True:
                    index += 1
                    if lore_raw[index] == '>':
                        if index+1 < len(lore_raw) and lore_raw[index+1] == ' ':
                            index += 1
                        break
            else:
                lore.append(lore_raw[index])
            index += 1

        # Appends lore list together to new string
        lore = ''.join(lore)

        return lore

    @staticmethod
    def parse_stat_gain(response):


        stat_gain = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//tr//td'
                              '//text()').extract()

        while ' ' in stat_gain:
            stat_gain.remove(' ')

        stat_gain = [x.strip('\n') for x in stat_gain]

        stat_table = PrettyTable(['STR Gain', 'AGI Gain', 'INT Gain'])

        stat_table.add_row([stat_gain[0] + stat_gain[1],
                            stat_gain[2] + stat_gain[3],
                            stat_gain[4] + stat_gain[5]])

        stat_table.align = "l"

        return stat_table

    @staticmethod
    def parse_data(response):

        # Keys for data table
        bold = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//tr//th//text()').extract()

        # Stripping unnecessary values from data key
        bold = [x.strip('\n') for x in bold]
        while '' in bold:
            bold.remove('')
        while ' ' in bold:
            bold.remove(' ')

        # Values for data table
        data = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", '
                              '@class, " " ), concat( " ", "evenrowsgray", " " ))]//td/text()').extract()

        # Various lists to store level-specific data values
        level_base = []
        level_1 = []
        level_15 = []
        level_25 = []

        index = 0

        # Sorts data to appropriate level list
        while index < len(data):
            if index % 4 == 0:
                level_base.append(data[index].strip().strip('\n').replace('‒', '-'))
            elif index % 4 == 1:
                level_1.append(data[index].strip().strip('\n').replace('‒', '-'))
            elif index % 4 == 2:
                level_15.append(data[index].strip().strip('\n').replace('‒', '-'))
            else:
                level_25.append(data[index].strip().strip('\n').replace('‒', '-'))
            index += 1

        # Creates data table and populate it with correct headers
        data_table = PrettyTable([bold[0].strip(), bold[1].strip(), bold[2].strip(), bold[3].strip(), bold[4].strip()])
        index = 0

        # Places data values into data table
        while index < len(bold)-5:
            data_table.add_row([bold[index+5], level_base[index], level_1[index], level_15[index], level_25[index]])
            index += 1

        # Aligns table to left
        data_table.align = "l"

        return data_table

    @staticmethod
    def parse_misc_data(response):

        misc_key = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 5) and parent::*)]//*'
                                  '[contains(concat( " ", @class, " " ), concat( " ", "evenrowsgray", '
                                  '" " ))]//th//text()').extract()

        while ' ' in misc_key:
            misc_key.remove(' ')

        while '\n' in misc_key:
            misc_key.remove('\n')

        for i in range(len(misc_key)):
            misc_key[i] = misc_key[i].strip(' ')
            misc_key[i] = misc_key[i].strip('\n')

        misc_val_raw = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 5) and parent::*)]//*'
                                      '[contains(concat( " ", @class, " " ), concat( " ", "evenrowsgray", " " ))]'
                                      '//td//text()').extract()

        while ' ' in misc_val_raw:
            misc_val_raw.remove(' ')

        while '\n' in misc_val_raw:
            misc_val_raw.remove('\n')

        for i in range(len(misc_val_raw)):
            misc_val_raw[i] = misc_val_raw[i].strip(' ')
            misc_val_raw[i] = misc_val_raw[i].strip('\n')

        misc_val = []
        index = 0

        while index < len(misc_val_raw):
            if misc_val_raw[index] == '/' or misc_val_raw[index] == '+':
                misc_val.pop()
                misc_val.append(''.join(misc_val_raw[index - 1:index + 2]))
                index += 2
            else:
                misc_val.append(misc_val_raw[index])
                index += 1

        misc_data_table = PrettyTable(['Key', 'Value'])
        index = 0

        while index < len(misc_key):
            misc_data_table.add_row([misc_key[index], misc_val[index]])
            index += 1

        # Aligns table to left
        misc_data_table.align = "l"

        return misc_data_table

    @staticmethod
    def parse_abilities(response):
        # Normal abilities
        ability_normal = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "font-weight: '
                                        'bold; font-size: 110%; border-bottom: 1px solid black; background-color: '
                                        '#B44335; color: white; padding: 3px 5px;")]/text()').extract()

        # Removes unnecessary values from normal abilities
        while '\n' in ability_normal:
            ability_normal.remove('\n')

        # Ultimate ability
        ability_ult = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "font-weight: '
                                     'bold; font-size: 110%; border-bottom: 1px solid black; background-color: '
                                     '#414141; color: white; padding: 3px 5px;")]/text()').extract()

        # Removes unnecessary values from ultimate ability
        while '\n' in ability_ult:
            ability_ult.remove('\n')

        # Combines normal and ultimate abilities
        ability = ability_normal + ability_ult

        # Retrieves all bold keys from abilities
        ability_keys_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//b//text()').extract()

        # Retrieves all span values from abilities
        ability_values_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//span//text()').extract()

        # Removes whitespace values from ability_values
        while ' ' in ability_values_raw:
            ability_values_raw.remove(' ')

        index = 0
        ability_values = []

        # Removes brackets (AGHANIM'S/TALENT MODIFIERS) and keys from ability values
        while index < len(ability_values_raw):
            # Removes values in brackets
            if ability_values_raw[index][-1] == '(':
                ability_values.append(ability_values_raw[index][:-1])
                index += 1
                while True:
                    if ability_values_raw[index][-1] == ')':
                        break
                    index += 1
            # Checks for numerical values or Global range (exception case)
            elif ability_values_raw[index][0].isdigit() or "Global" in ability_values_raw[index]:
                ability_values.append(ability_values_raw[index].strip())
            index += 1

        # Removes all None values in list
        ability_values = list(filter(None, ability_values))

        cd_mana_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//text()').extract()

        for i in range(len(cd_mana_raw)):
            cd_mana_raw[i] = cd_mana_raw[i].strip().replace('\xa0', '')

        while '' in cd_mana_raw:
            cd_mana_raw.remove('')

        while 'Play' in cd_mana_raw:
            cd_mana_raw.remove('Play')

        index = 0
        cd_mana_clean = []

        while index < len(cd_mana_raw):
            if cd_mana_raw[index][-1] == '(':
                if cd_mana_raw[index] != '(':
                    cd_mana_clean.append(cd_mana_raw[index].strip('('))
                while True:
                    index += 1
                    if cd_mana_raw[index][-1] == ')':
                        index += 1
                        break
            else:
                cd_mana_clean.append(cd_mana_raw[index])
                index += 1

        cd_mana_indices = [item for item in range(len(cd_mana_clean)) if cd_mana_clean[item] == "Ability"]

        cd_mana_data = []

        # CD/Mana cost values
        while cd_mana_indices:

            cd_mana_list = []
            index = cd_mana_indices[0]

            while index < len(cd_mana_clean):
                if len(cd_mana_indices) > 1:
                    if index == cd_mana_indices[1]:
                        break
                else:
                    if index == len(cd_mana_indices):
                        break

                if cd_mana_clean[index] == ':' or cd_mana_clean[index] == '+':
                    index += 2
                    continue
                elif cd_mana_clean[index][0].isdigit():
                    cd_mana_list.append(cd_mana_clean[index])
                index += 1

            start = 0
            end = 0
            cd_mana_list_clean = []

            while end < len(cd_mana_list):
                if cd_mana_list[end][-1].isdigit():
                    cd_mana_list_clean.append(''.join(cd_mana_list[start:end + 1]))
                    start = end + 1
                end += 1

            cd_mana_data.append(cd_mana_list_clean)
            cd_mana_indices.pop(0)

        # Ability, Affects, and Damage values found in ability header
        ability_header_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "display: '
                                            'inline-block; width: 32%; vertical-align: top;")]//text()').extract()

        while ' ' in ability_header_raw:
            ability_header_raw.remove(' ')

        index = 0
        ability_header_clean = []

        # Cleans ability header list
        while index < len(ability_header_raw):
            # Appends multiple type values separated by '/' together
            if ability_header_raw[index].strip() == '/':
                ability_header_clean.pop()
                ability_header_clean.append(ability_header_raw[index - 1].strip() + ' ' +
                                            ability_header_raw[index].strip() + ' ' +
                                            ability_header_raw[index + 1].strip())
                index += 2
            elif ability_header_raw[index].strip()[-1] == '/':
                ability_header_clean.append(ability_header_raw[index] + ability_header_raw[index + 1])
                index += 2
            elif ability_header_raw[index].strip()[0] == '/':
                ability_header_clean.pop()
                ability_header_clean.append(ability_header_raw[index - 1] + ability_header_raw[index])
                index += 1
            # Removes values inside brackets from list
            elif ability_header_raw[index] == '(':
                index += 1
                while True:
                    if ability_header_raw[index] == ')':
                        index += 1
                        break
                    index += 1
            if index < len(ability_header_raw):
                ability_header_clean.append(ability_header_raw[index].strip())
            index += 1

        ability_header_data = []

        # Ability header indices, used to slice list to sub-lists
        ability_indices = [item for item in range(len(ability_header_clean)) if ability_header_clean[item] == "Ability"]

        # Slices ability header list using indices provided above
        for i in range(len(ability_indices)):
            if i != len(ability_indices) - 1:
                ability_header_data.append(ability_header_clean[ability_indices[i]:ability_indices[i + 1]])
            else:
                ability_header_data.append(ability_header_clean[ability_indices[i]:])

        # Ability key indices, used to slice list to sub-lists
        ability_indices = [item for item in range(len(ability_keys_raw)) if ability_keys_raw[item] == "Ability"]

        ability_keys_data = []

        # Slices ability key list using indices provided above
        for i in range(len(ability_indices)):
            if i != len(ability_indices) - 1:
                ability_keys_data.append(ability_keys_raw[ability_indices[i]:ability_indices[i + 1]])
            else:
                ability_keys_data.append(ability_keys_raw[ability_indices[i]:])

        # Removes ability headers and modifiers from sub-lists if applicable
        for i in range(len(ability_keys_data)):
            if "Ability" in ability_keys_data[i]:
                ability_keys_data[i].remove("Ability")
            if "Affects" in ability_keys_data[i]:
                ability_keys_data[i].remove("Affects")
            if "Damage" in ability_keys_data[i]:
                if ability_keys_data[i][ability_keys_data[i].index("Damage") + 2] == "Physical" or \
                                ability_keys_data[i][ability_keys_data[i].index("Damage") + 2] == "Magical" or \
                                ability_keys_data[i][ability_keys_data[i].index("Damage") + 2] == "Pure":
                    ability_keys_data[i].remove(ability_keys_data[i][ability_keys_data[i].index("Damage") + 2])
                    ability_keys_data[i].remove(ability_keys_data[i][ability_keys_data[i].index("Damage") + 1])
                elif ability_keys_data[i][ability_keys_data[i].index("Damage") + 1] == "Physical" or \
                                ability_keys_data[i][ability_keys_data[i].index("Damage") + 1] == "Magical" or \
                                ability_keys_data[i][ability_keys_data[i].index("Damage") + 1] == "Pure":
                    ability_keys_data[i].remove(ability_keys_data[i][ability_keys_data[i].index("Damage") + 1])
                ability_keys_data[i].remove("Damage")
            if "Modifiers" in ability_keys_data[i]:
                ability_keys_data[i] = ability_keys_data[i][:ability_keys_data[i].index("Modifiers")]

        # Index iterator through ability values list
        value_index = 0

        ability_dict = {}

        # Creates each ability's table from cleaned data
        for i in range(len(ability)):

            ability_table = PrettyTable(['Ability Name', ability[i]])

            for j in range(int(len(ability_header_data[i]) / 2)):
                ability_table.add_row(
                    [ability_header_data[i][j * 2].strip(), ability_header_data[i][j * 2 + 1].strip()])

            for j in range(len(ability_keys_data[i])):
                if ability_keys_data[i][j] == "Cast Animation":
                    ability_table.add_row([ability_keys_data[i][j].strip(), ability_values[value_index].strip() + '+' +
                                           ability_values[value_index + 1].strip()])
                    value_index += 2
                else:
                    ability_table.add_row([ability_keys_data[i][j].strip(), ability_values[value_index].strip()])
                    value_index += 1

            if cd_mana_data[i]:
                ability_table.add_row(['Cooldown', cd_mana_data[i][0]])

            if len(cd_mana_data[i]) == 2:
                ability_table.add_row(['Mana Cost', cd_mana_data[i][1]])

            # Aligns ability table to left
            ability_table.align = "l"

            # Sets dict key to ability name and value to ability table
            ability_dict[ability[i]] = ability_table

            # Clears table rows for next table
            ability_table.clear_rows()

        return ability_dict

    @staticmethod
    def parse_talent_tree(response):

        # XPath to talent tree data
        talent_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]'
                                    '//td//text()').extract()

        # Removes extra spaces generated in space of images/icons
        while ' ' in talent_raw:
            talent_raw.remove(' ')

        # Indices and list for talent table data
        start = 0
        end = 0
        talent_list = []

        # Appends items which do not end with newline character for talent_table formatting
        for x in talent_raw:
            end += 1
            if x[-1:] == '\n':
                talent_list.append(''.join(talent_raw[start:end]))
                start = end

        # Creates table to store talent tree data
        talent_tree_table = PrettyTable(['Talent Left', 'Level', 'Talent Right'])

        # Level and talent_list index for talent_table
        level = 25
        index = 0

        # Adds talent_list data to talent_table
        while level >= 10:
            talent_tree_table.add_row([talent_list[index].strip(), level, talent_list[index + 1].strip()])
            level -= 5
            index += 2

        # Aligns table to left
        talent_tree_table.align = "l"

        return talent_tree_table
