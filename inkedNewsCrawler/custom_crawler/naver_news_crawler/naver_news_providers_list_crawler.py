import time
from selenium import webdriver
from lxml import html

from inkedNewsCrawler.utils.web_drivers import get_chrome_options



def get_naver_press_list():
    url = "https://news.naver.com/"

    driver = webdriver.Chrome(chrome_options=get_chrome_options())
    driver.get(url)

    # Click load press
    btn = driver.find_element_by_xpath('//*[@id="index.press.btn"]')
    btn.click()
    time.sleep(1)

    html_source = driver.page_source
    driver.quit()


    tree = html.fromstring(html_source)
    providers = tree.xpath('//*[@id="index.press.area"]//li/a/text()')
    return providers



if __name__ == "__main__":
    press_l = get_naver_press_list()
    print(press_l)