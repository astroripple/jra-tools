"""開催一覧を1年分以上ロードする"""

from typing import List, Protocol, runtime_checkable
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.interface_adapter.iioloader import IOLoader


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
    loader: IOLoader

    def load(self) -> List[KaisaiData]:
        return self.loader.load()
