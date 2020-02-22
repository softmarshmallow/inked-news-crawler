from datetime import datetime
from typing import List, Dict


class StockCalendarEventModel:
    def __init__(self):
        self.eventName: str = ""
        self.eventContent: str = ""
        self.eventTime: datetime = datetime(2000, 1, 1)
        self.links: List[str] = []
        self.extraFields: Dict = {}

    def get_formatted_event_time(self):
        return self.eventTime.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return self.eventName + "\n" + str(self.links[0])

    def __repr__(self):
        return self.__str__()

