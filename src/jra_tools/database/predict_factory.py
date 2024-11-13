"""推論データを生成する"""
from typing import List, Any
from dataclasses import dataclass
from jrdb_model import (
    PredictData,
    KaisaiData,
)
from ..machine_learning.input_creator import InputCreator


@dataclass
class PredictFactory:
    """推論データ生成クラス"""

    kaisais: List[KaisaiData]
    model: Any  # Kerasのモデルインスタンス

    def create(self) -> List[PredictData]:
        """推論データを生成する

        Returns:
            List[PredictData]: 未登録の推論データ一覧
        """
        input_data = InputCreator(self.kaisais)
        preds = self.model.predict(input_data.x_data)
        w = 0
        entities = []
        for k in self.kaisais:
            for r in k.races:
                for h in r.racehorses:
                    hn = h.num - 1
                    pp1 = preds[0][w][hn]
                    pp2 = preds[1][w][hn]
                    pp3 = preds[2][w][hn]
                    rentai_rate = 1 - ((1 - pp1) * (1 - pp2))
                    fukusho_rate = 1 - ((1 - pp1) * (1 - pp2) * (1 - pp3))
                    entities.append(
                        PredictData(
                            racehorsekey=h.racehorsekey,
                            pp_icchaku=float(pp1),
                            pp_nichaku=float(pp2),
                            pp_sanchaku=float(pp3),
                            rentai_rate=rentai_rate,
                            fukusho_rate=fukusho_rate,
                            tansho_odds=1 / pp1,
                            fukusho_odds=1 / fukusho_rate,
                        )
                    )
                w += 1
        return entities
