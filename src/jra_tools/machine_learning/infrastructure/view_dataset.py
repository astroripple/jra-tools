"""featuresのビュー(分析用のPostgres)から、学習用のデータセット・推論の入力を作る.

仕様の最上位のsourceのビューを読む。ビューの列の契約:

- 入力のビュー(仕様のsource。例: features.entries_v1): 1頭1行で、レースの前に分かる列だけ。
  racehorsekey・racekey・race_date(date)・umabanと、仕様の特徴量の列
- ラベルのビュー(例: features.labels_v1): 1頭1行の確定後の値。
  racehorsekey・finish_order・win1_num・win1_ret

読み込むたびに、ビューの定義のハッシュ(view_digest)を仕様のview_digestと照合し、
違えば止める。ハッシュは、そのビューと、依存するビュー・関数の定義(Postgresが保存している形)
から作るため、関係のないビューを足したり変えたりしても変わらない。
学習の前にpin_view_digestで今のハッシュを仕様に書き、その仕様をモデルと一緒に保存する。

読んだ表(1頭1行のDataFrame)はread_view_frameでそのまま得られる。テンソルへの組み立ては
frame_datasetが行う。
"""

import dataclasses
from datetime import date
from typing import Any, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import Connection, Engine, text

from jra_tools.machine_learning.entity.feature_spec import FeatureSpec
from jra_tools.machine_learning.infrastructure.mysql_loader import _periods, _to_date
from jra_tools.machine_learning.usecase.frame_dataset import (
    InputDataset,
    frame_to_dataset,
    frame_to_input,
)
from jra_tools.machine_learning.usecase.table_dataset import TableDataset

# 入力のビューに必要な列
ENTRY_COLUMNS = ("racehorsekey", "racekey", "race_date", "umaban")
# ラベルのビューに必要な列
LABEL_COLUMNS = ("racehorsekey", "finish_order", "win1_num", "win1_ret")
# 表でラベルのビューの行の有無を表す列
_LABEL_MARKER = "_label"
# 既定のラベルのビュー
DEFAULT_LABELS = "features.labels_v1"
# モデルの出力のうち、1着・2着・3着の確率(PredictFactoryと同じ)
PROBABILITY_OUTPUTS = ("activation_4", "activation_5", "activation_6")

# ビューと、依存するビュー・関数を、pg_dependでたどって定義を集める。
# 表(staging)は名前だけを含める。search_pathはpg_catalogにしてから流す(名前をすべて
# スキーマ付きで出すため。接続ごとのsearch_pathでハッシュが変わらないように)。
_DIGEST_SQL = """
with recursive deps(oid, kind) as (
  select cast(:view as regclass)::oid, 'r'
  union
  select d.refobjid,
         case d.refclassid when 'pg_class'::regclass then 'r' else 'f' end
  from deps
  join pg_depend d
    on (deps.kind = 'r' and d.classid = 'pg_rewrite'::regclass
        and d.objid in (select rw.oid from pg_rewrite rw where rw.ev_class = deps.oid))
    or (deps.kind = 'f' and d.classid = 'pg_proc'::regclass and d.objid = deps.oid)
  where d.refclassid in ('pg_class'::regclass, 'pg_proc'::regclass)
    and d.refobjid <> deps.oid
)
select encode(sha256(convert_to(string_agg(def, chr(10) order by name), 'UTF8')), 'hex')
from (
  select distinct
    case kind when 'f' then oid::regprocedure::text else oid::regclass::text end as name,
    case
      when kind = 'f' then pg_get_functiondef(oid)
      when (select relkind from pg_class c where c.oid = deps.oid) in ('v', 'm')
        then 'view ' || oid::regclass::text || chr(10) || pg_get_viewdef(oid)
      else 'table ' || oid::regclass::text
    end as def
  from deps
) t
"""


def view_digest(connection: Connection, view: str) -> str:
    """ビューの定義のハッシュ.

    ビューと、依存するビュー・関数の定義から作る。空白やコメントだけの違いでは変わらない
    (Postgresが保存した形から作るため)。Postgresのメジャーバージョンを上げると、
    保存した形の出し方が変わり、ハッシュが変わることがある。

    Args:
        connection (Connection): Postgresの接続
        view (str): 「スキーマ.ビュー名」

    Raises:
        ValueError: ビューがない場合

    Returns:
        str: SHA-256の16進数

    """
    _check_exists(connection, view)
    search_path = connection.execute(text("select current_setting('search_path')"))
    previous = search_path.scalar()
    connection.execute(text("select set_config('search_path', 'pg_catalog', true)"))
    try:
        return connection.execute(text(_DIGEST_SQL), {"view": view}).scalar_one()
    finally:
        connection.execute(
            text("select set_config('search_path', :p, true)"), {"p": previous}
        )


def pin_view_digest(engine: Engine, spec: FeatureSpec) -> FeatureSpec:
    """仕様のview_digestを、今のビューのハッシュにした仕様を返す(学習の前に使う).

    Args:
        engine (Engine): Postgresのエンジン
        spec (FeatureSpec): ビューから読む仕様

    Returns:
        FeatureSpec: view_digestを書いた仕様

    """
    view = _view_of(spec)
    with engine.connect() as connection:
        return dataclasses.replace(spec, view_digest=view_digest(connection, view))


def check_view(connection: Connection, spec: FeatureSpec) -> None:
    """ビューに仕様の列があり、定義が学習時と同じかを確かめる.

    Args:
        connection (Connection): Postgresの接続
        spec (FeatureSpec): ビューから読む仕様

    Raises:
        ValueError: 列が足りない、または定義が学習時と違う場合

    """
    view = _view_of(spec)
    if spec.view_digest is None:
        raise ValueError(
            f"仕様{spec.name}にview_digestがありません(pin_view_digestで書いてください)"
        )
    _check_columns(connection, view, [*ENTRY_COLUMNS, *_columns(spec)])
    digest = view_digest(connection, view)
    if digest != spec.view_digest:
        raise ValueError(
            f"ビュー{view}の定義が、仕様{spec.name}の学習時と違います"
            f"(今{digest[:12]}、学習時{spec.view_digest[:12]})。"
            "仕様を書き直すか、ビューの版を上げてください"
        )


def load_view_input(engine: Engine, spec: FeatureSpec, ymd: int) -> InputDataset:
    """開催日の推論の入力を、ビューから作る.

    Args:
        engine (Engine): Postgresのエンジン
        spec (FeatureSpec): ビューから読む仕様(view_digestがあること)
        ymd (int): 開催日(YYYYMMDD)

    Returns:
        InputDataset: 入力と、各レースのレースキー。レースはレースキーの順

    """
    return frame_to_input(read_view_frame(engine, spec, ymd, ymd, labels=None), spec)


def predict_finish_probabilities(
    engine: Engine, spec: FeatureSpec, ymd: int, model: Any
) -> List[Tuple[str, float, float, float]]:
    """開催日の出走馬ごとの1着・2着・3着の確率を、ビューの入力からモデルで出す.

    確率だけを素の値で返す(連対率・オッズなどはPostgresのビューで出す)。
    出走馬の並びは、ビューを読んだ順(開催日・レースキー・馬番)。

    Args:
        engine (Engine): Postgresのエンジン
        spec (FeatureSpec): ビューから読む仕様(view_digestがあること)
        ymd (int): 開催日(YYYYMMDD)
        model (Any): 推論のモデル。predict(x)が、PROBABILITY_OUTPUTSの各名前に
            (レース, max_horses)の確率を持つdictを返すこと(Kerasのモデル・TFSMLayer)

    Returns:
        List[Tuple[str, float, float, float]]: (racehorsekey, 1着, 2着, 3着の確率)。
            その日に出走がなければ空

    """
    frame = read_view_frame(engine, spec, ymd, ymd, labels=None)
    if frame.empty:
        return []
    inputs = frame_to_input(frame, spec)
    preds = model.predict(inputs.x, verbose=0)
    # 各出走馬の、入力のレースの位置と枠(馬番 - 1)
    race = pd.Index(inputs.racekeys).get_indexer(frame["racekey"])
    slot = frame["umaban"].to_numpy(dtype=int) - 1
    probs = [np.asarray(preds[name])[race, slot] for name in PROBABILITY_OUTPUTS]
    return [
        (key, float(p1), float(p2), float(p3))
        for key, p1, p2, p3 in zip(frame["racehorsekey"], *probs, strict=True)
    ]


def load_view_dataset(
    engine: Engine,
    spec: FeatureSpec,
    start: int,
    end: int,
    labels: str = DEFAULT_LABELS,
) -> TableDataset:
    """期間内の学習用のデータセットを、ビューから作る. 1年ずつ読み込む.

    Args:
        engine (Engine): Postgresのエンジン
        spec (FeatureSpec): ビューから読む仕様(view_digestがあること)
        start (int): 開始日(YYYYMMDD)
        end (int): 終了日(YYYYMMDD)
        labels (str): ラベルのビュー

    Returns:
        TableDataset: 学習用のデータセット。レースは開催日・レースキーの順

    """
    return frame_to_dataset(read_view_frame(engine, spec, start, end, labels), spec)


def read_view_frame(
    engine: Engine,
    spec: FeatureSpec,
    start: int,
    end: int,
    labels: Optional[str] = DEFAULT_LABELS,
) -> pd.DataFrame:
    """期間内の出走を、1頭1行の表で読む. 1年ずつ、1年ごとに1トランザクションで読む.

    Args:
        engine (Engine): Postgresのエンジン
        spec (FeatureSpec): ビューから読む仕様(view_digestがあること)
        start (int): 開始日(YYYYMMDD)
        end (int): 終了日(YYYYMMDD)
        labels (Optional[str]): ラベルのビュー。Noneならラベル・払戻を読まない(推論)

    Returns:
        pd.DataFrame: racehorsekey・racekey・umabanと仕様の列(ラベルのビューがあれば
            finish_order・win1_num・win1_retも)。開催日・レースキー・馬番の順

    """
    chunks = []
    for s, e in _periods(_to_date(start), _to_date(end)):
        with engine.begin() as connection:
            chunks.append(_read(connection, spec, s, e, labels))
    return pd.concat(chunks, ignore_index=True)


def _read(
    connection: Connection,
    spec: FeatureSpec,
    start: date,
    end: date,
    labels: Optional[str],
) -> pd.DataFrame:
    """1トランザクションで、ビューを照合してから読む.

    先にビューを共有ロックし、読み終わるまでapply_viewsに作り直されないようにする。
    """
    view = _view_of(spec)
    for name in [view, labels] if labels else [view]:
        _check_exists(connection, name)
    quote = connection.dialect.identifier_preparer.quote
    connection.exec_driver_sql(
        f"lock table {_qualified(quote, view)}"
        + (f", {_qualified(quote, labels)}" if labels else "")
        + " in access share mode"
    )
    check_view(connection, spec)
    keys = ["racehorsekey", "racekey", "umaban"]
    features = _columns(spec)
    columns = [f"e.{quote(c)}" for c in dict.fromkeys([*keys, *features])]
    join = ""
    if labels:
        _check_columns(connection, labels, LABEL_COLUMNS)
        columns += [f"l.racehorsekey as {_LABEL_MARKER}"]
        columns += [f"l.{quote(c)}" for c in LABEL_COLUMNS[1:]]
        join = f" left join {_qualified(quote, labels)} l using (racehorsekey)"
    # 名前はすべてidentifier_preparerで引用している。値はパラメーターで渡す
    result = connection.execute(
        text(
            f"select {', '.join(columns)} from {_qualified(quote, view)} e{join}"  # noqa: S608
            " where e.race_date between :start and :end"
            " order by e.race_date, e.racekey, e.umaban"
        ),
        {"start": start, "end": end},
    )
    frame = pd.DataFrame(result.all(), columns=list(result.keys()))
    for column in features:
        _check_not_null(frame, column, f"{view}.{column}が値なしの出走があります")
    if labels:
        _check_not_null(frame, _LABEL_MARKER, "成績がありません")
        _check_not_null(frame, "win1_num", "払戻データがありません")
        _check_not_null(frame, "win1_ret", "払戻データがありません")
        frame = frame.drop(columns=_LABEL_MARKER)
    return frame


def _view_of(spec: FeatureSpec) -> str:
    if spec.source is None:
        raise ValueError(
            f"仕様{spec.name}にsource(ビュー)がありません。jrdb-modelから読む仕様です"
        )
    return spec.source


def _columns(spec: FeatureSpec) -> List[str]:
    """仕様が読む列(重複を除き、最初に出た順). 確定後の値(ラベルの列)は使えない."""
    columns = list(dict.fromkeys(feature.source for feature in spec.features))
    labels = [c for c in columns if c in (_LABEL_MARKER, *LABEL_COLUMNS[1:])]
    if labels:
        raise ValueError(f"ラベルの列は入力に使えません: {labels}")
    return columns


def _check_exists(connection: Connection, view: str) -> None:
    if connection.execute(text("select to_regclass(:v)"), {"v": view}).scalar() is None:
        raise ValueError(f"ビューがありません: {view}")


def _check_columns(connection: Connection, view: str, required: Sequence[str]) -> None:
    _check_exists(connection, view)
    existing = set(
        connection.execute(
            text(
                "select attname from pg_attribute"
                " where attrelid = cast(:v as regclass) and attnum > 0"
                " and not attisdropped"
            ),
            {"v": view},
        ).scalars()
    )
    missing = [column for column in required if column not in existing]
    if missing:
        raise ValueError(f"ビュー{view}に列がありません: {missing}")


def _check_not_null(frame: pd.DataFrame, column: str, message: str) -> None:
    missing = frame[column].isna()
    if missing.any():
        raise ValueError(f"{message}: {frame.loc[missing, 'racehorsekey'].iloc[0]}")


def _qualified(quote, name: str) -> str:
    schema, _, view = name.partition(".")
    return f"{quote(schema)}.{quote(view)}"
