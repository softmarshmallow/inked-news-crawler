from datetime import datetime


def get_date_input(date_name: str) -> datetime:
    date_str = input(date_name + " (YYYYmmdd) :: ")
    date = datetime.strptime(date_str, '%Y%m%d')
    return date
