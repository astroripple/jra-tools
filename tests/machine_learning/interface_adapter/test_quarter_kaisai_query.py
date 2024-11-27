"""四半期用クエリのテスト"""

from typing import Callable
from dataclasses import dataclass
from pytest_mock import MockerFixture


@dataclass
class MockSpecifiedLoader:
    start: int
    end: int
    load: Callable

    @property
    def period(self) -> str:
        return "sample_period"


def test_quarter_kaisai_query(mocker: MockerFixture):
    """loadが意図した期間で呼び出されることを確認する

    Args:
        mocker (MockerFixture): _description_
    """
    from jra_tools.machine_learning.usecase.iquery import (
        IQuery,
    )
    from jra_tools.machine_learning.interface_adapter.quarter_kaisai_query import (
        QuarterKaisaiQuery,
    )

    mock_loader_factory = mocker.patch("test_quarter_kaisai_query.MockSpecifiedLoader")
    mock_loader = mock_loader_factory.return_value
    mock_loader.load.assert_not_called()

    query = QuarterKaisaiQuery(2000, 2, MockSpecifiedLoader)
    query.load()

    assert isinstance(query, IQuery)
    mock_loader_factory.assert_called_once_with(20000401, 20000630)
    mock_loader.load.assert_called_once_with()
