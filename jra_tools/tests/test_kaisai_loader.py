"""開催データ大量ロードモジュールのユニットテスト"""

from pytest_mock import MockerFixture


def test_load(mocker: MockerFixture):
    """get_kaisaisを複数回に分けで呼び出すことを確認する"""
    mock_kaisais = mocker.patch(
        "src.jra_tools.machine_learning.kaisai_loader.get_kaisais"
    )

    for call in mock_kaisais.mock_calls:
        assert call.call_list == []
