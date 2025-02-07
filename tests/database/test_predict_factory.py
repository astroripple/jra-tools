"""モデルが推論可能なことをテストする."""

from pathlib import Path
from typing import List

import keras
from jrdb_model import KaisaiData


def test_predict(sample_kaisais: List[KaisaiData]):
    from jra_tools.database.predict_factory import PredictFactory

    # keras v2の既存モデルを暫定的にフィクスチャーにしている。
    model_path = Path(__file__).parent / "ResNet_4blocks_20130101_20191231"
    layer = keras.layers.TFSMLayer(model_path, call_endpoint="serving_default")

    factory = PredictFactory(sample_kaisais, keras.Sequential([layer]))
