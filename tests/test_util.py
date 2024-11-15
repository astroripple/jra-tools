"""utilのユニットテスト"""

import os
import numpy as np
from jra_tools.machine_learning import util
from jra_tools.machine_learning.icreator import ICreator


def test_create_payout(sample_kaisais):
    """KaisaiListから払戻金のndarrayが作成されていることを確認する

    Args:
        sample_kaisais (KaisaiList): 開催一覧
    """
    data = util.create_payout(sample_kaisais)
    assert len(data) == 24


def test_save(sample_kaisais):
    """payoutのndarrayがローカルに保存されることを確認する"""
    try:
        pc = util.PayoutCreator(sample_kaisais)
        pc.save("testfile")
        with open("payout_testfile.dump", "rb") as f:
            data = np.load(f)

        assert isinstance(pc, ICreator)
        assert len(data) == 24
    finally:
        if os.path.exists("payout_testfile.dump"):
            os.remove("payout_testfile.dump")
