"""トレーニングデータセットをローカルに作成する"""

from typing import Callable, List, Protocol, runtime_checkable
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.icreator import ICreator
from jra_tools import save_input_data_from, save_payout_from


@runtime_checkable
class IDatasetCreator(Protocol):
    only_input: bool
    input_creator: ICreator
    payout_creator: ICreator

    def save(self, period: str) -> None:
        """指定したperiodでファイルを保存する"""


@dataclass
class DatasetCreator:
    only_input: bool
    input_creator: ICreator
    payout_creator: ICreator

    def save(self, period: str) -> None:
        """ローカルにファイルを保存する

        Args:
            period (str): 指定する期間
        """
        self.input_creator.save(period)
        if not self.only_input:
            self.payout_creator.save(period)


SaveDataFn = Callable[[List[KaisaiData], str], None]


def save_dataset_from(
    kaisais: List[KaisaiData],
    name: str,
    only_input: bool,
    save_input_fn: SaveDataFn,
    save_payout_fn: SaveDataFn,
):
    save_input_fn(kaisais, name)
    if not only_input:
        save_payout_fn(kaisais, name)
