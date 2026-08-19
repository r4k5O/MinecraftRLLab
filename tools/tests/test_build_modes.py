from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
INSTALLER_WORKFLOW = (ROOT / ".github" / "workflows" / "installer.yml").read_text(encoding="utf-8")


class BuildModesTest(unittest.TestCase):
    def test_dependencies_are_installed_normally_from_requirements(self):
        self.assertIn("python -m pip install -r requirements-build.txt", WORKFLOW)
        self.assertIn("Dependencies installed from prebuilt wheels", WORKFLOW)

    def test_full_source_dependency_build_is_gone(self):
        forbidden = ("full_source_deps.py", "full-source", "MCRL_FORGE_KEY", "MCRL_FORGE_JOBS", "MCRL_QT_REF", "MCRL_PYSIDE_REF", "MCRL_TORCH_REF", "forge_gate.py", "A deeper furnace has awakened")
        for token in forbidden:
            self.assertNotIn(token, WORKFLOW)

    def test_obsolete_forge_files_are_removed(self):
        obsolete = (ROOT / ".github" / ".forge.md", ROOT / "tools" / ".forge_token.py", ROOT / "tools" / "forge_gate.py", ROOT / "tools" / "full_source_deps.py", ROOT / "tools" / "tests" / "test_forge_gate.py", ROOT / "tools" / "tests" / "test_full_source_plan.py")
        for path in obsolete:
            self.assertFalse(path.exists(), path)

    def test_native_build_uses_dense_real_output_without_hard_caps(self):
        self.assertIn("python tools/build_client.py --output dist", WORKFLOW)
        self.assertIn("tools/log_mux.py", WORKFLOW)
        self.assertNotIn("VISIBLE_LOG_LIMIT", WORKFLOW)
        self.assertNotIn("--max-visible", WORKFLOW)
        self.assertIn("--progress-every 1", WORKFLOW)
        self.assertIn("--compiler-every 1", WORKFLOW)
        self.assertIn("--sample-every 8", WORKFLOW)

    def test_nuitka_cache_is_persistent_and_platform_scoped(self):
        for token in ("actions/cache@v4", "NUITKA_CACHE_DIR", ".nuitka-cache", "runner.os", "runner.arch", "restore-keys"):
            self.assertIn(token, WORKFLOW)

    def test_installer_has_separate_path_filtered_workflow(self):
        for token in ("MinecraftRLLab-Setup.exe", "MinecraftRLLab-Setup", "paths:", "installer/**", "gh release create setup", "--latest=false"):
            self.assertIn(token, INSTALLER_WORKFLOW)

    def test_installer_uses_platform_correct_pythonpath(self):
        self.assertIn("pythonpath: 'client;.'", INSTALLER_WORKFLOW)
        self.assertIn("pythonpath: 'client:.'", INSTALLER_WORKFLOW)
        self.assertIn("PYTHONPATH: ${{ matrix.pythonpath }}", INSTALLER_WORKFLOW)
        self.assertNotIn("PYTHONPATH: client:.", INSTALLER_WORKFLOW)


if __name__ == "__main__":
    unittest.main()
