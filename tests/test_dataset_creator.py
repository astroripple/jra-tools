"""データセット作成関数のユニットテスト"""

from typing import List
from dataclasses import dataclass
from unittest.mock import MagicMock
from jrdb_model import KaisaiData
from jra_tools.machine_learning.dataset_creator import create_dataset_from


@dataclass
class DummyCreator:
    kaisais: List[KaisaiData]

    save = MagicMock()


def test_create_dataset_from(sample_kaisais):
    create_dataset_from(
        sample_kaisais, "test_period", False, DummyCreator, DummyCreator
    )

    assert DummyCreator.save.call_count == 2
