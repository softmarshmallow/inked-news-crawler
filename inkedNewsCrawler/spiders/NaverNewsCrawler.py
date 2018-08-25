# -*- coding: euc-kr -*-
from datetime import datetime

import os
from typing import List

from dateutil.rrule import rrule, DAILY
import scrapy
from parsel import Selector

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_content_crawler_threaded import \
    NaverArticleContentParser
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import \
    read_links_from_file, check_if_links_empty, check_if_content_empty, extract_aid, \
    NaverNewsLinkModel
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


class NavernewscrawlerSpider(scrapy.Spider):
    name = 'NaverNewsCrawler'
    allowed_domains = ['news.naver.com']

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
        # print(response.body)
        # html_body = response.body.decode()
        # selector = Selector(text=html_body)
        result = NaverArticleContentParser(selector=response, link_data=link_data, redirect_url=response.request.url).parse()
        yield result
