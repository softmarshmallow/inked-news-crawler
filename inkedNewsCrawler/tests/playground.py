from datetime import datetime

from inkedNewsCrawler.custom_crawler.naver_news_link_crawler.naver_news_link_crawl_helper import \
    read_links_from_file

from inkedNewsCrawler.utils.naver_news_content_helper import ContentCrawlChecker

c = ContentCrawlChecker()

a = c.check_article_crawled("0000004474")
print(a)
