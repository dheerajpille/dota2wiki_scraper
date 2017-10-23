# -*- coding: utf-8 -*-
import scrapy


class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'

    def __init__(self, domain=None, *args, **kwargs):
        super(Dota2wikiSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://dota2.gamepedia.com/%s' % kwargs.get('hero')]

    def parse(self, response):
        lore = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "biobox", " " ))]//tr[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]//td').extract()

        # TODO: yield/return this later
        print(lore)
