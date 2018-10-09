from threading import Thread
import time
from datetime import datetime




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
CRAWLER_REFRESH_RATE = 0.5


latest_news_links_data_list = []
latest_news_content_list = []


class LiveNewsLinkCrawler(Thread):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()

    def run(self):
        while True:
            ...



class LiveNewsContentCrawler(Thread):
    def __init__(self):
        super().__init__()
        ...

    def run(self):
        ...






def main():
    pass


if __name__ == '__main__':
    main()