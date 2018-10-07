import calendar
from typing import List

import requests
from lxml import html
from lxml.etree import tostring
from datetime import date, datetime
import time
from urllib.parse import urljoin
from dateutil.rrule import rrule, DAILY, MONTHLY

from inkedNewsCrawler.custom_crawler.news_event_crawler.event_model import StockCalendarEventModel
from inkedNewsCrawler.custom_crawler.news_event_crawler.event_register_service import \
    register_calendar_event_to_server

BASE_URL = "http://everystocks.com/"

def build_url(year, month):
    url = BASE_URL + "index.php?mid=calendar&pYear=%s&pMonth=%s" % (
        str(year), str(month))
    return url




def main():
    all_data_list = get_all_events()
    for event_data in all_data_list:
        register_calendar_event_to_server(event_data)
    # 1. Get all calendar events
    # 2. Loop each events, send to server


def get_all_events() -> List[StockCalendarEventModel]:
    all_event_data_list = []

    start_date = datetime(2017, 8, 1)
    # end_date = datetime(2020, 1, 1)
    end_date = datetime(2018, 1, 1)
    months = rrule(MONTHLY, dtstart=start_date, until=end_date)
    for month in months:
        print(month)
        month_events = parse_month(month.year, month.month)
        all_event_data_list.extend(month_events)

    return all_event_data_list



def request_with_retries(url):
    try:
        return requests.get(url)
    except Exception:
        print("OVERHEAD:: sleep")
        time.sleep(0.5)
        return request_with_retries(url)

def parse_month(year, month) -> List[StockCalendarEventModel]:
    eventDataList = []
    url = build_url(year, month)
    r = request_with_retries(url)
    tree = html.fromstring(r.text)

    month_range = calendar.monthrange(year, month)
    for day in range(1, month_range[1] + 1):

        xpath = "//div[@id='day_schedule_container_{}-{}-{}']".format(year, month, day)
        date_events_root = tree.xpath(xpath)[0]

        event_items = date_events_root.xpath("//div[@class='drag']")
        for item in event_items:
            blog_url = item.xpath('./a/@href')[0]
            blog_url = urljoin(BASE_URL, blog_url)
            content = parse_blog_content(blog_url)
            print("blog_url", blog_url)
            print("content", content)
            print("\n")
            # region Create model
            data = StockCalendarEventModel()
            data.eventName = item.text_content()
            data.eventContent = content
            data.eventTime = datetime(year, month, day)
            data.links = [blog_url]
            data.extraFields = {"source": "everystocks.com", "version": "0.0.1", "production": True}
            # endregion
            eventDataList.append(data)

    return eventDataList


def parse_blog_content(blog_url) -> str:
    # EX. http://everystocks.com/index.php?mid=calendar&pYear=2017&pMonth=8&document_srl=731

    r = request_with_retries(blog_url)
    tree = html.fromstring(r.text)

    # remove unused element
    remove_target = tree.xpath('//div[@class="document_popup_menu"]')[0]
    remove_target.getparent().remove(remove_target)

    p = tree.xpath('//*[@id="content"]/div/div[3]/div/div[2]/div')[0]
    content = p.text_content()
    return content


if __name__ == '__main__':
    main()
