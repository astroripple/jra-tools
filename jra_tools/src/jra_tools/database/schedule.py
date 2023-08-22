"""Yahoo競馬からスケジュールを確認する"""
from typing import List
import re
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup

YEAR = int(datetime.now().strftime("%Y"))
MONTH = int(datetime.now().strftime("%m"))


async def annual_schedule(year: int = YEAR) -> List[int]:
    """指定して年間スケジュールを取得する

    Args:
        year (int, optional): 取得する年. Defaults to YEAR.

    Returns:
        List[int]: 開催される日付一覧
    """
    tasks = [open_days(month, year) for month in range(1, 13)]
    months = await asyncio.gather(*tasks)
    return [day for month in months for day in month]


async def open_days(month: int = MONTH, year: int = YEAR) -> List[int]:
    """指定した年、月の開催一覧を取得する

    Args:
        month (int, optional): 月. Defaults to MONTH.
        year (int, optional): 年. Defaults to YEAR.

    Returns:
        List[int]: 開催される日付一覧
    """
    base_url = "https://sports.yahoo.co.jp/keiba/schedule/monthly"
    payload = {"year": str(year), "month": str(month)}
    soup = BeautifulSoup(await _fetch_html(base_url, payload), "lxml")
    return [int(f"{year:04d}{month:02d}{day:02d}") for day in _parse_to_days(soup)]


async def _fetch_html(url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=payload) as response:
            return await response.text()


def _parse_to_days(soup: BeautifulSoup) -> List[int]:
    return list(
        set(
            [
                int(re.sub("\\D", "", s.contents[0]))
                for s in soup.select(".hr-tableSchedule__data--date")
            ]
        )
    )
