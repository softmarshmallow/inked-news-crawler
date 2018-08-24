import json
from datetime import datetime

import os
from typing import List
from urllib.parse import urlparse, parse_qs
import re

from inkedNewsCrawler.settings import DATA_ROOT


class NaverNewsLinkModel:
    def __init__(self, aid, date, provider, full_content_link):
        self.aid = aid
        self.date = date
        self.provider = provider
        self.full_content_link = full_content_link

    def __str__(self):
        return self.date.strftime("%Y.%m.%d") + "//" + self.aid + "//" + self.full_content_link


def get_date_str(date: datetime):
    return date.strftime("%Y%m%d")


# aid stands for <<Article ID>>
def extract_aid(link:str)->str:
    query_string = urlparse(link).query
    try:
        aid = parse_qs(query_string)['aid'][0]
    except KeyError:
        print("Key Error", link)
        return None
    return aid


def naver_article_url_builder(aid:str, mode="print")->str:
    if mode == "full_content":
        return "https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=001&oid=032&aid=" + aid
    elif mode == "print":
        return "https://news.naver.com/main/tool/print.nhn?oid=032&aid=" + aid
    raise Exception


def get_link_file_path(date: datetime) -> str:
    date_str = get_date_str(date)
    file_name = os.path.join(DATA_ROOT, 'naver_news_link_data/naver_date_article_links_%s.json' % date_str)
    return file_name


def write_links_to_file(date: datetime, links: [{str, str}]):
    file_name = get_link_file_path(date)
    with open(file_name, 'w') as outfile:
        json.dump(links, outfile)


def read_links_from_file(date: datetime) -> List[NaverNewsLinkModel]:
    links = []
    file_name = get_link_file_path(date)
    with open(file_name) as f:
        data = json.load(f)
        for record in data:
            full_content_link = record["link"]
            provider = record["provider"]
            aid = extract_aid(full_content_link)
            link_data = NaverNewsLinkModel(aid=aid, date=date, provider=provider, full_content_link=full_content_link)
            links.append(link_data)
    return links


def check_if_file_is_exists(file: str):
    if os.path.isfile(file):
        return True
    else:
        return False


# False = "file is crawled" // True = "file is empty"
def check_if_file_is_empty(file: str, mode="full") -> bool:
    if check_if_file_is_exists(file):
        # File exists
        if mode == "light":
            return False
        elif mode == "full":
            with open(file) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("FILE CONTAINS Invalid content", file)
                    return True
                if len(data) == 0:
                    # is an empty file
                    print("File IS EMPTY", file)
                    return True
            # file exists and full with content
            # print("File IS READY with:", len(data), "records ",  file)
            return False
    else:
        # No file
        return True


def get_articles_count_at_date(date: datetime):
    file = get_link_file_path(date)
    if check_if_file_is_exists(file):
        with open(file) as f:
            try:
                return len(json.load(f))
            except json.JSONDecodeError:
                return 0
    return 0


def check_if_links_empty(date:datetime, mode="full") -> bool:
    fileName = get_link_file_path(date)
    return check_if_file_is_empty(fileName, mode=mode)

# region LEGACY
def get_content_file_path(date: datetime) -> str:
    date_str = get_date_str(date)
    file_name = os.path.join(DATA_ROOT, 'naver_news_content_data/naver_date_article_contents_%s.json' % date_str)
    return file_name


def write_contents_to_file(date: datetime, contents: []):
    file_name = get_content_file_path(date)
    with open(file_name, 'w') as outfile:
        json.dump(contents, outfile)


def read_contents_from_file(date: datetime) -> []:
    contents = []
    file_name = get_link_file_path(date)
    with open(file_name) as f:
        data = json.load(f)
        for record in data:
            # Record to instance
            contents.append(record)
    return contents


def check_if_content_empty(date:datetime) -> bool:
    file_name = get_content_file_path(date)
    return check_if_file_is_empty(file_name)
# endregion


if __name__ == "__main__":
    date = datetime(2000, 1, 1)
    experiment_date = datetime(2020, 1, 2)
    experiment_date_x = datetime(2030, 1, 2)

    write_links_to_file(
        experiment_date,
        links=[{"link": "http://google.com/", "provider": "null"}, {"link": "http://google.com/", "provider": "null"}, {"link": "http://google.com/", "provider": "null"}]
    )

    print(check_if_content_empty(experiment_date_x))
