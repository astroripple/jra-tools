"""MysqlLoaderのユニットテスト"""

from pytest_mock import MockerFixture
from jra_tools.machine_learning.interface_adapter.ispecified_loader import (
    SpecifiedLoader,
)


def test_mysql_loader(mocker: MockerFixture):
    mock_get_kaisais = mocker.patch(
        "jra_tools.machine_learning.infrastructure.mysql_loader.get_kaisais"
    )
    # pylint: disable=import-outside-toplevel
    from jra_tools.machine_learning.infrastructure.mysql_loader import MysqlLoader

    loader = MysqlLoader(10000101, 10001001)
    entities = loader.load()

    assert isinstance(loader, SpecifiedLoader)
    assert entities == []
    mock_get_kaisais.assert_called_once_with(10000101, 10001001)
    assert loader.period == "10000101_10001001"
