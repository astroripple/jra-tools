"""特徴量の仕様のユニットテスト."""

from datetime import date
from pathlib import Path

import pytest

from jra_tools.machine_learning.entity.feature_spec import (
    Encode,
    Feature,
    Transform,
    default_feature_spec,
    load_feature_spec,
    parse_feature_spec,
    save_feature_spec,
)
from jra_tools.machine_learning.infrastructure.model_feature_spec import (
    saved_model_input_shape,
)

MODEL_DIR = Path(__file__).parents[2] / "database" / "ResNet_4blocks_20130101_20191231"


def test_default_spec_matches_model():
    """同梱の仕様が、稼働中のモデルの入力の形と一致することを確認する."""
    spec = default_feature_spec()

    assert spec.size == 23
    spec.check_input_shape(saved_model_input_shape(MODEL_DIR))


def test_default_spec_groups():
    """同梱の仕様のグループと次元数を確認する."""
    spec = default_feature_spec()

    assert [(g.name, g.transform, g.size) for g in spec.groups] == [
        ("scores", Transform.STANDARDIZE_PER_RACE, 15),
        ("categories", Transform.NONE, 8),
    ]


def test_check_input_shape_mismatch():
    """入力の形が仕様と一致しないとエラーになることを確認する."""
    with pytest.raises(ValueError, match="一致しません"):
        default_feature_spec().check_input_shape((None, 18, 22))


def test_load_feature_spec(tmp_path: Path):
    """YAMLファイルから仕様を読み込めることを確認する."""
    path = tmp_path / "spec.yaml"
    path.write_text(
        "name: sample\n"
        "max_horses: 18\n"
        "groups:\n"
        "  - name: g\n"
        "    transform: none\n"
        "    features:\n"
        "      - {name: idm, source: racehorse.idm}\n"
        "      - {name: waku, source: racehorse.waku, encode: onehot, size: 8}\n",
        encoding="utf-8",
    )

    spec = load_feature_spec(path)

    assert spec.size == 9
    assert spec.groups[0].features[1] == Feature(
        "waku", "racehorse.waku", Encode.ONEHOT, 8, 1
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"source": "racehorse.waku", "encode": Encode.ONEHOT, "size": 0}, "1以上"),
        ({"source": "racehorse.idm", "size": 2}, "numberのsizeは1"),
    ],
)
def test_invalid_feature(kwargs, message):
    """不正な特徴量の定義がエラーになることを確認する."""
    with pytest.raises(ValueError, match=message):
        Feature(name="x", **kwargs)


def _data(**head):
    return {
        "name": "sample",
        "max_horses": 18,
        **head,
        "groups": [
            {
                "name": "g",
                "transform": "none",
                "features": [
                    {"name": "idm"},
                    {
                        "name": "waku",
                        "source": "waku_no",
                        "encode": "onehot",
                        "size": 8,
                    },
                ],
            }
        ],
    }


def test_view_spec(tmp_path: Path):
    """ビューから読む仕様: 特徴量のsourceは列名で、省略するとnameになる. 書き出して読み戻せる."""
    spec = parse_feature_spec(_data(source="features.entries_v1", view_digest="abc"))
    path = tmp_path / "spec.yaml"
    save_feature_spec(spec, path)

    assert spec.source == "features.entries_v1"
    assert spec.view_digest == "abc"
    assert [f.source for f in spec.features] == ["idm", "waku_no"]
    assert load_feature_spec(path) == spec


def test_orm_spec_has_no_view_fields(tmp_path: Path):
    """今の本番モデルの仕様は、ビューの項目を持たず、書き出しても増えない."""
    spec = default_feature_spec()
    path = tmp_path / "spec.yaml"
    save_feature_spec(spec, path)

    assert spec.source is None
    assert spec.view_digest is None
    assert "source: features" not in path.read_text(encoding="utf-8")
    assert "view_digest" not in path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (
            {
                **_data(),
                "groups": [
                    {
                        "name": "g",
                        "transform": "none",
                        "features": [{"name": "idm", "source": "idm"}],
                    }
                ],
            },
            "テーブル名.列名",
        ),
        (_data(source="entries_v1"), "スキーマ.ビュー名"),
        (
            {
                **_data(source="features.entries_v1"),
                "groups": [
                    {
                        "name": "g",
                        "transform": "none",
                        "features": [{"name": "idm", "source": "racehorse.idm"}],
                    }
                ],
            },
            "列名だけ",
        ),
    ],
)
def test_invalid_source(data, message):
    """sourceの書式が仕様の読み方と合わないとエラーになる."""
    with pytest.raises(ValueError, match=message):
        parse_feature_spec(data)


def test_digest_without_source():
    """view_digestはビューから読む仕様にだけ書ける."""
    data = {**_data(), "view_digest": "abc"}
    data["groups"][0]["features"] = [{"name": "idm", "source": "racehorse.idm"}]

    with pytest.raises(ValueError, match="view_digest"):
        parse_feature_spec(data)


def test_training_period(tmp_path: Path):
    """学習期間を書いた仕様は、日付として読み、書き出して読み戻せる."""
    spec = parse_feature_spec(
        _data(
            source="features.entries_v1",
            train_from=date(2013, 1, 1),
            train_to="2019-12-31",
        )
    )
    path = tmp_path / "spec.yaml"
    save_feature_spec(spec, path)

    assert (spec.train_from, spec.train_to) == (date(2013, 1, 1), date(2019, 12, 31))
    assert "train_from: 2013-01-01" in path.read_text(encoding="utf-8")
    assert load_feature_spec(path) == spec


def test_training_period_is_optional(tmp_path: Path):
    """学習期間は省略でき、書き出しても増えない."""
    spec = default_feature_spec()
    path = tmp_path / "spec.yaml"
    save_feature_spec(spec, path)

    assert (spec.train_from, spec.train_to) == (None, None)
    assert "train_from" not in path.read_text(encoding="utf-8")
    assert "train_to" not in path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("period", "message"),
    [
        ({"train_from": date(2013, 1, 1)}, "両方"),
        ({"train_from": date(2020, 1, 1), "train_to": date(2019, 12, 31)}, "より後"),
    ],
)
def test_invalid_training_period(period, message):
    """学習期間は両方書き、初日は最終日より後にしない."""
    with pytest.raises(ValueError, match=message):
        parse_feature_spec(_data(source="features.entries_v1", **period))
