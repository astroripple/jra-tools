"""開催データ大量ロードモジュールのユニットテスト"""

from pytest_mock import MockerFixture


def test_load(mocker: MockerFixture):
    """get_kaisaisを複数回に分けで呼び出すことを確認する"""
    mock_get_kaisais = mocker.patch(
        "jra_tools.machine_learning.kaisai_loader.get_kaisais"
    )
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
