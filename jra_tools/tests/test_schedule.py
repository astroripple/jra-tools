"""Yahoo競馬のクローラーテスト"""
from pytest_mock import MockFixture
from src.jra_tools.database.schedule import annual_schedule


def test_annual_schedule(mocker: MockFixture):
    """スケジューラをテストする

    Args:
        mocker (MockFixture): モッカーオブジェクト
    """
    patched_request = mocker.patch("src.jra_tools.database.schedule.requests")

    days = annual_schedule(2018)

    assert len(days) == 109
    assert days[0] == 20180106
    assert days[-1] == 20181228
    assert days[54] == 20180701
