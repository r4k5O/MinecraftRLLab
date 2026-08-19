# MinecraftRLLab Self-Update + Bootstrap Installer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe in-app self-updates, a stable first-install bootstrap/deinstaller, and reusable Nuitka compiler caches while preserving the current release/verification semantics.

**Architecture:** Extend the existing GitHub release client with deterministic asset selection and staged downloads. Installed builds use a managed `app/` payload plus a small maintenance helper for post-exit swaps/rollback/uninstall; the GUI owns update checks/download initiation. A separate installer workflow builds the bootstrap only when installer sources change, while normal Nightly builds gain persistent Nuitka caches.

**Tech Stack:** Python 3.13 stdlib, PySide6, Nuitka, GitHub Actions (`actions/cache@v4`), Windows registry via `winreg`, Linux `.desktop` integration.

**Spec:** `docs/superpowers/specs/2026-08-19-self-update-installer-design.md`

## Global Constraints

- Third-party Python dependencies are installed from prebuilt wheels; dependency source compilation stays removed.
- Normal Nightly release order remains build -> publish prerelease -> release-triggered verification.
- `main` is not updated until implementation and local verification are complete.
- Updates never overwrite models, training data, settings, or arbitrary user paths.
- Release archives and SHA-256 data are verified before activation.
- Windows and Linux x64 remain supported targets.
- The bootstrap installer is not rebuilt for every app Nightly.

---

### Task 1: Release asset selection and installed-build comparison

**Files:**
- Modify: `client/rl_client/update/models.py`
- Modify: `client/rl_client/update/github.py`
- Modify: `client/rl_client/version.py`
- Test: `client/tests/test_update_and_server.py`

**Interfaces:**
- Produces: `ReleaseBuild.build_number -> int | None`
- Produces: `ReleaseBuild.asset_for(platform: str) -> dict | None`
- Produces: `ReleaseBuild.checksum_asset() -> dict | None`
- Produces: `GitHubReleaseClient.is_newer(release, installed_build) -> bool`
- Produces: `load_build_info().build` as the installed build identifier.

- [ ] Write tests for numeric build extraction, deterministic Windows/Linux archive selection, checksum selection, and comparison against installed build.
- [ ] Run `PYTHONPATH=client:. python -m pytest client/tests/test_update_and_server.py -q` and verify RED failures reference missing new interfaces.
- [ ] Implement model properties and comparison helpers with exact asset suffixes `-Windows-x64.zip` and `-Linux-x64.tar.gz`.
- [ ] Re-run the focused test file and verify GREEN.

### Task 2: Download, checksum verification, and safe archive staging

**Files:**
- Create: `client/rl_client/update/package.py`
- Test: `client/tests/test_update_package.py`

**Interfaces:**
- Produces: `parse_sha256sums(text: str) -> dict[str, str]`
- Produces: `sha256_file(path: Path) -> str`
- Produces: `verify_file(path: Path, expected: str) -> None`
- Produces: `safe_extract_archive(archive: Path, destination: Path) -> Path`
- Produces: `validate_package_root(root: Path, platform: str) -> dict`
- Produces: `download_to(url: str, destination: Path, progress=None) -> Path`

- [ ] Write tests for checksum parsing, a matching/mismatching digest, ZIP/TAR extraction, absolute/traversal-path rejection, `PACKAGE_INFO.json` platform validation, and expected main-executable presence.
- [ ] Run focused tests and verify they fail before implementation.
- [ ] Implement only stdlib-based download/hash/archive code; reject archive members resolving outside the destination.
- [ ] Re-run focused tests and verify GREEN.

### Task 3: Managed installation metadata, atomic apply, rollback, and uninstall allow-list

**Files:**
- Create: `client/rl_client/update/install.py`
- Create: `tools/maintenance_helper.py`
- Test: `client/tests/test_update_install.py`
- Test: `tools/tests/test_maintenance_helper.py`

**Interfaces:**
- Produces: `InstallLayout.from_root(root: Path) -> InstallLayout`
- Produces: `InstallMetadata.load/save(...)`
- Produces: `activate_staged_update(layout, staged_app, launch_command, health_timeout) -> None`
- Produces: `allowed_uninstall_paths(layout, remove_user_data=False) -> tuple[Path, ...]`
- Helper CLI: `--apply-plan <json>`, `--uninstall <metadata.json> [--remove-user-data]`.

- [ ] Write temp-directory tests proving payload swap, rollback restoration, default preservation of `models/` and `user-data/`, and refusal to delete paths outside managed roots.
- [ ] Run focused tests and verify RED.
- [ ] Implement metadata/layout and helper operations; use rename/replace operations within one install root and preserve rollback until a health marker exists.
- [ ] Re-run focused tests and verify GREEN.

### Task 4: In-app self-update UI and auto-check

**Files:**
- Create: `client/rl_client/update/service.py`
- Modify: `client/rl_client/ui/screens/updates.py`
- Modify: `client/rl_client/ui/main_window.py`
- Modify: `client/rl_client/app.py`
- Modify: `client/rl_client/i18n/keys.py`
- Modify: `client/rl_client/i18n/locales/en.py`
- Modify: `client/rl_client/i18n/locales/de.py`
- Modify: `client/rl_client/i18n/locales/fr.py`
- Modify: `client/rl_client/i18n/locales/es.py`
- Test: `client/tests/test_update_service.py`
- Test: existing UI smoke tests.

**Interfaces:**
- Produces: `UpdateService.check(channel) -> UpdateCandidate | None`
- Produces: `UpdateService.stage(candidate, progress=None) -> StagedUpdate`
- Produces: `UpdateService.launch_apply(staged) -> None`
- UI signals: `check_requested(str)` and `install_requested()`.

- [ ] Write service tests using fake GitHub client/download functions; verify same/older builds are not offered and newer ones stage only after checksum validation.
- [ ] Run tests and verify RED.
- [ ] Implement service and update screen states/buttons.
- [ ] Wire `MainWindow` so user clicks `Download & install`, then the app launches the helper and exits; auto-check runs once after window creation when enabled.
- [ ] Re-run service tests plus `--ui-smoke` and verify GREEN.

### Task 5: Stable bootstrap installer + real DeInstaller registration

**Files:**
- Create: `installer/bootstrap.py`
- Create: `installer/platform_integration.py`
- Create: `installer/README.md`
- Create: `.github/workflows/installer.yml`
- Test: `installer/tests/test_bootstrap.py`
- Test: `installer/tests/test_platform_integration.py`

**Interfaces:**
- Bootstrap CLI: `MinecraftRLLab-Setup[.exe] [--channel verified|nightly] [--install-root PATH]`
- Produces: install layout compatible with Task 3.
- Windows integration registers uninstall command under the per-user uninstall registry hive and creates Start Menu shortcut through a generated PowerShell command.
- Linux integration writes a user `.desktop` entry and uninstall launcher under the user data/application directories.

- [ ] Write tests for release choice, install-root construction, generated Windows uninstall metadata/commands, and Linux desktop-entry content without touching the real registry/home.
- [ ] Run tests and verify RED.
- [ ] Implement bootstrap using Task 1/2/3 primitives; default to verified channel and allow explicit Nightly selection.
- [ ] Add installer workflow triggered only by `installer/**`, `tools/maintenance_helper.py`, relevant update-core paths, or manual dispatch; compile Windows/Linux bootstrap and maintenance helper with Nuitka onefile and publish artifacts (not app Nightly releases).
- [ ] Re-run installer tests and validate YAML.

### Task 6: Faster repeat native builds and package contract

**Files:**
- Modify: `.github/workflows/build.yml`
- Modify: `tools/package_release.py`
- Modify: `tools/tests/test_build_modes.py`
- Test: package tests under `tools/tests/`.

**Interfaces:**
- Environment: `NUITKA_CACHE_DIR=${{ github.workspace }}/.nuitka-cache`
- Cache action: platform/Python/requirements/build-tool hash key plus broader restore key.
- Packages contain `PACKAGE_INFO.json`, app payload, plugin, and maintenance helper expected by installed mode.

- [ ] Add RED workflow assertions for `actions/cache@v4`, `NUITKA_CACHE_DIR`, no full-source dependency mode, and deterministic package names.
- [ ] Implement persistent Nuitka cache using the documented `NUITKA_CACHE_DIR`; retain existing pip cache and dense compiler output.
- [ ] Ensure helper binaries are packaged where available without breaking portable archives.
- [ ] Re-run tool tests and YAML parsing.

### Task 7: Full verification and main rollout

**Files:**
- Update docs only if verification exposes mismatches.

- [ ] Run `PYTHONPATH=client:. python -m pytest client/tests tools/tests installer/tests -q`.
- [ ] Run `PYTHONPATH=client:. python -m unittest discover -s client/tests -v`.
- [ ] Run `PYTHONPATH=client:. python -m compileall -q client tools installer`.
- [ ] Parse `.github/workflows/build.yml`, `.github/workflows/test-release.yml`, and `.github/workflows/installer.yml` with PyYAML.
- [ ] Run exact Java 25/Gradle 9.7 `:plugin:runTests :plugin:jar` if local prepared Paper libs are available.
- [ ] Verify `main` still points at the pre-feature commit while tests run.
- [ ] Move `main` once to the final verified feature commit so, with `cancel-in-progress: false`, the current run is not cancelled and the feature build queues next.
