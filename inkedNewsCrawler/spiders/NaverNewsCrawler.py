# -*- coding: utf-8 -*-
from datetime import datetime
from pprint import pprint

import os
from dateutil.rrule import rrule, DAILY
import scrapy
from selenium import webdriver
from inkedNewsCrawler.custom_crawler.naver_crawl_helper import read_links_from_file, check_if_links_empty, check_if_content_empty
dirname = os.path.dirname(__file__)


def read_urls_from_file():
    full_links = []
    start_date = datetime(1990, 1, 1)
    end_date = datetime(1990, 2, 1)
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
        title = response.xpath("//h3[@class='font1']/text()").extract()
        body = response.xpath("//div[@class='article_body']/text()").extract()
        body_html = response.xpath("//div[@class='article_body']").extract()
        time = response.xpath("//span[@class='t11']/text()").extract_first()
        press_img_html = response.xpath("//a[@class='press_logo']/img").extract()
        yield {
            "title": title,
            "body_html": body_html,
            "body": body,
            "time": time,
            "press_img_html": press_img_html
        }

