"""Yahoo競馬のクローラーテスト."""

import os
import pickle
from typing import Generator

import pytest
from aiohttp.client_exceptions import ClientConnectionError
from aioresponses import aioresponses

from jra_tools.database.schedule import (
    annual_schedule,
    open_days,
    open_kaisais,
    to_kaisaikey,
)


@pytest.fixture
def server() -> Generator[aioresponses, None, None]:
    """リクエストを受け付けるサーバーをモックする.

    Yields:
        Generator[aioresponses, None, None]: _description_

    """
    file_path = os.path.join(os.path.dirname(__file__), "yahoo_keiba.pkl")
    with aioresponses() as m, open(file_path, mode="rb") as f:
        m.get(
            "https://sports.yahoo.co.jp/keiba/schedule/monthly?month=12&year=2018",
            status=200,
            body=pickle.load(f),  # noqa: S301 リポジトリ内のテストデータ
        )
        yield m


@pytest.mark.asyncio
async def test_open_days(server: aioresponses):
    """対象の年、月に対するユニットテスト.

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


@pytest.mark.asyncio
async def test_annual_schedule(server: aioresponses):
    """スケジューラをテストする.

    12の並列リクエストの内、一つでもコネクションができないとエラーが発生する.

    Args:
        server (aioresponses): モックサーバー

    """
    with pytest.raises(ClientConnectionError) as e:
        await annual_schedule(2018)

    server.assert_called()
    assert (
        str(e.value)
        == "Connection refused: GET https://sports.yahoo.co.jp/keiba/schedule/monthly?month=1&year=2018"
    )


@pytest.mark.asyncio
async def test_open_kaisais(server: aioresponses):
    """場ごとの開催日を、日付とJRDBの開催キーで返す(同じ日の複数の場は別の行).

    Args:
        server (aioresponses): モックサーバー

    """
    kaisais = await open_kaisais(12, 2018)

    server.assert_called_once()
    assert len(kaisais) == 24
    assert kaisais[:3] == [
        (20181201, "061851"),
        (20181201, "071841"),
        (20181201, "091851"),
    ]
    assert kaisais[-2:] == [(20181228, "061859"), (20181228, "091859")]


@pytest.mark.asyncio
async def test_open_kaisais_lists_substitute_day_only():
    """代替競馬は代替日だけに出る(2025年1回京都3日は2/8(土)の中止で2/10(月)に開催).

    10日目以降の日目は開催キーで16進になる(1回小倉10日 → 10251a)。
    """
    file_path = os.path.join(os.path.dirname(__file__), "yahoo_keiba_202502.html")
    with aioresponses() as m, open(file_path, encoding="utf-8") as f:
        m.get(
            "https://sports.yahoo.co.jp/keiba/schedule/monthly?month=2&year=2025",
            status=200,
            body=f.read(),
        )
        kaisais = await open_kaisais(2, 2025)

    kyoto = [k for k in kaisais if k[1].startswith("08")]
    assert (20250210, "082513") in kyoto
    assert all(day != 20250208 for day, _ in kyoto)
    assert (20250223, "10251a") in kaisais
    assert len(kaisais) == 24


@pytest.mark.parametrize(
    ("groups", "kaisaikey"),
    [
        (("18", "06", "05", "01"), "061851"),
        (("25", "08", "01", "03"), "082513"),
        (("25", "10", "01", "10"), "10251a"),
        (("25", "05", "02", "12"), "05252c"),
    ],
)
def test_to_kaisaikey(groups: tuple, kaisaikey: str):
    """Yahoo競馬の年・場・回・日目を、JRDBの開催キー(日目は16進)にする."""
    assert to_kaisaikey(*groups) == kaisaikey


def test_to_kaisaikey_rejects_values_out_of_one_digit():
    """回・日目が開催キーの1桁に収まらなければエラー."""
    with pytest.raises(ValueError, match="開催キーにできない"):
        to_kaisaikey("25", "05", "10", "01")
