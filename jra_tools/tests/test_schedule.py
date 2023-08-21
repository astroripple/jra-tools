"""Yahoo競馬のクローラーテスト"""
import pickle
from typing import Generator
from unittest.mock import MagicMock
from pytest import fixture
from pytest_mock import MockFixture
from src.jra_tools.database.schedule import annual_schedule, open_days


@fixture
def patched_get(mocker: MockFixture) -> Generator[MagicMock, None, None]:
    """requestsモジュールをパッチしておく

    Args:
        mocker (MockFixture): モッカー

    Yields:
        _type_: request.get
    """
    patched_requests = mocker.patch("src.jra_tools.database.schedule.requests")
    patched_get = patched_requests.get
    mock_response = patched_get.return_value
    with open("jra_tools/tests/yahoo_keiba.pkl", mode="rb") as f:
        mock_response.text = pickle.load(f)
    yield patched_get


def test_open_days(patched_get: MagicMock):
    """対象の年、月に対するユニットテスト

    Args:
        patched_get (MagicMock): パッチ済みのrequests.get
    """
    days = open_days(12, 2018)

    assert patched_get.call_args_list[0][0] == (
        "https://sports.yahoo.co.jp/keiba/schedule/monthly",
        {"year": "2018", "month": "12"},
    )
    assert days == [
        20181201,
        20181202,
        20181208,
        20181209,
        20181215,
        20181216,
        20181222,
        20181223,
        20181228,
    ]


# def test_annual_schedule(patched_get):
#     """スケジューラをテストする

#     Args:
#         mocker (MockFixture): モッカーオブジェクト
#     """

#     days = annual_schedule(2018)

#     assert len(patched_get.call_args_list) == 12
#     assert patched_get.call_args_list[0][0] == (
#         "https://keiba.yahoo.co.jp/schedule/list/2018/",
#         {"month": "1"},
#     )
#     # assert len(days) == 109
#     # assert days[0] == 20180106
#     assert days[-1] == 20181228
#     # assert days[54] == 20180701
