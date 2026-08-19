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
    def test_sampler_has_no_hard_cap(self):
        from tools.log_mux import VisibleLogSampler
        self.assertNotIn("max_visible", VisibleLogSampler.__dataclass_fields__)
        sampler = VisibleLogSampler(sample_every=8, head_lines=0)
        for i in range(100_000):
            sampler.should_emit(f"ordinary tool noise {i}")
        self.assertFalse(hasattr(sampler, "limit_reached"))

    def test_ninja_style_progress_lines_are_nearly_all_visible(self):
        from tools.log_mux import VisibleLogSampler
        sampler = VisibleLogSampler(sample_every=8, progress_every=1, head_lines=0)
        visible = [line for i in range(1, 1652) if sampler.should_emit(line := f"[{i}/1651] Building CXX object src/file{i}.cpp.obj")]
        self.assertGreaterEqual(len(visible), 1600)

    def test_scons_compiler_commands_are_nearly_all_visible(self):
        from tools.log_mux import VisibleLogSampler
        sampler = VisibleLogSampler(sample_every=8, compiler_every=1, head_lines=0)
        lines = [f"gcc -o module{i}.o -c module{i}.c" for i in range(500)]
        self.assertGreaterEqual(len([line for line in lines if sampler.should_emit(line)]), 450)
        windows = [f'C:\\LLVM\\bin\\cl.exe /c module{i}.c /Fomodule{i}.obj' for i in range(100)]
        self.assertGreaterEqual(len([line for line in windows if sampler.should_emit(line)]), 90)

    def test_important_lines_are_always_emitted(self):
        from tools.log_mux import VisibleLogSampler
        sampler = VisibleLogSampler(sample_every=10_000, head_lines=0)
        self.assertTrue(sampler.should_emit("warning: something suspicious"))
        self.assertTrue(sampler.should_emit("fatal error: compiler exploded"))

    def test_run_logged_preserves_full_log_and_dense_progress_console(self):
        from tools.log_mux import run_logged
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "full.log"
            out = io.StringIO()
            cmd = [sys.executable, "-S", "-c", "for i in range(1651): print(f'[{i+1}/1651] Building CXX object x{i}.cpp')"]
            with contextlib.redirect_stdout(out):
                run_logged(cmd, log_path=log, sample_every=8, progress_every=1, compiler_every=1, head_lines=0)
            self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 1651)
            visible_compile_lines = [line for line in out.getvalue().splitlines() if "Building CXX object" in line]
            self.assertGreaterEqual(len(visible_compile_lines), 1600)
            self.assertIn("Full log:", out.getvalue())
            self.assertNotIn("hard cap", out.getvalue().lower())


class BuildClientVerbosityTests(unittest.TestCase):
    def test_nuitka_keeps_real_compiler_and_progress_output_without_verbose_noise(self):
        build = (ROOT / "tools" / "build_client.py").read_text(encoding="utf-8")
        self.assertIn('"--show-scons"', build)
        self.assertIn('"--show-progress"', build)
        self.assertNotIn('"--verbose"', build)

    def test_windows_nuitka_uses_low_memory_but_linux_does_not(self):
        from tools.build_client import make_nuitka_command

        out = ROOT / "dist-test"
        client = ROOT / "client"
        windows = make_nuitka_command(out, client, platform_name="Windows")
        linux = make_nuitka_command(out, client, platform_name="Linux")
        self.assertIn("--low-memory", windows)
        self.assertNotIn("--low-memory", linux)


if __name__ == "__main__":
    unittest.main()
