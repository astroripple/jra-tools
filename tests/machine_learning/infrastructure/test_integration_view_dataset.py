"""ビューから読むデータセットの結合テスト. 環境変数TEST_POSTGRESのPostgresを使う(なければ飛ばす)."""

import dataclasses
import os
from typing import Iterator, List

import numpy as np
import pytest
from jrdb_model import KaisaiData, db
from sqlalchemy import Engine, create_engine, text

from jra_tools.machine_learning.entity.feature_spec import (
    FeatureSpec,
    default_feature_spec,
    parse_feature_spec,
)
from jra_tools.machine_learning.infrastructure.sql_dataset import load_dataset
from jra_tools.machine_learning.infrastructure.view_dataset import (
    load_view_dataset,
    load_view_input,
    pin_view_digest,
    predict_finish_probabilities,
    read_view_frame,
    view_digest,
)
from tests.machine_learning.infrastructure.conftest import sample_rows

pytestmark = pytest.mark.skipif(
    "TEST_POSTGRES" not in os.environ, reason="TEST_POSTGRESがない"
)

SCHEMAS = ("staging", "model", "features")

# 今の本番モデルの23次元を、そのまま列にしたビュー(ORMの経路と同じ結合)
ENTRIES_SQL = """
create view features.entries_v1 as
select r.racehorsekey, r.racekey, model.jrdb_date(k.ymd) as race_date, r.num as umaban,
       k.turf_baba_in, r.idm, r.jockey_score, r.info_score, r.train_score,
       r.trainer_score, r.train_code, r.jockey_rate_rentai, r.kakutoku_money,
       r.ls_score_order, r.up_score_order, r.expect_jokey_win_rate,
       r.expect_jokey_rentai_rate, c.waku_win_rate, c.waku_rentai_rate, r.waku
from staging.kaisai k
join staging.bangumi b on b.kaisaikey = k.kaisaikey and b.ymd = k.ymd
join staging.racehorse r on r.racekey = b.racekey
left join staging.calculated_score c on c.racehorsekey = r.racehorsekey
"""
LABELS_SQL = """
create view features.labels_v1 as
select r.racehorsekey, s.order_of_arrival as finish_order, ri.win1_num, ri.win1_ret
from staging.racehorse r
join staging.seiseki s on s.racehorsekey = r.racehorsekey
left join staging.returninfo ri on ri.racekey = r.racekey
"""
FUNCTION_SQL = """
create function model.jrdb_date(v integer) returns date
language sql immutable return to_date(v::text, 'YYYYMMDD')
"""


def _view_spec() -> FeatureSpec:
    """今の本番モデルの仕様を、entries_v1から読む形に書き換えたもの."""
    data = {
        "name": "resnet4_view",
        "max_horses": 18,
        "source": "features.entries_v1",
        "groups": [
            {
                "name": group.name,
                "transform": str(group.transform),
                "features": [
                    {
                        "name": f.name,
                        "source": f.column,
                        "encode": str(f.encode),
                        "size": f.size,
                        "base": f.base,
                    }
                    for f in group.features
                ],
            }
            for group in default_feature_spec().groups
        ],
    }
    return parse_feature_spec(data)


def _drop(engine: Engine) -> None:
    with engine.begin() as conn:
        for schema in SCHEMAS:
            conn.exec_driver_sql(f"drop schema if exists {schema} cascade")


@pytest.fixture
def engine(sample_kaisais: List[KaisaiData]) -> Iterator[Engine]:
    """sample_kaisaisをstagingに登録し、entries_v1・labels_v1を作ったPostgres."""
    engine = create_engine(
        os.environ["TEST_POSTGRES"],
        connect_args={"options": "-csearch_path=staging"},
    )
    _drop(engine)
    with engine.begin() as conn:
        for schema in SCHEMAS:
            conn.exec_driver_sql(f"create schema {schema}")
        db.metadata.create_all(conn)
        # seisekiの外部キー(seisekirace)の行はサンプルにないため、制約を効かせずに入れる
        conn.exec_driver_sql("set local session_replication_role = replica")
        for name, rows in sample_rows(sample_kaisais).items():
            conn.execute(db.metadata.tables[name].insert(), rows)
        conn.exec_driver_sql(FUNCTION_SQL)
        conn.exec_driver_sql(ENTRIES_SQL)
        conn.exec_driver_sql(LABELS_SQL)
    yield engine
    _drop(engine)
    engine.dispose()


def _period(kaisais: List[KaisaiData]):
    days = [kaisai.ymd for kaisai in kaisais]
    return min(days), max(days)


def test_same_as_sql_dataset(engine: Engine, sample_kaisais: List[KaisaiData]):
    """同じDBから、今の経路(load_dataset)と同じ入力・正解ラベル・払戻ができる."""
    start, end = _period(sample_kaisais)
    with engine.connect() as conn:
        expected = load_dataset(conn, default_feature_spec(), start, end)
    spec = pin_view_digest(engine, _view_spec())

    actual = load_view_dataset(engine, spec, start, end)

    assert len(actual.racekeys) == 24
    assert list(actual.racekeys) == list(expected.racekeys)
    # レースごとの標準化の計算の順が違うため、浮動小数点の誤差の範囲で一致
    assert np.allclose(actual.x, expected.x, rtol=0, atol=1e-9)
    for a, e in zip(actual.labels, expected.labels, strict=True):
        assert np.array_equal(a, e)
    assert np.array_equal(actual.payout, expected.payout)


def test_load_view_input(engine: Engine, sample_kaisais: List[KaisaiData]):
    """開催日の入力が、学習用のデータセットのその日の分と同じになる."""
    spec = pin_view_digest(engine, _view_spec())
    start, end = _period(sample_kaisais)
    dataset = load_view_dataset(engine, spec, start, end)
    ymd = sample_kaisais[0].ymd
    day_racekeys = {
        race.racekey for k in sample_kaisais if k.ymd == ymd for race in k.races
    }

    inputs = load_view_input(engine, spec, ymd)

    assert set(inputs.racekeys) == day_racekeys
    index = [list(dataset.racekeys).index(key) for key in inputs.racekeys]
    assert np.array_equal(inputs.x, dataset.x[index])


def test_digest_is_per_view(engine: Engine):
    """関係のないビューを足してもハッシュは変わらず、依存する定義を変えると変わる."""
    with engine.connect() as conn:
        before = view_digest(conn, "features.entries_v1")
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create view features.entries_v2 as select racehorsekey from features.entries_v1"
        )
    with engine.connect() as conn:
        assert view_digest(conn, "features.entries_v1") == before
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create or replace function model.jrdb_date(v integer) returns date"
            " language sql immutable return to_date(v::text, 'YYYYMMDD') + 0"
        )
    with engine.connect() as conn:
        assert view_digest(conn, "features.entries_v1") != before


def test_digest_ignores_search_path(engine: Engine):
    """接続のsearch_pathが違っても、同じハッシュになる."""
    other = create_engine(os.environ["TEST_POSTGRES"])
    try:
        with engine.connect() as a, other.connect() as b:
            assert view_digest(a, "features.entries_v1") == view_digest(
                b, "features.entries_v1"
            )
            assert a.execute(text("show search_path")).scalar() == "staging"
    finally:
        other.dispose()


def test_digest_mismatch(engine: Engine, sample_kaisais: List[KaisaiData]):
    """学習時とビューの定義が違うと、読み込みを止める."""
    spec = pin_view_digest(engine, _view_spec())
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "create or replace function model.jrdb_date(v integer) returns date"
            " language sql immutable return to_date(v::text, 'YYYYMMDD') + 0"
        )

    with pytest.raises(ValueError, match="学習時と違います"):
        load_view_input(engine, spec, sample_kaisais[0].ymd)


def test_digest_required(engine: Engine, sample_kaisais: List[KaisaiData]):
    """view_digestのない仕様では読まない."""
    with pytest.raises(ValueError, match="view_digestがありません"):
        load_view_input(engine, _view_spec(), sample_kaisais[0].ymd)


def test_missing_column(engine: Engine, sample_kaisais: List[KaisaiData]):
    """ビューにない列を仕様が使うと止める."""
    spec = pin_view_digest(engine, _view_spec())
    group = dataclasses.replace(
        spec.groups[0],
        features=(
            *spec.groups[0].features,
            dataclasses.replace(spec.groups[0].features[0], source="no_such"),
        ),
    )
    spec = dataclasses.replace(spec, groups=(group, *spec.groups[1:]))

    with pytest.raises(ValueError, match=r"列がありません: \['no_such'\]"):
        load_view_input(engine, spec, sample_kaisais[0].ymd)


@pytest.mark.parametrize(
    ("table", "key", "message"),
    [
        (
            "calculated_score",
            "racehorsekey",
            "features.entries_v1.waku_win_rateが値なし",
        ),
        ("seiseki", "racehorsekey", "成績がありません"),
        ("returninfo", "racekey", "払戻データがありません"),
    ],
)
def test_missing_row(
    engine: Engine, sample_kaisais: List[KaisaiData], table, key, message
):
    """値のない出走があると止める(ORMの経路の「行がなければエラー」と同じ)."""
    horse = sample_kaisais[0].races[0].racehorses[0]
    spec = pin_view_digest(engine, _view_spec())
    with engine.begin() as conn:
        conn.execute(
            text(f"delete from staging.{table} where {key} = :v"),  # noqa: S608 テストの固定値
            {"v": getattr(horse, key)},
        )
    start, end = _period(sample_kaisais)

    with pytest.raises(ValueError, match=message):
        load_view_dataset(engine, spec, start, end)


def test_view_spec_rejected_by_orm_path(engine: Engine, sample_kaisais):
    """ビューから読む仕様は、今の経路では使えない."""
    start, end = _period(sample_kaisais)
    with engine.connect() as conn, pytest.raises(ValueError, match="ビュー"):
        load_dataset(conn, _view_spec(), start, end)


def test_read_view_frame(engine: Engine, sample_kaisais: List[KaisaiData]):
    """1頭1行の表を、開催日・レースキー・馬番の順で読める. 推論ではラベルを読まない."""
    spec = pin_view_digest(engine, _view_spec())
    start, end = _period(sample_kaisais)

    frame = read_view_frame(engine, spec, start, end)
    inputs = read_view_frame(engine, spec, start, end, labels=None)

    horses = sum(len(r.racehorses) for k in sample_kaisais for r in k.races)
    assert len(frame) == horses
    assert {"finish_order", "win1_num", "win1_ret"} <= set(frame.columns)
    assert "_label" not in frame.columns
    assert "finish_order" not in inputs.columns
    assert frame[["racekey", "umaban"]].equals(inputs[["racekey", "umaban"]])
    assert frame["racekey"].is_monotonic_increasing or len(sample_kaisais) > 1


def test_label_column_as_feature(engine: Engine, sample_kaisais: List[KaisaiData]):
    """確定後の値(ラベルの列)を入力に使う仕様は止める."""
    spec = pin_view_digest(engine, _view_spec())
    feature = dataclasses.replace(spec.groups[0].features[0], source="finish_order")
    group = dataclasses.replace(spec.groups[0], features=(feature,))
    spec = dataclasses.replace(spec, groups=(group, *spec.groups[1:]))

    with pytest.raises(ValueError, match="ラベルの列は入力に使えません"):
        load_view_input(engine, spec, sample_kaisais[0].ymd)


class _FakeModel:
    """出力の値がレースの位置・枠で決まるモデル. 受け取った入力を残す."""

    def __init__(self):
        self.x = None

    def predict(self, x, verbose="auto"):
        self.x = x
        races, slots = x.shape[0], x.shape[1]
        base = np.arange(races)[:, None] * 100 + np.arange(slots)[None, :]
        return {
            "activation_4": base + 0.1,
            "activation_5": base + 0.2,
            "activation_6": base + 0.3,
        }


def test_predict_finish_probabilities(engine: Engine, sample_kaisais: List[KaisaiData]):
    """出走馬ごとに、その馬のレース・馬番の枠の確率を返す. 入力はload_view_inputと同じ."""
    spec = pin_view_digest(engine, _view_spec())
    ymd = sample_kaisais[0].ymd
    inputs = load_view_input(engine, spec, ymd)
    model = _FakeModel()

    actual = predict_finish_probabilities(engine, spec, ymd, model)

    assert np.array_equal(model.x, inputs.x)
    horses = [
        (h.racehorsekey, race.racekey, h.num)
        for k in sample_kaisais
        if k.ymd == ymd
        for race in k.races
        for h in race.racehorses
    ]
    assert len(actual) == len(horses)
    racekeys = list(inputs.racekeys)
    expected = {
        key: tuple(racekeys.index(racekey) * 100 + num - 1 + d for d in (0.1, 0.2, 0.3))
        for key, racekey, num in horses
    }
    assert {key: probs for key, *probs in actual} == {
        k: list(v) for k, v in expected.items()
    }
    assert all(isinstance(v, float) for row in actual for v in row[1:])


def test_predict_finish_probabilities_no_races(engine: Engine):
    """出走のない日は、モデルを呼ばずに空を返す."""
    spec = pin_view_digest(engine, _view_spec())
    model = _FakeModel()

    assert predict_finish_probabilities(engine, spec, 19000101, model) == []
    assert model.x is None
