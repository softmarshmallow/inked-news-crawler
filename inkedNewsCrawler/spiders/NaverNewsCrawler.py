# -*- coding: euc-kr -*-
from datetime import datetime

import os
from typing import List

import arrow
from dateparser import parse
from dateutil.rrule import rrule, DAILY
import scrapy
from inkedNewsCrawler.utils.sanitize_html import remove_unused_tags_html
from inkedNewsCrawler.custom_crawler.naver_news_link_crawler.naver_news_link_crawl_helper import \
    read_links_from_file, check_if_links_empty, check_if_content_empty, extract_aid, \
    NaverNewsLinkModel
from inkedNewsCrawler.items import NaverNewsContentItem
from inkedNewsCrawler.utils.naver_news_content_helper import ContentCrawlChecker

dirname = os.path.dirname(__file__)


start_date = datetime(2016, 1, 4)
end_date = datetime(2016, 1, 4)


def read_urls_from_file() -> List[NaverNewsLinkModel]:
    link_data_list = []

    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    for date in dates:
        # if link exists but content not parsed
        if not check_if_links_empty(date):
            if check_if_content_empty(date):
                links = read_links_from_file(date)
                link_data_list.extend(links)

    return link_data_list


def detect_url_type(url):
    if "entertain.naver.com/" in url:
        return "entertain"
    elif "sports.news.naver.com/" in url:
        return "sports"
    elif "news.naver.com/" in url:
        return "default"
    else:
        print("this url belongs nowhere", url)
        raise Exception



def translate_time(time_str:str):
    time_str = time_str.replace("오전", "AM")
    time_str = time_str.replace("오후", "PM")
    return time_str


class NavernewscrawlerSpider(scrapy.Spider):
    name = 'NaverNewsCrawler'
    allowed_domains = ['news.naver.com']

    def __init__(self, a):
        ...

    def start_requests(self):
        checker = ContentCrawlChecker()
        url_data_list = read_urls_from_file()
        for url_data in url_data_list:
            if checker.check_article_crawled(url_data.aid):
                print("Already parsed", url_data.aid)
                pass
            else:
                meta = {"naver_link_data": url_data}
                yield scrapy.Request(url_data.full_content_link, callback=self.parse, dont_filter=True, meta=meta)

    def parse(self, response):
        link_data = response.meta["naver_link_data"]
        url_type = detect_url_type(response.request.url)
        try:
            if url_type == "default":
                data = self.parse_from_full_content_url(response=response)
            elif url_type == "entertain":
                data = self.parse_from_entertainment_url(response=response)
            elif url_type == "sports":
                data = self.parse_from_sports_url(response=response)

            else:
                raise Exception

            item = NaverNewsContentItem()
            item["article_id"] = link_data.aid
            item["article_url"] = response.request.url
            item["title"] = data[0]
            item["body_html"] = data[1]
            item["time"] = data[2].strftime("%Y-%m-%d %H:%M:%S")
            item["provider"] = link_data.provider
            yield item
        except AttributeError as e:
            print("AttributeError ERR", link_data, e)

    def parse_from_print_content_url(self, response):
        # FIXME DO NOT USE
        title = response.xpath("//h3[@class='font1']/text()").extract_first()
        body = response.xpath("//div[@class='article_body']/text()").extract_first()
        body_html = response.xpath("//div[@class='article_body']").extract_first()
        time = response.xpath("//span[@class='t11']/text()").extract_first()
        # press_img_html = response.xpath("//a[@class='press_logo']/img").extract_first()

        return title, body, body_html, time

    def parse_from_full_content_url(self, response):
        title = response.xpath('//*[@id="articleTitle"]/text()').extract_first()
        body_html = response.xpath('//*[@id="articleBodyContents"]').extract_first()
        body_html = remove_unused_tags_html(body_html)

        # 2018-03-04 23:58
        raw_time = response.xpath('//*[@id="main_content"]//div[@class="article_info"]//span[@class="t11"]/text()').extract_first()
        time = arrow.get(raw_time, 'YYYY-MM-DD HH:mm').datetime

        return title, body_html, time

    def parse_from_entertainment_url(self, response):

        title = response.xpath('//*[@id="content"]//h2[@class="end_tit"]/text()').extract_first()
        body_html = response.xpath('//*[@id="articeBody"]').extract_first()
        body_html = remove_unused_tags_html(body_html)

        # 2018.08.23 오후 5:04 == > 2016.01.01 10:25
        raw_time = response.xpath('//*[@id="content"]//div[@class="article_info"]/span[@class="author"]/em/text()').extract_first()
        raw_time = translate_time(raw_time)
        time = arrow.get(raw_time, 'YYYY.MM.DD A h:mm').datetime

        return title, body_html, time

    def parse_from_sports_url(self, response):
        title = response.xpath('//*[@id="content"]//div[@class="news_headline"]//h4/text()').extract_first()
        body_html = response.xpath('//*[@id="newsEndContents"]').extract_first()
        body_html = remove_unused_tags_html(body_html)

        #  기사입력 2018.08.23 오후 06:36 == > 2016.01.01 10:25
        raw_time = response.xpath('//*[@id="content"]//div[@class="news_headline"]/div[@class="info"]/span[1]/text()').extract_first()
        raw_time = translate_time(raw_time)
        time = arrow.get(raw_time, '기사입력 YYYY.MM.DD A h:mm').datetime

        return title, body_html, time
