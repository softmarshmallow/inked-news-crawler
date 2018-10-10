from datetime import datetime
from multiprocessing.pool import ThreadPool
from threading import Thread
from timeit import repeat
from typing import List

import time
from selenium.webdriver import Chrome

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_content_crawler_threaded import \
    NaverNewsSingleArticleContentCrawler
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import \
    NaverNewsLinkModel
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_link_crawler_threaded import \
    NaverDateNewsLinkCrawler
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
CRAWLER_REFRESH_RATE = 0.2


latest_news_links_data_list = []
latest_news_content_list = []



MAX_QUEUE = 500


class LiveNewsLinkCrawler(Thread):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()
        self.refresh_count = 0
        self.last_news_link_data: NaverNewsLinkModel = None
        self.latest_news_link_list: List[NaverNewsLinkModel] = []
        chrome_options = get_chrome_options()
        self.driver = Chrome(chrome_options=chrome_options)
        self.should_continue_crawling = True
        self.conflict_check_list: List[NaverNewsLinkModel] = []


    def run(self):
        while True:
            if self.refresh_required():
                self.crawl()
                self.refresh_count += 1

    def refresh_required(self) -> bool:
        target_elapsed_time = CRAWLER_REFRESH_RATE * self.refresh_count
        # print("target_elapsed_time", target_elapsed_time)
        if (datetime.now() - self.start_time).total_seconds() > target_elapsed_time:
            return True
        return False

    def crawl(self):
        crawler = NaverDateNewsLinkCrawler(date=datetime.now(), driver=self.driver, on_items_complete=None, skip_crawled_date=False, on_page_crawled=self.on_page_crawled)
        crawler.load_page()
        self.should_continue_crawling = True

        while self.should_continue_crawling:
            crawler.parse_article_in_page()
            crawler.move_to_next_page()

    def on_page_crawled(self, link_data_list):
        self.should_continue_crawling = not self.reached_last_article(link_data_list)

    def reached_last_article(self, new_data_list: List[NaverNewsLinkModel]):
        """
        마지막으로 받아온 뉴스를 만났는지 확인함.
        :return:
        """

        # 이전 데이터가 없을경우, 최초 실행일 경우
        if self.last_news_link_data is None:
            self.last_news_link_data = new_data_list[0]
            return True

        is_reached = False
        index = 0
        for n in new_data_list:
            if n.article_url == self.last_news_link_data.article_url:
                self.last_news_link_data = new_data_list[0]
                is_reached = True
                break
            index += 1
        # Add items

        none_added_items = list(new_data_list[:index+1])
        none_added_items.reverse()
        for none_added_item in none_added_items:
            self.add_to_queue(none_added_item)

        return is_reached

    def add_to_queue(self, link_data_item):
        for i in self.conflict_check_list:
            if i.article_url == link_data_item.article_url:
                return

        self.conflict_check_list.append(link_data_item)
        latest_news_links_data_list.append(link_data_item)
        print(link_data_item)

        while len(self.conflict_check_list) > MAX_QUEUE:
            self.conflict_check_list.pop(0)



# ThreadPool?
# or single thread
class LiveNewsContentCrawler(Thread):
    def __init__(self):
        super().__init__()
        self.threads_count = 4
        ...

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
        print("data", data)
        self.send_to_server(data)

    def crawl_single_article(self, link_data, callback):
        NaverNewsSingleArticleContentCrawler(link_data, callback).parse_single_article_with_callback()

    def send_to_server(self, data):
        post_crawled_news(data)


def main():
    LiveNewsLinkCrawler().start()
    LiveNewsContentCrawler().start()


if __name__ == '__main__':
    # main()
    main()
