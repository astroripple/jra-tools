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


def save_payout(payout: np.ndarray, period: str):
    with open(f"payout_{period}.dump", "wb") as f:
        payout.dump(f)


def save_payout_from(kaisais: List[KaisaiData], period: str):
    """開催一覧から払戻金データをローカルに保存する

    Args:
        kaisais (List[KaisaiData]): 開催一覧
        period (str): ファイル名
    """
    save_payout(create_payout(kaisais), period)


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
        save_payout(self.payout, period)
