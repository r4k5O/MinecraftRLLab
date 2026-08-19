# Build Pipeline

## 1. Build workflow

`build.yml` is the high-priority production path. It never waits for the release test workflow.

1. Generate build metadata.
2. Build the Java 25 / Paper 26.2 plugin.
3. Build the PySide6 client natively on Windows and Linux with Nuitka.
4. Keep Nuitka/SCons compiler output visible.
5. Package the compiled client together with the plugin JAR.
6. Generate checksums.
7. Publish a prerelease immediately with `verification:pending`.

## 2. Test workflow

`test-release.yml` is triggered by `release.published`.

Before it starts real tests, `build-priority-gate` polls the Actions API. If a `build.yml` run is queued or in progress, it waits. This gate is intentionally separate from tests so a release can already be downloaded as a Nightly.

When the queue becomes empty, verification runs:

- Python RL/source tests
- build-priority scheduler tests
- Java plugin test suite
- exact Windows release archive smoke check
- exact Linux release archive smoke check
- plugin JAR content check
- native executable `--health-check`

If all verification passes, the release is changed from prerelease to normal release and its marker becomes `verification:passed`. If verification fails, the release remains a prerelease and becomes `verification:failed`.

## 3. Why this produces large real logs

The native build is intentionally a source compilation, not a freezer-only copy operation. Nuitka translates followed Python modules into C/C++ source and invokes SCons with the platform compiler. `--show-scons` exposes compiler operation in the GitHub log.

The desktop app is split into focused modules (UI screens, widgets, update client, server installer, metrics, state, RL core) so the compiler has real modules to process. More application functionality can be added as separate modules without fake no-op code.
