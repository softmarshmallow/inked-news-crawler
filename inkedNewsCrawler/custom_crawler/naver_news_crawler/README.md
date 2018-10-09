
# Overview
네이버 뉴스 속보 크롤러 입니다.

http://news.naver.com 뉴스 속보를 클롤링 해옵니다.

### url example

> ex. https://news.naver.com/main/list.nhn?mode=LSD&sid1=001&mid=sec&listType=title&date=20181010&page=2







# Crawling Policy



| 구분             | 값                         |
| :--------------- | -------------------------- |
| 크롤링 가능 구간 | 1990.01.01 ~             |
| 최초 크롤링 구간 | 1990.01.01 ~ 현재              |
| 지속 크롤링 구간 | 현재 |
| 크롤링 주기      | 0.2초 마다 1회 |







## uid

news.naver.com 의 DB 와 솔루션의 DB를 싱크 해야합니다.

데이터가 수시로 변경되기때문에 세로운 데이터가 생성되었는지, 삭제되었는지 확인해야 합니다.

제공된 데이터를 분별할수있는 UID는 다음과 같이 설계합니다.



> UID:: \$YYYYMMDD\$naver_news_url