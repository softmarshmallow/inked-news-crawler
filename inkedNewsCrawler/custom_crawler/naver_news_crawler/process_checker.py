from datetime import datetime
from typing import List

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import check_if_links_empty, check_if_file_is_exists, get_articles_count_at_date, get_content_file_path, check_if_content_empty
from inkedNewsCrawler.utils.date_input_manager import get_date_input

START_DATE = datetime(2013, 10, 1)
END_DATE = datetime(2018, 8, 1)


def get_total_links_count():
    total = 0
    for date in rrule(DAILY, dtstart=START_DATE, until=END_DATE):
        count = get_articles_count_at_date(date)
        total += count
        print(date, count, total)
    return total


def get_date_range(read_input=True, by_month=False) -> List[List]:
    # start urls
    if read_input:
        start_date = get_date_input("start date")
        end_date = get_date_input("end date")
    else:
        start_date = START_DATE
        end_date = END_DATE

    if by_month:
        months_and_dates = [] # [[1, 2, 3, ... 31], [1, 2, 3, ... 30], [1, 2, 3,  ... 30]]
        #  PER month // TODO
        months = rrule(MONTHLY, dtstart=start_date, until=end_date)

        for month in months:
            # print("MONTH: ", month)
            next_month = month + relativedelta(months=+1, days=-1)
            days_in_month = rrule(DAILY, dtstart=month, until=next_month)
            days = []
            for day_in_month in days_in_month:
                if day_in_month > end_date:
                    break
                days.append(day_in_month)
                # print("Day in month :", day_in_month)
            months_and_dates.append(days)
        #

        return months_and_dates

    else:
        dates = rrule(DAILY, dtstart=start_date, until=end_date)
        return [dates]

def check_link_crawl_process(mode="light", from_s3=False):
    month_dates_group = get_date_range(read_input=False, by_month=True)
    for month_dates in month_dates_group:
        completed_in_month = 0
        non_crawled_dates = []
        days_in_month = len(month_dates)
        for day in month_dates:

            if not check_if_links_empty(day, mode=mode):
                completed_in_month += 1
            else:
                non_crawled_dates.append(day)

        which_month = month_dates[0].strftime("%Y.%m")
        print(which_month, completed_in_month, days_in_month, "Complete:", (completed_in_month==days_in_month), non_crawled_dates[:5])


def check_crawl_process(mode="light", type="link", from_s3=False):

    month_dates_group = get_date_range(read_input=False, by_month=True)
    for month_dates in month_dates_group:
        completed_in_month = 0
        non_crawled_dates = []
        days_in_month = len(month_dates)
        for day in month_dates:
            is_empty = False
            if type == "link":
                is_empty = check_if_links_empty(day, mode=mode, from_s3=from_s3)
            elif type == "content":
                is_empty = check_if_content_empty(date=day, from_s3=from_s3)

            if not is_empty:
                completed_in_month += 1
            else:
                non_crawled_dates.append(day)

        which_month = month_dates[0].strftime("%Y.%m")
        print(type, which_month, completed_in_month, days_in_month, "Complete:", (completed_in_month==days_in_month), non_crawled_dates[:5])

if __name__ == "__main__":
    if input("Read Total Links Count? (Y/N)") in ["y", "Y"]:
        print("Total Links Count ::",  get_total_links_count())

    mode = input("enter mode : ( light / full )")
    type = input("enter type : ( link / content )")
    check_crawl_process(type=type, mode=mode, from_s3=True)
