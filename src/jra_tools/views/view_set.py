"""model・featuresのビューの定義を読む.

具体的な定義は使う側(sazanami-batchのviews/)が持ち、ここは読み方だけを持つ。

    views/
      views.yaml          管理するスキーマ・関数のSQL・作る順のビューの一覧
      model/races.sql     ビュー1つにつき1ファイル。SELECT文だけを書く
      tests/*.sql         テスト。返した行があれば失敗(dbtの個別のテストと同じ)

views.yamlの例:

    schemas: [model, features]
    functions: [functions.sql]
    views:
      - model.races
      - model.entries

- schemas: apply_viewsがビューと関数を作り直すスキーマ。ビューと関数はこのどれかに置く。
  スキーマ自体と、そこに置いた表は消さない
- functions: ビューより先に流すSQL(共通の変換の関数など)。省略できる
- views: 「スキーマ.ビュー名」を作る順に並べる。SQLは<スキーマ>/<ビュー名>.sql
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Tuple

import yaml

VIEWS_FILE = "views.yaml"
TESTS_DIR = "tests"


@dataclass(frozen=True)
class View:
    """1つのビュー."""

    schema: str
    name: str
    sql: str

    @property
    def qualified_name(self) -> str:
        """「スキーマ.ビュー名」."""
        return f"{self.schema}.{self.name}"


@dataclass(frozen=True)
class ViewTest:
    """1つのテスト. sqlが返した行が失敗."""

    name: str
    sql: str


@dataclass(frozen=True)
class ViewSet:
    """views/の定義一式."""

    schemas: Tuple[str, ...]
    functions: Tuple[str, ...]
    views: Tuple[View, ...]
    tests: Tuple[ViewTest, ...]
    # views.yaml・関数・ビューのSQLから求めたハッシュ。テストは含めない
    digest: str


def parse_view_set(
    data: Mapping[str, Any],
    read: Callable[[str], str],
    tests: Tuple[ViewTest, ...] = (),
) -> ViewSet:
    """views.yamlの中身からViewSetを作る.

    Args:
        data (Mapping[str, Any]): views.yamlの中身
        read (Callable[[str], str]): views/からの相対パスを受け取り、ファイルの中身を返す関数
        tests (Tuple[ViewTest, ...]): テスト

    Returns:
        ViewSet: 定義一式

    """
    schemas = tuple(data["schemas"])
    functions = tuple(read(path) for path in data.get("functions", []))
    views = []
    for qualified_name in data["views"]:
        schema, _, name = qualified_name.partition(".")
        if not schema or not name:
            raise ValueError(
                f"ビューは「スキーマ.ビュー名」で指定してください: {qualified_name}"
            )
        if schema not in schemas:
            raise ValueError(f"ビューのスキーマがschemasにありません: {qualified_name}")
        views.append(View(schema, name, read(f"{schema}/{name}.sql")))
    names = [view.qualified_name for view in views]
    duplicated = sorted({name for name in names if names.count(name) > 1})
    if duplicated:
        raise ValueError(f"同じビューが複数あります: {duplicated}")
    return ViewSet(
        schemas, functions, tuple(views), tests, _digest(data, functions, views)
    )


def load_view_set(directory: Path | str) -> ViewSet:
    """views/のフォルダから定義一式を読む.

    Args:
        directory (Path | str): views/のフォルダ

    Returns:
        ViewSet: 定義一式

    """
    root = Path(directory)
    with open(root / VIEWS_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    tests = tuple(
        ViewTest(path.stem, path.read_text(encoding="utf-8"))
        for path in sorted((root / TESTS_DIR).glob("*.sql"))
    )
    return parse_view_set(
        data, lambda path: (root / path).read_text(encoding="utf-8"), tests
    )


def _digest(
    data: Mapping[str, Any], functions: Tuple[str, ...], views: list[View]
) -> str:
    """定義が変わったかを判定するためのハッシュ."""
    sha = hashlib.sha256()
    sha.update(yaml.safe_dump(dict(data), sort_keys=True).encode())
    for sql in functions:
        sha.update(b"\0function\0" + sql.encode())
    for view in views:
        sha.update(f"\0view\0{view.qualified_name}\0".encode() + view.sql.encode())
    return sha.hexdigest()
