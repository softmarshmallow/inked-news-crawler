from pymongo import MongoClient

from inkedNewsCrawler.custom_crawler.naver_news_crawler.models import NaverNewsContentModel

client = MongoClient('localhost', 27017)
db = client['inked-content-db']
collection = db.raw


def insert(news: NaverNewsContentModel):
    if not check_conflict(news):
        collection.insert_one(news.serialize())


def check_conflict(news: NaverNewsContentModel) -> bool:
    return collection.find({'article_url': news.article_url}).count() > 0


if __name__ == "__main__":
    pass