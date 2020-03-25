from datetime import datetime
from inkedNewsCrawler.custom_crawler.naver_news_crawler.configs import TIME_FORMAT


class NaverNewsContentModel:
    def __init__(self, **kwargs):
        self.article_id = None
        self.article_url: str = None
        self.redirect_url: str = None
        self.origin_url: str = None
        self.title: str = None
        self.body_html: str = None
        self.publish_time: datetime = None
        self.provider: str = None
        self.meta: NaverNewsMetaModel = NaverNewsMetaModel()

        if kwargs is not None: # dict base serialization
            self.article_id = kwargs['article_id']
            self.article_url = kwargs['article_url']
            self.redirect_url = kwargs['article_id']
            self.origin_url = kwargs['origin_url']
            self.title = kwargs['title']
            self.body_html = kwargs['body_html']
            self.publish_time = datetime.strptime(kwargs['time'], TIME_FORMAT)
            self.provider = kwargs['provider']

    def serialize(self, debug=False):
        if debug: # shorter serialization for debug logging purpose
            item = {
                "time": self.publish_time.isoformat(),
                "title": self.title,
                "origin_url": self.origin_url,
                "content": self.body_html[0:30],
                "provider": self.provider,
                "meta": self.meta.serialize()
            }
        else:
            item = {
                "article_id": self.article_id,
                "time": self.publish_time.isoformat(),
                "title": self.title,
                "article_url": self.article_url,
                "origin_url": self.origin_url,
                "content": self.body_html,
                "provider": self.provider,
                "meta": self.meta.serialize()
            }
        return item

    def __str__(self):
        return str(self.serialize(debug=True))


class NaverNewsMetaModel:
    def __init__(self, **kwargs):
        self.article_id = None
        self.source = "NAVER" # this will not change

        if kwargs is not None: # dict base serialization
            self.provider = kwargs['provider']
            self.article_id = kwargs['article_id']

    def serialize(self, debug=False):
        item = {
            "article_id": self.article_id,
            "provider": self.provider,
            "source": self.source,
        }
        return item