"""クリエイターインターフェース"""

from typing import List, Protocol, runtime_checkable
from jrdb_model import KaisaiData


@runtime_checkable
class ICreator(Protocol):
    """kaisaisをndarrayに変換するインターフェース"""

    kaisais: List[KaisaiData]

    def save(self, name: str):
        """ローカルにデータセットを保存する

        Args:
            name (str): 拡張子を除いたファイル名
        """
