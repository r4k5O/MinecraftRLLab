#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys


@dataclass(frozen=True)
class BuildStage:
    name: str
    description: str


def source_build_plan() -> tuple[BuildStage, ...]:
    return (
        BuildStage("qtbase", "Build Qt Base (Core/Gui/Widgets runtime) from source with CMake + Ninja"),
        BuildStage("pyside6-shiboken6", "Generate and compile Shiboken6 + PySide6 bindings from source"),
        BuildStage("numpy", "Build NumPy from its source distribution"),
        BuildStage("torch", "Build CPU PyTorch from the upstream source tree"),
        BuildStage("pyqtgraph", "Build pyqtgraph wheel from source"),
        BuildStage("zstandard", "Build python-zstandard native extension from source"),
        BuildStage("ordered-set", "Build ordered-set wheel from source"),
        BuildStage("nuitka", "Build/install Nuitka from source before compiling MinecraftRLLab"),
    )


def banner(index: int, total: int, title: str) -> None:
    line = "═" * 96
    print(f"\n{line}\n🔥 FORGE [{index}/{total}] {title}\n{line}\n", flush=True)


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def clone(url: str, dest: Path, ref: str, recursive: bool = False) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    cmd = ["git", "clone", "--depth", "1", "--branch", ref]
    if recursive:
        cmd += ["--recurse-submodules", "--shallow-submodules"]
    cmd += [url, str(dest)]
    run(cmd)


def pip(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    run([sys.executable, "-m", "pip", *args], cwd=cwd, env=env)


def build_qt(work: Path, jobs: int) -> Path:
    qt_src = work / "qtbase-src"
    qt_build = work / "qtbase-build"
    qt_install = work / "qt"
    clone("https://github.com/qt/qtbase.git", qt_src, os.getenv("MCRL_QT_REF", "6.11"))
    if qt_build.exists():
        shutil.rmtree(qt_build)
    if qt_install.exists():
        shutil.rmtree(qt_install)
    run([
        "cmake", "-S", str(qt_src), "-B", str(qt_build), "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={qt_install}",
        "-DQT_BUILD_TESTS=OFF", "-DQT_BUILD_EXAMPLES=OFF",
    ])
    run(["cmake", "--build", str(qt_build), "--parallel", str(jobs)])
    run(["cmake", "--install", str(qt_build)])
    shutil.rmtree(qt_src, ignore_errors=True)
    shutil.rmtree(qt_build, ignore_errors=True)
    return qt_install


def qtpaths(qt_install: Path) -> Path:
    exe = "qtpaths.exe" if os.name == "nt" else "qtpaths"
    candidate = qt_install / "bin" / exe
    if not candidate.exists():
        raise SystemExit(f"qtpaths not found at {candidate}")
    return candidate


def build_pyside(work: Path, qt_install: Path, jobs: int, env: dict[str, str]) -> None:
    src = work / "pyside-setup"
    clone("https://github.com/pyside/pyside-setup.git", src, os.getenv("MCRL_PYSIDE_REF", "6.11"))
    command = [
        sys.executable, "setup.py", "install",
        f"--qtpaths={qtpaths(qt_install)}", "--ignore-git", f"--parallel={jobs}",
        "--verbose-build", "--module-subset=Core,Gui,Widgets", "--standalone",
    ]
    run(command, cwd=src, env=env)
    shutil.rmtree(src, ignore_errors=True)


def build_source_wheel(requirement: str, wheelhouse: Path, env: dict[str, str]) -> None:
    pip("wheel", "--no-binary=:all:", "--no-cache-dir", "-v", "--wheel-dir", str(wheelhouse), requirement, env=env)


def install_latest_wheel(wheelhouse: Path, prefix: str) -> None:
    wanted = prefix.lower().replace("-", "_") + "-"
    matches = [p for p in wheelhouse.glob("*.whl") if p.name.lower().replace("-", "_").startswith(wanted)]
    matches.sort(key=lambda p: p.stat().st_mtime)
    if not matches:
        raise SystemExit(f"No wheel starting with {prefix}- was produced")
    pip("install", "--force-reinstall", "--no-deps", str(matches[-1]))


def build_torch(work: Path, wheelhouse: Path, jobs: int, env: dict[str, str]) -> None:
    src = work / "pytorch"
    ref = os.getenv("MCRL_TORCH_REF", "main")
    clone("https://github.com/pytorch/pytorch.git", src, ref, recursive=True)
    torch_env = dict(env)
    torch_env.update({
        "USE_CUDA": "0",
        "USE_ROCM": "0",
        "BUILD_TEST": "0",
        "MAX_JOBS": str(jobs),
        "CMAKE_BUILD_PARALLEL_LEVEL": str(jobs),
    })
    req = src / "requirements.txt"
    if req.exists():
        pip("install", "--no-binary=:all:", "--no-cache-dir", "-v", "-r", str(req), env=torch_env)
    pip("wheel", "--no-build-isolation", "--no-deps", "-v", "--wheel-dir", str(wheelhouse), ".", cwd=src, env=torch_env)
    install_latest_wheel(wheelhouse, "torch")
    shutil.rmtree(src, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="MinecraftRLLab hidden full-source dependency forge")
    parser.add_argument("--work", default=".forge-source")
    parser.add_argument("--wheelhouse", default=".forge-wheelhouse")
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()

    plan = source_build_plan()
    if args.plan:
        for i, stage in enumerate(plan, 1):
            print(f"[{i}/{len(plan)}] {stage.name}: {stage.description}")
        return 0

    root = Path.cwd()
    work = (root / args.work).resolve()
    wheelhouse = (root / args.wheelhouse).resolve()
    work.mkdir(parents=True, exist_ok=True)
    wheelhouse.mkdir(parents=True, exist_ok=True)
    jobs = max(2, min(os.cpu_count() or 2, int(os.getenv("MCRL_FORGE_JOBS", "8"))))

    source_env = dict(os.environ)
    source_env.update({
        "PIP_NO_BINARY": ":all:",
        "CMAKE_BUILD_PARALLEL_LEVEL": str(jobs),
        "NINJA_STATUS": "[%f/%t] ",
    })
    if not source_env.get("CLANG_INSTALL_DIR"):
        if os.name == "nt":
            llvm = Path(r"C:\Program Files\LLVM")
            if llvm.exists():
                source_env["CLANG_INSTALL_DIR"] = str(llvm)
        else:
            llvm_config = shutil.which("llvm-config")
            if llvm_config:
                prefix = subprocess.check_output([llvm_config, "--prefix"], text=True).strip()
                if prefix:
                    source_env["CLANG_INSTALL_DIR"] = prefix

    pip("install", "--upgrade", "pip", "setuptools", "wheel", "build", "packaging", "cmake", "ninja")

    stage = 0
    stage += 1; banner(stage, len(plan), plan[0].description)
    qt_install = build_qt(work, jobs)
    source_env["PATH"] = str(qt_install / "bin") + os.pathsep + source_env.get("PATH", "")
    if os.name != "nt":
        source_env["LD_LIBRARY_PATH"] = str(qt_install / "lib") + os.pathsep + source_env.get("LD_LIBRARY_PATH", "")

    stage += 1; banner(stage, len(plan), plan[1].description)
    build_pyside(work, qt_install, jobs, source_env)

    stage += 1; banner(stage, len(plan), plan[2].description)
    build_source_wheel("numpy>=2.0", wheelhouse, source_env)
    install_latest_wheel(wheelhouse, "numpy")

    stage += 1; banner(stage, len(plan), plan[3].description)
    build_torch(work, wheelhouse, jobs, source_env)

    direct = [
        ("pyqtgraph>=0.13.7", "pyqtgraph", plan[4]),
        ("zstandard>=0.23", "zstandard", plan[5]),
        ("ordered-set>=4.1", "ordered_set", plan[6]),
        ("Nuitka>=2.6", "nuitka", plan[7]),
    ]
    for requirement, wheel_prefix, info in direct:
        stage += 1; banner(stage, len(plan), info.description)
        build_source_wheel(requirement, wheelhouse, source_env)
        install_latest_wheel(wheelhouse, wheel_prefix)

    run([sys.executable, "-c", "import numpy, torch, PySide6, pyqtgraph, zstandard, nuitka; print('FORGE_IMPORT_CHECK=OK')"], env=source_env)
    print("\n🔥 FORGE DEPENDENCY BUILD COMPLETE\n", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
