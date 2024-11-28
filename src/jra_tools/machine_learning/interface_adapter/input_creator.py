"""推論に必要なデータセットを作成する"""

from typing import List
import numpy as np
from jrdb_model import KaisaiData
from jra_tools.machine_learning.usecase.training_tool import (
    create_score_data_matrix,
    standardize,
)
from jra_tools.machine_learning.usecase.category_data import get_category_data


class InputCreator:
    """KaisaiDataを元にndarrayを作成する"""

    def __init__(self, kaisais: List[KaisaiData]):
        self.kaisais = kaisais
        self.x_data = create_input_data(kaisais)

    def save(self, name: str) -> None:
        """入力データを永続化する

        Args:
            name (str): ファイル名。拡張子も含めること。
        """
        save_input_data(self.x_data, name)


def save_input_data(x_data: np.ndarray, name: str) -> None:
    with open(f"x_{name}.dump", mode="wb") as f:
        x_data.dump(f)


def create_input_data(kaisais: List[KaisaiData]) -> np.ndarray:
    """開催一覧から推論モデル用入力データを作成する
    Args:
        kaisais (List[KaisaiData]): 開催一覧

    Returns:
        np.ndarray: 推論モデルの入力データ
    """
    score_data = standardize(create_score_data_matrix(kaisais))
    cd = get_category_data(kaisais)
    return np.concatenate((score_data, cd), axis=2)


def save_input_data_from(kaisais: List[KaisaiData], name: str):
    """開催一覧から入力データのndarrayをローカルに保存する

    Args:
        kaisais (List[KaisaiData]): 開催一覧
        name (str): ファイル名
    """
    save_input_data(create_input_data(kaisais), name)
