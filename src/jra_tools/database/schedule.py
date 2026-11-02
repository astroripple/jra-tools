"""Yahoo競馬からスケジュールを確認する."""

import asyncio
import re
from datetime import datetime
from typing import List, Tuple

import aiohttp
from bs4 import BeautifulSoup

YEAR = int(datetime.now().strftime("%Y"))
MONTH = int(datetime.now().strftime("%m"))


async def annual_schedule(year: int = YEAR) -> List[int]:
    """指定して年間スケジュールを取得する.

    Args:
        year (int, optional): 取得する年. Defaults to YEAR.

    Returns:
        List[int]: 開催される日付一覧

    """
    tasks = [open_days(month, year) for month in range(1, 13)]
    months = await asyncio.gather(*tasks)
    return [day for month in months for day in month]


async def open_days(month: int = MONTH, year: int = YEAR) -> List[int]:
    """指定した年、月の開催一覧を取得する.

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


async def annual_kaisais(year: int = YEAR) -> List[Tuple[int, str]]:
    """指定した年の開催(日付と開催キー)の一覧を取得する.

    Args:
        year (int, optional): 取得する年. Defaults to YEAR.

    Returns:
        List[Tuple[int, str]]: (日付, JRDBの開催キー)の一覧

    """
    tasks = [open_kaisais(month, year) for month in range(1, 13)]
    months = await asyncio.gather(*tasks)
    return [kaisai for month in months for kaisai in month]


async def open_kaisais(month: int = MONTH, year: int = YEAR) -> List[Tuple[int, str]]:
    """指定した年、月の開催(日付と開催キー)の一覧を取得する.

    場ごとの開催日を返す。代替競馬は実際に開催した日(代替日)の行になる。
    途中で中止して残りを代替日に開催した場合も、代替日の行だけになる。

    Args:
        month (int, optional): 月. Defaults to MONTH.
        year (int, optional): 年. Defaults to YEAR.

    Returns:
        List[Tuple[int, str]]: (日付, JRDBの開催キー)の一覧

    """
    base_url = "https://sports.yahoo.co.jp/keiba/schedule/monthly"
    payload = {"year": str(year), "month": str(month)}
    soup = BeautifulSoup(await _fetch_html(base_url, payload), "lxml")
    return sorted(
        (int(f"{year:04d}{month:02d}{day:02d}"), kaisaikey)
        for day, kaisaikey in _parse_to_kaisais(soup)
    )


async def _fetch_html(url, payload):
    async with (
        aiohttp.ClientSession() as session,
        session.get(url, params=payload) as response,
    ):
        return await response.text()


def _parse_to_days(soup: BeautifulSoup) -> List[int]:
    return list(
        {
            int(re.sub("\\D", "", s.contents[0]))
            for s in soup.select(".hr-tableSchedule__data--date")
        }
    )


# 日ごとのレース一覧のリンク(/keiba/race/list/YYBBKKDD: 年2桁・場コード・回・日目)
_RACE_LIST = re.compile(r"/keiba/race/list/(\d{2})(\d{2})(\d{2})(\d{2})$")


def _parse_to_kaisais(soup: BeautifulSoup) -> List[Tuple[int, str]]:
    kaisais = set()
    for cell in soup.select(".hr-tableSchedule__data--date"):
        day = int(re.sub("\\D", "", cell.contents[0]))
        for link in cell.select("a[href*='/keiba/race/list/']"):
            matched = _RACE_LIST.search(link["href"])
            if matched is None:
                raise ValueError(f"レース一覧のリンクを読めません: {link['href']}")
            kaisais.add((day, to_kaisaikey(*matched.groups())))
    return sorted(kaisais)


def to_kaisaikey(year: str, bacode: str, kai: str, nichi: str) -> str:
    """Yahoo競馬の開催(年2桁・場コード・回・日目)を、JRDBの開催キーにする.

    JRDBの開催キーは場コード2桁・年2桁・回1桁・日目1桁(16進)。例: 2025年1回小倉10日 → 10251a

    Args:
        year (str): 年(2桁)
        bacode (str): 場コード(2桁)
        kai (str): 回(2桁)
        nichi (str): 日目(2桁)

    Returns:
        str: 開催キー

    """
    if not 1 <= int(kai) <= 9 or not 1 <= int(nichi) <= 15:  # noqa: PLR2004 開催キーの1桁に収まる範囲
        raise ValueError(f"開催キーにできない回・日目です: {kai}回{nichi}日")
    return f"{bacode}{year}{int(kai)}{int(nichi):x}"
