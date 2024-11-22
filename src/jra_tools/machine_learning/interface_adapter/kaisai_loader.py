"""開催一覧を1年分以上ロードする"""

from typing import List, Tuple, Protocol, runtime_checkable
from dataclasses import dataclass
import datetime as dt
from jra_tools.machine_learning.infrastructure.kaisai_creator import (
    get_kaisais,
    KaisaiData,
)


@runtime_checkable
class IQuery(Protocol):
    @property
    def period(self) -> str:
        """期間を示すプロパティ"""

    def load(self) -> List[KaisaiData]:
        """開催データ一覧を取得する

        Returns:
            List[KaisaiData]: 開催データ一覧
        """


@dataclass
class KaisaiLoader:
    start: int
    end: int

    def load(self) -> List[KaisaiData]:
        return load(self.start, self.end)

    @property
    def period(self) -> str:
        return f"{self.start}_{self.end}"
