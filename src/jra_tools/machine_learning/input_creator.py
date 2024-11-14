"""推論に必要なデータセットを作成する"""

from typing import List
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
    _start, _end, period = _training_period(start, end)
    _create_dataset(_start, _end, period, only_input)


def create_quarter_dataset(year: int, quarter: int, only_input: bool = True) -> None:
    """指定した四半期のデータセットをファイルに保存する

    Args:
        year (int): YYYY
        quarter (int): 1 - 4
        only_input (bool, optional): 入力データのみを作成するか. Defaults to True.
    """
    _start, _end, period = _quarter_period(year, quarter)
    _create_dataset(_start, _end, period, only_input)


def _quarter_period(year: int, quarter: int):
    start_month = int(12 / 4 * (quarter - 1) + 1)
    end_month = start_month + 2
    return (
        int(f"{year}{start_month:02}01"),
        int(f"{year}{end_month:02}{30 if end_month in [2,4,6,9,11] else 31}"),
        f"{year}_{start_month:02}_{end_month:02}",
    )


def _create_dataset(start: int, end: int, period: str, only_input: bool):
    from jra_tools import load

    try:
        kaisais, period = load(start, end)
        _create_dataset_from(kaisais, period, only_input)
    except Exception as e:
        raise RuntimeError("データセットの作成中にエラー") from e


def _training_period(start, end):
    return (
        int(f"{start}0101"),
        int(f"{end}1231"),
        "data" if start == 2012 and end == 2018 else f"{start}_{end}",
    )


def _save_x(kaisais, period: str):
    ic = InputCreator(kaisais)
    ic.save(f"x_{period}.dump")


def _save_payout(kaisais, period: str):
    from jra_tools import create_payout

    payout = create_payout(kaisais)

    with open(f"payout_{period}.dump", "wb") as f:
        payout.dump(f)


def _create_dataset_from(kaisais, period: str, only_input: bool):
    _save_x(kaisais, period)
    if not only_input:
        _save_payout(kaisais, period)
