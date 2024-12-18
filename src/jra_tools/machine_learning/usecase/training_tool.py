"""トレーニングに利用する関数"""

from typing import List
from functools import reduce
import numpy as np
from sklearn.preprocessing import StandardScaler
from jrdb_model import KaisaiData, BangumiData, RacehorseData


def create_score_data_matrix(kaisais: List[KaisaiData]) -> np.ndarray:
    """開催データからトレーニング用データマトリクスを作成する

    Args:
        kaisais (List[KaisaiData]): 開催データ

    Returns:
        np.ndarray: 数値データ行列[レース, 馬, 特徴量]
    """
    base_matrix = np.zeros(
        [
            reduce(lambda x, y: x + len(y.races), kaisais, 0),
            18,
            number_of_score_features(kaisais[0]),
        ]
    )
    return _set_scores(base_matrix, kaisais)


def _set_scores(score_data: np.ndarray, kaisais: List[KaisaiData]) -> np.ndarray:
    w = 0
    for kaisai in kaisais:
        for race in kaisai.races:
            score_data = _set_race_scores(score_data, race, w, _kaisai_scores(kaisai))
            w = w + 1
    return score_data


def _set_race_scores(
    matrix: np.ndarray, race: BangumiData, race_num: int, kaisai_scores
) -> np.ndarray:
    scores = kaisai_scores
    scores += _race_scores(race)
    for horse in race.racehorses:
        matrix = _set_score_data(
            matrix,
            race_num,
            horse.num - 1,
            _filter_string_to_int(scores + _horse_scores(horse)),
        )
    return matrix


def standardize(matrix: np.ndarray) -> np.ndarray:
    """行列に標準化処理を施す

    Args:
        matrix (np.ndarray): 数値データ行列_

    Returns:
        np.ndarray: 標準化済み行列
    """
    sds = matrix
    for i, element in enumerate(matrix):
        ss = StandardScaler()
        ss.fit(element)
        sds[i] = ss.transform(element)
    return sds


def number_of_score_features(kaisai: KaisaiData) -> int:
    """開催データから特徴量の数量を取得する

    Args:
        kaisai (KaisaiData): 開催データ

    Returns:
        int: 特徴量の数
    """
    return len(
        _kaisai_scores(kaisai)
        + _race_scores(kaisai.races[0])
        + _horse_scores(kaisai.races[0].racehorses[0])
    )


def _set_score_data(
    matrix: np.ndarray, race_num: int, horse_num: int, scores: List
) -> np.ndarray:
    features = len(matrix[race_num, horse_num])
    if features != len(scores):
        raise RuntimeError("特徴量の数と行列の次元数が一致しません")
    for s in range(features):
        matrix[race_num, horse_num, s] = scores[s]
    return matrix


def _kaisai_scores(kaisai: KaisaiData) -> List:
    return [
        kaisai.turf_baba_in,
        kaisai.turf_baba_center,
        kaisai.turf_baba_out,
        kaisai.turf_baba_sa,
        kaisai.turf_baba_straight_saiuchi,
        kaisai.turf_baba_straight_in,
        kaisai.turf_baba_straight_center,
        kaisai.turf_baba_straight_out,
        kaisai.turf_baba_straight_oosoto,
        kaisai.dart_baba_in,
        kaisai.dart_baba_center,
        kaisai.dart_baba_out,
        kaisai.dart_baba_sa,
        kaisai.renzoku_day,
        kaisai.turf_length,
        kaisai.precipitation,
    ]


def _race_scores(race: BangumiData):
    return [race.num_of_all_horse]


def _horse_scores(horse: RacehorseData) -> List:
    return [
        horse.idm,
        horse.jockey_score,
        horse.info_score,
        horse.routin,
        horse.train_score,
        horse.trainer_score,
        horse.train_code,
        horse.trainer_hyoka_code,
        horse.jockey_rate_rentai,
        horse.gekiso_score,
        horse.kinryo,
        horse.kakutoku_money,
        horse.shukaku_money,
        horse.joken,
        horse.ten_score,
        horse.pace_score,
        horse.up_score,
        horse.position_score,
        horse.commit_weight,
        horse.commit_weight_increase,
        horse.gekiso_order,
        horse.ls_score_order,
        horse.ten_score_order,
        horse.pace_score_order,
        horse.up_score_order,
        horse.position_score_order,
        horse.expect_jokey_win_rate,
        horse.expect_jokey_rentai_rate,
        horse.taikei,
        horse.senaka,
        horse.do,
        horse.siri,
        horse.tomo,
        horse.harabukuro,
        horse.head,
        horse.neck,
        horse.breast,
        horse.shoulder,
        horse.zencho,
        horse.kocho,
        horse.maehaba,
        horse.ushirohaba,
        horse.maetsunagi,
        horse.ushirotsunagi,
        horse.tail,
        horse.furikata,
        horse.horse_start_score,
        horse.horse_latestart_rate,
        horse.mambaken_score,
        horse.runtimes_first_train,
        horse.days_after_first_train,
        horse.trainer_rank,
        horse.trainanalysis.oikiri_score,
        horse.trainanalysis.shiage_score,
        horse.trainoikiri.kaisu,
        horse.trainoikiri.train_f,
        horse.trainoikiri.ten_f,
        horse.trainoikiri.mid_f,
        horse.trainoikiri.end_f,
        horse.trainoikiri.ten_f_score,
        horse.trainoikiri.mid_f_score,
        horse.trainoikiri.end_f_score,
        horse.trainoikiri.oikiri_score,
        horse.calculated_score.waku_win_rate,
        horse.calculated_score.waku_rentai_rate,
    ]


def _filter_string_to_int(scores: List) -> List[int]:
    return [0 if isinstance(score, str) else score for score in scores]
