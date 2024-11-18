"""ツールを組み合わせたユースケースのテスト"""

from unittest.mock import MagicMock
from pytest_mock import MockerFixture
import pytest


@pytest.fixture
def mock_create_dataset(mocker: MockerFixture) -> MagicMock:
    """create_datasetが任意の期間で呼び出されることを確認するモック"""

    return mocker.patch("jra_tools.machine_learning.util._create_dataset")


def test_create_training_dataset(mock_create_dataset: MagicMock):
    """四半期データセットのユースケース

    Args:
        mock_create_dataset (MagicMock): モック済みcreate_dataset_from
    """
    from jra_tools.machine_learning import util

    util.create_quarter_dataset(2013, 1, 3)

    mock_create_dataset.assert_called_once_with(
        20130101,
        20130331,
        "2013_01_03",
        3,
    )


def test_create_quarter_dataset(mock_create_dataset: MagicMock):
    """四半期データセットのユースケース

    Args:
        mock_create_dataset (MagicMock): モック済みcreate_dataset_from
    """
    pass
