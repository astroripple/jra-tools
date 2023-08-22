"""開催データに紐づくデータを結合した状態でロードする"""
from typing import List
from sqlalchemy.orm import joinedload
from jrdb_model import KaisaiData, app


def get_kaisais(start: int, end: int) -> List[KaisaiData]:
    """指定した期間の開催データを取得する

    Args:
        start (int): YYYYMMDD
        end (int): YYYYMMDD

    Returns:
        list[KaisaiData]: 開催データ一覧
    """
    with app.app_context():
        return (
            KaisaiData.query.filter(KaisaiData.ymd >= start, KaisaiData.ymd <= end)
            .options(joinedload("*"))
            .all()
        )
