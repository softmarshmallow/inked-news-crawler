import calendar
import requests
from lxml import html
from lxml.etree import tostring
from _datetime import date, datetime
from dateutil.rrule import rrule, DAILY

base_url = ""


def build_url(year, month):
    url = "http://everystocks.com/index.php?mid=calendar&pYear=%s&pMonth=%s" % (
    str(year), str(month))
    return url


def main():
    parse_month(2018, 1)


def parse_month(year, month):
    r = requests.request("get", url=build_url(year, month))
    tree = html.fromstring(r.text)

    month_range = calendar.monthrange(year, month)
    for d in range(1, month_range[1]+1):

        xpath = "//div[@id='day_schedule_container_{}-{}-{}']".format(year, month, d)
        date_events_root = tree.xpath(xpath)[0]

        items = date_events_root.xpath("//div[@class='drag']")
        for item in items:
            print(item.text_content())

#             Create model



if __name__ == '__main__':
    main()
