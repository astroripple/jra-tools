"""開催データ大量ロードモジュールのユニットテスト"""

from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from pytest import fixture


@fixture
def mock_get_kaisais(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("jra_tools.machine_learning.kaisai_loader.get_kaisais")


def test_load(mock_get_kaisais: MagicMock):
    """get_kaisaisを複数回に分けで呼び出すことを確認する"""
    # pylint: disable=import-outside-toplevel
    from jra_tools.machine_learning.kaisai_loader import load

    load(20120501, 20150925)

    expected_args = (
        (20120501, 20121231),
        (20130101, 20131231),
        (20140101, 20141231),
        (20150101, 20150925),
    )
    assert mock_get_kaisais.call_count == 4
    for call, args in zip(mock_get_kaisais.call_args_list, expected_args):
        assert call.args == args


def test_load_in_oneyear(mock_get_kaisais: MagicMock):
    """get_kaisaisを1回呼び出すことを確認する"""
    # pylint: disable=import-outside-toplevel
    from jra_tools.machine_learning.kaisai_loader import load

    load(20120501, 20120925)

    expected_args = ((20120501, 20120925),)
    assert mock_get_kaisais.call_count == 1
    for call, args in zip(mock_get_kaisais.call_args_list, expected_args):
        assert call.args == args
