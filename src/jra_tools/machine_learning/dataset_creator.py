"""トレーニングデータセットをローカルに作成する"""

from typing import Callable, List, Protocol
from dataclasses import dataclass
from jrdb_model import KaisaiData
from jra_tools.machine_learning.icreator import ICreator


class IDatasetCreator(Protocol):
    """データセットクリエイターインターフェース

    Args:
        Protocol (_type_): _description_
    """

    kaisais: List[KaisaiData]
    only_input: bool
    input_factory: Callable[..., ICreator]
    payout_factory: Callable[..., ICreator]
    save: Callable[[str], None]


@dataclass
class DatasetCreator:
    kaisais: List[KaisaiData]
    only_input: bool
    input_factory: Callable[..., ICreator]
    payout_factory: Callable[..., ICreator]

    def save(self, period: str):
        ic = self.input_factory(self.kaisais)
        assert isinstance(ic, ICreator)
        ic.save(period)
        if not self.only_input:
            pc = self.payout_factory(self.kaisais)
            assert isinstance(pc, ICreator)
            pc.save(period)


def create_dataset_from(
    kaisais: List[KaisaiData],
    period: str,
    only_input: bool,
    input_factory: Callable[..., ICreator],
    payout_factory: Callable[..., ICreator],
):
    """開催一覧をndarrayに変換して、トレーニングデータセットを保存する

    Args:
        kaisais (List[KaisaiData]): 開催一覧
        period (str): 保存するファイル名(拡張子を除く)
        only_input (bool): 入力データのみを保存する
        input_factory (Callable[..., ICreator]): インプットデータを作成するクラス
        payout_factory (Callable[..., ICreator]): 払戻データを作成するクラス
    """
    ic = input_factory(kaisais)
    assert isinstance(ic, ICreator)
    ic.save(period)
    if not only_input:
        pc = payout_factory(kaisais)
        assert isinstance(pc, ICreator)
        pc.save(period)
