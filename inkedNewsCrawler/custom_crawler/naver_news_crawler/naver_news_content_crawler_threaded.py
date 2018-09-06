import json
from datetime import datetime
from multiprocessing.pool import ThreadPool
import atexit
import requests
from dateutil.rrule import rrule, DAILY
from parsel import Selector
from itertools import repeat

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import \
    detect_url_type, IOManager, check_if_file_is_empty, get_content_file_path
from inkedNewsCrawler.utils.random_proxy import get_random_proxy_for_requests
from inkedNewsCrawler.utils.sanitize_html import remove_unused_tags_html
import arrow

exceptions = []


class NaverNewsSingleArticleContentCrawler:
    def __init__(self, link_data, callback=None):
        self.link_data = link_data
        self.callback = callback

    def main(self):
        data = self.parse_single_article()
        if self.callback is not None:
            self.callback(data)
        return data

    def parse_single_article(self):
        proxies = get_random_proxy_for_requests()
        r = requests.get(url=self.link_data.full_content_link, proxies=proxies)
        selector = Selector(text=r.text)
        content_data = NaverArticleContentParser(link_data=self.link_data, redirect_url=r.url,
                                                 selector=selector).parse()
        return content_data
        # print(content_data)


class NaverNewsContentCrawler:
    def __init__(self, date, callback, check_if_crawled=True, from_s3=True,
                 thread_for_each_request=True, threads_count=1024):
        self.date = date
        self.from_s3 = from_s3
        self.callback = callback
        self.check_if_crawled = check_if_crawled
        self.content_data_list = []
        self.thread_for_each_request = thread_for_each_request
        self.iom = IOManager(from_s3=from_s3)
        self.crawled_count = 0
        self.total_links_count = 0
        self.threads_count = threads_count

    def main(self):
        if self.check_if_crawled:
            file_path = get_content_file_path(date=self.date, from_s3=self.from_s3)
            empty = check_if_file_is_empty(file_path, from_s3=self.from_s3)
            if not empty:
                print("Already Parsed", file_path)
                return

        link_data_list = self.iom.read_links_from_file(self.date)
        self.total_links_count = len(link_data_list)
        print("START Content Crawling", self.date, self.total_links_count)

        if self.thread_for_each_request:
            i = 0
            print("start thread", self.threads_count)
            pool = ThreadPool(self.threads_count)
            pool.starmap(self.crawl_single_article, zip(link_data_list, repeat(self.log_progress)))
            # close the pool and wait for the work to finish
            pool.close()
            pool.join()
        else:
            i = 0
            for link_data in link_data_list:
                i += 1
                self.crawl_single_article(link_data)
                self.log_progress()

        self.callback(self.date, self.content_data_list)
        return

    def log_progress(self, data=None):
        self.crawled_count += 1
        if self.crawled_count % 100 == 0:
            print(self.date, self.crawled_count, "of", self.total_links_count, datetime.now())

    def crawl_single_article(self, link_data, callback=None):
        content_data = NaverNewsSingleArticleContentCrawler(link_data, callback=callback).main()
        self.content_data_list.append(content_data)


def translate_time(time_str: str):
    time_str = time_str.replace("오전", "AM")
    time_str = time_str.replace("오후", "PM")
    return time_str


class NaverArticleContentParser:
    """
    without requst, it only parses, crawled html.
    """

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
            # print("ERR", self.link_data, e)
            # skipped_urls.append(self.link_data)
            # TODO add skipped support
            ...

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
        origin_url = response.xpath(
            '''//*[@id="main_content"]//div[@class="article_info"]//div[@class="sponsor"]/a[@class="btn_artialoriginal nclicks(are.ori,'214', 'nilGParam', '214_57772f5131149491')"]/@href''').extract_first()
        # 2018-03-04 23:58
        raw_time = response.xpath(
            '//*[@id="main_content"]//div[@class="article_info"]//span[@class="t11"]/text()').extract_first()
        time = arrow.get(raw_time, 'YYYY-MM-DD HH:mm').datetime

        return title, body_html, time, origin_url

    def parse_from_entertainment_url(self, response):

        title = response.xpath('//*[@id="content"]//h2[@class="end_tit"]/text()').extract_first()
        body_html = response.xpath('//*[@id="articeBody"]').extract_first()
        body_html = remove_unused_tags_html(body_html)
        origin_url = response.xpath(
            '//*[@id="content"]//div[@class="article_info"]/a[@alt="기사원문"]/@href').extract_first()

        # 2018.08.23 오후 5:04 == > 2016.01.01 10:25
        raw_time = response.xpath(
            '//*[@id="content"]//div[@class="article_info"]/span[@class="author"]/em/text()').extract_first()
        raw_time = translate_time(raw_time)
        time = arrow.get(raw_time, 'YYYY.MM.DD A h:mm').datetime

        return title, body_html, time, origin_url

    def parse_from_sports_url(self, response):
        title = response.xpath(
            '//*[@id="content"]//div[@class="news_headline"]//h4/text()').extract_first()
        body_html = response.xpath('//*[@id="newsEndContents"]').extract_first()
        body_html = remove_unused_tags_html(body_html)
        origin_url = response.xpath(
            '//*[@id="content"]//div[@class="info"]/a[@class="press_link"]/@href').extract_first()

        #  기사입력 2018.08.23 오후 06:36 == > 2016.01.01 10:25
        raw_time = response.xpath(
            '//*[@id="content"]//div[@class="news_headline"]/div[@class="info"]/span[1]/text()').extract_first()
        raw_time = translate_time(raw_time)
        time = arrow.get(raw_time, '기사입력 YYYY.MM.DD A h:mm').datetime

        return title, body_html, time, origin_url


def save_to_file(date, contents, from_s3=True):
    iom = IOManager(from_s3=from_s3)
    iom.write_contents_to_file(date=date, contents=contents)


def start_crawl(date, threads_count):
    NaverNewsContentCrawler(date=date, check_if_crawled=True, callback=save_to_file,
                            from_s3=True, threads_count=threads_count).main()


def crawl_all_content_NOTHREAD(start_date, end_date, threads_count):
    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    for date in dates:
        start_crawl(date, threads_count)


def crawl_all_content(THREAD_COUNT, start_date, end_date):
    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    pool = ThreadPool(THREAD_COUNT)
    pool.map(start_crawl, dates)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()


def crawl_all_content_with_thread(use_thread=True):
    start_date_str = input("start_date (YYYYmmdd) :: ")
    end_date_str = input("end_date (YYYYmmdd) :: ")
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    if use_thread:
        THREAD_COUNT = int(input("Thread counts:: "))
        crawl_all_content(THREAD_COUNT=THREAD_COUNT, start_date=start_date, end_date=end_date)
    else:
        thread_count_per_date = int(input("Thread counts per dates:: "))
        crawl_all_content_NOTHREAD(start_date=start_date, end_date=end_date, threads_count=thread_count_per_date)

def crawl_all_content_with_thread_by_date():
    target_date_str = input("target date (YYYYmmdd) :: ")

    target_date = datetime.strptime(target_date_str, '%Y%m%d')

    start_crawl(target_date)


if __name__ == "__main__":
    def exit_handler():
        from inkedNewsCrawler.utils.email_notification import send_email
        exception_str = json.dumps(exceptions)
        send_email("Crawling Content Complete Please Check...", extra=exception_str)


    atexit.register(exit_handler)
    # crawl_all_content_with_thread()
    crawl_all_content_with_thread(use_thread=False)
