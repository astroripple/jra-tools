"""特徴量の仕様(推論モデルの入力の形)を定義する.

仕様はYAMLで書き、学習に使った仕様をモデルと一緒に保存する。
入力の次元は、groupsの並び順・featuresの並び順のとおりに並ぶ。

値の読み方は2つある。
- 最上位にsourceがない仕様: 各特徴量のsourceはjrdb-modelの「テーブル名.列名」。ORMの経路で読む
- 最上位にsource(featuresのビュー「スキーマ.ビュー名」)がある仕様: 各特徴量のsourceは
  そのビューの列名(省略するとname)。view_digestは学習時のビューの定義のハッシュで、
  読み込むときにDBのビューと照合する(view_dataset)

train_from・train_to(学習期間。初日・最終日を含む)は、学習したモデルの仕様に書く(省略可)。
推論する日が学習期間に入っていないかを、使う側(batch)が確かめるため。
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import yaml

# パッケージに同梱している仕様のファイルを置くパッケージ
SPECS_PACKAGE = "jra_tools.machine_learning.specs"
# 現行の推論モデル(ResNet_4blocks_20130101_20191231)の仕様
DEFAULT_SPEC = "resnet4_2013_2019.yaml"


class Transform(StrEnum):
    """グループ単位の変換."""

    NONE = "none"
    # レースごとにStandardScalerで標準化する(空き枠の0の行も含めた18行で計算する)
    STANDARDIZE_PER_RACE = "standardize_per_race"


class Encode(StrEnum):
    """特徴量ごとの値の表し方."""

    NUMBER = "number"
    ONEHOT = "onehot"


@dataclass(frozen=True)
class Feature:
    """1つの特徴量.

    sourceは、ORMの経路では「テーブル名.列名」(例: racehorse.idm)、ビューの経路では列名。
    onehotの場合、値がbaseのときに先頭の次元が1になる。
    """

    name: str
    source: str
    encode: Encode = Encode.NUMBER
    size: int = 1
    base: int = 1

    def __post_init__(self):
        """onehotの次元数を検証する. sourceの書式はFeatureSpecが検証する."""
        if self.encode == Encode.ONEHOT and self.size < 1:
            raise ValueError(f"onehotのsizeは1以上を指定してください: {self}")
        if self.encode == Encode.NUMBER and self.size != 1:
            raise ValueError(f"numberのsizeは1です: {self}")

    @property
    def table(self) -> str:
        """sourceのテーブル名."""
        return self.source.partition(".")[0]

    @property
    def column(self) -> str:
        """sourceの列名."""
        return self.source.partition(".")[2]


@dataclass(frozen=True)
class FeatureGroup:
    """変換をまとめて適用する特徴量の組."""

    name: str
    transform: Transform
    features: Tuple[Feature, ...]

    @property
    def size(self) -> int:
        """グループの次元数."""
        return sum(feature.size for feature in self.features)


@dataclass(frozen=True)
class FeatureSpec:
    """推論モデルの入力の仕様. 入力の形は(レース数, max_horses, size).

    sourceはfeaturesのビュー(「スキーマ.ビュー名」)。Noneならjrdb-modelから読む(ORMの経路)。
    view_digestは学習時のビューの定義のハッシュ(view_dataset.view_digest)。
    """

    name: str
    max_horses: int
    groups: Tuple[FeatureGroup, ...]
    source: Optional[str] = None
    view_digest: Optional[str] = None
    train_from: Optional[date] = None
    train_to: Optional[date] = None

    def __post_init__(self):
        """学習期間・sourceの書式を検証する."""
        if (self.train_from is None) != (self.train_to is None):
            raise ValueError("train_fromとtrain_toは両方書いてください")
        if (
            self.train_from is not None
            and self.train_to is not None
            and self.train_from > self.train_to
        ):
            raise ValueError(
                f"学習期間の初日{self.train_from}が最終日{self.train_to}より後です"
            )
        if self.source is None:
            if self.view_digest is not None:
                raise ValueError("view_digestはsource(ビュー)がある仕様にだけ書けます")
            for feature in self.features:
                table, _, column = feature.source.partition(".")
                if not table or not column:
                    raise ValueError(
                        f"sourceは「テーブル名.列名」で指定してください: {feature}"
                    )
            return
        schema, _, view = self.source.partition(".")
        if not schema or not view:
            raise ValueError(
                f"仕様のsourceは「スキーマ.ビュー名」で指定してください: {self.source}"
            )
        for feature in self.features:
            if "." in feature.source:
                raise ValueError(
                    f"ビューから読む仕様の特徴量のsourceは列名だけです: {feature}"
                )

    @property
    def features(self) -> Tuple[Feature, ...]:
        """すべての特徴量(groupsの並び順)."""
        return tuple(feature for group in self.groups for feature in group.features)

    @property
    def size(self) -> int:
        """1頭あたりの特徴量の次元数."""
        return sum(group.size for group in self.groups)

    def check_input_shape(self, shape: Sequence[Any]) -> None:
        """推論モデルの入力の形(先頭はバッチの次元)が仕様と一致するか確かめる.

        Args:
            shape (Sequence[Any]): モデルの入力の形(例: (None, 18, 23))

        Raises:
            ValueError: 形が仕様と一致しない場合

        """
        if tuple(shape[1:]) != (self.max_horses, self.size):
            raise ValueError(
                f"モデルの入力の形{tuple(shape)}が、仕様{self.name}"
                f"(None, {self.max_horses}, {self.size})と一致しません"
            )


def parse_feature_spec(data: Mapping[str, Any]) -> FeatureSpec:
    """辞書(YAMLを読み込んだもの)から仕様を作る."""
    from_view = "source" in data
    return FeatureSpec(
        name=data["name"],
        max_horses=data["max_horses"],
        groups=tuple(
            FeatureGroup(
                name=group["name"],
                transform=Transform(group["transform"]),
                features=tuple(
                    Feature(
                        name=feature["name"],
                        source=feature.get("source", feature["name"])
                        if from_view
                        else feature["source"],
                        encode=Encode(feature.get("encode", Encode.NUMBER)),
                        size=feature.get("size", 1),
                        base=feature.get("base", 1),
                    )
                    for feature in group["features"]
                ),
            )
            for group in data["groups"]
        ),
        source=data.get("source"),
        view_digest=data.get("view_digest"),
        train_from=_date(data.get("train_from")),
        train_to=_date(data.get("train_to")),
    )


def _date(value: Any) -> Optional[date]:
    """YAMLの日付(dateに読まれる)か、YYYY-MM-DDの文字列を日付にする."""
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def feature_spec_to_dict(spec: FeatureSpec) -> Dict[str, Any]:
    """仕様を、parse_feature_specで読み戻せる辞書にする."""
    head: Dict[str, Any] = {"name": spec.name, "max_horses": spec.max_horses}
    if spec.source is not None:
        head["source"] = spec.source
    if spec.view_digest is not None:
        head["view_digest"] = spec.view_digest
    if spec.train_from is not None:
        head["train_from"] = spec.train_from
        head["train_to"] = spec.train_to
    return {
        **head,
        "groups": [
            {
                "name": group.name,
                "transform": str(group.transform),
                "features": [
                    {"name": feature.name, "source": feature.source}
                    if feature.encode == Encode.NUMBER
                    else {
                        "name": feature.name,
                        "source": feature.source,
                        "encode": str(feature.encode),
                        "size": feature.size,
                        "base": feature.base,
                    }
                    for feature in group.features
                ],
            }
            for group in spec.groups
        ],
    }


def load_feature_spec(path: Path | str) -> FeatureSpec:
    """YAMLファイルから仕様を読み込む."""
    with open(path, encoding="utf-8") as f:
        return parse_feature_spec(yaml.safe_load(f))


def save_feature_spec(spec: FeatureSpec, path: Path | str) -> None:
    """仕様をYAMLファイルに書き出す."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            feature_spec_to_dict(spec), f, allow_unicode=True, sort_keys=False
        )


def default_feature_spec() -> FeatureSpec:
    """現行の推論モデルの仕様を、パッケージに同梱したファイルから読み込む."""
    text = resources.files(SPECS_PACKAGE).joinpath(DEFAULT_SPEC).read_text("utf-8")
    return parse_feature_spec(yaml.safe_load(text))
