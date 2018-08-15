import json
from datetime import datetime

import os
from urllib.parse import urlparse, parse_qs
import re

from settings import DATA_ROOT


def get_date_str(date: datetime):
    return date.strftime("%Y%m%d")


def extract_aid(link:str)->str:
    query_string = urlparse(link).query
    aid = parse_qs(query_string)['aid'][0]
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


def read_links_from_file(date) -> []:
    links = []
    file_name = get_link_file_path(date)
    with open(file_name) as f:
        data = json.load(f)
        for record in data:
            link = record["link"]
            aid = extract_aid(link)
            new_link = naver_article_url_builder(aid, "print")
            links.append(new_link)
    return links


def check_if_file_is_empty(file:str) -> bool:
    if os.path.isfile(file):
        # File exists
        with open(file) as f:
            data = json.load(f)
            if len(data) == 0:
                # is an empty file
                # print("File IS EMPTY", file)
                return True
        # file exists and full with content
        # print("File IS READY with:", len(data), "records ",  file)
        return False
    else:
        # No file
        return True


def check_if_links_empty(date:datetime) -> bool:
    fileName = get_link_file_path(date)
    return check_if_file_is_empty(fileName)


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



if __name__ == "__main__":
    date = datetime(2000, 1, 1)
    experiment_date = datetime(2020, 1, 2)
    experiment_date_x = datetime(2030, 1, 2)

    write_links_to_file(
        experiment_date,
        links=[{"link": "http://google.com/", "provider": "null"}, {"link": "http://google.com/", "provider": "null"}, {"link": "http://google.com/", "provider": "null"}]
    )

    print(check_if_content_empty(experiment_date_x))
