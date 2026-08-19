from __future__ import annotations

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class LogMuxTests(unittest.TestCase):
    def test_sampler_caps_visible_output(self):
        from tools.log_mux import VisibleLogSampler

        sampler = VisibleLogSampler(max_visible=25, sample_every=5, head_lines=3)
        emitted = []
        for i in range(500):
            line = f"[{i+1}/500] Building CXX object file_{i}.cpp"
            if sampler.should_emit(line):
                emitted.append(line)

        self.assertLessEqual(len(emitted), 25)
        self.assertGreater(len(emitted), 3)
        self.assertTrue(sampler.limit_reached or sampler.suppressed > 0)

    def test_important_lines_are_prioritized_before_limit(self):
        from tools.log_mux import VisibleLogSampler

        sampler = VisibleLogSampler(max_visible=20, sample_every=50, head_lines=1)
        self.assertTrue(sampler.should_emit("starting"))
        for i in range(10):
            sampler.should_emit(f"[{i+1}/100] Building CXX object x{i}.cpp")
        self.assertTrue(sampler.should_emit("warning: something suspicious"))
        self.assertTrue(sampler.should_emit("fatal error: compiler exploded"))

    def test_run_logged_preserves_full_log_while_capping_console(self):
        from tools.log_mux import run_logged

        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "full.log"
            out = io.StringIO()
            cmd = [sys.executable, "-c", "for i in range(200): print(f'[{i+1}/200] Building CXX object x{i}.cpp')"]
            with contextlib.redirect_stdout(out):
                run_logged(cmd, log_path=log, max_visible=30, sample_every=7)

            full_lines = log.read_text(encoding="utf-8").splitlines()
            visible_compile_lines = [line for line in out.getvalue().splitlines() if "Building CXX object" in line]
            self.assertEqual(len(full_lines), 200)
            self.assertLessEqual(len(visible_compile_lines), 30)
            self.assertIn("Full log:", out.getvalue())


class WorkflowBudgetTests(unittest.TestCase):
    def test_build_workflow_caps_all_large_output_sources(self):
        workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
        self.assertIn("MCRL_FORGE_VISIBLE_LOG_LIMIT: '12000'", workflow)
        self.assertIn("MCRL_NUITKA_VISIBLE_LOG_LIMIT: '8000'", workflow)
        self.assertIn("MCRL_GRADLE_VISIBLE_LOG_LIMIT: '5000'", workflow)
        self.assertIn("tools/log_mux.py", workflow)
        self.assertIn("build-logs-${{ matrix.platform }}", workflow)
        self.assertNotIn('find "$DIST_DIR" -type f | sort', workflow)


if __name__ == "__main__":
    unittest.main()
