"""開催日の登録漏れの確認のテスト."""

from pathlib import Path
from typing import List, Tuple

import pytest
from jrdb_model import db
from pytest_mock import MockerFixture
from sqlalchemy import String, create_engine

from jra_tools.database import db_checker


def _kaisai_db(
    rows: List[Tuple[str, int]], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """開催(開催キー、日付)を登録したSQLiteのDBを、環境変数DBに設定する(create_appが読む).

    必須のほかの列は、型に合わせた仮の値にする(この確認は開催キーと日付しか読まない)。
    """
    url = f"sqlite:///{tmp_path / 'kaisai.db'}"
    engine = create_engine(url)
    db.metadata.create_all(engine)
    table = db.metadata.tables["kaisai"]
    filler = {
        c.name: "" if isinstance(c.type, String) else 0
        for c in table.columns
        if not c.nullable and not c.primary_key
    }
    with engine.begin() as connection:
        connection.execute(
            table.insert(),
            [{**filler, "kaisaikey": key, "ymd": ymd} for key, ymd in rows],
        )
    engine.dispose()
    monkeypatch.setenv("DB", url)


def test_db_days_returns_registered_days_of_the_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """指定年の開催の日付を、重複なしで昇順に返す(前後の年は含めない)."""
    _kaisai_db(
        [
            ("062451", 20241228),
            ("062511", 20250105),
            ("082511", 20250105),
            ("082513", 20250210),
            ("062611", 20260104),
        ],
        tmp_path,
        monkeypatch,
    )

    assert db_checker.db_days(2025) == [20250105, 20250210]


def test_missing_days_returns_open_days_not_registered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
):
    """Yahoo競馬の開催日のうち、開催の登録がない日を昇順に返す.

    年間スケジュールはasyncなので、同期の関数の中で最後まで実行する。
    """
    _kaisai_db([("062511", 20250105), ("082513", 20250210)], tmp_path, monkeypatch)
    schedule = mocker.patch(
        "jra_tools.database.schedule.annual_schedule",
        mocker.AsyncMock(return_value=[20250210, 20250208, 20250105, 20250209]),
    )

    assert db_checker.missing_days(2025) == [20250208, 20250209]
    schedule.assert_awaited_once_with(2025)


def test_missing_days_is_empty_when_all_days_are_registered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
):
    """開催日がすべて登録済みなら空."""
    _kaisai_db([("062511", 20250105), ("082513", 20250210)], tmp_path, monkeypatch)
    mocker.patch(
        "jra_tools.database.schedule.annual_schedule",
        mocker.AsyncMock(return_value=[20250105, 20250210]),
    )

    assert db_checker.missing_days(2025) == []


def test_missing_kaisais_finds_a_missing_venue_on_a_registered_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
):
    """同じ日のほかの場が登録済みでも、未登録の場の開催を返す."""
    _kaisai_db(
        [("052513", 20250208), ("102515", 20250208), ("082513", 20250210)],
        tmp_path,
        monkeypatch,
    )
    mocker.patch(
        "jra_tools.database.schedule.annual_kaisais",
        mocker.AsyncMock(
            return_value=[
                (20250208, "052513"),
                (20250208, "102515"),
                (20250209, "052514"),
                (20250209, "082514"),
                (20250210, "082513"),
            ]
        ),
    )

    assert db_checker.missing_kaisais(2025) == [
        (20250209, "052514"),
        (20250209, "082514"),
    ]


def test_missing_kaisais_ignores_the_cancelled_day_of_a_substitute_race(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
):
    """途中で中止して代替日に残りを開催した場合、DBの中止日の行は未登録の判定に関係しない.

    2011年1回小倉7日はDBに2/12(中止の日)と2/14(代替日)の2行、Yahoo競馬には2/14だけ。
    """
    _kaisai_db([("101117", 20110212), ("101117", 20110214)], tmp_path, monkeypatch)
    mocker.patch(
        "jra_tools.database.schedule.annual_kaisais",
        mocker.AsyncMock(return_value=[(20110214, "101117")]),
    )

    assert db_checker.missing_kaisais(2011) == []
