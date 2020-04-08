from datetime import datetime
from multiprocessing.pool import ThreadPool
from threading import Thread
from timeit import repeat
from typing import List
import warnings
import time
from selenium.webdriver import Chrome

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_content_crawler_threaded import \
    NaverNewsSingleArticleContentCrawler
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import \
    NaverNewsLinkModel
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_link_crawler_threaded import \
    NaverDateNewsLinkCrawler
from inkedNewsCrawler.services.database_direct import insert
from inkedNewsCrawler.services.vps_news_service import post_crawled_news
from inkedNewsCrawler.utils.web_drivers import get_chrome_options

# #OVERVIEW
# single selenium instance running...
# refresh every 0.5 second
# read news links until last saved news appears, including pagination
# call 'new_news_link_discovered'
# crawl new news on different thread
# on news content crawled, send to server

# On serverside, Add URL checker
# - query same news time range
# - query same news URL
# - (safe) query news title, check if same.
# if not, add. if conflicts, remove.


# Crawler refresh rate in seconds
# recommended 5 주기가 빠를수록 누락되는 데이터가 생김. 이는 네이버뉴스측 문제로, 최신순으로 업데이트 되는 과정에서 가장 최근 보다 하단에 새로운 뉴스가 배치되는 경우가 있음.
CRAWLER_REFRESH_RATE = 1

latest_news_links_data_list = []
latest_news_content_list = []

MAX_QUEUE = 500


class LiveNewsLinkCrawler(Thread):
    def __init__(self, driver):
        super().__init__()
        self.start_time = datetime.now()
        self.refresh_count = 0
        self.last_news_link_data: NaverNewsLinkModel = None
        self.latest_news_link_list: List[NaverNewsLinkModel] = []
        self.driver = driver
        self.should_continue_crawling = True
        self.conflict_check_list: List[NaverNewsLinkModel] = []

    def run(self):
        while True:
            if self.refresh_required():
                self.crawl()

    def refresh_required(self) -> bool:
        target_elapsed_time = CRAWLER_REFRESH_RATE * self.refresh_count
        # print("target_elapsed_time", target_elapsed_time)
        if (datetime.now() - self.start_time).total_seconds() > target_elapsed_time:
            self.refresh_count += 1
            return True
        return False

    def crawl(self):
        crawler = NaverDateNewsLinkCrawler(date=datetime.now(), driver=self.driver,
                                           on_items_complete=None, skip_crawled_date=False,
                                           on_page_crawled=self.on_page_crawled)
        crawler.load_page()
        self.should_continue_crawling = True

        while self.should_continue_crawling:
            crawler.parse_article_in_page()
            crawler.move_to_next_page()

    def on_page_crawled(self, link_data_list):
        if link_data_list is None or len(link_data_list) == 0:
            warnings.warn("page is crawled, but no links are parsed.. please check")
            return
        (is_reached, reach_index) = self.reached_last_article(link_data_list)

        self.should_continue_crawling = not is_reached

        link_data_list.reverse()
        for data in link_data_list:
            self.add_to_queue(data)

        # none_added_items = list(link_data_list[:index+1])
        # none_added_items.reverse()
        # for none_added_item in none_added_items:
        #     self.add_to_queue(none_added_item)

    def reached_last_article(self, new_data_list: List[NaverNewsLinkModel]) -> (bool, int):

        if new_data_list is None or len(new_data_list):
            warnings.warn("news data list is empty or none.. passing")
            return True, -1

        """
        마지막으로 받아온 뉴스를 만났는지 확인함. via URL
        마지막으로 받아온 뉴스가 새로 받아온 뉴스에서 사라질 경우? via Time
        :return:
        """
        index = 0


        # 이전 데이터가 없을경우, 최초 실행일 경우
        if self.last_news_link_data is None:
            self.last_news_link_data = new_data_list[0]
            return True, index

        is_reached = False
        for n in new_data_list:
            over_timed = self.last_news_link_data.publish_time > n.publish_time
            reached_article = n.article_url == self.last_news_link_data.article_url
            if not reached_article and over_timed:
                warnings.warn("There was an exception, haven't reached last article yet, but time was older (its providers fault, nothing we can do..)")

            if reached_article or over_timed:
                self.last_news_link_data = new_data_list[0]
                is_reached = True
                break
            index += 1
        # Add items

        if not is_reached:
            warnings.warn("CHECK THIS:: " + str(self.last_news_link_data) + str(new_data_list))
        return is_reached, index

    def add_to_queue(self, link_data_item):
        for i in self.conflict_check_list:
            if i.article_url == link_data_item.article_url:
                return

        self.conflict_check_list.append(link_data_item)
        latest_news_links_data_list.append(link_data_item)
        print("add_to_queue", link_data_item)

        while len(self.conflict_check_list) > MAX_QUEUE:
            self.conflict_check_list.pop(0)

    def check_conflict(self, link_data_item):
        for i in self.conflict_check_list:
            if i.article_url == link_data_item.article_url:
                return True
        return False


class LiveNewsContentCrawler(Thread):
    def __init__(self):
        super().__init__()
        self.threads_count = 4

    def run(self):

        # pool = ThreadPool(self.threads_count)
        # pool.starmap(self.crawl_single_article, zip(latest_news_links_data_list, repeat(self.on_item_crawl)))
        # close the pool and wait for the work to finish
        # pool.close()
        # pool.join()

        while True:
            if len(latest_news_links_data_list) > 0:
                self.crawl_single_article(latest_news_links_data_list[0], self.on_item_crawl)
                latest_news_links_data_list.pop(0)
            else:
                time.sleep(CRAWLER_REFRESH_RATE)

    def on_item_crawl(self, data):
        if (data is None):
            warnings.warn("data from `NaverNewsSingleArticleContentCrawler` is none, please check for more details")
        else:
            self.send_to_server(data)

    def crawl_single_article(self, link_data, callback):
        NaverNewsSingleArticleContentCrawler(link_data,
                                             callback).parse_single_article_with_callback()
        ...

    def send_to_server(self, data):
        if data is not None:
            post_crawled_news(data)
            # insert(data)


driver = None


def main(accepted_langs, do_schedule_restart=True):
    global driver
    if do_schedule_restart:
        schedule_restart()

    if driver is None:
        chrome_options = get_chrome_options(headless=True)
        driver = Chrome(chrome_options=chrome_options)
    LiveNewsLinkCrawler(driver=driver).start()
    LiveNewsContentCrawler().start()


def schedule_restart():
    import threading
    from datetime import datetime, timedelta

    today = datetime.today()
    today = datetime(year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0, microsecond=0)
    now = datetime.now()
    run_at = today + timedelta(days=1, hours=1)
    print(f"crawler is scheduled to restart at {run_at}")
    delay = (run_at - now).total_seconds()
    threading.Timer(delay, restart_program).start()


def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    import os
    import sys
    import psutil
    import logging

    driver.quit()

    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

    # os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == '__main__':
    # main()
    main(accepted_langs=['ko'])
