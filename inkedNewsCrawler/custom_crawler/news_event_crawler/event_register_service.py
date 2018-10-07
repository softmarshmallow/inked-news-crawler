from datetime import datetime

import requests

from inkedNewsCrawler.custom_crawler.news_event_crawler.event_model import StockCalendarEventModel

'''
크롤링한 데이터를 서버로 전송하는 코드.
'''

BASE_SERVER_URL = "http://nginx-lb-429321543.ap-northeast-2.elb.amazonaws.com/"
request_url = BASE_SERVER_URL + "api/stock_events/"



def register_calendar_event_to_server(stockCalendarEventData: StockCalendarEventModel, isTest=True):
    payload = \
        {
            'event_name': stockCalendarEventData.eventName,
            'event_content': stockCalendarEventData.eventContent,
            'event_time': stockCalendarEventData.get_formatted_event_time(),
            'links': stockCalendarEventData.links,
            'extra_fields': stockCalendarEventData.extraFields
        }

    # print(request_url)
    if not isTest:
        result = requests.post(request_url, json=payload)
        print(result.text)
    else:
        print("TestMode: skip server connection")
        print(stockCalendarEventData)


if __name__ == '__main__':

    test_data = StockCalendarEventModel()
    test_data.eventTime = datetime(2018, 12, 25)
    test_data.eventName = "크리스마스"
    test_data.eventContent = "행복한 크리스마스 입니당~"
    test_data.links = ["http://christmas.com/",]
    test_data.extraFields = {"isTest": True}

    register_calendar_event_to_server(test_data)
