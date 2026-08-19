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
    def test_sampler_has_no_hard_cap_and_samples_long_streams(self):
        from tools.log_mux import VisibleLogSampler

        self.assertNotIn("max_visible", VisibleLogSampler.__dataclass_fields__)
        sampler = VisibleLogSampler(sample_every=10, head_lines=3)
        emitted = []
        for i in range(100_000):
            line = f"[{i+1}/100000] Building CXX object file_{i}.cpp"
            if sampler.should_emit(line):
                emitted.append(line)

        self.assertGreater(len(emitted), 1_000)
        self.assertLess(len(emitted), 20_000)
        self.assertFalse(hasattr(sampler, "limit_reached"))

    def test_important_lines_are_always_emitted(self):
        from tools.log_mux import VisibleLogSampler

        sampler = VisibleLogSampler(sample_every=10_000, head_lines=0)
        self.assertTrue(sampler.should_emit("warning: something suspicious"))
        self.assertTrue(sampler.should_emit("fatal error: compiler exploded"))

    def test_run_logged_preserves_full_log_while_sampling_console(self):
        from tools.log_mux import run_logged

        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "full.log"
            out = io.StringIO()
            cmd = [sys.executable, "-c", "for i in range(2000): print(f'[{i+1}/2000] Building CXX object x{i}.cpp')"]
            with contextlib.redirect_stdout(out):
                run_logged(cmd, log_path=log, sample_every=20, head_lines=5)

            full_lines = log.read_text(encoding="utf-8").splitlines()
            visible_compile_lines = [line for line in out.getvalue().splitlines() if "Building CXX object" in line]
            self.assertEqual(len(full_lines), 2000)
            self.assertGreater(len(visible_compile_lines), 5)
            self.assertLess(len(visible_compile_lines), 200)
            self.assertIn("Full log:", out.getvalue())
            self.assertNotIn("hard cap", out.getvalue().lower())


class BuildClientVerbosityTests(unittest.TestCase):
    def test_nuitka_keeps_scons_but_drops_extra_verbosity(self):
        build = (ROOT / "tools" / "build_client.py").read_text(encoding="utf-8")
        self.assertIn('"--show-scons"', build)
        self.assertNotIn('"--verbose"', build)
        self.assertNotIn('"--show-progress"', build)


if __name__ == "__main__":
    unittest.main()
