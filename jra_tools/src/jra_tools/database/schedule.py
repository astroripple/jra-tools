"""Yahoo競馬からスケジュールを確認する"""
from typing import List
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

YEAR = int(datetime.now().strftime("%Y"))
MONTH = int(datetime.now().strftime("%m"))


def annual_schedule(year: int = YEAR) -> List[int]:
    """指定して年間スケジュールを取得する

    Args:
        year (int, optional): 取得する年. Defaults to YEAR.

    Returns:
        List[int]: 開催される日付一覧
    """
    return [day for month in range(1, 13) for day in open_days(month, year)]


def open_days(month: int = MONTH, year: int = YEAR) -> List[int]:
    """指定した年、月の開催一覧を取得する

    Args:
        month (int, optional): 月. Defaults to MONTH.
        year (int, optional): 年. Defaults to YEAR.

    Returns:
        List[int]: 開催される日付一覧
    """
    base_url = "https://sports.yahoo.co.jp/keiba/schedule/monthly"
    payload = {"year": str(year), "month": str(month)}
    soup = BeautifulSoup(requests.get(base_url, payload).text, "lxml")
    return [int(f"{year:04d}{month:02d}{day:02d}") for day in _parse_to_days(soup)]


def _parse_to_days(soup: BeautifulSoup) -> List[int]:
    days = []
    for s in soup.select(".hr-tableSchedule__data--date"):
        day = re.sub("\\D", "", s.contents[0])
        if day != "":
            days.append(int(day))
    return list(set(days))
