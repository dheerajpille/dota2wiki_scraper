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

        table = PrettyTable(['Talent 1', 'Level', 'Talent 2'])

        # Talent tree XPath
        # TODO: get text from spans and hyperlinks
        talent = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]'
                                '//td/text()').extract()

        while "\n" in talent:
            talent.remove("\n")

        level = 25

        while level >= 10:
            table.add_row([talent[0], level, talent[1]])
            level -= 5

        # TODO: yield/return these
        print(lore)
        print(talent)
        print(table)
