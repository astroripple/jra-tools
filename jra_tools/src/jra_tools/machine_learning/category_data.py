"""カテゴリ変数を取得する"""
import numpy as np
from jrdb_model import KaisaiData, BangumiData, RacehorseData
from .jrdbdummies import CategoryGetter


def getCategoryData(kaisais: list[KaisaiData]) -> np.ndarray:
    categories = _getCategories(kaisais)
    return _convertToMatrix(categories)


def _convertToMatrix(categories) -> np.ndarray:
    matrix = np.zeros([len(categories), 18, len(categories[0][0])])
    for raceNum in range(len(categories)):
        for horseNum in range(len(categories[raceNum])):
            matrix[raceNum][horseNum] = categories[raceNum][horseNum]
    return matrix


def _getCategories(kaisais: list[KaisaiData]) -> list[np.ndarray]:
    return [
        _getRaceCategories(kaisai, race) for kaisai in kaisais for race in kaisai.races
    ]


def _getRaceCategories(kaisai: KaisaiData, race: BangumiData) -> np.ndarray:
    horses = sorted(race.racehorses, key=lambda h: h.racehorsekey)
    for horse in horses:
        if horse.num == 1:
            dummies = _getCategory(kaisai, race, horse)
        else:
            dummies = np.vstack((dummies, _getCategory(kaisai, race, horse)))
    return dummies


def _getCategory(
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
            cg.getTorikeshi(_filterStrToInt(horse.torikeshi)),
            cg.getBanushikaicode(_filterStrToInt(horse.banushikai_code)),
            cg.getTraintype(_filterStrToInt(horse.trainanalysis.train_type)),
        )
    )


def _filterStrToInt(e):
    return 0 if type(e) is str else e
