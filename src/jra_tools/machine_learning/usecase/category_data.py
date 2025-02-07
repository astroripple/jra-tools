"""カテゴリ変数を取得する."""

from typing import List

import numpy as np
from jrdb_model import BangumiData, KaisaiData, RacehorseData

from jra_tools.machine_learning.entity.jrdbdummies import CategoryGetter


def get_category_data(kaisais: List[KaisaiData]) -> np.ndarray:
    """開催データからカテゴリデータを取得する.

    Args:
        kaisais (List[KaisaiData]): 開催データ

    Returns:
        np.ndarray: 開催データマトリクス

    """
    return _convert_to_matrix(_get_categories(kaisais))


def _convert_to_matrix(categories: List[np.ndarray]) -> np.ndarray:
    matrix = np.zeros([len(categories), 18, len(categories[0][0])])
    for race_num, race in enumerate(categories):
        for horse_num, horse in enumerate(race):
            matrix[race_num][horse_num] = horse
    return matrix


def _get_categories(kaisais: List[KaisaiData]) -> List[np.ndarray]:
    return [
        _get_race_categories(kaisai, race)
        for kaisai in kaisais
        for race in kaisai.races
    ]


def _get_race_categories(kaisai: KaisaiData, race: BangumiData) -> np.ndarray:
    for horse in sorted(race.racehorses, key=lambda h: h.racehorsekey):
        if horse.num == 1:
            dummies = _get_category(kaisai, race, horse)
        else:
            dummies = np.vstack((dummies, _get_category(kaisai, race, horse)))
    return dummies


def _get_category(
    kaisai: KaisaiData, race: BangumiData, horse: RacehorseData
) -> np.ndarray:
    cg = CategoryGetter()
    return np.hstack((cg.getWaku(horse.waku),))


def _filter_str_to_int(value):
    return 0 if isinstance(value, str) else value
