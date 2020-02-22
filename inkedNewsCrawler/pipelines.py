# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy import log

from scrapy.conf import settings
from scrapy.exceptions import DropItem


class InkednewscrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

#
# class MongoDBPipeline(object):
#
#     def __init__(self):
#         connection = pymongo.MongoClient(
#             settings['MONGODB_SERVER'],
#             settings['MONGODB_PORT']
#         )
#         db = connection[settings['MONGODB_DB']]
#         self.collection = db[settings['MONGODB_COLLECTION']]
#
#     def process_item(self, item, spider):
#         valid = True
#         for data in item:
#             if not data:
#                 valid = False
#                 raise DropItem("Missing {0}!".format(data))
#         if valid:
#             self.collection.insert(dict(item))
#             log.msg("news added to MongoDB database!",
#                     level=log.DEBUG, spider=spider)
#         return item
