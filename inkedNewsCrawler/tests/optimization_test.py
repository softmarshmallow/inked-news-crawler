from datetime import datetime

from inkedNewsCrawler.custom_crawler.naver_news_link_crawler.naver_news_link_crawler_threaded import NaverDateNewsLinkCrawler
from selenium import webdriver

def callback(date, result):
    for r in result:
        print(r)
date = datetime(2018, 8, 3)

# driver = webdriver.PhantomJS()
# NaverDateNewsLinkCrawler(date, driver, callback, skip_crawled_date=False).parse()


from inkedNewsCrawler.utils.web_drivers import get_chrome_options
chrome_options = get_chrome_options(headless=False)
chrome_driver = webdriver.Chrome(chrome_options=chrome_options)
NaverDateNewsLinkCrawler(date, chrome_driver, callback, skip_crawled_date=False).parse()
