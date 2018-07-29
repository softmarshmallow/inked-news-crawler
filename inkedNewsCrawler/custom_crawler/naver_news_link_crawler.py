from datetime import datetime
import json
from dateutil.rrule import DAILY, rrule
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

MAX_PAGES_PER_PAGINATION = 10

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
prefs = {"profile.managed_default_content_settings.images":2}
options.add_experimental_option("prefs",prefs)
options.set_headless(True)



class NaverDateNewsLinkCrawler:
    def __init__(self, date):
        self.date = date
        self.date_str = date.strftime("%Y%m%d")
        self.url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=title&date=%s' % self.date_str
        self.driver = webdriver.Chrome(chrome_options=options)
        self.links = []
        print("Crawl", self.date_str)

    def parse(self):
        self.driver.get(self.url)

        while True:
            self.parse_available_pages()
            try:
                next = self.driver.find_element_by_xpath("//*[@id='main_content']/div[@class='paging']/a[@class='next nclicks(fls.page)']")
            except NoSuchElementException:
                break
            try:
                # NextPage + 10
                # next.click()
                self.driver.execute_script("arguments[0].click();", next)

            except:
                break

        self.driver.quit()
        self.save_to_file()

    def parse_available_pages(self):
        for i in range(0, MAX_PAGES_PER_PAGINATION):
            self.parse_article_in_page()
            # region click next available page in pager
            try:
                pages = self.driver.find_elements_by_xpath("//*[@id='main_content']/div[@class='paging']/a[@class='nclicks(fls.page)']")
                page = pages[i]
                self.driver.execute_script("arguments[0].click();", page)
                # page.click()
            except IndexError:
                return
            # endregion

    def parse_article_in_page(self):
        articles = self.driver.find_elements_by_xpath("//*[@id='main_content']/div[@class='list_body newsflash_body']//a[@class='nclicks(fls.list)']")

        for article in articles:
            href = article.get_attribute('href')
            provider = article.find_element_by_xpath("../span[@class='writing']").text
            data = {"link": href, "provider": provider}
            self.links.append(data)

    def save_to_file(self):
        with open('data/naver_date_article_links_%s.json'% self.date_str, 'w') as outfile:
            json.dump(self.links, outfile)



def crawl_all_links():
    # start urls
    start_date = datetime(1990, 1, 1)
    end_date = datetime(2018, 7, 1)

    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        NaverDateNewsLinkCrawler(dt).parse()


if __name__ == "__main__":
    crawl_all_links()

