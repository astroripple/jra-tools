"""Yahoo競馬のクローラーテスト"""
import pickle
from typing import Generator
import pytest
from aioresponses import aioresponses
from src.jra_tools.database.schedule import open_days


@pytest.fixture
def server() -> Generator[aioresponses, None, None]:
    """リクエストを受け付けるサーバーをモックする

    Yields:
        Generator[aioresponses, None, None]: _description_
    """
    with aioresponses() as m:
        with open("jra_tools/tests/yahoo_keiba.pkl", mode="rb") as f:
            m.get(
                "https://sports.yahoo.co.jp/keiba/schedule/monthly?month=12&year=2018",
                status=200,
                body=pickle.load(f),
            )
            yield m


@pytest.mark.asyncio
async def test_open_days(server: aioresponses):
    """対象の年、月に対するユニットテスト

    Args:
        server (aioresponses): モックサーバー
    """
    days = await open_days(12, 2018)

    server.assert_called_once()
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
#     assert days[-1] == 20181228
