from dateutil.rrule import DAILY, rrule
import sys
from inkedNewsCrawler.custom_crawler.naver_news_crawler.models import NaverNewsContentModel
from inkedNewsCrawler.custom_crawler.naver_news_crawler.naver_news_crawl_helper import IOManager
from datetime import datetime
import warnings
from inkedNewsCrawler.services.vps_news_service import post_crawled_news_batch, post_crawled_news
from inkedNewsCrawler.filters.lang_filter import accept_languages
import numpy as np

iom = IOManager()

if __name__ == "__main__":
    start_date = datetime(2016, 6, 21)
    end_date = datetime(2018, 1, 1)
    dates = rrule(DAILY, dtstart=start_date, until=end_date)
    for date in dates:
            print(date)
            data = iom.read_raw_contents_from_file(date=date)
            model_list = []
            i = 0
            for r in data:
                i += 1
                try:
                    filter_lang = accept_languages(['ko'], r['title'])
                    if filter_lang:
                        model = NaverNewsContentModel(**r).serialize()
                        model_list.append(model)
                except Exception as e:
                    # warnings.warn(str(e))
                    ...
                sys.stdout.write(f"\rreading data... {i} of {len(data)}")
                sys.stdout.flush()

            # split posting since data payload is too large
            for data_arr in np.array_split(model_list, 10):
                list = data_arr.tolist()
                res, m = post_crawled_news_batch(list)
                sys.stdout.write(f"\rposted data... {len(list)} of {len(data)}")
                sys.stdout.flush()
                if not res:
                    warnings.warn(str(m))
