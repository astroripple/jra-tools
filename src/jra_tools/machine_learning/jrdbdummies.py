import numpy as np


class CategoryGetter:
    # 開催データ
    def getKaisaikbn(self, value):
        return self.categories(3, value)

    def getDayofweek(self, value):
        types = {"日": 1, "月": 2, "火": 3, "水": 4, "木": 5, "金": 6, "土": 7}
        return self.categories(7, types[value])

    def getTenko(self, value):
        return self.categories(6, value)

    def getBabaabst(self, value):
        return self.categories(4, value)

    def getBabadetail(self, baba):
        return self.categories(3, baba)

    def getTurfkind(self, kind):
        return self.categories(3, kind)

    def getTennatsu(self, ten):
        return self.categories(2, ten)

    def getStopfreeze(self, st):
        return self.categories(2, st)

    # 番組データ
    def getDistance(self, value):
        if 2400 < value <= 2500:
            return self.categories(12, 9)
        if 2500 < value <= 3000:
            return self.categories(12, 10)
        if 3000 < value <= 3200:
            return self.categories(12, 11)
        if 3200 < value:
            return self.categories(12, 12)
        return self.categories(12, (value // 200) - 4)

    def getTdscode(self, tds):
        return self.categories(3, tds)

    def getRightleft(self, rl):
        return self.categories(4, rl)

    def getInout(self, inout):
        return self.categories(4, inout)

    def getShubetsu(self, s):
        return self.categories(5, s)

    def getJoken(self, value):
        types = ["04", "05", "08", "09", "10", "15", "16", "A1", "A2", "A3", "OP"]
        return self.categories(11, types.index(value) + 1)

    def getJuryo(self, j):
        return self.categories(4, j)

    def getGrade(self, g):
        return self.categories(5, g)

    def getCourse(self, c):
        return self.categories(5, c)

    # RaceHorse
    # 汎用メソッド利用
    def getNum(self, num):
        return self.categories(18, num)

    def getLegtype(self, leg_type):
        return self.categories(7, int(leg_type))

    def getOmotekiseicode(self, omotekisei_code):
        return self.categories(4, omotekisei_code)

    def getBrinkers(self, brinkers):
        return self.categories(4, brinkers)

    def getMinarai(self, minarai):
        return self.categories(4, minarai)

    def getWaku(self, waku):
        return self.categories(8, waku)

    def getTurfadjustcode(self, turf_adjust_code):
        return self.categories(5, turf_adjust_code)

    def getTorikeshi(self, torikeshi):
        return self.categories(2, torikeshi)

    def getSex(self, sex):
        return self.categories(3, sex)

    def getBanushikaicode(self, banushikai_code):
        return self.categories(11, banushikai_code)

    def getYuso(self, yuso):
        return self.categories(5, yuso)

    def getKokyuflg(self, kokyu_flg):
        return self.categories(3, kokyu_flg)

    def getTurfdartsteepleflg(self, turf_dart_steeple_flg):
        return self.categories(3, turf_dart_steeple_flg)

    def getDistanceflg(self, distance_flg):
        return self.categories(2, distance_flg)

    def getClassflg(self, class_flg):
        return self.categories(4, class_flg)

    def getTenkyuflg(self, tenkyu_flg):
        return self.categories(4, tenkyu_flg)

    def getKyoseiflg(self, kyosei_flg):
        return self.categories(4, kyosei_flg)

    def getTraincoursekind(self, train_course_kind):
        return self.categories(6, train_course_kind)

    def getSaka(self, saka):
        return self.categories(2, saka)

    def getWood(self, wood):
        return self.categories(2, wood)

    def getDart(self, dart):
        return self.categories(2, dart)

    def getTurf(self, turf):
        return self.categories(2, turf)

    def getPool(self, pool):
        return self.categories(2, pool)

    def getSteeple(self, steeple):
        return self.categories(2, steeple)

    def getPolitruck(self, politruck):
        return self.categories(2, politruck)

    def getTraindistance(self, train_distance):
        return self.categories(5, train_distance)

    def getTrainjuten(self, train_juten):
        return self.categories(5, train_juten)

    def getOikirikind(self, oikiri_kind):
        return self.categories(4, oikiri_kind)

    def getZensoIjokbn(self, zenso_ijo_kbn):
        return self.categories(7, zenso_ijo_kbn)

    def getZensoCourseposition(self, zenso_course_position):
        return self.categories(9, zenso_course_position)

    def getZensoRacelegtype(self, zenso_race_leg_type):
        return self.categories(7, zenso_race_leg_type)

    def getZensoCorner4courseposition(self, zenso_corner4_course_position):
        return self.categories(8, zenso_corner4_course_position)

    def getUmakigocode(self, uk):
        return self.categories(28, uk)

    # 独自メソッド利用
    def getBacode(self, value):
        if (1 > value) or (value > 10):
            value = 11
        return self.categories(11, value)

    def getDistanceadjust(self, value):
        if 0 <= value <= 6:
            value = value + 1
        else:
            value = 8
        return self.categories(8, value)

    def getJockeyshirushi(self, value):
        if 0 <= value <= 6:
            value = value + 1
        else:
            value = 8
        return self.categories(8, value)

    def getDartadjustcode(self, d):
        if 0 <= value <= 3:
            value = value + 1
        else:
            value = 5
        return self.categories(5, value)

    def getGekisotype(self, value):
        types = {"00": 1, "A1": 2, "A2": 3, "A3": 4, "A4": 5, "B1": 6, "B2": 7}
        return self.categories(7, types[value])

    def getRestreasoncode(self, value):
        if 0 <= value <= 7:
            return self.categories(11, value + 1)
        if 11 <= value <= 16:
            return self.categories(11, value - 2)
        if value == 21:
            return self.categories(11, 15)

    def getNorikaeflg(self, value):
        if 0 <= value <= 1:
            value = value + 1
        else:
            value = 3
        return self.categories(3, value)

    def getHobokusakirank(self, value):
        types = {"0": 1, "A": 2, "B": 3, "C": 4, "D": 5, "E": 6}
        return self.categories(6, types[value])

    def getTraintype(self, value):
        return self.categories(11, int(value))

    def getTrainvolhyoka(self, value):
        types = {"A": 1, "B": 2, "C": 3, "D": 4, " ": 5}
        return self.categories(5, types[value])

    # 汎用メソッド

    def categories(self, category_count, value):
        cat = np.zeros([category_count])
        cat[value - 1] = 1
        return cat
