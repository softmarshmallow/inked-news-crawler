import json
import os.path
from datetime import datetime, timedelta
from multiprocessing.dummy import Pool as ThreadPool
from typing import Callable, List
import warnings
import atexit
import re
import time
from dateutil.rrule import DAILY, rrule
from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from langdetect import detect

from inkedNewsCrawler.custom_crawler.naver_news_crawler.configs import TIME_FORMAT
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import \
    check_if_links_empty, \
    IOManager, NaverNewsLinkModel

dirname = os.path.dirname(__file__)

# news.naver.com pagination count
MAX_PAGES_PER_PAGINATION = 10

exceptions = []

FROM_S3 = True
SKIP_CRAWLED = True


class NaverDateNewsLinkCrawler:
    """

네이버뉴스 속보의 페이징 시스템
- 원하는 페이지로 주소 접속이 불가능함. js 버튼클릭을 통해서 가능함.
- 한 페지네이션당 10 페이지가 제공됨.
- 페이징 섹션은 현제 페이지 버튼은 클릭이 불가능함.
- 다음 버튼으로 다음 페지네이션으로 이동가능함.

    """

    def __init__(self, date, driver, on_page_crawled: Callable, on_items_complete: Callable,
                 skip_crawled_date=True):
        self.link_data_list: List[NaverNewsLinkModel] = []
        self.date = date
        self.date_str = date.strftime("%Y%m%d")
        self.url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=title&date=%s' % self.date_str
        self.driver = driver
        self.on_page_crawled = on_page_crawled
        self.on_items_complete = on_items_complete
        self.skip_crawled_date = skip_crawled_date
        self.article_count = 0
        self.current_page_number = 1
        self.page_index_in_pagination = 0
        self.pagination_pages = []

    def load_page(self) -> bool:
        if self.skip_crawled_date and not check_if_links_empty(date=self.date, from_s3=FROM_S3):
            print("ALREADY CRAWLED:", self.date_str)
            return False
        self.driver.get(self.url)
        # Call on first load
        self.on_page_loaded()
        return True

    def crawl_all(self):

        loaded = self.load_page()
        if not loaded:
            return

        print("Crawl", self.date_str, "// AT:", datetime.now())
        while True:
            self.parse_article_in_page()
            page_moved = self.move_to_next_page()
            if not page_moved:
                break

        self.on_items_complete(self.date, self.link_data_list)
        # self.save_to_file()
        print("Crawl Complete", self.date_str, " // AT:", datetime.now())

    def move_to_next_pagination(self) -> bool:
        try:
            # 다음 페지네이션 버튼을 찾는다
            next_btn = self.driver.find_element_by_xpath(
                "//*[@id='main_content']/div[@class='paging']/a[@class='next nclicks(fls.page)']")
        except NoSuchElementException:
            return False
        try:
            # 다음 페지네이션 버튼을 클릭한다.
            self.driver.execute_script("arguments[0].click();", next_btn)
            self.page_index_in_pagination = 0
            self.on_page_loaded()

        except:
            return False
        return True

    def on_page_loaded(self):
        # 페이지 이동후
        # 한 페지네이션에 있는 페이지들을 받아온다.
        self.driver.implicitly_wait(10)
        self.pagination_pages = self.driver.find_elements_by_xpath(
            "//*[@id='main_content']/div[@class='paging']/a[@class='nclicks(fls.page)']")

    def move_to_next_page(self) -> bool:
        if self.current_page_number % 100 == 0: print(self.date_str, self.current_page_number,
                                                      self.article_count)

        # region click next available page in pager
        try:
            page = self.pagination_pages[self.page_index_in_pagination]
            try:
                # 다음 페이지를 클릭한다.
                self.driver.execute_script("arguments[0].click();", page)
                self.on_page_loaded()
                self.page_index_in_pagination += 1
                self.current_page_number += 1

            except Exception as e:
                error_data = {"Error": str(e), "ErrPage": self.current_page_number,
                              "Date": self.date_str}
                exceptions.append(error_data)
                print(error_data)
                return False
        except IndexError:
            moved_to_next_pagination = self.move_to_next_pagination()
            if not moved_to_next_pagination:
                return False
            return True
            # raise Exception("next page is not available")
        # endregion
        return True

    def parse_article_in_page(self):
        html_source = self.driver.page_source
        page_link_data_list = NewsLinkPageArticleParser(page_html=html_source,
                                                        page_date=self.date,
                                                        page_number=self.current_page_number).parse()

        # single item added Callback
        if self.on_page_crawled is not None:
            self.on_page_crawled(page_link_data_list)

        self.link_data_list.extend(page_link_data_list)


class NewsLinkPageArticleParser:
    '''한 속보 페이지에 있는 뉴스를 파싱한다.

    - 뉴스 제목
    - 뉴스 url
    - 뉴스 시간
    - 언론사

    :return list of news_link_data
    '''

    def __init__(self, page_html, page_number, page_date: datetime):
        self.page_html = page_html
        self.page_date: datetime = page_date
        self.page_number = page_number
        self.current_article_number_in_page = 0
        self.link_data_list: List[NaverNewsLinkModel] = []

    def parse(self) -> List[NaverNewsLinkModel]:
        tree = html.fromstring(self.page_html)
        articles = tree.xpath(
            "//*[@id='main_content']/div[@class='list_body newsflash_body']//li")

        # articles = self.driver.find_elements_by_xpath(
        #     "//*[@id='main_content']/div[@class='list_body newsflash_body']//a[@class='nclicks(fls.list)']")

        for article in articles:
            self.current_article_number_in_page += 1
            # try:
            href = article.xpath("./a/@href")[0]
            # region title
            title = article.xpath("./a/text()")
            if len(title) > 0:
                title = title[0]
            else:
                title = ""
            # endregion

            publish_time = self.parse_time(article)

            # region provider
            provider = article.xpath("./span[@class='writing']/text()")
            if len(provider) > 0:
                provider = provider[0]
            else:
                provider = ""
            # endregion

            data = NaverNewsLinkModel(title=title, publish_time=publish_time, provider=provider,
                                      article_url=href)
            self.link_data_list.append(data)

            # except Exception as e:
            #     ...
            # error_data = {"NewsLinkPageArticleParser:Error": str(e), "Article": self.current_article_number_in_page, "Date": self.page_date, "Page": self.page_number}
            # exceptions.append(error_data)
            # print(error_data)
        return self.link_data_list

    def parse_time(self, article_node) -> datetime:

        # region publish_time
        publish_time = datetime.now().strftime(TIME_FORMAT)

        # 일반 시간 // 과거 일경우
        normal_publish_time_text = article_node.xpath("./span[@class='date']/text()")

        # 최근 일경우, 하지만 1시간 이상일경우 "1시간전" 으로 표시됨
        humanized_publish_time_outdated = article_node.xpath(
            "./span[@class='date is_outdated']/text()")

        # 최근 일경우, 1시간 미만 일경우, "12분전" 으로 표시됨
        humanized_publish_time_new = article_node.xpath("./span[@class='date is_new']/text()")

        if len(normal_publish_time_text) > 0:
            normal_publish_time_text = normal_publish_time_text[0]
            publish_time = datetime.strptime(normal_publish_time_text, "%Y.%m.%d %H:%M")

        elif len(humanized_publish_time_outdated) > 0:
            publish_time_text = datetime.now().strftime(TIME_FORMAT) + "/" + \
                           humanized_publish_time_outdated[0]
            warnings.warn("this time is not convertible. :: " + publish_time_text)

            publish_time = self.page_date
        elif len(humanized_publish_time_new) > 0:
            delta_str = humanized_publish_time_new[0]
            delta = [int(s) for s in re.findall(r'\d+', delta_str)][0]
            publish_time = datetime.now() - timedelta(minutes=delta)
            publish_time = publish_time
        # endregion

        return publish_time


def save_to_file(date, links, from_s3=FROM_S3):
    iom = IOManager(from_s3=from_s3)
    iom.write_links_to_file(date=date, links=links)


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
    NaverDateNewsLinkCrawler(date=dt, driver=driver, on_items_complete=save_to_file,
                             skip_crawled_date=SKIP_CRAWLED, on_page_crawled=None).crawl_all()
    finish_using_driver(driver)


def crawl_all_links(THREAD_COUNT, start_date, end_date):
    dates = rrule(DAILY, dtstart=start_date, until=end_date)

    from inkedNewsCrawler.utils.web_drivers import get_chrome_options
    chrome_options = get_chrome_options(headless=False)
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
