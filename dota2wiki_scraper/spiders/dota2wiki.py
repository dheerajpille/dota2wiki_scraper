# -*- coding: utf-8 -*-
import scrapy


class Dota2wikiSpider(scrapy.Spider):
    name = 'dota2wiki'

    def __init__(self, domain=None, *args, **kwargs):
        allowed_domains = ['https://www,dota2.com']
        self.start_urls = ['http://https://www,dota2.com/']

    def parse(self, response):
        pass
