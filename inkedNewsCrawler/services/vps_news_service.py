from typing import List
import warnings
from inkedNewsCrawler.custom_crawler.naver_news_crawler.models import NaverNewsContentModel
from inkedNewsCrawler.services.api_controller import BASE_SERVER_URL
import requests


request_url = BASE_SERVER_URL + "api/news/"
print(request_url)


def post_crawled_news(news_content_data: NaverNewsContentModel):
    try:
        json_serializable = news_content_data.serialize()
        r = requests.post(request_url, json=json_serializable)
        if 200 <= r.status_code < 300:
            # print("CREATED", r.text)
            pass
        else:
            warnings.warn(f"FAILED ${r.status_code} \n${r.text}\n\n${news_content_data}")

    except Exception as e:
        print(e)



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
