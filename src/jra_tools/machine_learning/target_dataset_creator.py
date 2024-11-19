"""DBから指定した期間のデータセットを作成する"""

from typing import Callable
from dataclasses import dataclass
from jra_tools.machine_learning.icreator import ICreator
from jra_tools import IDatasetCreator, IKaisaiLoader


@dataclass
class TargetDatasetCreator:
    """指定した日付のデータセットを作成する

    Raises:
        RuntimeError: 作成中に発生したエラー
    """

    start: int
    end: int
    only_input: bool
    loader_factory: Callable[..., IKaisaiLoader]
    dataset_creator_factory: Callable[..., IDatasetCreator]
    input_factory: Callable[..., ICreator]
    payout_factory: Callable[..., ICreator]

    def save(self, period: str):
        """指定したperiodの名前でファイルを保存する

        Args:
            period (str): 期間

        Raises:
            RuntimeError: 作成中に発生したエラー
        """
        try:

            loader = self.loader_factory(self.start, self.end)
            creator = self.dataset_creator_factory(
                loader.load(), self.only_input, self.input_factory, self.payout_factory
            )
            creator.save(period)
        except Exception as e:
            raise RuntimeError("データセットの作成中にエラー") from e
