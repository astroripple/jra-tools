import numpy as np
from . import training_tool


class LabelCreator:
    def __init__(self, kaisais):
        num_race = training_tool.numberOfRaces(kaisais)
        num_max_horse = 18
        self.t_icchaku = np.zeros([num_race, num_max_horse])
        self.t_nichaku = np.zeros([num_race, num_max_horse])
        self.t_sanchaku = np.zeros([num_race, num_max_horse])
        self.t_yonchaku = np.zeros([num_race, num_max_horse])
        self.t_gochaku = np.zeros([num_race, num_max_horse])
        w_num = 0
        for kaisai in kaisais:
            for race in kaisai.races:
                for horse in race.racehorses:
                    oa = horse.result.order_of_arrival
                    if oa == 1:
                        self.t_icchaku[w_num, horse.num - 1] = 1
                    elif oa == 2:
                        self.t_nichaku[w_num, horse.num - 1] = 1
                    elif oa == 3:
                        self.t_sanchaku[w_num, horse.num - 1] = 1
                    elif oa == 4:
                        self.t_yonchaku[w_num, horse.num - 1] = 1
                    elif oa == 5:
                        self.t_gochaku[w_num, horse.num - 1] = 1
                w_num += 1
        self.labels = [
            self.t_icchaku,
            self.t_nichaku,
            self.t_sanchaku,
            self.t_yonchaku,
            self.t_gochaku,
        ]
