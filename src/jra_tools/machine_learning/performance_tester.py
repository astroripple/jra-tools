from tensorflow.keras.models import load_model
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt
import numpy as np
from .input_creator import InputCreator
from .label_creator import LabelCreator


class PerformanceTester:
    CONDS = {
        "04": "1勝クラス",
        "05": "1勝クラス",
        "08": "2勝クラス",
        "09": "2勝クラス",
        "10": "2勝クラス",
        "15": "3勝クラス",
        "16": "3勝クラス",
        "A1": "新馬",
        "A2": "未出走",
        "A3": "未勝利",
        "OP": "オープン",
    }

    def __init__(self, model_name, kaisais):
        self.model = load_model(model_name)
        self.model_name = model_name
        self.kaisais = kaisais
        self.recoveries = self.get_recoveries(kaisais)
        ymds = list(set([kaisai.ymd for kaisai in kaisais]))
        ymds.sort()
        self.period = f"{ymds[0]} - {ymds[-1]}"

    def output_performance(self):
        self.draw_annual_performance(self.get_monthly_recovery(self.recoveries))
        self.draw_course_recovery(self.get_course_recovery(self.recoveries))
        self.draw_cond_win_rates(self.kaisais)
        self.draw_cond_recovery_rates(self.kaisais)

    def draw_model(self):
        plot_model(self.model, to_file=f"{self.model_name}.png")

    def get_recoveries(self, kaisais):
        return [self.get_kaisai_recovery(kaisai) for kaisai in kaisais]

    def get_kaisai_recovery(self, kaisai):
        ic = InputCreator([kaisai])
        lc = LabelCreator([kaisai])
        preds = self.model.predict(ic.x_data)

        cnt = 0
        win = 0
        bet = 0
        ret = 0
        for race in kaisai.races:
            icchaku = np.argsort(preds[0][cnt])[::-1]
            w_icchaku = icchaku[0]
            bet += 100
            if w_icchaku == np.argmax(lc.t_icchaku[cnt]):
                win += 1
                ret += race.returninfo.win1_ret
            cnt += 1
        return {
            "ymd": kaisai.ymd,
            "course": kaisai.course_name,
            "race_count": cnt,
            "win": win,
            "bet": bet,
            "ret": ret,
        }

    def get_monthly_recovery(self, recoveries):
        rate = {}
        for recovery in recoveries:
            if str(recovery["ymd"])[:6] in rate:
                rate[str(recovery["ymd"])[:6]]["bet"] += recovery["bet"]
                rate[str(recovery["ymd"])[:6]]["ret"] += recovery["ret"]
                rate[str(recovery["ymd"])[:6]]["race_count"] += recovery["race_count"]
                rate[str(recovery["ymd"])[:6]]["win"] += recovery["win"]
            else:
                inital = {
                    str(recovery["ymd"])[:6]: {
                        "bet": recovery["bet"],
                        "ret": recovery["ret"],
                        "race_count": recovery["race_count"],
                        "win": recovery["win"],
                    }
                }
                rate.update(inital)
        return rate

    def draw_annual_performance(self, monthlyRecovery):
        title = f"月別パフォーマンス({self.period})"

        recovery_rates = [v["ret"] / v["bet"] for v in monthlyRecovery.values()]
        win_rates = [v["win"] / v["race_count"] for v in monthlyRecovery.values()]
        fig, ax = plt.subplots()
        ax.plot([i for i in range(1, 13)], recovery_rates, label="Recovery")
        ax.plot([i for i in range(1, 13)], win_rates, label="Win")

        ax.set_title(title)
        ax.set_ylabel("rate")
        ax.set_xlim(1, 12)
        ax.set_xlabel("Month")
        ax.legend()
        fig.savefig(f"{title}.svg")

    def get_course_recovery(self, recoveries):
        rate = {}
        for recovery in recoveries:
            if recovery["course"] in rate:
                rate[recovery["course"]]["bet"] += recovery["bet"]
                rate[recovery["course"]]["ret"] += recovery["ret"]
                rate[recovery["course"]]["race_count"] += recovery["race_count"]
                rate[recovery["course"]]["win"] += recovery["win"]
            else:
                inital = {
                    recovery["course"]: {
                        "bet": recovery["bet"],
                        "ret": recovery["ret"],
                        "race_count": recovery["race_count"],
                        "win": recovery["win"],
                    }
                }
                rate.update(inital)
        return rate

    def draw_course_recovery(self, course_recovery):
        title = f"コース別パフォーマンス ({self.period})"
        fig, ax = plt.subplots()

        ret_mean = sum([v["ret"] for v in course_recovery.values()]) / sum(
            [v["bet"] for v in course_recovery.values()]
        )
        win_mean = sum([v["win"] for v in course_recovery.values()]) / sum(
            [v["race_count"] for v in course_recovery.values()]
        )
        ax.axhline(ret_mean, color="blue", linewidth=2, linestyle=":")
        ax.axhline(win_mean, color="orange", linewidth=2, linestyle=":")

        labels = [v for v in course_recovery.keys()]
        x = np.arange(len(labels))
        width = 0.35

        ax.bar(
            x - width / 2,
            [v["ret"] / v["bet"] for v in course_recovery.values()],
            width,
            label="回収率",
        )
        ax.bar(
            x + width / 2,
            [v["win"] / v["race_count"] for v in course_recovery.values()],
            width,
            label="的中率",
        )
        ax.set_title(title)
        ax.set_ylabel("rate")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        fig.savefig(f"{title}.svg")

    def get_race_recoveries(self, kaisai):
        ic = InputCreator([kaisai])
        lc = LabelCreator([kaisai])
        preds = self.model.predict(ic.x_data)

        cnt = 0
        recoveries = []
        for race in kaisai.races:
            win = 0
            bet = 0
            ret = 0
            icchaku = np.argsort(preds[0][cnt])[::-1]
            w_icchaku = icchaku[0]
            bet += 100
            if w_icchaku == np.argmax(lc.t_icchaku[cnt]):
                win += 1
                ret += race.returninfo.win1_ret
            recoveries.append(
                {
                    "ymd": kaisai.ymd,
                    "course": kaisai.course_name,
                    "shubetsu": race.shubetsu,
                    "joken": race.joken,
                    "win": win,
                    "bet": bet,
                    "ret": ret,
                }
            )
            cnt += 1
        return recoveries

    def get_kaisais_recoveries(self, kaisais):
        return [self.get_race_recoveries(kaisai) for kaisai in kaisais]

    def get_joken_recovery(self, kaisais):
        kaisais_recoveries = self.get_kaisais_recoveries(kaisais)
        rate = {}
        for kaisai_recoveries in kaisais_recoveries:
            for r in kaisai_recoveries:
                month = str(r["ymd"])[:6]
                if month in rate:
                    if r["joken"] in rate[month]:
                        rate[month][r["joken"]]["count"] += 1
                        rate[month][r["joken"]]["win"] += r["win"]
                        rate[month][r["joken"]]["bet"] += 100
                        rate[month][r["joken"]]["ret"] += r["ret"]
                    else:
                        rate[month].update(
                            {
                                r["joken"]: {
                                    "count": 1,
                                    "win": r["win"],
                                    "bet": 100,
                                    "ret": r["ret"],
                                }
                            }
                        )
                else:
                    rate.update(
                        {
                            month: {
                                r["joken"]: {
                                    "count": 1,
                                    "win": r["win"],
                                    "bet": 100,
                                    "ret": r["ret"],
                                }
                            }
                        }
                    )
        return rate

    def get_win_rate(self, joken_recovery, cond):
        results = []
        for month in joken_recovery.keys():
            result = joken_recovery[month].get(cond, 0)
            results.append(result["win"] / result["count"] if result != 0 else 0)
        return results

    def get_recovery_rate(self, joken_recovery, cond):
        results = []
        for month in joken_recovery.keys():
            result = joken_recovery[month].get(cond, 0)
            results.append(result["ret"] / result["bet"] if result != 0 else 0)
        return results

    def draw_cond_win_rates(self, kaisais):
        joken_recovery = self.get_joken_recovery(kaisais)
        title = f"月別一番手評価馬的中率({self.period})"
        fig, ax = plt.subplots()
        for cond in ["A1", "A3", "05", "10", "16", "OP"]:
            win_rates = self.get_win_rate(joken_recovery, cond)
            ax.plot([i for i in range(1, 13)], win_rates, label=f"{self.CONDS[cond]}")

        ax.set_title(title)
        ax.set_ylabel("Win Rate")
        ax.set_xlim(1, 12)
        ax.set_xlabel("Month")
        ax.legend()
        fig.savefig(f"{title}.svg")

    def draw_cond_recovery_rates(self, kaisais):
        joken_recovery = self.get_joken_recovery(kaisais)
        title = f"月別一番手評価馬回収率({self.period})"
        fig, ax = plt.subplots()
        for cond in ["A1", "A3", "05", "10", "16", "OP"]:
            recovery_rates = self.get_recovery_rate(joken_recovery, cond)
            ax.plot(
                [i for i in range(1, 13)], recovery_rates, label=f"{self.CONDS[cond]}"
            )

        ax.set_title(title)
        ax.set_ylabel("Recovery Rate")
        ax.set_xlim(1, 12)
        ax.set_xlabel("Month")
        ax.legend()
        fig.savefig(f"{title}.svg")
