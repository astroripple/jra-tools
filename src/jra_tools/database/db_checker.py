"""DBに登録済みの開催日を確認する."""

import asyncio

from jrdb_model import KaisaiData, create_app

from . import schedule


def missing_days(year):
    """指定年の開催日のうち、DBに未登録の日付を返す.

    開催日はYahoo競馬の年間スケジュール(代替日を含む)。同期の関数なので、イベントループの中からは呼べない。
    """
    open_days = asyncio.run(schedule.annual_schedule(year))
    return sorted(set(open_days) - set(db_days(year)))


def db_days(year):
    """指定年の開催日のうち、DBに登録済みの日付を返す."""
    start_date = int(f"{year}0101")
    end_date = int(f"{year}1231")
    app = create_app()
    with app.app_context():
        kaisais = KaisaiData.query.filter(
            KaisaiData.ymd >= start_date, KaisaiData.ymd <= end_date
        ).all()
    return sorted({k.ymd for k in kaisais})
