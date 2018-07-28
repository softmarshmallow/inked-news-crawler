# -*- coding: utf-8 -*-
from datetime import datetime
from pprint import pprint

import re
import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from dateutil.rrule import rrule, DAILY
import urllib.parse




class MtNewslinkSpider(CrawlSpider):
    name = 'MT_NewsLink'
    allowed_domains = ['news.mt.co.kr']

    # 2000.1.1~ 2018.4.1
    start_date = datetime(2000, 1, 1)
    # end_date = datetime(2018, 4, 1)
    end_date = datetime(2000, 4, 1)

    start_urls = []
    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        start_urls.append('http://news.mt.co.kr/newsTotalList.html?pDepth1=newsTotal&pDate=%s' % dt.strftime("%Y%m%d"))

    # rules = (
    #     # Extract links for next pages
    #     Rule(LinkExtractor(restrict_xpaths=("//*[@id=\"paging_t17\"]/span/a")), callback="parse_page_articles", follow=True),
    # )

    def parse(self, response):
        url = response.url
        last_page_no = self.parse_last_page(response)
        for p in range(1, last_page_no):
            paged_url = url + "&" + "page=%s" % p
            next_resp = yield Request(paged_url)
            self.parse_page_articles(next_resp)

    def parse_last_page(self, response):
        last_page = response.xpath("//*[@id='paging_t17']/button[@class='end']/@onclick").extract_first()
        last_page_no = re.findall(r"page=(.*?)'", last_page)[0]
        last_page_no = int(last_page_no)

        return last_page_no


    def parse_page_articles(self, response):
        articles = response.xpath("//div[@id='content']//a[@class='subject']/@href").extract()
        for article_url in articles:
            yield {"article_url" : article_url}

