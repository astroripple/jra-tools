from horseview.horsemodel import KaisaiData
import schedule


def missing_days(year):
    open_days = schedule.annual_schedule(year)
    return sorted(set(open_days) - set(db_days(year)))


def db_days(year):
    start_date = int("{}0101".format(year))
    end_date = int("{}1231".format(year))
    kaisais = KaisaiData.query.filter(
        KaisaiData.ymd >= start_date, KaisaiData.ymd <= end_date
    ).all()
    return sorted(set([k.ymd for k in kaisais]))
