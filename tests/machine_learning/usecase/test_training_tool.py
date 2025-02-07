"""数値データの入力型の定義."""

from typing import List

from jrdb_model import KaisaiData

from jra_tools.machine_learning.usecase.training_tool import create_score_data_matrix


def test_create_score_data_matrix(sample_kaisais: List[KaisaiData]):
    """開催データから数値データを作成するテスト.

    Args:
        sample_kaisais (List[KaisaiData]): 開催一覧

    """
    scores = create_score_data_matrix(sample_kaisais)

    assert scores.shape == (24, 18, 15)
