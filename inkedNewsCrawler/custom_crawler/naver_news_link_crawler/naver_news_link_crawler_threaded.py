import json
from datetime import datetime
from typing import Callable

from lxml import html

import os.path

from dateutil.rrule import DAILY, rrule
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import atexit
import time
from multiprocessing.dummy import Pool as ThreadPool
from inkedNewsCrawler.custom_crawler.naver_news_link_crawler.naver_news_link_crawl_helper import \
    check_if_links_empty, \
    write_links_to_file

dirname = os.path.dirname(__file__)

MAX_PAGES_PER_PAGINATION = 10

exceptions = []


class NaverDateNewsLinkCrawler:
    def __init__(self, date, driver, callback: Callable, skip_crawled_date=True):
        self.links = []
        self.date = date
        self.date_str = date.strftime("%Y%m%d")
        self.url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=title&date=%s' % self.date_str
        self.driver = driver
        self.callback = callback
        self.skip_crawled_date = skip_crawled_date
        self.article_count = 0
        self.page_count = 0

        print("Crawl", self.date_str, "// AT:", datetime.now())

    def parse(self):
        if self.skip_crawled_date and not check_if_links_empty(date=self.date):
            print("ALREADY CRAWLED:", self.date_str)
            return
        self.driver.get(self.url)

        while True:
            self.parse_available_pages()
            try:
                next = self.driver.find_element_by_xpath(
                    "//*[@id='main_content']/div[@class='paging']/a[@class='next nclicks(fls.page)']")
            except NoSuchElementException:
                break
            try:
                # NextPage + 10
                # next.click()
                self.driver.execute_script("arguments[0].click();", next)

            except:
                break
        self.callback(self.date, self.links)
        # self.save_to_file()
        print("Crawl Complete", self.date_str, " // AT:", datetime.now())

    def parse_available_pages(self):
        for i in range(0, MAX_PAGES_PER_PAGINATION):
            self.page_count += 1
            if self.page_count % 100 == 0: print(self.date_str, self.page_count, self.article_count)

            self.parse_article_in_page()
            # region click next available page in pager
            try:

                pages = self.driver.find_elements_by_xpath(
                    "//*[@id='main_content']/div[@class='paging']/a[@class='nclicks(fls.page)']")
                page = pages[i]
                try:
                    # page.click()
                    self.driver.execute_script("arguments[0].click();", page)
                except Exception as e:
                    error_data = {"Error": e, "ErrPage": self.page_count, "Date": self.date_str}
                    exceptions.append(error_data)
                    print(error_data)
            except IndexError:
                return
            # endregion

    def parse_article_in_page(self):

        html_source = self.driver.page_source
        tree = html.fromstring(html_source)
        articles = tree.xpath(
            "//*[@id='main_content']/div[@class='list_body newsflash_body']//li")

        # articles = self.driver.find_elements_by_xpath(
        #     "//*[@id='main_content']/div[@class='list_body newsflash_body']//a[@class='nclicks(fls.list)']")

        for article in articles:
            self.article_count += 1
            try:
                href = article.xpath("./a/@href")[0]
                # region title
                title = article.xpath("./a/text()")
                if len(title) > 0:
                    title = title[0]
                else:
                    title = ""
                # endregion

                # region publish_time
                publish_time = article.xpath("./span[@class='date']/text()")
                if len(publish_time) > 0:
                    publish_time = publish_time[0]
                else:
                    publish_time = article.xpath("./span[@class='date is_outdated']/text()")
                    publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "/" + publish_time[0]
                # endregion

                # region provider
                provider = article.xpath("./span[@class='writing']/text()")
                if len(provider) >0:
                    provider = provider[0]
                else:
                    provider = ""
                # endregion

                data = {"link": href, "title": title, "provider": provider, "time": publish_time}
                self.links.append(data)

            except Exception as e:
                error_data = {"Error": e, "Article": self.article_count, "Date": self.date_str, "Page": self.page_count}
                exceptions.append(error_data)
                print(error_data)


def save_to_file(date, links):
    write_links_to_file(date=date, links=links)


available_drivers = []
used_drivers = []


def use_available_driver():
    while len(available_drivers) == 0:
        time.sleep(0.1)
    driver = available_drivers[0]
    available_drivers.remove(driver)
    used_drivers.append(driver)
    return driver


def finish_using_driver(driver):
    used_drivers.remove(driver)
    available_drivers.append(driver)


def start_crawl(dt):
    driver = use_available_driver()
    NaverDateNewsLinkCrawler(dt, driver, save_to_file).parse()
    finish_using_driver(driver)


def crawl_all_links(THREAD_COUNT, start_date, end_date):
    dates = rrule(DAILY, dtstart=start_date, until=end_date)

    from inkedNewsCrawler.utils.web_drivers import get_chrome_options
    chrome_options = get_chrome_options()
    # instantiate browsers
    for i in range(THREAD_COUNT):
        print("SETUP Driver %i" % (i + 1))
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver = webdriver.PhantomJS()

        available_drivers.append(driver)
        # pass

    pool = ThreadPool(THREAD_COUNT)
    pool.map(start_crawl, dates)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()

    #  Clean drivers
    for driver in available_drivers:
        driver.quit()


def main():
    def exit_handler():
        from inkedNewsCrawler.utils.email_notification import send_email
        exception_str = json.dumps(exceptions)
        send_email("Crawling Complete Please Check...", extra=exception_str)

    atexit.register(exit_handler)

    THREAD_COUNT = int(input("Thread counts:: "))
    start_date_str = input("start_date (YYYYmmdd) :: ")
    end_date_str = input("end_date (YYYYmmdd) :: ")

    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    crawl_all_links(THREAD_COUNT, start_date, end_date)


if __name__ == "__main__":
    main()
