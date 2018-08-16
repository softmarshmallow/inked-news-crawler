# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InkednewscrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NaverNewsContentItem(scrapy.Item):
    article_id = scrapy.Field()
    article_url = scrapy.Field()
    title = scrapy.Field()
    body_html = scrapy.Field()
    body_text = scrapy.Field()
    time = scrapy.Field()
    provider = scrapy.Field()
