# -*- coding: utf-8 -*-
import scrapy

from prettytable import PrettyTable

class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'

    def __init__(self, domain=None, *args, **kwargs):
        super(Dota2wikiSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://dota2.gamepedia.com/%s' % kwargs.get('hero')]

    def parse(self, response):

        # Lore XPath
        lore = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//'
                              'tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//td/text()').extract()

        gain_table = PrettyTable(['STR Gain', 'AGI Gain', 'INT Gain'])

        gain = response.xpath('//tr[(((count(preceding-sibling::*) + 1) = 3) and parent::*)]//tr//td/text()').extract()

        while ' ' in gain:
            gain.remove(' ')

        gain_table.add_row([gain[0], gain[1], gain[2]])

        talent_table = PrettyTable(['Talent 1', 'Level', 'Talent 2'])

        # Talent tree XPath
        # TODO: get text from spans and hyperlinks
        talent = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]'
                                '//td/text()').extract()

        while "\n" in talent:
            talent.remove("\n")

        level = 25
        index = 0

        while level >= 10:
            talent_table.add_row([talent[index], level, talent[index+1]])
            level -= 5
            index += 2

        # TODO: yield/return these
        print(gain_table)
