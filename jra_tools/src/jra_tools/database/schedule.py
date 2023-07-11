import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

YEAR = int(datetime.now().strftime("%Y"))
MONTH = int(datetime.now().strftime("%m"))


def annual_schedule(year=YEAR):
    return [day for month in range(1, 13) for day in open_days(month, year)]


def open_days(month=MONTH, year=YEAR):
    base_url = f"https://keiba.yahoo.co.jp/schedule/list/{year}/"
    payload = {"month": str(month)}
    soup = BeautifulSoup(requests.get(base_url, payload).text, "lxml")
    return [int(f"{year:04d}{month:02d}{day:02d}") for day in _parse_to_days(soup)]


def _parse_to_days(soup):
    days = []
    for s in soup.find("table").find_all("tr"):
        if s.td is not None:
            day = re.sub("\\D", "", s.td.contents[0])
            if day != "":
                days.append(int(day))
    return list(set(days))
