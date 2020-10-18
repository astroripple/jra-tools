import numpy as np
from sklearn.preprocessing import StandardScaler


def createScoreDataMatrix(kaisais):
    num_max_horse = 18
    num_race = numberOfRaces(kaisais)
    num_score = numberOfScoreFeatures(kaisais[0])
    baseMatrix = np.zeros([num_race, num_max_horse, num_score])
    return _setScores(baseMatrix, kaisais)


def _setScores(score_data, kaisais):
    w = 0
    for kaisai in kaisais:
        for race in kaisai.races:
            scores = _addKaisaiScores([], kaisai)
            score_data = _setRaceScores(score_data, race, w, scores)
            w = w + 1
    return score_data


def _setRaceScores(matrix, race, raceNum, kaisaiScores):
    raceScores = kaisaiScores
    raceScores.append(race.num_of_all_horse)
    for horse in race.racehorses:
        scores = _addHorseScores(raceScores, horse)
        matrix = _setScoreData(matrix, raceNum, horse.num - 1, scores)
    return matrix


def standardize(matrix):
    sds = matrix
    for i in range(len(matrix)):
        ss = StandardScaler()
        ss.fit(matrix[i])
        sds[i] = ss.transform(matrix[i])
    return sds


def numberOfRaces(kaisais):
    num_race = 0
    for kaisai in kaisais:
        num_race += len(kaisai.races)
    return num_race


def numberOfScoreFeatures(kaisai):
    dummyScores = _addKaisaiScores([], kaisai)
    dummyScores.append(kaisai.races[0].num_of_all_horse)
    dummyScores = _addHorseScores(dummyScores, kaisai.races[0].racehorses[0])
    return len(dummyScores)


def _setScoreData(matrix, raceNum, horseNum, scores):
    features = len(matrix[raceNum, horseNum])
    if features != len(scores):
        return error
    for s in range(features):
        matrix[raceNum, horseNum, s] = scores[s]
    return matrix


def _addKaisaiScores(scores, kaisai):
    return scores + [
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


def _addHorseScores(scores, horse):
    horseScores = [
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
    ]
    return scores + _filterStringToInt(horseScores)


def _filterStringToInt(scores):
    return [0 if type(score) is str else score for score in scores]
