
# Overview
모두의 재테크 주식 켈린더 크롤러 입니다.

http://everystocks.com 의 주식 달력 서비스를 크롤링 해옵니다.

### url example

> ex. http://everystocks.com/index.php?mid=calendar&pGanjioption=1&pYear=2018&pMonth=11



# Crawling Policy

크롤링 주기: 6시간 마다 1회.
크롤링 가능 구간: 2017.8 ~
최초 크롤링 구간: 2017.8 ~ current month + 2
지속 크롤링 구간: current month (date) ~ + 2



## uid

everstocks 의 DB 와 솔루션의 DB를 싱크 해야합니다.

데이터가 수시로 변경되기때문에 세로운 데이터가 생성되었는지, 삭제되었는지 확인해야 합니다.

제공된 데이터를 분별할수있는 UID는 다음과 같이 설계합니다.



> UID:: \$YYYYMMDD\$everystocks_calendar_event_blog_url