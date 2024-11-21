from typing import List
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.kaisai_loader import load


class QuarterKaisaiQuery:
    """四半期データ用クエリ"""

    def __init__(self, year: int, quarter: int):
        assert 2000 <= year <= 2100, "2000年以降を指定してください"
        assert isinstance(year, int)
        self.year = year
        assert 1 <= quarter <= 4, "1 - 4を指定してください"
        self.quarter = quarter

    def load(self) -> List[KaisaiData]:
        return load(self._start, self._end)

    @property
    def _start(self) -> int:
        return int(f"{self.year}{self._start_month:02}01")

    @property
    def _end(self) -> int:
        return int(
            f"{self.year}{self._end_month:02}{30 if self._end_month in [2,4,6,9,11] else 31}"
        )

    @property
    def period(self) -> str:
        """データセットの期間"""
        return f"{self.year}_{self._start_month:02}_{self._end_month:02}"

    @property
    def _start_month(self) -> int:
        return int(12 / 4 * (self.quarter - 1) + 1)

    @property
    def _end_month(self) -> int:
        return self._start_month + 2
