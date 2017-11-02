# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Dota2WikiScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    lore = scrapy.Field()
    stat_gain = scrapy.Field()
    data = scrapy.Field()
    misc_data = scrapy.Field()
    abilities = scrapy.Field()
    talent_tree = scrapy.Field()
    pass


class Hero(scrapy.Item):
    title = scrapy.Field()
    lore = scrapy.Field()
    stat_gain = scrapy.Field()
    data = scrapy.Field()
    misc_data = scrapy.Field()
    abilities = scrapy.Field()
    talent_tree = scrapy.Field()
