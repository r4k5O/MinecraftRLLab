from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")


def test_dependencies_are_installed_normally_from_requirements():
    assert "python -m pip install -r requirements-build.txt" in WORKFLOW
    assert "Dependencies installed from prebuilt wheels" in WORKFLOW


def test_full_source_dependency_build_is_gone():
    forbidden = (
        "full_source_deps.py",
        "full-source",
        "MCRL_FORGE_KEY",
        "MCRL_FORGE_JOBS",
        "MCRL_QT_REF",
        "MCRL_PYSIDE_REF",
        "MCRL_TORCH_REF",
        "forge_gate.py",
        "A deeper furnace has awakened",
    )
    for token in forbidden:
        assert token not in WORKFLOW


def test_obsolete_forge_files_are_removed():
    obsolete = (
        ROOT / ".github" / ".forge.md",
        ROOT / "tools" / ".forge_token.py",
        ROOT / "tools" / "forge_gate.py",
        ROOT / "tools" / "full_source_deps.py",
        ROOT / "tools" / "tests" / "test_forge_gate.py",
        ROOT / "tools" / "tests" / "test_full_source_plan.py",
    )
    for path in obsolete:
        assert not path.exists(), path


def test_native_build_uses_dense_real_output_without_hard_caps():
    assert "python tools/build_client.py --output dist" in WORKFLOW
    assert "tools/log_mux.py" in WORKFLOW
    assert "VISIBLE_LOG_LIMIT" not in WORKFLOW
    assert "--max-visible" not in WORKFLOW
    assert "--progress-every 1" in WORKFLOW
    assert "--compiler-every 1" in WORKFLOW
    assert "--sample-every 8" in WORKFLOW
