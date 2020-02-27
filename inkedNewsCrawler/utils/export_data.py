import json
from datetime import datetime

from dateutil.rrule import rrule, DAILY

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import IOManager

start_date = datetime(2015, 1, 1)
end_date = datetime(2018, 8, 1)
iom = IOManager(from_s3=False)
# Export data as plain text


def export_data():
    all_title_list = []
    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    for date in dates:
        print(date)
        data_list = iom.read_links_from_file(date)
        for data in data_list:
            all_title_list.extend(data.title)

    json.dump(all_title_list, "export.json", ensure_ascii=False)


if __name__ == "__main__":
    export_data()
