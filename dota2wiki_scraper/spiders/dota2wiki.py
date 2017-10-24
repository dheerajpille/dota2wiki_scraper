# -*- coding: utf-8 -*-
import scrapy

from prettytable import PrettyTable

class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'

    def __init__(self, domain=None, *args, **kwargs):
        super(Dota2wikiSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://dota2.gamepedia.com/%s' % kwargs.get('hero')]

    def parse(self, response):

        title = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//tr'
                               '[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//th'
                               '/text()').extract()[1].strip()

        # Lore XPath
        lore = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//'
                              'tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//td/text()').extract()

        gain_table = PrettyTable(['STR Gain', 'AGI Gain', 'INT Gain'])

        gain = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//tr//td/text()').extract()

        while ' ' in gain:
            gain.remove(' ')

        gain_table.add_row([gain[0].strip(), gain[1].strip(), gain[2].strip()])

        talent_table = PrettyTable(['Talent 1', 'Level', 'Talent 2'])

        # Talent tree XPath
        # TODO: get text from spans and hyperlinks
        talent_raw = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]//td//text()').extract()

        while ' ' in talent_raw:
            talent_raw.remove(' ')

        start = 0
        end = 0
        talent_list = []

        for x in talent_raw:
            end += 1
            if x[-1:] == '\n':
                talent_list.append(''.join(talent_raw[start:end]))
                start = end

        level = 25
        index = 0

        while level >= 10:
            talent_table.add_row([talent_list[index], level, talent_list[index+1]])
            level -= 5
            index += 2

        # TODO: yield/return these
        print(talent_table)
