"""モデルが推論可能なことをテストする."""

from typing import List

from jrdb_model import KaisaiData


def test_predict(sample_kaisais: List[KaisaiData]):
    from jra_tools.database.predict_factory import PredictFactory

    factory = PredictFactory(sample_kaisais, 1)
