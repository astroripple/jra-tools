"""開催データに紐づくデータを結合した状態でロードする."""

import datetime as dt
from dataclasses import dataclass
from typing import List, Tuple

from jrdb_model import KaisaiData, create_app
from sqlalchemy.orm import joinedload


def get_kaisais(start: int, end: int) -> List[KaisaiData]:
    """指定した期間の開催データを取得する.

    Args:
        start (int): YYYYMMDD
        end (int): YYYYMMDD

    Returns:
        list[KaisaiData]: 開催データ一覧

    """
    app = create_app()
    with app.app_context():
        return (
            KaisaiData.query.filter(KaisaiData.ymd >= start, KaisaiData.ymd <= end)
            .options(joinedload("*"))
            .all()
        )


@dataclass
class MysqlLoader:
    """MySQLからエンティティを取得する."""

    start: int
    end: int

    def load(self) -> List[KaisaiData]:
        return load(self.start, self.end)

    @property
    def period(self) -> str:
        return f"{self.start}_{self.end}"


def load(start: int, end: int) -> List[KaisaiData]:
    """データを1年毎にまとめてロードして、マージ結果を取得する.

    Args:
        start (int): YYYYMMDD
        end (int): YYYYMMDD

    Returns:
        List[KaisaiData]: 開催データ一覧

    """
    return [
        kaisai
        for start_date, end_date in _periods(_to_date(start), _to_date(end))
        for kaisai in get_kaisais(_to_int(start_date), _to_int(end_date))
    ]


def _periods(s: dt.datetime, e: dt.datetime) -> List[Tuple[dt.datetime, dt.datetime]]:
    if s.year < e.year:
        return [
            (s, dt.datetime(year=s.year, month=12, day=31)),
            *[_period(i) for i in range(s.year + 1, e.year)],
            (dt.datetime(year=e.year, month=1, day=1), e),
        ]
    if s.year == e.year and s <= e:
        return [(s, e)]
    raise RuntimeError("開始日 <= 終了日となるように入力してください")


def _period(year: int) -> Tuple[dt.datetime, dt.datetime]:
    return (
        dt.datetime(year=year, month=1, day=1),
        dt.datetime(year=year, month=12, day=31),
    )


def _to_date(date: int) -> dt.datetime:
    return dt.datetime.strptime(str(date), "%Y%m%d")


def _to_int(date: dt.datetime) -> int:
    return int(date.strftime("%Y%m%d"))
