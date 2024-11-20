"""トレーニングデータセットをローカルに作成する"""

from typing import Callable, List, Protocol, runtime_checkable
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.icreator import ICreator


CreatorFactory = Callable[[List[KaisaiData]], ICreator]


@runtime_checkable
class IDatasetCreator(Protocol):

    kaisais: List[KaisaiData]
    factories: List[CreatorFactory]

    def save(self, period: str) -> None:
        """指定したperiodでファイルを保存する"""


@dataclass
class DatasetCreator:
    kaisais: List[KaisaiData]
    factories: List[CreatorFactory]

    def save(self, period: str) -> None:
        """ローカルにndarrayファイルを保存する

        Args:
            period (str): 指定する期間
        """
        for factory in self.factories:
            creator = factory(self.kaisais)
            creator.save(period)


SaveDataFn = Callable[[List[KaisaiData], str], None]


def save_dataset_from(
    kaisais: List[KaisaiData],
    name: str,
    save_input_fn: SaveDataFn,
    save_payout_fn: SaveDataFn,
):
    save_input_fn(kaisais, name)
    save_payout_fn(kaisais, name)
