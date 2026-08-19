# Learning Hub, Kids UI, and Internationalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add multilingual onboarding, a separate Kids UI, tutorials, progress/achievements, and demo learning to MinecraftRLLab.

**Architecture:** Keep RL/server backends intact and add framework-independent learning/i18n/profile modules plus two Qt shells. The existing research UI remains available while `app.py` routes first run and Kids mode to their dedicated windows.

**Tech Stack:** Python 3.12+, PySide6, pyqtgraph, existing PyTorch RL backend, JSON settings/progress storage.

**Spec:** `docs/superpowers/specs/2026-08-19-learning-kids-i18n-design.md`

## Global Constraints
- Existing Paper 26.2 plugin protocol remains compatible.
- Existing Windows/Linux Nuitka build and build-before-tests workflows remain intact.
- English is the translation fallback.
- Shipped locales: English, German, French, Spanish.
- Kids mode is a separate QMainWindow with separate screens.
- Learning/demo state must not fake real Minecraft training success.

---

### Task 1: Translation and profile core
**Files:** create `client/rl_client/i18n/*`, `client/rl_client/profiles/*`; modify `client/rl_client/settings.py`; test `client/tests/test_learning_i18n.py`.

- [x] Write tests for translation lookup, fallback, formatting, locale completeness, experience profile metadata, and settings round-trip.
- [x] Run tests and verify they fail because the new modules/fields do not exist.
- [x] Implement the translation/profile/settings modules.
- [x] Run tests and verify they pass.

### Task 2: Tutorial, progress, achievements, and demo core
**Files:** create `client/rl_client/learning/*`; test `client/tests/test_learning_i18n.py`.

- [x] Add tests for tutorial event advancement, progress persistence, achievement unlocking, and deterministic demo episodes.
- [x] Run tests and verify they fail for missing learning modules.
- [x] Implement models, catalog, engine, progress store, achievements, glossary, and demo environment.
- [x] Run tests and verify they pass.

### Task 3: First-run onboarding and routing
**Files:** create `client/rl_client/ui/onboarding.py`; modify `client/rl_client/app.py` and `client/rl_client/settings.py`.

- [x] Add pure routing tests for first-run/research/kids mode selection.
- [x] Verify RED.
- [x] Implement `select_shell()` plus onboarding UI and app routing.
- [x] Verify GREEN and syntax-compile Qt modules.

### Task 4: Dedicated Kids UI
**Files:** create `client/rl_client/ui/kids/*` and `client/rl_client/ui/theme_kids.py`.

- [x] Define/test child-friendly goal and learning view-models independently of Qt.
- [x] Verify RED.
- [x] Implement KidsMainWindow, Home, Missions, Learn, Progress, and Server screens using the shared RL/API backend.
- [x] Verify GREEN and syntax-compile Qt modules.

### Task 5: Translate research shell and add Learning Hub
**Files:** modify `client/rl_client/ui/main_window.py`, screen modules, settings; create `client/rl_client/ui/screens/learning.py`.

- [x] Add translation-key coverage tests for all research navigation/screen titles introduced by this change.
- [x] Verify RED.
- [x] Inject `Translator` into research screens, add Learning Hub, and expose language/mode settings.
- [x] Verify GREEN and syntax-compile Qt modules.

### Task 6: Packaging, docs, and full verification
**Files:** modify `README.md`, build/package scripts if required.

- [x] Ensure Nuitka includes locale/learning modules and bundled plugin unchanged.
- [x] Run all Python tests, build-priority tests, Python compileall, and offline Paper plugin tests/build.
- [x] Validate both GitHub workflow YAML files.
- [x] Create clean `MinecraftRLLab-GitHub-Learning.zip` and integrity-test the archive.
