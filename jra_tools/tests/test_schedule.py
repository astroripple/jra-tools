"""Yahoo競馬のクローラーテスト"""
import pickle
from pytest_mock import MockFixture
from src.jra_tools.database.schedule import annual_schedule


def test_annual_schedule(mocker: MockFixture):
    """スケジューラをテストする

    Args:
        mocker (MockFixture): モッカーオブジェクト
    """
    patched_requests = mocker.patch("src.jra_tools.database.schedule.requests")
    patched_get = patched_requests.get
    mock_response = patched_get.return_value
    with open("jra_tools/tests/yahoo_keiba.pkl", mode="rb") as f:
        mock_response.text = pickle.load(f)
        # print(mock_response.text)

    days = annual_schedule(2018)

    assert len(patched_get.call_args_list) == 12
    assert patched_get.call_args_list[0][0] == (
        "https://keiba.yahoo.co.jp/schedule/list/2018/",
        {"month": "1"},
    )
    # assert len(days) == 109
    # assert days[0] == 20180106
    # assert days[-1] == 20181228
    # assert days[54] == 20180701
