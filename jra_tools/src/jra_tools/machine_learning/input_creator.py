from . import training_tool
from . import category_data
import numpy as np


class InputCreator:
    def __init__(self, kaisais):
        score_data = training_tool.createScoreDataMatrix(kaisais)
        sds = training_tool.standardize(score_data)
        cd = category_data.getCategoryData(kaisais)
        self.x_data = np.concatenate((sds, cd), axis=2)
