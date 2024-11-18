"""DB周りのユーティリティ"""

from typing import List
from functools import reduce
import numpy as np
from jra_tools import KaisaiData


def create_payout(kaisais: List[KaisaiData]) -> np.ndarray:
    """払戻データをndarrayに変換する

    Args:
        kaisais (list[KaisaiData]): 開催データ一覧

    Returns:
        np.ndarray: (レース数, 18)
    """
    payout_data = np.zeros([reduce(lambda x, y: x + len(y.races), kaisais, 0), 18])

    num_race = 0
    for kaisai in kaisais:
        for race in kaisai.races:
            payout_data[num_race, race.returninfo.win1_num - 1] = (
                race.returninfo.win1_ret
            )
            num_race += 1
    return payout_data


class PayoutCreator:
    """kaisaisから払戻金を作るクラス"""

    def __init__(self, kaisais):
        self.kaisais = kaisais
        self.payout = create_payout(kaisais)

    def save(self, period: str):
        """payoutのndarrayをローカルに保存する

        Args:
            period (str): 拡張子を除いたファイル名
        """
        with open(f"payout_{period}.dump", "wb") as f:
            self.payout.dump(f)