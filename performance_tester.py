import numpy as np
from tensorflow.keras.models import Model,load_model
from .input_creator import InputCreator
from .label_creator import LabelCreator

class PeformanceTester:
    def __init__(self, model_name, kaisais):
        #モデルのロード
        self.model = load_model(modelname)
        self.recoveries = get_recoveries(kaisais)

    def output_performance():
        draw_annual_performance(get_monthly_recovery(self.recoveries))
        draw_course_recovery(get_course_recovery(self.recoveries))

    def get_recoveries(kaisais):
        ic = InputCreator(kaisais)
        lc = LabelCreator(kaisais)    
        preds = self.model.predict(ic.x_data)

        w = 0
        results = []
        
        for kaisai in kaisais:
            cnt = 0
            win = 0
            bet = 0
            ret = 0
            for race in kaisai.races:
                icchaku = np.argsort(preds[0][w])[::-1]
                w_icchaku = icchaku[0]
                cnt += 1
                bet += 100
                if w_icchaku == np.argmax(lc.t_icchaku[w]):
                    win += 1
                    ret += race.returninfo.win1_ret
                w += 1
            results.append({"ymd": kaisai.ymd, "course": kaisai.course_name, "race_count": cnt, "win": win, "bet": bet, "ret": ret})

        return results

    def get_monthly_recovery(recoveries):
        rate = {}
        for recovery in recoveries:
            if str(recovery['ymd'])[:6] in rate:
                rate[str(recovery['ymd'])[:6]]["bet"] += recovery['bet']
                rate[str(recovery['ymd'])[:6]]["ret"] += recovery['ret']
                rate[str(recovery['ymd'])[:6]]["race_count"] += recovery['race_count']
                rate[str(recovery['ymd'])[:6]]["win"] += recovery['win']
            else:
                inital = {
                    str(recovery['ymd'])[:6]: {
                        "bet": recovery['bet'],
                        "ret": recovery['ret'],
                        "race_count": recovery['race_count'],
                        "win": recovery['win']
                    }
                }
                rate.update(inital)
        return rate

    def draw_annual_performance(monthlyRecovery):
        total_recovery_rate = []
        total_win_rate = []
        title = '月別年間パフォーマンス'
        for v in monthlyRecovery.values():
            total_recovery_rate.append(v["ret"] / v["bet"])
            total_win_rate.append(v["win"] / v["race_count"])
        
        fig, ax = plt.subplots()
        ax.plot([i for i in range(1, 13)], total_recovery_rate, label='Recovery')
        ax.plot([i for i in range(1, 13)], total_win_rate, label='Win')
        ax.set_title(title)
        ax.set_ylabel('rate')
        ax.set_xlim(1, 12)
        ax.set_xlabel('Month')
        ax.legend()    
        fig.savefig(f"{title}.svg")

    def get_course_recovery(recoveries):
        rate = {}
        for recovery in recoveries:
            if recovery['course'] in rate:
                rate[recovery['course']]["bet"] += recovery['bet']
                rate[recovery['course']]["ret"] += recovery['ret']
                rate[recovery['course']]["race_count"] += recovery['race_count']
                rate[recovery['course']]["win"] += recovery['win']
            else:
                inital = {
                    recovery['course']: {
                        "bet": recovery['bet'],
                        "ret": recovery['ret'],
                        "race_count": recovery['race_count'],
                        "win": recovery['win']
                    }
                }
                rate.update(inital)
        return rate

    def draw_course_recovery(course_recovery):
        title = 'コース別年間パフォーマンス'
        fig, ax = plt.subplots()

        labels = [v for v in course_recovery.keys()]
        x = np.arange(len(labels))
        width = 0.35

        ax.bar(x - width/2, [v['ret'] / v['bet'] for v in course_recovery.values()], width, label='回収率')
        ax.bar(x + width/2, [v['win'] / v['race_count'] for v in course_recovery.values()], width, label='的中率')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        fig.savefig(f"{title}.svg")