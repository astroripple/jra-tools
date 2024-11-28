"""MysqlLoaderのユニットテスト"""

from pytest_mock import MockerFixture


def test_mysql_loader(mocker: MockerFixture):
    mock_get_kaisais = mocker.patch(
        "jra_tools.machine_learning.infrastructure.mysql_loader.get_kaisais"
    )

    from jra_tools.machine_learning.infrastructure.mysql_loader import MysqlLoader

    loader = MysqlLoader(1, 1)
    entities = loader.load()

    assert entities == []
    mock_get_kaisais.assert_called_once_with()
