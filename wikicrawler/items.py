# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# used for reporting scraped data
class WikicrawlerItem(scrapy.Item):
    path_root = scrapy.Field()
    depth = scrapy.Field()
    status = scrapy.Field()
