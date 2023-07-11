from sqlalchemy.orm import joinedload
from jrdb_model import KaisaiData


def get_kaisais(start: int, end: int) -> list[KaisaiData]:
    return (
        KaisaiData.query.filter(KaisaiData.ymd >= start, KaisaiData.ymd <= end)
        .options(joinedload("*"))
        .all()
    )
