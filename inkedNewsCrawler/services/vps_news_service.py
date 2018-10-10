from inkedNewsCrawler.services.api_controller import BASE_SERVER_URL
import requests


request_url = BASE_SERVER_URL + "api/news"


def post_crawled_news(news_content_data):
    r = requests.post(request_url, json=news_content_data)
    if r.status_code == 200:
        print("CREATED", r.text)
    else:
        print("FAILED", r.status_code, news_content_data)




if __name__ == "__main__":
    ...