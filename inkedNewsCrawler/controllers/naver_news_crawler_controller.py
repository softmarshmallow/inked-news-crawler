from pydispatch import dispatcher
from scrapy import signals
from scrapy.crawler import CrawlerProcess

from inkedNewsCrawler.spiders.NaverNewsCrawler import NavernewscrawlerSpider

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


def crawler_results(r):
    raise Exception(r)


dispatcher.connect(crawler_results, signal=signals.item_passed)
process.crawl(NavernewscrawlerSpider, a=9)
process.start() # the script will block here until the crawling is finished
