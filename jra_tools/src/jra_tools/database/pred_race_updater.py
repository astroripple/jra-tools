from jrdb_model import PredictRaceData, PredictData, db
from ..machine_learning.input_creator import InputCreator


class PredictRaceUpdater:
    def __init__(self, kaisais):
        self.kaisais = kaisais

    def updatePredict(self, model):
        inputData = InputCreator(self.kaisais)
        preds = model.predict(inputData.x_data)
        w = 0
        for k in self.kaisais:
            for r in k.races:
                for h in r.racehorses:
                    hn = h.num - 1
                    pp1 = preds[0][w][hn]
                    pp2 = preds[1][w][hn]
                    pp3 = preds[2][w][hn]
                    # pp4 = preds[3][w][hn]
                    # pp5 = preds[4][w][hn]
                    rentai_rate = 1 - ((1 - pp1) * (1 - pp2))
                    fukusho_rate = 1 - ((1 - pp1) * (1 - pp2) * (1 - pp3))
                    pd = PredictData(
                        racehorsekey=h.racehorsekey,
                        pp_icchaku=float(pp1),
                        pp_nichaku=float(pp2),
                        pp_sanchaku=float(pp3),
                        rentai_rate=rentai_rate,
                        fukusho_rate=fukusho_rate,
                        tansho_odds=1 / pp1,
                        fukusho_odds=1 / fukusho_rate,
                    )
                    db.session.add(pd)
                w += 1
        db.session.commit()

    def update(self):
        for kaisai in self.kaisais:
            for race in kaisai.races:
                pred = PredictRaceData(
                    racekey=race.racekey,
                    umaren=self.umarenOddses(race),
                    wide=self.wideOddses(race),
                    wakuren=self.wakurenOddses(race),
                )
                db.session.add(pred)
        db.session.commit()

    def umarenOddses(self, race):
        return self.oddses(race, "umaren")

    def umarenOdds(self, horse1, horse2):
        p1 = 1 / self.umatanOdds(horse1, horse2)
        p2 = 1 / self.umatanOdds(horse2, horse1)
        p = p1 + p2
        return 1 / p

    def umatanOdds(self, horse1, horse2):
        p1 = horse1.predict.pp_icchaku
        p2 = horse2.predict.pp_nichaku / (1 - horse1.predict.pp_nichaku)
        p = p1 * p2
        return 1 / p

    def wideOddses(self, race):
        return self.oddses(race, "wide")

    def oddses(self, race, baken):
        odds_dict = {}
        for i, horse1 in enumerate(race.racehorses):
            for j in range(i + 1, len(race.racehorses)):
                horse2 = race.racehorses[j]
                odds_dict.update(
                    {
                        f"{horse1.num}-{horse2.num}": self.wideOdds(horse1, horse2)
                        if baken == "wide"
                        else self.umarenOdds(horse1, horse2)
                    }
                )
        return odds_dict

    def wideOdds(self, horse1, horse2):
        p = (
            horse1.predict.pp_icchaku * horse2.predict.pp_nichaku / (1 - horse1.predict.pp_nichaku)
            + horse1.predict.pp_icchaku * horse2.predict.pp_sanchaku / (1 - horse1.predict.pp_sanchaku)
        )
        p += (
            horse1.predict.pp_nichaku * horse2.predict.pp_icchaku / (1 - horse1.predict.pp_icchaku)
            + horse1.predict.pp_nichaku * horse2.predict.pp_sanchaku / (1 - horse1.predict.pp_sanchaku)
        )
        p += (
            horse1.predict.pp_sanchaku * horse2.predict.pp_icchaku / (1 - horse1.predict.pp_icchaku)
            + horse1.predict.pp_sanchaku * horse2.predict.pp_nichaku / (1 - horse1.predict.pp_nichaku)
        )
        return 1 / p

    def wakurenOddses(self, race):
        odds_dict = {}
        for i in range(8):
            for j in range(i, 8):
                gate1 = i + 1
                gate2 = j + 1
                odds_dict.update(
                    {f"{gate1}-{gate2}": self.wakurenOdds(race, gate1, gate2)}
                )
        return odds_dict

    def wakurenOdds(self, race, gate1, gate2):
        horses1 = [horse for horse in race.racehorses if horse.waku == gate1]
        if gate1 == gate2:
            return self.wakurenSameOdds(horses1)
        horses2 = [horse for horse in race.racehorses if horse.waku == gate2]
        pp = 0
        if len(horses1) == 0 or len(horses2) == 0:
            return 0
        for horse1 in horses1:
            for horse2 in horses2:
                pp += 1 / self.umarenOdds(horse1, horse2)
        return 1 / pp

    def wakurenSameOdds(self, horses):
        if len(horses) <= 1:
            return 0
        pp = 0
        for i, horse1 in enumerate(horses):
            for j in range(i + 1, len(horses)):
                horse2 = horses[j]
                pp += 1 / self.umarenOdds(horse1, horse2)
        return 1 / pp
