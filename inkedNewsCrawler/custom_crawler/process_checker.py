from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY

from ..custom_crawler.naver_crawl_helper import check_if_links_empty
from ..utils.date_input_manager import get_date_input


def get_date_range(read_input=True, by_month = False):
    # start urls

    if read_input:
        start_date = get_date_input("start date")
        end_date = get_date_input("end date")
    else:
        # For debug purpose
        start_date = datetime(1990, 1, 1)
        end_date = datetime(2020, 1, 1)

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

def check_link_crawl_process():
    month_dates_group = get_date_range(read_input=False, by_month=True)
    for month_dates in month_dates_group:
        completed_in_month = 0
        days_in_month = len(month_dates)
        for day in month_dates:
            if not check_if_links_empty(day):
                completed_in_month += 1

        which_month = month_dates[0].strftime("%Y.%m")
        print(which_month, completed_in_month, days_in_month)


if __name__ == "__main__":
    check_link_crawl_process()