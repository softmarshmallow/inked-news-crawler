from typing import List

from inkedNewsCrawler.custom_crawler.naver_news_crawler.models import NaverNewsContentModel
from inkedNewsCrawler.services.api_controller import BASE_SERVER_URL
import requests


request_url = BASE_SERVER_URL + "api/news"


def post_crawled_news(news_content_data: NaverNewsContentModel):
    json_serializable = news_content_data.serialize()
    r = requests.post(request_url, json=json_serializable)
    if r.status_code == 200:
        print("CREATED", r.text)
    else:
        print("FAILED", r.status_code, news_content_data)




if __name__ == "__main__":
    post_crawled_news({
        "article_id": 0000,
        "article_url": "",
        "redirect_url": "",
        "origin_url": "origin_url",
        "title": "Title",
        "body_html": "empty",
        "time": "2100-12-25 12:12:12",
        "provider": "inked-developer-test-channel"
    })
