import pymongo
from inkedNewsCrawler.settings import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION


class ContentCrawlChecker:
    def __init__(self):
        connection = pymongo.MongoClient(MONGODB_URI)
        db = connection[MONGODB_DATABASE]
        self.collection = db[MONGODB_COLLECTION]

    def check_article_crawled(self, article_id):
        return self.collection.find_one({"article_id": article_id}) is not None
