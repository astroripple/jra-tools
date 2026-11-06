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
