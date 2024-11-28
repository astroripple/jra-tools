"""トレーニング用ローダーのテスト"""

from jra_tools.machine_learning.usecase.iquery import IQuery
from jra_tools.machine_learning.interface_adapter.training_kaisai_query import (
    TrainingKaisaiQuery,
)
from pytest_mock import MockerFixture


def test_training_kaisai_query(mocker: MockerFixture):
    """loadが意図した期間で呼び出されることを確認する

    Args:
        mocker (MockerFixture): _description_
    """
    mock_loader_factory = mocker.patch("mock_specified_loader.MockSpecifiedLoader")
    mock_loader = mock_loader_factory.return_value
    mock_loader.load.assert_not_called()
    from mock_specified_loader import MockSpecifiedLoader

    query = TrainingKaisaiQuery(2000, 2100, MockSpecifiedLoader)
    query.load()

    assert isinstance(query, IQuery)
    mock_loader_factory.assert_called_once_with(20000101, 21001231)
    mock_loader.load.assert_called_once_with()
    assert query.period == "2000_2100"
