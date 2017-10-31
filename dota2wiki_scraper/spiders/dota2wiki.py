# -*- coding: utf-8 -*-
import scrapy

from prettytable import PrettyTable

from dota2wiki_scraper.items import Dota2WikiScraperItem

class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'

    def __init__(self, domain=None, *args, **kwargs):
        super(Dota2wikiSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://dota2.gamepedia.com/%s' % kwargs.get('hero')]

    def parse(self, response):

        # Normal abilities
        ability_normal = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "font-weight: '
                                        'bold; font-size: 110%; border-bottom: 1px solid black; background-color: '
                                        '#B44335; color: white; padding: 3px 5px;")]/text()').extract()

        while '\n' in ability_normal:
            ability_normal.remove('\n')

        # Ultimate ability
        ability_ult = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "font-weight: '
                                     'bold; font-size: 110%; border-bottom: 1px solid black; background-color: '
                                     '#414141; color: white; padding: 3px 5px;")]/text()').extract()

        while '\n' in ability_ult:
            ability_ult.remove('\n')

        # Combines normal and ultimate abilities
        ability = ability_normal + ability_ult

        ability_keys_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//b//text()').extract()

        # TODO: used to be /text() instead of //text()
        ability_values_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//span//text()').extract()

        while ' ' in ability_values_raw:
            ability_values_raw.remove(' ')

        index = 0
        ability_values = []

        # Removes brackets (AGHANIM'S/TALENT MODIFIERS) and keys from ability values
        while index < len(ability_values_raw):
            if ability_values_raw[index][-1] == '(':
                ability_values.append(ability_values_raw[index][:-1])
                index += 1
                while True:
                    if ability_values_raw[index][-1] == ')':
                        break
                    index += 1
            elif ability_values_raw[index][0].isdigit():
                ability_values.append(ability_values_raw[index].strip())
            index += 1

        # Removes all None values in list
        ability_values = list(filter(None, ability_values))

        # Cooldown for all abilities
        cooldown_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "display:'
                                      'inline-block; margin:8px 0px 0px 50px; width:190px; vertical-align:top;")]'
                                      '/text() | '
                                      '//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "display:'
                                      'inline-block; margin:8px 0px 0px 50px; width:370px; vertical-align:top;")]'
                                      '/text()').extract()

        index = 0
        cooldown_data = []

        while index < len(cooldown_raw):
            cooldown_list = []
            while cooldown_raw[index][-1] == '/':
                cooldown_list.append(cooldown_raw[index])
                index += 1
            cooldown_list.append(cooldown_raw[index])
            cooldown_data.append(''.join(cooldown_list))
            index += 1

        mana_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div[contains(@style, "display:inline-block; margin:8px 0px 0px; width:190px; vertical-align:top;")]/text()').extract()

        for i in range(len(mana_raw)):
            mana_raw[i] = mana_raw[i].strip('\n')

        cd_mana_raw = response.xpath('//*[(@id = "mw-content-text")]//div//div//div//div//text()').extract()

        for i in range(len(cd_mana_raw)):
            cd_mana_raw[i] = "".join(cd_mana_raw[i].split())

        while '' in cd_mana_raw:
            cd_mana_raw.remove('')

        index = 0
        cd_mana_clean = []

        while index < len(cd_mana_raw):
            if cd_mana_raw[index][-1] == '(':
                while True:
                    index += 1
                    if cd_mana_raw[index][-1] == ')':
                        index += 1
                        break
            else:
                cd_mana_clean.append(cd_mana_raw[index])
                index += 1

        print(cd_mana_clean)

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
                ability_header_clean.append(ability_header_raw[index-1].strip() + ' ' +
                                            ability_header_raw[index].strip() + ' ' +
                                            ability_header_raw[index+1].strip())
                index += 2
            elif ability_header_raw[index].strip()[-1] == '/':
                ability_header_clean.append(ability_header_raw[index] + ability_header_raw[index+1])
                index += 2
            elif ability_header_raw[index].strip()[0] == '/':
                ability_header_clean.pop()
                ability_header_clean.append(ability_header_raw[index-1] + ability_header_raw[index])
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

        index = 0

        ability_header_data = []

        # Ability header indices, used to slice list to sub-lists
        ability_indices = [item for item in range(len(ability_header_clean)) if ability_header_clean[item] == "Ability"]

        # Slices ability header list using indices provided above
        for i in range(len(ability_indices)):
            if i != len(ability_indices)-1:
                ability_header_data.append(ability_header_clean[ability_indices[i]:ability_indices[i+1]])
            else:
                ability_header_data.append(ability_header_clean[ability_indices[i]:])

        # Ability key indices, used to slice list to sub-lists
        ability_indices = [item for item in range(len(ability_keys_raw)) if ability_keys_raw[item] == "Ability"]

        ability_keys_data = []

        # Slices ability key list using indices provided above
        for i in range(len(ability_indices)):
            if i != len(ability_indices)-1:
                ability_keys_data.append(ability_keys_raw[ability_indices[i]:ability_indices[i+1]])
            else:
                ability_keys_data.append(ability_keys_raw[ability_indices[i]:])

        # Removes ability headers and modifiers from sub-lists if applicable
        for i in range(len(ability_keys_data)):
            if "Ability" in ability_keys_data[i]:
                ability_keys_data[i].remove("Ability")
            if "Affects" in ability_keys_data[i]:
                ability_keys_data[i].remove("Affects")
            if "Damage" in ability_keys_data[i]:
                ability_keys_data[i].remove(ability_keys_data[i][ability_keys_data[i].index("Damage")+1])
                ability_keys_data[i].remove("Damage")
            if "Modifiers" in ability_keys_data[i]:
                ability_keys_data[i] = ability_keys_data[i][:ability_keys_data[i].index("Modifiers")]

        # Index iterator through ability values list
        value_index = 0

        for i in range(len(ability)):

            ability_table = PrettyTable(['Ability Name', ability[i]])

            for j in range(int(len(ability_header_data[i])/2)):
                ability_table.add_row([ability_header_data[i][j*2].strip(), ability_header_data[i][j*2+1].strip()])

            for j in range(len(ability_keys_data[i])):
                if ability_keys_data[i][j] == "Cast Animation":
                    ability_table.add_row([ability_keys_data[i][j].strip(), ability_values[value_index].strip() + '+' +
                                           ability_values[value_index+1].strip()])
                    value_index += 2
                else:
                    ability_table.add_row([ability_keys_data[i][j].strip(), ability_values[value_index].strip()])
                    value_index += 1

            # Check for cooldown_length with passives using passive boolean
            ability_table.add_row(['Cooldown', cooldown_data[i]])

            ability_table.clear_rows()

        # TODO: add cooldown/mana cost where applicable

    def parse_title(self, response):

        # Hero title without leading and trailing spaces
        title = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//tr'
                               '[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//th'
                               '/text()').extract()[1].strip()

        yield title

    def parse_lore(self, response):

        # Hero lore XPath
        lore = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//'
                              'tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//td/text()').extract()

        yield lore

    def parse_stat_gain(self, response):

        stat_table = PrettyTable(['STR Gain', 'AGI Gain', 'INT Gain'])

        stat = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//tr//td'
                              '//text()').extract()

        while ' ' in stat:
            stat.remove(' ')

        stat_table.add_row([stat[0] + stat[1],
                            stat[2] + stat[3],
                            stat[4] + stat[5]])

        yield stat_table

    def parse_data(self, response):
        header = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "evenrowsgray", " " ))]'
                                '//th[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//text()').extract()

        header = [x.strip() for x in header]

        while '' in header:
            header.remove('')

        data_table = PrettyTable([header[0], 'Base', '1', '15', '25'])

        data = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "evenrowsgray", " " ))]//td'
                              '//text()').extract()

        index = 0

        level_base = []
        level_1 = []
        level_15 = []
        level_25 = []

        while index < len(data):
            if index % 4 == 0:
                level_base.append(data[index])
            elif index % 4 == 1:
                level_1.append(data[index])
            elif index % 4 == 2:
                level_15.append(data[index])
            else:
                level_25.append(data[index])
            index += 1

        index = 0

        while index < len(header) - 1:
            data_table.add_row([header[index + 1], level_base[index], level_1[index], level_15[index], level_25[index]])
            index += 1

        yield(data_table)

    def parse_misc_data(self, response):

        misc_table = PrettyTable(['Key', 'Value'])

        misc_key = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "oddrowsgray", " " ))]//th'
                                  '//text()').extract()

        while ' ' in misc_key:
            misc_key.remove(' ')

        while '\n' in misc_key:
            misc_key.remove('\n')

        misc_val_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "oddrowsgray", " " ))]//td'
                                      '//text()').extract()

        while ' ' in misc_val_raw:
            misc_val_raw.remove(' ')

        while '\n' in misc_val_raw:
            misc_val_raw.remove('\n')

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

        index = 0

        while index < 10:
            misc_table.add_row([misc_key[index], misc_val[index]])
            index += 1

        print(misc_table)

    def parse_talent(self, response):

        talent_table = PrettyTable(['Talent Left', 'Level', 'Talent Right'])

        # Talent tree XPath
        talent_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]'
                                    '//td//text()').extract()

        # Removes extra spaces generated in space of images/icons
        while ' ' in talent_raw:
            talent_raw.remove(' ')

        # Indices and list for talent_table data
        start = 0
        end = 0
        talent_list = []

        # Appends items which do not end with newline character for talent_table formatting
        for x in talent_raw:
            end += 1
            if x[-1:] == '\n':
                talent_list.append(''.join(talent_raw[start:end]))
                start = end

        # Level and talent_list index for talent_table
        level = 25
        index = 0

        # Adds talent_list data to talent_table
        while level >= 10:
            talent_table.add_row([talent_list[index], level, talent_list[index + 1]])
            level -= 5
            index += 2

        yield(talent_table)
