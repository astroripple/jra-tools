"""期間してい可能なローダーのインターフェース"""

from typing import List, Protocol, runtime_checkable
from jrdb_model import KaisaiData


@runtime_checkable
class SpecifiedLoader(Protocol):
    """IOロードのインターフェース"""

    start: int
    end: int

    def load(self) -> List[KaisaiData]:
        """開催データ一覧を取得する

        Returns:
            List[KaisaiData]: 開催データ一覧
        """

    @property
    def period(self) -> str:
        """期間にアクセス可能"""
