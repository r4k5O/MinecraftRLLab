# MinecraftRLLab Setup

`bootstrap.py` is the stable first-install bootstrap. The compiled Setup binary queries the public GitHub releases API, downloads the newest package for the selected channel, verifies `SHA256SUMS.txt`, installs the managed `app/` payload, and copies itself to `updater/MinecraftRLLab-Maintenance[.exe]`.

After installation, MinecraftRLLab performs normal update checks and downloads itself. The copied maintenance binary is used only after the running app exits to swap payloads, roll back failed health checks, and perform uninstall/deinstall operations.

The default channel is `verified`. Use `--channel nightly` only when intentionally opting into unverified Nightly builds.
