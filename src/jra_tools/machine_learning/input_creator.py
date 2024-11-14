﻿"""推論に必要なデータセットを作成する"""

from typing import Tuple, List
import numpy as np
from jrdb_model import KaisaiData
from . import training_tool
from . import category_data


class InputCreator:
    """KaisaiDataを元にndarrayを作成する"""

    def __init__(self, kaisais: List[KaisaiData]):
        score_data = training_tool.create_score_data_matrix(kaisais)
        sds = training_tool.standardize(score_data)
        cd = category_data.get_category_data(kaisais)
        self.x_data = np.concatenate((sds, cd), axis=2)

    def save(self, name: str) -> None:
        """入力データを永続化する

        Args:
            name (str): ファイル名。拡張子も含めること。
        """
        with open(name, mode="wb") as f:
            self.x_data.dump(f)


def create_training_dataset(start: int, end: int, only_input: bool = True):
    """指定した期間のデータセットを作成する

    Args:
        start (int): YYYY
        end (int): YYYY

    Raises:
        RuntimeError: データのロードまたは保存中にエラーが発生
    """
    try:
        kaisais, period = _load(start, end)
        _save_x(kaisais, period)
        if not only_input:
            _save_payout(kaisais, period)
    except Exception as e:
        raise RuntimeError("トレーニングデータの作成中にエラーが発生しました") from e


def _load(start, end) -> Tuple[List[KaisaiData], str]:
    from jra_tools import load

    kaisais = load(int(f"{start}0101"), int(f"{end}1231"))
    period = "data" if start == 2012 and end == 2018 else f"{start}_{end}"
    return kaisais, period


def _save_x(kaisais, period: str):
    ic = InputCreator(kaisais)
    ic.save(f"x_{period}.dump")


def _save_payout(kaisais, period: str):
    from jra_tools import create_payout

    payout = create_payout(kaisais)

    with open(f"payout_{period}.dump", "wb") as f:
        payout.dump(f)
