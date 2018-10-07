from datetime import datetime
from typing import List, Dict


class StockCalendarEventModel:
    def __init__(self):
        self.eventName: str
        self.eventContent: str
        self.eventTime: datetime
        self.links: List[str]
        self.extraFields: Dict
