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
