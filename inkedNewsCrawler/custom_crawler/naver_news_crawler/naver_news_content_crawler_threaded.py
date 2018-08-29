import json
from datetime import datetime
from multiprocessing.pool import ThreadPool
import atexit
import requests
from dateutil.rrule import rrule, DAILY
from parsel import Selector

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import detect_url_type, IOManager
from inkedNewsCrawler.utils.sanitize_html import remove_unused_tags_html
import arrow

exceptions = []


class NaverNewsContentCrawler:
    def __init__(self, date, callback, check_if_crawled=True, from_s3=True):
        self.date = date
        self.callback = callback
        self.check_if_crawled = check_if_crawled
        self.content_data_list = []
        self.iom = IOManager(from_s3=from_s3)

    def main(self):
        link_data_list = self.iom.read_links_from_file(self.date)
        total_links_count = len(link_data_list)
        print("START Content Crawling", self.date, total_links_count)
        i = 0
        for link_data in link_data_list:
            i += 1
            self.parse_single_article(link_data)
            if i % 100 == 0:
                print(self.date, i, datetime.now())

        self.callback(self.date, self.content_data_list)
        return self.content_data_list

    def parse_single_article(self, link_data):

        r = requests.get(url=link_data.full_content_link)
        selector = Selector(text=r.text)
        content_data = NaverArticleContentParser(link_data=link_data, redirect_url=r.url, selector=selector).parse()
        # print(content_data)
        self.content_data_list.append(content_data)


def translate_time(time_str:str):
    time_str = time_str.replace("오전", "AM")
    time_str = time_str.replace("오후", "PM")
    return time_str



class NaverArticleContentParser:
    def __init__(self, selector: Selector, link_data, redirect_url):
        self.selector = selector
        self.link_data = link_data
        self.redirect_url = redirect_url
        self.url_type = detect_url_type(redirect_url)

    def parse(self):
        try:
            if self.url_type == "default":
                data = self.parse_from_full_content_url(response=self.selector)
            elif self.url_type == "entertain":
                data = self.parse_from_entertainment_url(response=self.selector)
            elif self.url_type == "sports":
                data = self.parse_from_sports_url(response=self.selector)
            else:
                raise Exception

            # item = NaverNewsContentItem()
            item = {}
            item["article_id"] = self.link_data.aid
            item["article_url"] = self.link_data.full_content_link
            item["redirect_url"] = self.redirect_url
            item["origin_url"] = data[3]
            item["title"] = data[0]
            item["body_html"] = data[1]
            # item["time"] = data[2].strftime("%Y-%m-%d %H:%M:%S")
            item["time"] = self.link_data.time
            item["provider"] = self.link_data.provider
            return item
        except Exception as e:
            print("ERR", self.link_data, e)


    @DeprecationWarning
    def parse_from_print_content_url(self, response):
        # FIXME DO NOT USE
        title = response.xpath("//h3[@class='font1']/text()").extract_first()
        body = response.xpath("//div[@class='article_body']/text()").extract_first()
        body_html = response.xpath("//div[@class='article_body']").extract_first()
        time = response.xpath("//span[@class='t11']/text()").extract_first()
        # press_img_html = response.xpath("//a[@class='press_logo']/img").extract_first()

    def parse_from_full_content_url(self, response):
        title = response.xpath('//*[@id="articleTitle"]/text()').extract_first()
        body_html = response.xpath('//*[@id="articleBodyContents"]').extract_first()
        body_html = remove_unused_tags_html(body_html)
        origin_url = response.xpath('''//*[@id="main_content"]//div[@class="article_info"]//div[@class="sponsor"]/a[@class="btn_artialoriginal nclicks(are.ori,'214', 'nilGParam', '214_57772f5131149491')"]/@href''').extract_first()
        # 2018-03-04 23:58
        raw_time = response.xpath('//*[@id="main_content"]//div[@class="article_info"]//span[@class="t11"]/text()').extract_first()
        time = arrow.get(raw_time, 'YYYY-MM-DD HH:mm').datetime

        return title, body_html, time, origin_url

    def parse_from_entertainment_url(self, response):

        title = response.xpath('//*[@id="content"]//h2[@class="end_tit"]/text()').extract_first()
        body_html = response.xpath('//*[@id="articeBody"]').extract_first()
        body_html = remove_unused_tags_html(body_html)
        origin_url = response.xpath('//*[@id="content"]//div[@class="article_info"]/a[@alt="기사원문"]/@href').extract_first()

        # 2018.08.23 오후 5:04 == > 2016.01.01 10:25
        raw_time = response.xpath('//*[@id="content"]//div[@class="article_info"]/span[@class="author"]/em/text()').extract_first()
        raw_time = translate_time(raw_time)
        time = arrow.get(raw_time, 'YYYY.MM.DD A h:mm').datetime

        return title, body_html, time, origin_url

    def parse_from_sports_url(self, response):
        title = response.xpath('//*[@id="content"]//div[@class="news_headline"]//h4/text()').extract_first()
        body_html = response.xpath('//*[@id="newsEndContents"]').extract_first()
        body_html = remove_unused_tags_html(body_html)
        origin_url = response.xpath('//*[@id="content"]//div[@class="info"]/a[@class="press_link"]/@href').extract_first()

        #  기사입력 2018.08.23 오후 06:36 == > 2016.01.01 10:25
        raw_time = response.xpath('//*[@id="content"]//div[@class="news_headline"]/div[@class="info"]/span[1]/text()').extract_first()
        raw_time = translate_time(raw_time)
        time = arrow.get(raw_time, '기사입력 YYYY.MM.DD A h:mm').datetime

        return title, body_html, time, origin_url






def save_to_file(date, contents, from_s3=True):
    iom = IOManager(from_s3=from_s3)
    iom.write_contents_to_file(date=date, contents=contents)


def start_crawl(date):
    NaverNewsContentCrawler(date=date, callback=save_to_file).main()


def crawl_all_content(THREAD_COUNT, start_date, end_date):

    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    pool = ThreadPool(THREAD_COUNT)
    pool.map(start_crawl, dates)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()


if __name__ == "__main__":
    def exit_handler():
        from inkedNewsCrawler.utils.email_notification import send_email
        exception_str = json.dumps(exceptions)
        send_email("Crawling Content Complete Please Check...", extra=exception_str)

    atexit.register(exit_handler)

    THREAD_COUNT = int(input("Thread counts:: "))
    start_date_str = input("start_date (YYYYmmdd) :: ")
    end_date_str = input("end_date (YYYYmmdd) :: ")
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    crawl_all_content(THREAD_COUNT=THREAD_COUNT, start_date=start_date, end_date=end_date)
