# -*- coding: utf-8 -*-
import scrapy

from prettytable import PrettyTable

from dota2wiki_scraper.items import Hero


class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'
    command = ''

    def __init__(self, domain=None, *args, **kwargs):
        super(Dota2wikiSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://dota2.gamepedia.com/%s' % kwargs.get('hero')]
        self.command = kwargs.get('command')

    def parse(self, response):

        # Defines hero as Hero item defined in items.py
        hero = Hero()

        #print(self.command)

        # Uses defined static parse methods to fill Hero fields
        hero['title'] = self.parse_title(response)
        #print(hero['title'])
        hero['lore'] = self.parse_lore(response)
        #print(hero['lore'])
        hero['stat_gain'] = self.parse_stat_gain(response)
        #print(hero['stat_gain'])
        hero['data'] = self.parse_data(response)
        #print(hero['data'])
        hero['misc_data'] = self.parse_misc_data(response)
        #print(hero['misc_data'])
        # hero['abilities'] = self.parse_abilities(response)
        #print(hero['abilities'])
        hero['talent_tree'] = self.parse_talent_tree(response)
        #print(hero['talent_tree'])

        try:
            print(
                {
                    # TODO: complete help command
                    'title': hero['title'],
                    'lore': hero['lore'],
                    'stat_gain' : hero['stat_gain'],
                    'data': hero['data'],
                    'misc_data': hero['misc_data'],
                    'abilities': hero['abilities'],
                    'talent_tree': hero['talent_tree'],
                    'help': 'List of scraping commands\n'
                            '   <hero> title\n'
                            '   <hero> lore\n'
                            '   <hero> stat_gain\n'
                            '   <hero> data\n'
                            '   <hero> misc_data\n'
                            '   <hero> abilities <ability>\n'
                            '   <hero> talent_tree'
                }[self.command]
            )
        except KeyError:
            print("Unknown command \'" + self.command + "\'.\n"
                  "Type \'help\' to get a list of all available commands.")

    @staticmethod
    def parse_title(response):

        # Hero title without leading and trailing spaces
        title = response.xpath('//*[@id="heroBio"]/div[1]/text()').extract()[0].strip()

        return title

    @staticmethod
    def parse_lore(response):

        # Hero lore
        lore_raw = response.xpath('//*[@id="heroBio"]/div[3]/div[1]/div[2]//text()').extract()

        lore = []
        index = 0

        # Trims trailing newline from lore passages
        while index < len(lore_raw):
            # TODO: make sure \n is replaced with a space if possible or a newline
            lore.append(lore_raw[index].rstrip())
            index += 1

        # Appends lore list together to new string
        lore = ''.join(lore)

        return lore

    @staticmethod
    def parse_stat_gain(response):

        # Scraped stat gain data, including stat base and stat gain per level
        stat_gain = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//td//div//div//' +
                                   'text()').extract()[0:6]

        # Removing unnecessary values from stat gain
        while ' ' in stat_gain:
            stat_gain.remove(' ')
        stat_gain = [x.strip('\n').replace(' ', '') for x in stat_gain]

        # Creates stat gain table to hold stat gain data
        stat_gain_table = PrettyTable(['STR Gain', 'AGI Gain', 'INT Gain'])

        # Adds all stat gain values to table
        stat_gain_table.add_row([stat_gain[0] + stat_gain[1],
                                 stat_gain[2] + stat_gain[3],
                                 stat_gain[4] + stat_gain[5]])

        # Aligns table to left
        stat_gain_table.align = "l"

        return stat_gain_table

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

        # Getting the first 15 bolded values
        bold = bold[0:15]

        # Values for data table
        data = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat' +
                              '( " ", @class, " " ), concat( " ", "evenrowsgray", " " ))]//td/text()').extract()

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

        # Gets miscellaneous data keys
        misc_key = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "oddrowsgray", " " ))]' +
                                  '//th//text()').extract()

        # Removes unnecessary data from miscellaneous keys
        while ' ' in misc_key:
            misc_key.remove(' ')
        while '\n' in misc_key:
            misc_key.remove('\n')
        for i in range(len(misc_key)):
            misc_key[i] = misc_key[i].strip(' ').strip('\n')

        # Getting the first 12 key values
        misc_key = misc_key[0:12]

        # Gets miscellaneous data values
        misc_val_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "oddrowsgray", " " ))]' +
                                      '//td//text()').extract()

        # Removes unnecessary data from miscellaneous values
        while ' ' in misc_val_raw:
            misc_val_raw.remove(' ')
        while '\n' in misc_val_raw:
            misc_val_raw.remove('\n')
        for i in range(len(misc_val_raw)):
            misc_val_raw[i] = misc_val_raw[i].strip(' ').strip('\n')

        misc_val = []
        index = 0

        # Appends values separated by '/' or '+' together
        while index < len(misc_val_raw):
            if misc_val_raw[index] == '/' or misc_val_raw[index] == '+':
                misc_val.pop()
                misc_val.append(''.join(misc_val_raw[index - 1:index + 2]))
                index += 2
            else:
                misc_val.append(misc_val_raw[index])
                index += 1

        # Creates miscellaneous data table to hold miscellaneous data
        misc_data_table = PrettyTable(['Key', 'Value'])
        index = 0

        # Adds miscellaneous data to table
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

        # TODO: fix not getting ability keys and values

        # Retrieves all bold keys from abilities
        ability_keys_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//b//text()').extract()

        # Retrieves all span values from abilities
        ability_values_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//span//text()').extract()

        # Removes whitespace values from ability_values
        while ' ' in ability_values_raw:
            ability_values_raw.remove(' ')

        ability_values = []
        index = 0

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

        # Retrieves cooldown and mana costs for each ability
        cd_mana_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//text()').extract()

        # Removes unnecessary information from cooldown and mana cost data
        for i in range(len(cd_mana_raw)):
            cd_mana_raw[i] = cd_mana_raw[i].strip().replace('\xa0', '')
        while '' in cd_mana_raw:
            cd_mana_raw.remove('')
        while 'Play' in cd_mana_raw:
            cd_mana_raw.remove('Play')

        cd_mana_clean = []
        index = 0

        # Removes brackets (AGHANIM'S/TALENT MODIFIERS) from cd/mana cost values
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

        # Marks indices of each ability for slicing
        cd_mana_indices = [item for item in range(len(cd_mana_clean)) if cd_mana_clean[item] == "Ability"]

        cd_mana_data = []

        # Gets cooldown and mana cost values for each ability, if applicable
        while cd_mana_indices:

            # Empty list for new ability's cooldown/mana cost values
            cd_mana_list = []
            index = cd_mana_indices[0]

            # Only gets cooldown and mana cost values, since those values have no key specified
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

            cd_mana_list_clean = []
            start = 0
            end = 0

            # Appends multiple values connected by '/'
            while end < len(cd_mana_list):
                if cd_mana_list[end][-1].isdigit():
                    cd_mana_list_clean.append(''.join(cd_mana_list[start:end + 1]))
                    start = end + 1
                end += 1

            # Appends cooldown and mana cost data to list
            cd_mana_data.append(cd_mana_list_clean)

            # Pops first element of indices for next loop
            cd_mana_indices.pop(0)

        # Ability, Affects, and Damage values found in ability header
        ability_header_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "display: '
                                            'inline-block; width: 32%; vertical-align: top;")]//text()').extract()

        while ' ' in ability_header_raw:
            ability_header_raw.remove(' ')

        index = 0
        ability_header_clean = []

        # Appends values separated by '/' and removes values in brackets
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

            # Table with hero's ability name
            ability_table = PrettyTable(['Ability Name', ability[i]])

            # Iterates through ability header data and appends them to table
            for j in range(int(len(ability_header_data[i]) / 2)):
                ability_table.add_row(
                    [ability_header_data[i][j * 2].strip(), ability_header_data[i][j * 2 + 1].strip()])

            # Iterates through other ability data and appends them to table
            for j in range(len(ability_keys_data[i])):
                if ability_keys_data[i][j] == "Cast Animation":
                    ability_table.add_row([ability_keys_data[i][j].strip(), ability_values[value_index].strip() + '+' +
                                           ability_values[value_index + 1].strip()])
                    value_index += 2
                else:
                    ability_table.add_row([ability_keys_data[i][j].strip(), ability_values[value_index].strip()])
                    value_index += 1

            # Adds cooldown and mana cost, if applicable
            if cd_mana_data[i]:
                ability_table.add_row(['Cooldown', cd_mana_data[i][0]])
            if len(cd_mana_data[i]) == 2:
                ability_table.add_row(['Mana Cost', cd_mana_data[i][1]])

            # Aligns table to left
            ability_table.align = "l"

            # Sets dict key to ability name and value to ability table
            ability_dict[ability[i]] = ability_table

            # Clears table rows for next table
            ability_table.clear_rows()

        print(ability_dict['Waveform'])

        return ability_dict

    @staticmethod
    def parse_talent_tree(response):

        # XPath to talent tree data
        talent_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]' +
                                    '//td//text()').extract()

        # Removes extra spaces generated in space of images/icons
        while ' ' in talent_raw:
            talent_raw.remove(' ')

        # Indices and list for talent table data
        index = 0
        talent_list = []

        # Appends items which modify a hero ability for talent_table formatting
        while index < len(talent_raw):
            if talent_raw[index][-1:] == ' ':
                if index+2 < len(talent_raw) and talent_raw[index+2][0] == ' ':
                    talent_list.append(''.join(talent_raw[index:index+3]))
                    index += 3
                else:
                    talent_list.append(''.join(talent_raw[index:index+2]))
                    index += 2
            elif index+1 < len(talent_raw) and talent_raw[index+1][0] == ' ':
                talent_list.append(''.join(talent_raw[index:index+2]))
                index += 2
            else:
                talent_list.append(talent_raw[index])
                index += 1

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

        print(talent_tree_table)

        return talent_tree_table
