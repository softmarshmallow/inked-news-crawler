from datetime import datetime

from inkedNewsCrawler.custom_crawler.naver_news_crawler.configs import TIME_FORMAT


class NaverNewsContentModel:
    def __init__(self):
        self.article_id = None
        self.article_url: str = None
        self.redirect_url: str = None
        self.origin_url: str = None
        self.title: str = None
        self.body_html: str = None
        self.publish_time: datetime = None
        self.provider: str = None

    def serialize(self):
        item = {
            "article_id": self.article_id,
            "article_url": self.article_url,
            "redirect_url": self.redirect_url,
            "origin_url": self.origin_url,
            "title": self.title,
            "body_html": self.body_html,
            "time": self.publish_time.strftime(TIME_FORMAT),
            "provider": self.provider
        }
        return item

    def __str__(self):
        return str(self.serialize())

