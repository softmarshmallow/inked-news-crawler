from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import IOManager
from datetime import  datetime

from inkedNewsCrawler.services.vps_news_service import post_crawled_news_batch, post_crawled_news

iom = IOManager()

if __name__ == "__main__":
    content = iom.read_raw_contents_from_file(date=datetime(2017, 1, 1))
    for r in content:
        res = post_crawled_news(r, already_serialized=True)
        print(res)