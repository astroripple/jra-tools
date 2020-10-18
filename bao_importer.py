from horseview.horsemodel import sesobj, KaisaiData, UmarenOddsData

def getKaisaiInfo(kaisaikey):
    return {
        "ba" :kaisaikey[0:2],
        "year" :kaisaikey[2:4],
        "kai" :kaisaikey[4:5],
        "day" :kaisaikey[5:6]
    }

def getCourseCode(kaisaikey):
    return kaisaikey[0:2]

def getRaceKey(bao_info):
    if kaisaikeys[0]["ymd"] <= bao_info["ymd"] <= kaisaikeys[-1]["ymd"]:
        for key in kaisaikeys:
            if key["ymd"] == bao_info["ymd"] and key["course"] == bao_info["bacode"]:
                return key["key"] + bao_info["no"]

def getBaoCodeInfo(race_code):
        year_header = '19' if race_code[0] == '1' else '20'
        return {
            'year': year_header + race_code[1:3],
            'month': race_code[3:5],
            'day': race_code[5:7],
            'ymd': int(year_header + race_code[1:7]),
            'bacode': race_code[7:9],
            'no': race_code[9:11]
        }

def getUmarenOdds(odds):
    odds_dict = {}
    for i, odd_str in enumerate(odds):
        for j in range(0, len(odd_str), 6):
            odds_dict.update({f'{i+1}-{i+int((j+6)/6)+1}': int(odd_str[j:j+6])/10})
    return odds_dict