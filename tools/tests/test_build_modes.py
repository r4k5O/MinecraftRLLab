from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / '.github' / 'workflows' / 'build.yml').read_text(encoding='utf-8')


def test_normal_mode_is_the_default_and_is_exported_by_metadata():
    assert 'mode: ${{ steps.forge.outputs.mode }}' in WORKFLOW
    assert 'tools/forge_gate.py' in WORKFLOW


def test_normal_dependency_install_is_guarded_to_normal_mode():
    assert "needs.metadata.outputs.mode == 'normal'" in WORKFLOW
    assert 'pip install -r requirements-build.txt' in WORKFLOW


def test_full_source_dependency_build_is_guarded_to_full_source_mode():
    assert "needs.metadata.outputs.mode == 'full-source'" in WORKFLOW
    assert 'tools/full_source_deps.py' in WORKFLOW


def test_release_records_resolved_build_mode():
    assert 'BUILD_MODE: ${{ needs.metadata.outputs.mode }}' in WORKFLOW


def test_workflow_can_leave_forge_secret_empty_for_default_fallback():
    assert 'MCRL_FORGE_KEY: ${{ secrets.MCRL_FORGE_KEY }}' in WORKFLOW
