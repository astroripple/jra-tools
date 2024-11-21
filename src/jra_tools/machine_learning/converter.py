"""KaisaiDataを取得し、ndarrayに変換する"""

from typing import Callable, List
from jrdb_model import KaisaiData
from jra_tools.machine_learning.icreator import ICreator
from jra_tools.machine_learning.kaisai_loader import IQuery

CreatorFactory = Callable[[List[KaisaiData]], ICreator]


class Converter:
    """KaisaiDataをndarrayに変換するクラス"""

    def __init__(self, query: IQuery, factories: List[CreatorFactory]):
        self.query = query
        self.factories = factories

    def save(self, name: str):
        """指定したファイル名でndarrayを保存する

        Args:
            name (str): ファイル名
        """
        kaisais = self.query.load()
        for factory in self.factories:
            creator = factory(kaisais)
            creator.save(name)
