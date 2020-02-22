import calendar
import json
from multiprocessing.pool import ThreadPool
from itertools import repeat
from typing import List, Callable
import atexit
import requests
from lxml import html
from lxml.etree import tostring
from datetime import date, datetime
import time
from urllib.parse import urljoin
from dateutil.rrule import rrule, DAILY, MONTHLY

from inkedNewsCrawler.custom_crawler.news_event_crawler.event_model import StockCalendarEventModel
from inkedNewsCrawler.services.vps_stock_calendar_event_service import \
    register_calendar_event_to_server

BASE_URL = "http://everystocks.com/"


def build_url(year, month):
    url = BASE_URL + "index.php?mid=calendar&pYear=%s&pMonth=%s" % (
        str(year), str(month))
    return url


def main(start_date, end_date):
    def exit_handler():
        from inkedNewsCrawler.utils.email_notification import send_email
        # exception_str = json.dumps(exceptions)
        send_email("Event Crawling Complete Please Check...", extra="")

    atexit.register(exit_handler)
    # Add process listener


    # 1. Get all calendar events
    # 2. Loop each events, send to server
    months = rrule(MONTHLY, dtstart=start_date, until=end_date)
    for month in months:
        print(month)
        MonthEventsCrawler(year=month.year, month=month.month, callback=onCrawlComplete).crawl()




def onCrawlComplete(data_list):
    total = len(data_list)
    index = 0
    for event_data in data_list:
        print("Current: ", index, "  Total: ", total)
        register_calendar_event_to_server(event_data, isTest=False)
        time.sleep(0.1)
        index += 1


def request_with_retries(url):
    try:
        return requests.get(url)
    except Exception:
        print("OVERHEAD:: sleep")
        time.sleep(0.5)
        return request_with_retries(url)


class MonthEventsCrawler:
    def __init__(self, year, month, callback: Callable):
        self.year = year
        self.month = month
        self.url = build_url(year, month)
        self.eventDataList = []
        self.callback = callback

    def crawl(self):
        self.parse_month_events()
        self.callback(self.eventDataList)

    def parse_month_events(self):

        r = request_with_retries(self.url)
        tree = html.fromstring(r.text)

        month_range = calendar.monthrange(self.year, self.month)
        index = 0
        day_count_in_month = month_range[1]
        for day in range(1, day_count_in_month + 1):
            # FIXME Issue, 첫번째 달은 문제없음, 두번째 달의 펑션 콜일경우 하단에 IndexError 발생함..  클래스 모듈화를 한다면 없엘수 있을수도.
            # 어떤 변수가 공유되면서 발생하는 문제인것같음. 또는 쓰래드 공유시 발생한느 문제로 짐작중..
            xpath = "//div[@id='day_schedule_container_{}-{}-{}']".format(self.year, self.month, day)
            try:
                date_events_root = tree.xpath(xpath)[0]

                event_items = date_events_root.xpath("//div[@class='drag']")
                thread_count = len(event_items) if len(event_items) > 0 else 1
                pool = ThreadPool(thread_count)
                result = pool.starmap(parse_single_event,
                                      zip(event_items, repeat(datetime(self.year, self.month, day))))
                self.eventDataList.extend(result)
                # close the pool and wait for the work to finish
                pool.close()
                pool.join()
                index += 1
            except IndexError as e:
                print(tostring(tree))
                print(e)






def parse_single_event(event_item_node: html.HtmlElement, datetime):
    blog_url = event_item_node.xpath('./a/@href')[0]
    blog_url = urljoin(BASE_URL, blog_url)
    event_name = event_item_node.text_content()
    content = parse_blog_content(blog_url)
    event_date = datetime
    print("event_name", event_name)
    print("blog_url", blog_url)
    print("event_date", event_date)
    # print("content", content)
    print("\n")
    # region Create model
    data = StockCalendarEventModel()
    data.eventName = event_name
    data.eventContent = content
    data.eventTime = event_date
    data.links = [blog_url]
    data.extraFields = {"source": "everystocks.com", "version": "0.0.1", "production": True}
    # endregion
    return data


def parse_blog_content(blog_url) -> str:
    # EX. http://everystocks.com/index.php?mid=calendar&pYear=2017&pMonth=8&document_srl=731
    content = ""
    r = request_with_retries(blog_url)
    tree = html.fromstring(r.text)

    # remove unused element
    try:
        remove_target = tree.xpath('//div[@class="document_popup_menu"]')[0]
        remove_target.getparent().remove(remove_target)
    except IndexError:
        print("NO POPUP MENU, SKIP")
        ...
    try:
        p = tree.xpath('//*[@id="content"]/div/div[3]/div/div[2]/div')[0]
        content = str(p.text_content())
    except IndexError:
        print("NO CONTENT", blog_url)

    return content


if __name__ == '__main__':
    # start_date = datetime(2017, 8, 1)
    # # end_date = datetime(2020, 1, 1)
    # end_date = datetime(2019, 1, 1)
    print("AVAILABLE DATE RANGE: 2017.8. ~ 2019.2")
    start_date_str = input("start_date (YYYYmm) :: ")
    end_date_str = input("end_date (YYYYmm) :: ")

    start_date = datetime.strptime(start_date_str, '%Y%m')
    end_date = datetime.strptime(end_date_str, '%Y%m')
    main(start_date, end_date)
