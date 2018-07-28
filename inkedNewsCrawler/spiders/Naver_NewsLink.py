# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
from dateutil.rrule import rrule, DAILY
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


MAX_PAGES_PER_PAGINATION = 10

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
prefs = {"profile.managed_default_content_settings.images":2}
options.add_experimental_option("prefs",prefs)
options.set_headless(True)


class NaverNewslinkSpider(scrapy.Spider):
    name = 'Naver_NewsLink'
    allowed_domains = ['news.naver.com']

    start_urls = []
    start_date = datetime(1990, 1, 1)
    end_date = datetime(2018, 4, 1)

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        start_urls.append('https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=title&date=%s' % dt.strftime("%Y%m%d"))

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=options)
        self.f = open('NaverArticleLinks.txt', 'w')

    def parse(self, response):
        self.driver.get(response.url)

        while True:
            self.parse_available_pages()
            try:
                next = self.driver.find_element_by_xpath("//*[@id='main_content']/div[@class='paging']/a[@class='next nclicks(fls.page)']")
            except NoSuchElementException:
                break
            try:
                # NextPage + 10
                # next.click()
                self.driver.execute_script("arguments[0].click();", next)

            except:
                break

        self.driver.close()

    def parse_available_pages(self):
        for i in range(0, MAX_PAGES_PER_PAGINATION):
            self.parse_article_in_page()
            # region click next available page in pager
            try:
                pages = self.driver.find_elements_by_xpath("//*[@id='main_content']/div[@class='paging']/a[@class='nclicks(fls.page)']")
                page = pages[i]
                self.driver.execute_script("arguments[0].click();", page)
                # page.click()
            except IndexError:
                return
            # endregion

    def parse_article_in_page(self):
        articles = self.driver.find_elements_by_xpath("//*[@id='main_content']/div[@class='list_body newsflash_body']//a[@class='nclicks(fls.list)']")

        for article in articles:
            href = article.get_attribute('href')
            self.add_article(href)

    def add_article(self, article):
        self.f.write(article + "\n")
