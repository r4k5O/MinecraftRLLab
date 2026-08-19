# MinecraftRLLab Self-Update + Bootstrap Installer Design

Date: 2026-08-19
Status: proposed
Branch: `self-update-installer`

## Goals

1. Keep the current GitHub Nightly -> release -> verification workflow semantics.
2. Make repeat native builds faster without bringing back source builds of third-party dependencies.
3. Add a small, stable installer that is not rebuilt for every MinecraftRLLab Nightly.
4. Make MinecraftRLLab itself responsible for checking, downloading, validating, and initiating updates.
5. Provide a real uninstaller/deinstaller.
6. Preserve user models, training data, and settings by default during update and uninstall.
7. Push only the final verified implementation to `main`, so the currently running build can finish first and the new implementation becomes the next queued main build.

## Existing foundations

The client already contains a GitHub release updater model (`client/rl_client/update/github.py`, `models.py`) and an Updates screen wired from `MainWindow`. This design extends that existing update flow rather than replacing it.

The build already installs prebuilt Python wheels and compiles only MinecraftRLLab with Nuitka. Third-party dependency source builds remain removed.

## Distribution architecture

### Stable bootstrap installer

The repository will produce a small platform bootstrap installer independently from Nightly application releases.

Windows artifact:

- `MinecraftRLLab-Setup.exe`

Linux artifact:

- `MinecraftRLLab-Setup`

The installer itself is versioned rarely and does not need to be regenerated for every app release. It performs only first installation and repair of the installation shell:

1. Detect platform and architecture.
2. Query the public GitHub releases API for `r4k5O/MinecraftRLLab`.
3. Select the newest suitable release for the configured channel.
4. Select the platform archive asset.
5. Download the release archive plus checksum information.
6. Verify SHA-256 before extraction.
7. Install application files under the platform installation directory.
8. Install/register an uninstaller/deinstaller.
9. Create normal launch integration (Windows Start Menu / Installed Apps entry; Linux desktop entry when appropriate).
10. Launch MinecraftRLLab.

The bootstrap installer does not remain responsible for normal updates.

## Self-update architecture

MinecraftRLLab owns normal updates after installation.

### Update check

The existing update screen and GitHub release client are extended so the app can:

- determine the installed build from `BUILD_INFO.json`;
- determine the newest matching release;
- distinguish Verified and Nightly channels using the existing model;
- identify the correct Windows/Linux x64 asset;
- compare installed and available builds;
- show release name, verification state, build/tag, and download size.

Automatic update checks respect the existing `auto_check_updates` setting.

### Update download

When the user accepts an update, the app downloads into a staging directory outside the live application directory.

Proposed layout:

```text
MinecraftRLLab/
  app/                 # current immutable application payload
  updater/             # small update helper
  uninstall/           # uninstall helper/metadata
  user-data/           # settings and app-owned user data
  models/              # trained models
  update-staging/      # temporary downloaded update
```

Portable builds may retain their current flat layout; installed builds use the managed layout above.

The updater validates:

- expected asset filename/platform;
- archive integrity;
- SHA-256 from release checksum data;
- expected package metadata (`PACKAGE_INFO.json`);
- presence of the main executable before activation.

### Apply update

A running process cannot safely replace all of its own files, so MinecraftRLLab launches a minimal helper only for the final file swap.

Sequence:

1. App checks and downloads the update.
2. App validates everything while still running.
3. App launches the helper with paths and current PID.
4. App exits.
5. Helper waits for the old process to exit.
6. Helper moves current `app/` to a rollback directory.
7. Helper activates the staged `app/` atomically where possible.
8. Helper launches the new MinecraftRLLab with a post-update health marker.
9. If launch/health confirmation fails, helper restores the previous app payload.
10. Successful update deletes old rollback/staging data after confirmation.

No models, training data, settings, server data, or user files are overwritten by the application payload swap.

## Uninstaller / DeInstaller

A real uninstaller is registered at first install.

### Default uninstall

Remove:

- installed application payload;
- updater/helper binaries;
- shortcuts/desktop entries;
- install metadata;
- application caches;
- Windows Installed Apps registration where applicable.

Keep by default:

- trained models;
- training data;
- user settings.

The uninstaller offers an explicit option to remove all MinecraftRLLab user data as well.

The helper/uninstaller must not silently delete arbitrary directories. It may only delete paths recorded in validated installation metadata below the managed install/data roots.

## Build speed improvements

The application still uses prebuilt wheels. Faster repeat builds come from reusable compiler/build caches rather than dependency source compilation.

### GitHub Actions cache

Add platform-specific persistent caching for:

- Nuitka download/dependency cache;
- Nuitka bytecode/cache directories where supported;
- C compiler object cache (`ccache` on Linux; supported Nuitka/MSVC cache mechanism on Windows);
- existing pip cache remains enabled.

Cache keys include:

- platform;
- Python major/minor;
- dependency requirements hash;
- relevant build-tool configuration hash.

Restore keys are intentionally broader so small source changes can reuse unchanged compiler objects.

A cache miss must still produce a correct clean build.

## Build and release pipeline

The main application build remains:

```text
prebuilt Python wheels
  -> Paper plugin build
  -> native Nuitka Windows/Linux builds
  -> package archives
  -> publish Nightly immediately
  -> release-triggered verification
```

Portable archives remain release assets because they are also the payload downloaded by the installer/self-updater.

The installer itself is not rebuilt on every Nightly. It is built only when installer/bootstrap source changes or when explicitly dispatched.

## Release asset contract

Application releases continue to expose deterministic platform archive names so updater selection does not depend on fuzzy matching.

Required assets per application release:

- `MinecraftRLLab-<build>-Windows-x64.zip`
- `MinecraftRLLab-<build>-Linux-x64.tar.gz`
- `SHA256SUMS.txt`

The Paper plugin remains embedded in each application package and may also remain separately available if desired.

Installer release/assets are separate from ordinary Nightly application releases to keep the bootstrap stable.

## UI behavior

The existing Updates screen becomes functional rather than informational only.

States:

- checking;
- up to date;
- update available;
- downloading with bytes/progress;
- validating;
- ready to restart/apply;
- update failed with recoverable error;
- rollback performed.

Buttons:

- `Check for updates`
- `Download & install` when an update is available
- channel selector remains Verified/Nightly

Normal updates are initiated from inside MinecraftRLLab. The external installer is not opened for updates.

## Security and failure handling

- Only HTTPS GitHub API/release asset URLs from the configured repository are accepted.
- Checksums are mandatory before activation.
- Archive extraction rejects absolute paths and path traversal (`..`).
- Update activation happens only after complete validation.
- Current version remains recoverable until the new version has started successfully.
- Interrupted downloads/staging directories are safe to delete/retry.
- Failed Nightly verification does not silently replace a Verified installation unless the user intentionally uses the Nightly channel.

## Testing

Unit tests cover:

- release/asset selection for Windows/Linux and Verified/Nightly;
- build comparison;
- checksum parsing and verification;
- safe archive extraction/path traversal rejection;
- staging and installation metadata;
- updater command construction;
- rollback state machine;
- uninstall path allow-listing;
- preservation of user data by default;
- cache/workflow configuration invariants.

Integration-style tests use temporary directories and fake release payloads rather than overwriting the real running application.

Existing client/tool tests remain required.

## Main-branch rollout

Development stays on `self-update-installer`, which does not trigger the `main` build workflow. After implementation and verification, the finished tree is moved to `main` once. With `cancel-in-progress: false`, the currently running main build is not cancelled; the new main build queues behind it and represents the newest implementation.