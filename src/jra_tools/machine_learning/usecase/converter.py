"""KaisaiDataを取得し、ndarrayに変換する"""

from typing import Callable, List, Optional
from jrdb_model import KaisaiData
from jra_tools.machine_learning.usecase.icreator import ICreator
from jra_tools.machine_learning.usecase.iquery import IQuery

CreatorFactory = Callable[[List[KaisaiData]], ICreator]


class Converter:
    """KaisaiDataをndarrayに変換するクラス"""

    def __init__(self, query: IQuery, factories: List[CreatorFactory]):
        assert isinstance(query, IQuery)
        self.query = query
        self.factories = factories

    def save(self, name: Optional[str] = None):
        """指定したファイル名でndarrayを保存する

        Args:
            name (str): ファイル名
        """
        kaisais = self.query.load()
        for factory in self.factories:
            creator = factory(kaisais)
            assert isinstance(creator, ICreator)
            creator.save(name if name is not None else self.query.period)
