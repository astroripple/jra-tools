"""カテゴリ変数を取得する"""
from typing import List
import numpy as np
from jrdb_model import KaisaiData, BangumiData, RacehorseData
from .jrdbdummies import CategoryGetter


def get_category_data(kaisais: List[KaisaiData]) -> np.ndarray:
    """開催データからカテゴリデータを取得する

    Args:
        kaisais (List[KaisaiData]): 開催データ

    Returns:
        np.ndarray: 開催データマトリクス
    """
    categories = _get_categories(kaisais)
    return _convert_to_matrix(categories)


def _convert_to_matrix(categories: List[np.ndarray]) -> np.ndarray:
    matrix = np.zeros([len(categories), 18, len(categories[0][0])])
    for raceNum in range(len(categories)):
        for horseNum in range(len(categories[raceNum])):
            matrix[raceNum][horseNum] = categories[raceNum][horseNum]
    return matrix


def _get_categories(kaisais: List[KaisaiData]) -> List[np.ndarray]:
    return [
        _get_race_categories(kaisai, race)
        for kaisai in kaisais
        for race in kaisai.races
    ]


def _get_race_categories(kaisai: KaisaiData, race: BangumiData) -> np.ndarray:
    horses = sorted(race.racehorses, key=lambda h: h.racehorsekey)
    for horse in horses:
        if horse.num == 1:
            dummies = _get_category(kaisai, race, horse)
        else:
            dummies = np.vstack((dummies, _get_category(kaisai, race, horse)))
    return dummies


def _get_category(
    kaisai: KaisaiData, race: BangumiData, horse: RacehorseData
) -> np.ndarray:
    cg = CategoryGetter()
    return np.hstack(
        (
            cg.getTennatsu(kaisai.tennatsu),
            cg.getDistance(race.distance),
            cg.getBacode(horse.bacode),
            cg.getNum(horse.num),
            cg.getWaku(horse.waku),
            cg.getTorikeshi(_filter_str_to_int(horse.torikeshi)),
            cg.getBanushikaicode(_filter_str_to_int(horse.banushikai_code)),
            cg.getTraintype(_filter_str_to_int(horse.trainanalysis.train_type)),
        )
    )


def _filter_str_to_int(value):
    return 0 if isinstance(value, str) else value
