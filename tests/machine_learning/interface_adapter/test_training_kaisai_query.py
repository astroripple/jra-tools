"""トレーニング用ローダーのテスト"""

from pytest_mock import MockerFixture


def test_training_kaisai_query(mocker: MockerFixture):
    """loadが意図した期間で呼び出されることを確認する

    Args:
        mocker (MockerFixture): _description_
    """

    mock_load = mocker.patch("jra_tools.machine_learning.kaisai_loader.load")

    from jra_tools.machine_learning.kaisai_loader import IQuery
    from jra_tools.machine_learning.training_kaisai_query import TrainingKaisaiQuery

    query = TrainingKaisaiQuery(2000, 2100)
    query.load()

    assert isinstance(query, IQuery)
    mock_load.assert_called_once_with(20000101, 21001231)
