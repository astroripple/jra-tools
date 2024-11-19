from typing import Callable
from dataclasses import dataclass
from jra_tools.machine_learning.dataset_creator import IDatasetCreator
from jra_tools.machine_learning.icreator import ICreator
from jra_tools import IKaisaiLoader


@dataclass
class TargetDatasetCreator:
    start: int
    end: int
    only_input: bool
    loader_factory: Callable[..., IKaisaiLoader]
    dataset_creator_factory: Callable[..., IDatasetCreator]
    input_factory: Callable[..., ICreator]
    payout_factory: Callable[..., ICreator]

    def save(self, period: str):
        try:

            loader = self.loader_factory(self.start, self.end)
            creator = self.dataset_creator_factory(
                loader.load(), self.only_input, self.input_factory, self.payout_factory
            )
            creator.save(period)
        except Exception as e:
            raise RuntimeError("データセットの作成中にエラー") from e
