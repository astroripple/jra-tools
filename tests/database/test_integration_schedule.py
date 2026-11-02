"""Yahoo競馬のクローラー結合テスト."""

from asyncio import run

from jra_tools.database.schedule import open_days, open_kaisais


def test_open_days():
    """対象年、月の開催日をWebサイトに接続してテストする."""
    days = run(open_days(1, 2018))
    assert len(days) == 9
    assert days == [
        20180106,
        20180107,
        20180108,
        20180113,
        20180114,
        20180120,
        20180121,
        20180127,
        20180128,
    ]


def test_open_kaisais():
    """対象年、月の場ごとの開催日を、Webサイトに接続してテストする(ページの作りが変わっていないこと)."""
    kaisais = run(open_kaisais(1, 2018))
    assert {day for day, _ in kaisais} == set(run(open_days(1, 2018)))
    assert (20180106, "061811") in kaisais
    assert (20180106, "081811") in kaisais
