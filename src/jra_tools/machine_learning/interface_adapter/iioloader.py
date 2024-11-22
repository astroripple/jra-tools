"""IOロードのインターフェース"""

from typing import List, Protocol, runtime_checkable
from jrdb_model import KaisaiData


@runtime_checkable
class IOLoader(Protocol):
    """IOロードのインターフェース"""

    def load(self) -> List[KaisaiData]:
        """開催データ一覧を取得する

        Returns:
            List[KaisaiData]: 開催データ一覧
        """
