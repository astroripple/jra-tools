"""カテゴリデータ取得のユニットテスト"""

from typing import List
from jrdb_model import KaisaiData
from jra_tools.machine_learning.usecase.category_data import get_category_data


def test_get_category_data(sample_kaisais: List[KaisaiData]):
    """カテゴリカルデータを取得するテスト

    Args:
        sample_kaisais (List[KaisaiData]): 開催一覧
    """

    categories = get_category_data(sample_kaisais)

    assert categories.shape == (24, 18, 75)
