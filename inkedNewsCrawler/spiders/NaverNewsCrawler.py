# -*- coding: euc-kr -*-
from datetime import datetime

import os
from dateutil.rrule import rrule, DAILY
import scrapy
from inkedNewsCrawler.custom_crawler.naver_news_link_crawler.naver_news_link_crawl_helper import read_links_from_file, check_if_links_empty, check_if_content_empty, extract_aid
from inkedNewsCrawler.items import NaverNewsContentItem
from inkedNewsCrawler.utils.naver_news_content_helper import ContentCrawlChecker

dirname = os.path.dirname(__file__)


start_date = datetime(1990, 1, 1)
end_date = datetime(2020, 1, 1)


def read_urls_from_file():
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
    start_urls = []
    # print(start_urls)
    print("count:", len(start_urls))

    def start_requests(self):
        checker = ContentCrawlChecker()
        url_data_list = read_urls_from_file()
        for url_data in url_data_list:
            if checker.check_article_crawled(url_data.aid):
                print("Already parsed", url_data.aid)
                pass
            else:
                meta = {"naver_link_data": url_data}
                yield scrapy.Request(url_data.print_link, callback=self.parse, dont_filter=True, meta=meta)

    def parse(self, response):
        link_data = response.meta["naver_link_data"]

        title = response.xpath("//h3[@class='font1']/text()").extract_first()
        body = response.xpath("//div[@class='article_body']/text()").extract_first()
        body_html = response.xpath("//div[@class='article_body']").extract_first()
        time = response.xpath("//span[@class='t11']/text()").extract_first()
        press_img_html = response.xpath("//a[@class='press_logo']/img").extract_first()


        item = NaverNewsContentItem()
        item["article_id"] = link_data.aid
        item["article_url"] = response.request.url
        item["title"] = title.encode("utf-8").decode("utf-8")
        item["body_html"] = body_html.encode("utf-8").decode("utf-8")
        item["body_text"] = body.encode("utf-8").decode("utf-8")
        item["time"] = time.encode("utf-8").decode("utf-8")
        item["provider"] = link_data.provider

        yield item
