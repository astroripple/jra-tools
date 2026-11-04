"""model・featuresのビューをPostgresに反映する.

ビューはデータを持たないので、マイグレーションはしない。定義(ハッシュ)が変わったときだけ、
1トランザクションで、管理するスキーマのビューと関数を消して作り直し、ハッシュを記録する。
スキーマは消さない。同じスキーマに置いた表(推論の結果など)には触らない。
定義とstagingの列が合わなければCREATE VIEWでPostgresがエラーにし、全体が戻る(今のビューが残る)。

ハッシュを記録する表meta.view_versionは作らない。表を作るコマンド
(sazanami-batchのapply-model-and-meta-tables)が作り、ここは読み書きだけをする。
表の名前と列(digest・applied_at・label)は、そのコマンドとの約束。
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import DBAPIError, OperationalError

from jra_tools.views.view_set import ViewSet

# apply_viewsどうしの排他に使うadvisory lockのキー(任意の固定値)
ADVISORY_LOCK_KEY = 7_316_042_901
# lock_timeoutにかかったときのSQLSTATE
_LOCK_NOT_AVAILABLE = "55P03"

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApplyOptions:
    """apply_viewsの設定."""

    # 管理するスキーマを読めるようにするロール
    readers: Tuple[str, ...] = ()
    # 記録に残す文字列(batchのイメージのタグなど)
    label: str = ""
    # ロックを待つ上限(Postgresの書式。例: 10s)
    lock_timeout: str = "10s"
    # lock_timeoutにかかったときにやり直す回数
    retries: int = 5
    # やり直すまでの秒数
    retry_wait: float = 5.0


DEFAULT_OPTIONS = ApplyOptions()


class ViewVersionTableMissing(RuntimeError):
    """meta.view_versionがない. 表を作るコマンドを先に流していない."""


@dataclass(frozen=True)
class TestFailure:
    """失敗したテスト."""

    name: str
    rows: int


def apply_views(
    engine: Engine, view_set: ViewSet, options: ApplyOptions = DEFAULT_OPTIONS
) -> bool:
    """定義が変わっていれば、ビューを作り直す.

    ビューを作り直すときの排他ロックは、読んでいる最中のクエリ(Metabaseなど)が終わるまで待つ。
    待っている間は新しいクエリも止まるため、lock_timeoutで諦めて、間を置いてやり直す。

    Args:
        engine (Engine): Postgresのエンジン
        view_set (ViewSet): 定義一式
        options (ApplyOptions): 設定

    Returns:
        bool: 作り直したらTrue。定義が変わっていなければFalse

    Raises:
        ViewVersionTableMissing: meta.view_versionがない

    """
    for attempt in range(options.retries + 1):
        try:
            with engine.begin() as conn:
                return _apply(conn, view_set, options)
        except OperationalError as e:
            if _sqlstate(e) != _LOCK_NOT_AVAILABLE or attempt == options.retries:
                raise
            _logger.warning(
                "ロックを取れませんでした。%s秒後にやり直します(%d/%d)",
                options.retry_wait,
                attempt + 1,
                options.retries,
            )
            time.sleep(options.retry_wait)
    raise AssertionError("unreachable")


def applied_digest(conn: Connection) -> Optional[str]:
    """最後に反映した定義のハッシュ. 一度も反映していなければNone."""
    exists = conn.execute(text("select to_regclass('meta.view_version')")).scalar()
    if exists is None:
        return None
    return conn.execute(
        text("select digest from meta.view_version order by applied_at desc limit 1")
    ).scalar()


def run_view_tests(engine: Engine, view_set: ViewSet) -> List[TestFailure]:
    """テストを流し、行を返したテストを返す. ビューは反映済みであること.

    Args:
        engine (Engine): Postgresのエンジン
        view_set (ViewSet): 定義一式

    Returns:
        List[TestFailure]: 失敗したテスト。すべて通れば空

    """
    failures = []
    with engine.connect() as conn:
        for test in view_set.tests:
            cursor = conn.connection.cursor()
            _execute_definition(conn, test.sql, cursor)
            rows = len(cursor.fetchall())
            if rows:
                failures.append(TestFailure(test.name, rows))
    return failures


def _apply(conn: Connection, view_set: ViewSet, options: ApplyOptions) -> bool:
    conn.execute(
        text("select set_config('lock_timeout', :timeout, true)"),
        {"timeout": options.lock_timeout},
    )
    conn.execute(text("select pg_advisory_xact_lock(:key)"), {"key": ADVISORY_LOCK_KEY})
    if conn.execute(text("select to_regclass('meta.view_version')")).scalar() is None:
        raise ViewVersionTableMissing(
            "meta.view_versionがありません。表を作るコマンド"
            "(sazanami-batchのapply-model-and-meta-tables)を先に流してください"
        )
    if applied_digest(conn) == view_set.digest:
        _logger.info("ビューの定義は変わっていません(%s)", view_set.digest[:12])
        return False
    _logger.info("ビューを作り直します(%s)", view_set.digest[:12])
    quote = conn.dialect.identifier_preparer.quote
    for schema in view_set.schemas:
        conn.exec_driver_sql(f"create schema if not exists {quote(schema)}")
    _drop_views_and_routines(conn, view_set.schemas)
    for sql in view_set.functions:
        _execute_definition(conn, sql)
    for view in view_set.views:
        _execute_definition(
            conn,
            f"create view {quote(view.schema)}.{quote(view.name)} as\n{_body(view.sql)}",
        )
    for schema in view_set.schemas:
        for reader in options.readers:
            conn.exec_driver_sql(
                f"grant usage on schema {quote(schema)} to {quote(reader)}"
            )
            conn.exec_driver_sql(
                f"grant select on all tables in schema {quote(schema)} to {quote(reader)}"
            )
    conn.execute(
        text("insert into meta.view_version (digest, label) values (:digest, :label)"),
        {"digest": view_set.digest, "label": options.label},
    )
    _logger.info("ビューを%d個作りました", len(view_set.views))
    return True


def _drop_views_and_routines(conn: Connection, schemas: Tuple[str, ...]) -> None:
    """管理するスキーマのビューと関数を消す. 表(マテリアライズドビューを含む)は残す.

    ビューは、ほかのスキーマに置いた、これに依存するビュー(sandboxなど)も消える(CASCADE)。
    関数はCASCADEにしない。表の列の既定値などが関数を使っていれば、黙って消さずにエラーで止める。
    1つのDROP文にまとめるので、消すものどうしの依存(ビューが関数を使うなど)は順を気にしなくてよい。
    拡張機能が作ったものは消さない。
    """
    views = (
        conn.execute(
            text(
                "select c.oid::regclass::text from pg_class c"
                " join pg_namespace n on n.oid = c.relnamespace"
                " where n.nspname = any(:schemas) and c.relkind = 'v'"
                " and not exists (select 1 from pg_depend d"
                " where d.classid = 'pg_class'::regclass and d.objid = c.oid"
                " and d.deptype = 'e')"
            ),
            {"schemas": list(schemas)},
        )
        .scalars()
        .all()
    )
    if views:
        conn.exec_driver_sql(f"drop view {', '.join(views)} cascade")
    routines = (
        conn.execute(
            text(
                "select p.oid::regprocedure::text from pg_proc p"
                " join pg_namespace n on n.oid = p.pronamespace"
                " where n.nspname = any(:schemas) and p.prokind in ('f', 'p', 'a')"
                " and not exists (select 1 from pg_depend d"
                " where d.classid = 'pg_proc'::regclass and d.objid = p.oid"
                " and d.deptype = 'e')"
            ),
            {"schemas": list(schemas)},
        )
        .scalars()
        .all()
    )
    if routines:
        conn.exec_driver_sql(f"drop routine {', '.join(routines)}")


def _execute_definition(conn: Connection, sql: str, cursor: Any = None) -> None:
    """定義のSQLを、パラメーターなしでドライバに渡す.

    SQLAlchemyを通すと、SQLの「%」(LIKEの'%S'など)がプレースホルダーとして解釈されるため。
    """
    dbapi_error = conn.dialect.loaded_dbapi.Error
    try:
        (cursor or conn.connection.cursor()).execute(sql)
    except dbapi_error as e:
        # SQLAlchemyを通したときと同じ例外(ProgrammingError・OperationalErrorなど)にする
        raise DBAPIError.instance(sql, None, e, dbapi_error) from e


def _body(sql: str) -> str:
    """末尾の空白とセミコロンを取り除く(サブクエリやCREATE VIEWに埋め込むため)."""
    return sql.rstrip().rstrip(";").rstrip()


def _sqlstate(error: OperationalError) -> Optional[str]:
    orig = error.orig
    return getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
