# -*- coding: utf-8 -*-
from datetime import datetime
from pprint import pprint

from dateutil.rrule import rrule, DAILY
import scrapy
from selenium import webdriver


class NavernewscrawlerSpider(scrapy.Spider):
    name = 'NaverNewsCrawler'
    allowed_domains = ['news.naver.com']
    start_urls = []

    start_date = datetime(1990, 1, 1)
    # end_date = datetime(2018, 4, 1)
    end_date = datetime(1990, 1, 1)

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        start_urls.append('https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=title&date=%s' % dt.strftime("%Y%m%d"))

    def parse(self, response):
        for href in response.xpath("//*[@id='main_content']//div[@class='paging']/a[@class='next nclicks(fls.page)']/@href"):

            "//*[@id='main_content']/div[@class='paging']/a"




            nexpage_url = href.extract()

            yield scrapy.Request(nexpage_url, callback=self.parse_dir_contents)

    def parse_article_url(self, response):
        links = response.xpath("//*[@id='main_content']//a[class='nclicks(fls.list)']/@href").extract()
        yield links
