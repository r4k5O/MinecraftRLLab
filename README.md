# MinecraftRLLab

MinecraftRLLab is a reinforcement-learning environment for **Paper 26.2** plus a modern **PySide6 desktop client**. The repository builds the Paper plugin and native Windows/Linux client together, then publishes a Nightly immediately. Release verification runs afterwards and is **build-priority aware**: if any new build is queued or running, tests wait.

## Goals

The environment supports at least:

- 💎 find/obtain a diamond
- 🟪 construct and activate a Nether portal
- 🗡️ craft a wooden sword
- 🧟 kill a zombie

The client contains DQN training, replay memory, live observations, reward charts, episode history, GitHub build/update checking, and a Paper-plugin installer.

## Repository layout

```text
MinecraftRLLab/
├── client/                 # RL core + PySide6 desktop UI
│   ├── rl_client/
│   │   ├── core/
│   │   ├── server/
│   │   ├── update/
│   │   └── ui/
│   └── tests/
├── plugin/                 # Paper 26.2 / Java 25 plugin
├── tools/                  # Native build, packaging, build-priority gate
├── .github/workflows/
│   ├── build.yml           # build → package → publish Nightly
│   └── test-release.yml    # release → wait for builds → verify
└── docs/
```

## The build model

The project intentionally prioritizes **real builds** over tests:

```text
commit
  ↓
BUILD QUEUE
  ├─ Paper plugin (Gradle / Java 25)
  ├─ Windows native client (Nuitka → C/C++ → MSVC/SCons)
  └─ Linux native client   (Nuitka → C/C++ → GCC/SCons)
  ↓
package plugin + client
  ↓
publish Nightly immediately
  ↓
release verification workflow starts
  ↓
wait while build.yml has queued/in_progress runs
  ↓
only when build queue == 0: tests start
```

The client build uses Nuitka `--show-scons`, `--verbose`, and `--show-progress`, so the Actions log shows the actual native compilation instead of fake progress lines.

## Nightly vs Verified

- **Nightly**: compiled and packaged successfully, release is already downloadable, verification is pending or failed.
- **Verified**: the post-release workflow passed source tests, Paper tests, Windows artifact smoke test, and Linux artifact smoke test.

The app can check both channels from the GitHub Releases API.

## GitHub setup

1. Create a repository, for example `r4k5O/MinecraftRLLab`.
2. Upload this repository and push to `main`.
3. GitHub Actions builds automatically.
4. Change `github_owner` / `github_repo` in the app settings if you use a different repository name.

No custom GitHub secret is required for public releases; the workflows use the built-in `GITHUB_TOKEN` with explicit repository permissions.

## Local Python development

```bash
cd client
python -m venv .venv
# activate the environment
python -m pip install -r requirements.txt
python run_client.py
```

Health-check without opening the UI:

```bash
python client/run_client.py --health-check
```

## Local plugin build

The GitHub build resolves the Paper 26.2 API from Paper's Maven repository. For an offline local build with a Paperclip JAR:

```bash
python tools/prepare_paper_libs.py /path/to/paper-26.2.jar
gradle :plugin:jar
```

Java 25 is required.

## Native client build

```bash
cd client
python -m pip install -r requirements-build.txt
cd ..
python tools/build_client.py --output dist
```

Nuitka creates a standalone distribution. GitHub then inserts `MinecraftRLLab-Plugin.jar` into `server-plugin/` inside the downloadable package.

## Server plugin installation from the app

Open **Minecraft Server**, select the Paper server folder, then use **Install / Update Plugin**. The app copies the bundled plugin into the server's `plugins/` directory and removes older MinecraftRLLab JAR names when needed.

## Build-priority rule

`tools/build_queue.py` queries the GitHub Actions workflow runs for `build.yml`. The release verification workflow remains parked while any build has an active state such as `queued` or `in_progress`.

That means:

> If there is still something to build, build first. Test only when the build queue is empty.

## Learning Hub, Kids UI, and translations

MinecraftRLLab 0.3 includes four experience modes:

- 🧒 **Kids / First Steps** — a separate playful UI with missions, stars, guided tutorials and simplified server setup.
- 🌱 **Beginner** — research shell with learning guidance and fewer low-level pages.
- 🧠 **Research** — the complete RL dashboard and diagnostics.
- 🛠️ **Advanced** — research tooling plus guided learning.

First-party UI/tutorial translations are included for **English, German, French, and Spanish**. Every shipped locale is checked for required-key completeness by the unit tests.

Interactive tutorials mix explanatory **Next** steps with real event gates. For example, the first-training tutorial only advances when the matching goal is selected, the server is connected, training starts, a reward arrives, and an episode completes.

Kids mode also contains a clearly marked deterministic demo so someone can learn the UI before a Paper server is running. Demo success never counts as a real Minecraft achievement.

See [`docs/LEARNING_KIDS_AND_LANGUAGES.md`](docs/LEARNING_KIDS_AND_LANGUAGES.md) for the full learning and localization architecture.
