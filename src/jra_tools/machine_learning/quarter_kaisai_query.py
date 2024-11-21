from typing import List
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.kaisai_loader import load


@dataclass
class QuarterKaisaiQuery:
    """四半期データ用クエリ"""

    year: int
    quarter: int

    def load(self) -> List[KaisaiData]:
        return load(self._start, self._end)

    @property
    def _start(self):
        return (int(f"{self.year}{self._start_month:02}01"),)

    @property
    def _end(self):
        return (
            int(
                f"{self.year}{self._end_month:02}{30 if self._end_month in [2,4,6,9,11] else 31}"
            ),
        )

    @property
    def period(self):
        """データセットの期間"""
        return (f"{self.year}_{self._start_month:02}_{self._end_month:02}",)

    @property
    def _start_month(self):
        return int(12 / 4 * (self.quarter - 1) + 1)

    @property
    def _end_month(self):
        return self._start_month + 2
