from datetime import datetime

from inkedNewsCrawler.custom_crawler.naver_crawl_helper import read_links_from_file



r = read_links_from_file(date=datetime(3000, 1, 1))

print(r)
