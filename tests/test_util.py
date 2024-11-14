"""utilのユニットテスト"""

from typing import List
import os
import pickle
import pytest
from jra_tools.machine_learning import util


KaisaiList = List[util.KaisaiData]


@pytest.fixture
def sample_kaisais() -> KaisaiList:
    """開催データのフィクスチャ

    Returns:
        KaisaiList: ローカルからロードずみの開催データ一覧
    """
    file_path = os.path.join(os.path.dirname(__file__), "sample_kaisais.pkl")

    with open(file_path, "rb") as f:
        return pickle.load(f)


def test_create_payout(sample_kaisais: KaisaiList):
    """KaisaiListから払戻金のndarrayが作成されていることを確認する

    Args:
        sample_kaisais (KaisaiList): 開催一覧
    """
    data = util.create_payout(sample_kaisais)
    assert len(data) == 24
