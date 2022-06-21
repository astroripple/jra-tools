from jrdb_model import sesobj, UmarenOddsData, WideOddsData, WakurenOddsData
import csv


class BaoImporter:
    def __init__(self, kaisais):
        self.kaisaikeys = [
            {
                "course": self.getCourseCode(kaisai.kaisaikey),
                "ymd": kaisai.ymd,
                "key": kaisai.kaisaikey,
            }
            for kaisai in kaisais
        ]
        self.racekeys = [race.racekey for kaisai in kaisais for race in kaisai.races ]

    def getKaisaiInfo(self, kaisaikey):
        return {
            "ba": kaisaikey[0:2],
            "year": kaisaikey[2:4],
            "kai": kaisaikey[4:5],
            "day": kaisaikey[5:6],
        }

    def getCourseCode(self, kaisaikey):
        return kaisaikey[0:2]

    def getRaceKey(self, bao_info):
        if self.kaisaikeys[0]["ymd"] <= bao_info["ymd"] <= self.kaisaikeys[-1]["ymd"]:
            for key in self.kaisaikeys:
                if (
                    key["ymd"] == bao_info["ymd"]
                    and key["course"] == bao_info["bacode"]
                ):
                    return key["key"] + bao_info["no"]

    def getBaoCodeInfo(self, race_code):
        year_header = "19" if race_code[0] == "1" else "20"
        return {
            "year": year_header + race_code[1:3],
            "month": race_code[3:5],
            "day": race_code[5:7],
            "ymd": int(year_header + race_code[1:7]),
            "bacode": race_code[7:9],
            "no": race_code[9:11],
        }

    def getUmarenOdds(self, odds):
        odds_dict = {}
        for i, odd_str in enumerate(odds):
            for j in range(0, len(odd_str), 6):
                odds_dict.update(
                    {f"{i+1}-{i+int((j+6)/6)+1}": int(odd_str[j : j + 6]) / 10}
                )
        return odds_dict

    def getWideOdds(self, odds):
        odds_dict = {}
        for i, odd_str in enumerate(odds):
            for j in range(0, len(odd_str), 10):
                odds_dict.update(
                    {
                        f"{i+1}-{i+int((j+10)/10)+1}": {
                            "min": int(odd_str[j : j + 5]) / 10,
                            "max": int(odd_str[j + 5 : j + 10]) / 10,
                        }
                    }
                )
        return odds_dict

    def getWakurenOdds(self, odds_str):
        odds_dict = {}
        pos = 0
        for i in range(8):
            for j in range(i, 8):
                odd = odds_str[pos : pos + 5].strip()
                odd = int(odd) / 10 if odd else None
                odds_dict.update({f"{i+1}-{j+1}": odd})
                pos += 5
        return odds_dict

    def convertRaceCodeToRaceKey(self, raceCode):
        bao_info = self.getBaoCodeInfo(raceCode)
        return self.getRaceKey(bao_info)

    def importUmarenWideCsv(self, fileName):
        with open(fileName) as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                racekey = self.convertRaceCodeToRaceKey(str(int(float(row[2]))))
                if racekey:
                    odd = UmarenOddsData() if "umaren" in fileName else WideOddsData()
                    odd.racekey = racekey
                    odd.data_kbn = self._parseInt(row[0])
                    odd.registered_horses = self._parseInt(row[4])
                    odd.ran_horses = self._parseInt(row[5])
                    odd.sold_flg = self._parseInt(row[6])
                    odd.all_odds = (
                        self.getUmarenOdds(row[7].split())
                        if "umaren" in fileName
                        else self.getWideOdds(row[7].split())
                    )
                    odd.sum_of_all_bought_count = self._parseInt(row[8])
                    if racekey in self.racekeys:
                        sesobj.add(odd)
            sesobj.commit()

    def importWakurenCsv(self, fileName):
        with open(fileName) as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                racekey = self.convertRaceCodeToRaceKey(str(int(float(row[2]))))
                if racekey:
                    odd = WakurenOddsData()
                    odd.racekey = racekey
                    odd.data_kbn = self._parseInt(row[0])
                    odd.registered_horses = self._parseInt(row[4])
                    odd.ran_horses = self._parseInt(row[5])
                    odd.sold_flg = self._parseInt(row[8])
                    odd.all_odds = self.getWakurenOdds(row[12])
                    odd.sum_of_all_bought_count = self._parseInt(row[15])
                    if racekey in self.racekeys:
                        sesobj.add(odd)
            sesobj.commit()

    def _parseInt(self, str):
        return 0 if str == '' else str