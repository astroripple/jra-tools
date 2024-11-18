"""InputCreatorのユニットテスト"""

import os
import numpy as np
from jra_tools.machine_learning.icreator import ICreator
from jra_tools import InputCreator


def test_save(sample_kaisais):
    """saveメソッドのユニットテスト"""
    try:
        ic = InputCreator(sample_kaisais)
        ic.save("testfile")

        assert isinstance(
            ic, ICreator
        ), "InputCreatorがICreatorのプロトコルに適合しません"
        with open("x_testfile.dump", "rb") as f:
            data = np.load(f, allow_pickle=True)

        assert len(data) == 24
    finally:
        if os.path.exists("x_testfile.dump"):
            os.remove("x_testfile.dump")
