from __future__ import annotations
import unittest
from tools.build_queue import active_builds

class BuildPriorityTest(unittest.TestCase):
    def test_tests_wait_while_any_build_is_active(self):
        runs=[{"status":"completed"},{"status":"queued","run_number":2},{"status":"in_progress","run_number":3}]
        self.assertEqual([r["run_number"] for r in active_builds(runs)],[2,3])
    def test_tests_may_start_when_build_queue_is_empty(self):
        self.assertEqual(active_builds([{"status":"completed"},{"status":"completed"}]),[])

if __name__=="__main__":unittest.main()
