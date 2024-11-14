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


def create_training_input_data(start: int, end: int):
    """指定した期間のデータセットを作成する

    Args:
        start (int): YYYY
        end (int): YYYY

    Raises:
        RuntimeError: データのロードまたは保存中にエラーが発生
    """
    from jra_tools import load

    try:
        kaisais = load(int(f"{start}0101"), int(f"{end}1231"))
        ic = InputCreator(kaisais)
        period = "data" if start == 2012 and end == 2018 else f"{start}_{end}"
        ic.save(f"x_{period}.dump")
    except Exception as e:
        raise RuntimeError(
            "トレーニングの入力データの作成中にエラーが発生しました"
        ) from e
