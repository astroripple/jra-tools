from typing import List
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.kaisai_loader import load


@dataclass
class TrainingKaisaiQuery:
    """トレーニングデータ用クエリ"""

    start: int
    end: int

    def load(self) -> List[KaisaiData]:
        return load(self._start, self._end)

    @property
    def _start(self):
        return int(f"{self.start}0101")

    @property
    def _end(self):
        return int(f"{self.end}1231")

    @property
    def period(self):
        """データセットの期間"""
        return (
            (
                "data"
                if self.start == 2012 and self.end == 2018
                else f"{self.start}_{self.end}"
            ),
        )
