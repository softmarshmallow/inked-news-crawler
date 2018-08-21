import json
from datetime import datetime

import os.path

from dateutil.rrule import DAILY, rrule
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import atexit
import time
from multiprocessing.dummy import Pool as ThreadPool
from inkedNewsCrawler.custom_crawler.naver_news_link_crawler.naver_news_link_crawl_helper import check_if_links_empty, \
    write_links_to_file

dirname = os.path.dirname(__file__)

MAX_PAGES_PER_PAGINATION = 10

options = webdriver.ChromeOptions()
options.add_argument('--headless')
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
options.set_headless(True)

exceptions = []

class NaverDateNewsLinkCrawler:
    def __init__(self, date, driver):
        self.links = []
        self.date = date
        self.date_str = date.strftime("%Y%m%d")
        self.url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=title&date=%s' % self.date_str
        self.driver = driver

        print("Crawl", self.date_str, "// AT:", datetime.now())

    def parse(self):
        if not check_if_links_empty(date=self.date):
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

        self.save_to_file()

    def parse_available_pages(self):
        for i in range(0, MAX_PAGES_PER_PAGINATION):

            self.parse_article_in_page()
            # region click next available page in pager
            try:
                pages = self.driver.find_elements_by_xpath(
                    "//*[@id='main_content']/div[@class='paging']/a[@class='nclicks(fls.page)']")
                page = pages[i]
                # page.click()
                try:
                    self.driver.execute_script("arguments[0].click();", page)
                except:
                    exceptions.append({"ERR": page})
                    print("ERR", page)
            except IndexError:
                return
            # endregion

    def parse_article_in_page(self):
        articles = self.driver.find_elements_by_xpath(
            "//*[@id='main_content']/div[@class='list_body newsflash_body']//a[@class='nclicks(fls.list)']")

        for article in articles:
            try:
                href = article.get_attribute('href')
                provider = article.find_element_by_xpath("../span[@class='writing']").text
                data = {"link": href, "provider": provider}
                self.links.append(data)
            except:
                exceptions.append({"ERR": article})
                print("ERR", article)

    def save_to_file(self):
        write_links_to_file(date=self.date, links=self.links)
        print("Crawl Complete", self.date_str, " // AT:", datetime.now())


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
    NaverDateNewsLinkCrawler(dt, driver).parse()
    finish_using_driver(driver)


def crawl_all_links():
    THREAD_COUNT = int(input("Thread counts:: "))
    start_date_str = input("start_date (YYYYmmdd) :: ")
    end_date_str = input("end_date (YYYYmmdd) :: ")

    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    dates = rrule(DAILY, dtstart=start_date, until=end_date)

    # instantiate browsers
    for i in range(THREAD_COUNT):
        print("SETUP Driver %i" % (i+1))
        driver = webdriver.Chrome(chrome_options=options)
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


if __name__ == "__main__":
    def exit_handler():
        from inkedNewsCrawler.utils.email_notification import send_email
        send_email("Crawling Complete Please Check...", json.dumps(exceptions))


    atexit.register(exit_handler)

    crawl_all_links()
