
import os
from typing import List
from urllib.parse import urlparse, parse_qs
import json
from datetime import datetime
# region s3
import botocore
import boto3.s3
from botocore.exceptions import ClientError

from inkedNewsCrawler.custom_crawler.naver_news_crawler.configs import TIME_FORMAT
from inkedNewsCrawler.custom_crawler.naver_news_crawler.models import NaverNewsContentModel
from inkedNewsCrawler.settings import DATA_ROOT
from inkedNewsCrawler.utils.aws_credentials_reader import read_credentials


cred = read_credentials()
aws_access_key_id = cred[0]
aws_secret_access_key = cred[1]
s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket_name = 'naver-news-crawling-resources'


class NaverNewsLinkModel:
    def __init__(self, publish_time, title, provider, article_url):
        self.aid = extract_aid(article_url)
        self.title = title
        self.publish_time: datetime = publish_time
        self.provider = provider
        self.article_url = article_url

    def __str__(self):
        return str(self.publish_time) + " :: " + self.aid + " :: " + self.article_url + " :: " + self.title

    def to_dictionary(self):
        data = {"link": self.article_url, "title": self.title, "provider": self.provider, "time": self.publish_time.strftime(TIME_FORMAT)}
        return data


def detect_url_type(url):
    if "entertain.naver.com/" in url:
        return "entertain"
    elif "sports.news.naver.com/" in url:
        return "sports"
    elif "news.naver.com/" in url:
        return "default"
    else:
        print("this url belongs nowhere", url)
        raise Exception


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


def get_link_file_path(date: datetime, from_s3=False) -> str:
    date_str = get_date_str(date)
    file_name = 'naver_news_link_data/naver_date_article_links_%s.json' % date_str
    if from_s3:
        return file_name
    else:
        file_name = os.path.join(DATA_ROOT, file_name)
        return file_name


class IOManager:
    def __init__(self, from_s3=False):
        self.from_s3 = from_s3

    # TODO Add S3 Support
    def write_links_to_file(self, date: datetime, links: List[NaverNewsLinkModel]):
        file_name = get_link_file_path(date, from_s3=self.from_s3)

        dict_list = [x.to_dictionary() for x in links]

        if self.from_s3:
            if self.from_s3:
                object = s3.Object(bucket_name, file_name)
                data = json.dumps(dict_list, ensure_ascii=False)
                object.put(Body=data)
        else:
            with open(file_name, 'w', encoding='utf-8') as outfile:
                json.dump(dict_list, outfile, ensure_ascii=False)

    def read_links_from_file(self, date: datetime) -> List[NaverNewsLinkModel]:
        links = []
        file_name = get_link_file_path(date, from_s3=self.from_s3)
        if self.from_s3:
            try:
                obj = s3.Object(bucket_name, file_name)
                data = obj.get()["Body"].read()
                data = json.loads(data)
            except ClientError as e:
                print("Client Error", e, file_name)
                return []
        else:
            with open(file_name) as f:
                data = json.load(f)
        for record in data:
            full_content_link = record["link"]
            provider = record["provider"]
            time = record["time"]
            title = record["title"]
            link_data = NaverNewsLinkModel(publish_time=time, title=title, provider=provider, article_url=full_content_link)
            links.append(link_data)
        return links

    def write_contents_to_file(self, date: datetime, contents: List[NaverNewsContentModel]):
        file_name = get_content_file_path(date, from_s3=self.from_s3)
        content_dictionary = [x.serialize() for x in contents]

        if self.from_s3:
            object = s3.Object(bucket_name, file_name)
            data = json.dumps(content_dictionary, ensure_ascii=False)
            object.put(Body=data)
        else:
            with open(file_name, 'w', encoding="utf-8") as outfile:
                json.dump(content_dictionary, outfile, ensure_ascii=False)

    def read_contents_from_file(self, date: datetime) -> []:
        contents = []
        data = self.read_raw_contents_from_file(date)
        if data is None:
            return []

        for record in data:
            # Record to instance
            contents.append(record)
        return contents

    def read_raw_contents_from_file(self, date: datetime):
        file_name = get_content_file_path(date, from_s3=self.from_s3)
        if self.from_s3:
            try:
                obj = s3.Object(bucket_name, file_name)
                data = obj.get()["Body"].read()
                data = json.loads(data)
            except ClientError as e:
                print("Client Error", e, file_name)
                return None
        else:
            with open(file_name) as f:
                data = json.load(f)
        return data



def check_if_file_is_exists(file: str, from_s3=False):
    if from_s3:
        try:
            s3.Object(bucket_name, file).load()
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                print(e.response)
                return False
    else:
        if os.path.isfile(file):
            return True
        else:
            return False


# False = "file is crawled" // True = "file is empty"
def check_if_file_is_empty(file: str, mode="light", from_s3=False) -> bool:
    if from_s3:
        return not check_if_file_is_exists(file=file, from_s3=True)
    else:
        if check_if_file_is_exists(file):
            # File exists
            if mode == "light":
                return False
            elif mode == "full":
                with open(file, encoding="utf-8") as f:
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

# TODO Add s3Support
def get_articles_count_at_date(date: datetime, from_s3):
    file = get_link_file_path(date)
    if check_if_file_is_exists(file):
        with open(file) as f:
            try:
                return len(json.load(f))
            except json.JSONDecodeError:
                return 0
    return 0


def check_if_links_empty(date:datetime, mode="full", from_s3=False) -> bool:
    fileName = get_link_file_path(date, from_s3=from_s3)
    return check_if_file_is_empty(fileName, mode=mode, from_s3=from_s3)


def get_content_file_path(date: datetime, from_s3) -> str:
    date_str = get_date_str(date)
    file_name = 'naver_news_content_data/naver_date_article_contents_%s.json' % date_str
    if from_s3:
        return file_name
    else:
        file_name = os.path.join(DATA_ROOT, file_name)
        return file_name


def check_if_content_empty(date:datetime, from_s3=False) -> bool:
    file_name = get_content_file_path(date, from_s3=from_s3)
    return check_if_file_is_empty(file_name, from_s3=from_s3)
# endregion


if __name__ == "__main__":
    date = datetime(2000, 1, 1)
    experiment_date = datetime(2020, 1, 2)
    experiment_date_x = datetime(2030, 1, 2)

    iom = IOManager(from_s3=False)
    iom.write_links_to_file(
        experiment_date,
        links=[{"link": "http://google.com/", "provider": "null"}, {"link": "http://google.com/", "provider": "null"}, {"link": "http://google.com/", "provider": "null"}],
    )

    print(check_if_content_empty(experiment_date_x))
