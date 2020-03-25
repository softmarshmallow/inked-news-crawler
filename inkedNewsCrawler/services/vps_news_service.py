from typing import List
import warnings
from inkedNewsCrawler.custom_crawler.naver_news_crawler.models import NaverNewsContentModel
from inkedNewsCrawler.services.api_controller import BASE_SERVER_URL, API_KEY
import requests


request_url = BASE_SERVER_URL + "api/news/"
request_url_batch = BASE_SERVER_URL + "api/news/batch"
headers = {"Authorization": f"Api-Key {API_KEY}"}


def post_crawled_news_batch(data):
    try:
        r = requests.post(request_url_batch, json=data, headers=headers)
        if 200 <= r.status_code < 300:
            return True, '201'
        else:
            warnings.warn(f"FAILED {r.status_code} \n{r.text}")
            return False, r.text

    except Exception as e:
        print(e)
        return False, e


def post_crawled_news(news_content_data: NaverNewsContentModel, already_serialized=False):
    try:
        if already_serialized:
            jspn = news_content_data
        else:
            jspn = news_content_data.serialize()
        r = requests.post(request_url, json=jspn, headers=headers)
        if 200 <= r.status_code < 300:
            return True, '201'
        else:
            warnings.warn(f"FAILED {r.status_code} \n{r.text}")
            return False, r

    except Exception as e:
        print(e)
        return False, e



if __name__ == "__main__":
    post_crawled_news({
        "article_id": 0000,
        "article_url": "",
        "redirect_url": "",
        "origin_url": "origin_url",
        "title": "this is a test news",
        "content": "empty",
        "time": "2100-12-25 12:12:12",
        "provider": "inked-developer-test-channel"
    })
