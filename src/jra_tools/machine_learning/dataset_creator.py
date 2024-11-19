"""トレーニングデータセットをローカルに作成する"""

from typing import Callable, List, Protocol, runtime_checkable
from jrdb_model import KaisaiData
from jra_tools.machine_learning.icreator import ICreator


@runtime_checkable
class IDatasetCreator(Protocol):
    kaisais: List[KaisaiData]
    only_input: bool
    input_factory: Callable[..., ICreator]
    payout_factory: Callable[..., ICreator]

    def save(self, period: str) -> None:
        """指定したperiodでファイルを保存する"""


class DatasetCreator:

    def __init__(
        self,
        kaisais: List[KaisaiData],
        only_input: bool,
        input_factory: Callable[..., ICreator],
        payout_factory: Callable[..., ICreator],
    ):
        self.kaisais = kaisais
        self.only_input = only_input
        self.input_factory = input_factory
        self.payout_factory = payout_factory

    def save(self, period: str) -> None:
        """ローカルにファイルを保存する

        Args:
            period (str): 指定する期間
        """
        ic = self.input_factory(self.kaisais)
        assert isinstance(ic, ICreator)
        ic.save(period)
        if not self.only_input:
            pc = self.payout_factory(self.kaisais)
            assert isinstance(pc, ICreator)
            pc.save(period)
