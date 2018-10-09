from threading import Thread
import time
import random
from datetime import datetime

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_link_crawler_threaded import NaverDateNewsLinkCrawler


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
CRAWLER_REFRESH_RATE = 0.2


latest_news_links_data_list = []
latest_news_content_list = []


class LiveNewsLinkCrawler(Thread):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()
        self.refresh_count = 0

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

        ...



class LiveNewsContentCrawler(Thread):
    def __init__(self):
        super().__init__()
        ...

    def run(self):
        ...






def main():
    pass


def test():
    LiveNewsLinkCrawler().start()


if __name__ == '__main__':
    # main()
    test()
