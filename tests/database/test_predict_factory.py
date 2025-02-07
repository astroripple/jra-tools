"""モデルが推論可能なことをテストする."""

from pathlib import Path
from typing import List

import keras
import pytest
from jrdb_model import KaisaiData


@pytest.fixture
def v2_model() -> keras.Sequential:
    """Keras v2の既存モデル.

    Returns:
        keras.Sequential: keras v2で作成済みのモデルを取り込んだSequentailモデル

    """
    layer = keras.layers.TFSMLayer(
        Path(__file__).parent / "ResNet_4blocks_20130101_20191231",
        call_endpoint="serving_default",
    )
    return keras.Sequential([layer])


def test_predict(sample_kaisais: List[KaisaiData], v2_model: keras.Sequential):
    """モデルが推論可能なことを確認する.

    データの形がモデルと合っていないとうまく噛み合わない。
    モデルのバージョン管理はバッチで行っているため、整合性の問題あり。

    Args:
        sample_kaisais (List[KaisaiData]): 開催データ
        v2_model (keras.Sequential): 稼働中のモデル

    """
    from jra_tools.database.predict_factory import PredictFactory

    factory = PredictFactory(sample_kaisais, v2_model)
    entities = factory.create()

    assert len(entities) == 363
    assert entities[7].pp_icchaku == 0.2717929184436798
    assert entities[7].pp_nichaku == 0.18553103506565094
    assert entities[7].pp_sanchaku == 0.1153089627623558
