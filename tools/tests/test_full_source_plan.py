from tools.full_source_deps import source_build_plan


def test_full_source_plan_contains_every_direct_project_dependency():
    plan = source_build_plan()
    names = {stage.name for stage in plan}
    assert {'qtbase', 'pyside6-shiboken6', 'numpy', 'torch', 'pyqtgraph', 'zstandard', 'nuitka', 'ordered-set'} <= names


def test_qt_and_pyside_are_built_before_nuitka_application_compile():
    names = [stage.name for stage in source_build_plan()]
    assert names.index('qtbase') < names.index('pyside6-shiboken6')
    assert names.index('pyside6-shiboken6') < names.index('nuitka')
