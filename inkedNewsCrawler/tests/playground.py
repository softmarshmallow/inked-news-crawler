from datetime import datetime

from selenium.webdriver import Chrome

from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_link_crawler_threaded import \
    NaverDateNewsLinkCrawler

from inkedNewsCrawler.utils.web_drivers import get_chrome_options
chrome_options = get_chrome_options()
driver = Chrome(chrome_options=chrome_options)



def callback(a):
    ...


maxPerPage = 50

def main():
    crawler = NaverDateNewsLinkCrawler(date=datetime(2018, 1, 1), driver=driver, callback=callback, skip_crawled_date=False)
    crawler.load_page()

    for i in range(20):
        crawler.parse_article_in_page()
        crawler.move_to_next_page()
        max = maxPerPage*(i+1)
        print(crawler.link_data_list[max - 50:max])



if __name__ == "__main__":
    main()