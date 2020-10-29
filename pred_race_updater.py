from horseview.horsemodel import sesobj, PredictRaceData


class PredictRaceUpdater:
    def update(self, kaisais):
        for kaisai in kaisais:
            for race in kaisai.races:
                pred = PredictRaceData(
                    racekey=race.racekey,
                    umaren=self.umarenOddses(race),
                    wide=self.wideOddses(race),
                    wakuren=self.wakurenOddses(race),
                )
                sesobj.add(pred)
        sesobj.commit()

    def umarenOddses(self, race):
        return self.oddses(race, "umaren")

    def umarenOdds(self, horse1, horse2):
        p = (
            horse1.predict.pp_icchaku * horse2.predict.pp_nichaku
            + horse1.predict.pp_nichaku * horse2.predict.pp_icchaku
        )
        return 1 / p

    def wideOddses(self, race):
        return self.oddses(race, "wide")

    def oddses(self, race, baken):
        odds_dict = {}
        for i, horse1 in enumrate(race.racehorses):
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
            horse1.predict.pp_icchaku * horse2.predict.pp_nichaku
            + horse1.predict.pp_icchaku * horse2.predict.pp_sanchaku
        )
        p += (
            horse1.predict.pp_nichaku * horse2.predict.pp_icchaku
            + horse1.predict.pp_nichaku * horse2.predict.pp_sanchaku
        )
        p += (
            horse1.predict.pp_sanchaku * horse2.predict.pp_icchaku
            + horse1.predict.pp_sanchaku * horse2.predict.pp_icchaku
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
        for horse1 in horses1:
            for horse2 in horses2:
                pp += 1 / self.umarenOdds(horse1, horse2)
        return 1 / pp

    def wakurenSameOdds(self, horses):
        if len(horses) <= 1:
            return 0
        pp = 0
        for i, horse1 in enumrate(horses):
            for j in range(i + 1, len(horses)):
                horse2 = horses[j]
                pp += 1 / self.umarenOdds(horse1, horse2)
        return 1 / pp
