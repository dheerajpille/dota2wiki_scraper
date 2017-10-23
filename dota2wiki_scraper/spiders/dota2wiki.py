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

        # Talent tree XPath
        talent = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "wikitable", " " ))]'
                                '//td/text()').extract()

        while "\n" in talent:
            talent.remove("\n")

        # TODO: yield/return these
        print(talent)
