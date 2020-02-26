#!/bin/bash
cd /home/ubuntu/app/inked-news-crawler || pass
source venv/bin/activate
venv/bin/python -m pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:inkedNewsCrawler"
venv/bin/python inkedNewsCrawler/custom_crawler/naver_news_crawler/live_crawler.py