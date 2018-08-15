# -*- coding: euc-kr -*-
from datetime import datetime
from pprint import pprint

import os
from dateutil.rrule import rrule, DAILY
import scrapy
from selenium import webdriver
from inkedNewsCrawler.custom_crawler.naver_crawl_helper import read_links_from_file, check_if_links_empty, check_if_content_empty, extract_aid
dirname = os.path.dirname(__file__)


start_date = datetime(2000, 1, 1)
end_date = datetime(2000, 1, 2)


def read_urls_from_file():
    full_links = []

    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    for date in dates:
        # if link exists but content not parsed
        if not check_if_links_empty(date):
            if check_if_content_empty(date):
                links = read_links_from_file(date)
                full_links.extend(links)

    return full_links


class NavernewscrawlerSpider(scrapy.Spider):
    name = 'NaverNewsCrawler'
    allowed_domains = ['news.naver.com']
    start_urls = read_urls_from_file()
    # print(start_urls)
    print("count:", len(start_urls))

    def parse(self, response):

        title = response.xpath("//h3[@class='font1']/text()").extract_first()
        body = response.xpath("//div[@class='article_body']/text()").extract_first()
        body_html = response.xpath("//div[@class='article_body']").extract_first()
        time = response.xpath("//span[@class='t11']/text()").extract_first()
        press_img_html = response.xpath("//a[@class='press_logo']/img").extract_first()
        aid = extract_aid(response.request.url)
        # TODO FIx encoding
        yield {
            "aid": aid,
            "url": response.request.url,
            "title": title.encode("utf-8").decode("utf-8"),
            "body_html": body_html.encode("utf-8").decode("utf-8"),
            "body": body.encode("utf-8").decode("utf-8"),
            "time": time.encode("utf-8").decode("utf-8"),
            "press_img_html": press_img_html.encode("utf-8").decode("utf-8")
        }

