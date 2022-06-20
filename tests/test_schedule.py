import unittest, sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import schedule


class TestSchedule(unittest.TestCase):
    def test_annual_schedule(self):
        days = schedule.annual_schedule(2018)
        self.assertEqual(len(days), 109)
        self.assertEqual(days[0], 20180106)
        self.assertEqual(days[-1], 20181228)
        self.assertEqual(days[54], 20180701)


if __name__ == "__main__":
    # スクリプトとして実行された場合の処理
    unittest.main(verbosity=2)
