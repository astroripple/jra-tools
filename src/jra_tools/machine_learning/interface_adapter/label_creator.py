"""ラベルを作成する"""

from typing import List
from functools import reduce
import pickle
import numpy as np
from jrdb_model import KaisaiData


class LabelCreator:
    """ラベル作成クラス"""

    def __init__(self, kaisais: List[KaisaiData]):
        self.kaisais = kaisais
        num_race = reduce(lambda x, y: x + len(y.races), kaisais, 0)
        num_max_horse = 18
        self.t_icchaku = np.zeros([num_race, num_max_horse])
        self.t_nichaku = np.zeros([num_race, num_max_horse])
        self.t_sanchaku = np.zeros([num_race, num_max_horse])
        self.t_yonchaku = np.zeros([num_race, num_max_horse])
        self.t_gochaku = np.zeros([num_race, num_max_horse])
        w_num = 0
        for kaisai in kaisais:
            for race in kaisai.races:
                for horse in race.racehorses:
                    oa = horse.result.order_of_arrival
                    if oa == 1:
                        self.t_icchaku[w_num, horse.num - 1] = 1
                    elif oa == 2:
                        self.t_nichaku[w_num, horse.num - 1] = 1
                    elif oa == 3:
                        self.t_sanchaku[w_num, horse.num - 1] = 1
                    elif oa == 4:
                        self.t_yonchaku[w_num, horse.num - 1] = 1
                    elif oa == 5:
                        self.t_gochaku[w_num, horse.num - 1] = 1
                w_num += 1
        self.labels = [
            self.t_icchaku,
            self.t_nichaku,
            self.t_sanchaku,
            self.t_yonchaku,
            self.t_gochaku,
        ]

    def save(self, name: str):
        """ラベルデータをローカルに保存する

        Args:
            name (str): ファイル名
        """
        with open(f"{name}.dump", mode="wb") as f:
            pickle.dump(self.labels, f)
