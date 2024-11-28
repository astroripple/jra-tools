"""トレーニングデータ取得用クエリ"""

from typing import List, Callable
from jrdb_model import KaisaiData
from jra_tools.machine_learning.interface_adapter.ispecified_loader import (
    SpecifiedLoader,
)


def _validate_year(year: int):
    assert 2000 <= year <= 2100, "2000年以降を指定してください"
    assert isinstance(year, int)


class TrainingKaisaiQuery:
    """トレーニングデータ用クエリ"""

    def __init__(
        self,
        start: int,
        end: int,
        loader_factory: Callable[[int, int], SpecifiedLoader],
    ):
        _validate_year(start)
        _validate_year(end)
        assert start <= end, "終了年は開始年以降にしてください"
        self.start = start
        self.end = end
        self.loader = loader_factory(self._start, self._end)

    def load(self) -> List[KaisaiData]:
        return self.loader.load()

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
            "data"
            if self.start == 2012 and self.end == 2018
            else f"{self.start}_{self.end}"
        )
