from horseview.horsemodel import sesobj, PredictRaceData

class PredictRaceUpdater:
    def update(self, kaisais):
        for k in kaisais:
            for r in raisai.races:
                pred = PredictRaceData(
                    racekey=r.racekey,
                    umaren=self.umarenOddses(race),
                    wide=self.wideOddses(race),
                    wakuren=self.wakurenOddses(race)
                )
                sesobj.add(pred)
        sesobj.commit()
    
    def umarenOddses(self, race):
        odds_dict = {}
        for i, horse1 in enumrate(race.racehorses):
            for j in range(i+1, len(race.racehorses)):
                horse2 = race.racehorses[j]
                odds_dict.update({
                    f"{horse1.num}-{horse2.num}": self.umarenOdds(horse1, horse2)
                })
        return odds_dict

    def umarenOdds(self, horse1, horse2):
        p = horse1.predict.pp_icchaku * horse2.predict.pp_nichaku + horse1.predict.pp_nichaku * horse2.predict.pp_icchaku
        return 1/p

