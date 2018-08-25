from datetime import datetime

from dateutil.rrule import rrule, DAILY

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import read_links_from_file


providers = []

i = 0
for date in rrule(DAILY, dtstart=datetime(1990, 1, 1), until=datetime(2018, 8, 1)):
    links = read_links_from_file(date)
    for link_data in links:
        print(link_data.aid, link_data.time, link_data.title, link_data.provider)
        i += 1
        if link_data.provider not in providers:
            providers.append(link_data.provider)

        if i % 1000 == 0:
            print(providers)


print(providers)