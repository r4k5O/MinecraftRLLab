from __future__ import annotations

import unittest
from rl_client.core.metrics import EpisodeMetric, MetricHistory


class MetricHistoryTest(unittest.TestCase):
    def test_summary_metrics(self):
        history=MetricHistory()
        history.add(EpisodeMetric(1,10,2.0,True,"goal"))
        history.add(EpisodeMetric(2,20,-1.0,False,"timeout"))
        self.assertAlmostEqual(history.success_rate,0.5)
        self.assertEqual(history.best_reward,2.0)
        self.assertAlmostEqual(history.average_reward,0.5)


if __name__ == "__main__":unittest.main()
