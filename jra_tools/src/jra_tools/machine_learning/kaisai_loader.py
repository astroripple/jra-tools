"""開催一覧を1年分以上ロードする"""

from typing import List, Tuple
import datetime as dt
from .kaisai_creator import get_kaisais, KaisaiData


def load(start: int, end: int) -> List[KaisaiData]:
    """データを1年毎にまとめてロードして、マージ結果を取得する

    Args:
        start (int): YYYYMMDD
        end (int): YYYYMMDD

    Returns:
        List[KaisaiData]: _description_
    """
    s = _to_date(start)
    e = _to_date(end)

    periods = [
        (s, dt.datetime(year=s.year, month=12, day=31)),
        *[_period(i) for i in range(s.year + 1, e.year)],
        (dt.datetime(year=e.year, month=1, day=1), e),
    ]
    return [
        kaisai
        for start_date, end_date in periods
        for kaisai in get_kaisais(_to_int(start_date), _to_int(end_date))
    ]


def _period(year: int) -> Tuple[dt.datetime, dt.datetime]:
    return (
        dt.datetime(year=year, month=1, day=1),
        dt.datetime(year=year, month=12, day=31),
    )


def _to_date(date: int) -> dt.datetime:
    return dt.datetime.strptime(str(date), "%Y%m%d")


def _to_int(date: dt.datetime) -> int:
    return int(date.strftime("%Y%m%d"))
