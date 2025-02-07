"""ユニットテストで共通利用するフィクスチャー."""

import os
import pickle
from typing import List

import pytest
from jrdb_model import KaisaiData

KaisaiList = List[KaisaiData]


@pytest.fixture
def sample_kaisais() -> KaisaiList:
    """開催データのフィクスチャ.

    Returns:
        KaisaiList: ローカルからロードずみの開催データ一覧

    """
    file_path = os.path.join(os.path.dirname(__file__), "sample_kaisais.pkl")

    with open(file_path, "rb") as f:
        return pickle.load(f)
