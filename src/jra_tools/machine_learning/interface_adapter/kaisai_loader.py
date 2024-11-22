"""開催一覧を1年分以上ロードする"""

from typing import List
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.interface_adapter.iioloader import IOLoader


@dataclass
class KaisaiLoader:
    loader: IOLoader

    def load(self) -> List[KaisaiData]:
        return self.loader.load()
