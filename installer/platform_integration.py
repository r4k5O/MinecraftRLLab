from __future__ import annotations

import os
from pathlib import Path
import platform as platform_module
import subprocess
from typing import Mapping

from rl_client.update.install import InstallLayout, InstallMetadata


WINDOWS_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\MinecraftRLLab"


def default_install_root(platform_name: str, *, env: Mapping[str, str] | None = None, home: Path | None = None) -> Path:
    env_map = os.environ if env is None else env
    user_home = Path.home() if home is None else Path(home)
    if platform_name.lower() == "windows":
        local = env_map.get("LOCALAPPDATA")
        base = Path(local) if local else user_home / "AppData" / "Local"
        return base / "Programs" / "MinecraftRLLab"
    return user_home / ".local" / "share" / "MinecraftRLLab"


def _helper_path(layout: InstallLayout, platform_name: str) -> Path:
    return layout.updater / ("MinecraftRLLab-Maintenance.exe" if platform_name.lower() == "windows" else "MinecraftRLLab-Maintenance")


def windows_registry_values(layout: InstallLayout, metadata: InstallMetadata) -> dict[str, str | int]:
    helper = _helper_path(layout, "Windows")
    executable = layout.app / metadata.executable
    uninstall = f'"{helper}" --uninstall "{layout.metadata}"'
    return {
        "DisplayName": "MinecraftRLLab",
        "DisplayVersion": metadata.build,
        "Publisher": "r4k5O",
        "InstallLocation": str(layout.root),
        "DisplayIcon": str(executable),
        "UninstallString": uninstall,
        "NoModify": 1,
        "NoRepair": 0,
    }


def windows_shortcut_script(layout: InstallLayout, metadata: InstallMetadata, *, start_menu: Path | None = None) -> str:
    menu = start_menu or (Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming"))) / "Microsoft/Windows/Start Menu/Programs")
    shortcut = menu / "MinecraftRLLab.lnk"
    target = layout.app / metadata.executable
    working = layout.app
    return (
        "$ws=New-Object -ComObject WScript.Shell;"
        f"$s=$ws.CreateShortcut('{str(shortcut).replace(chr(39), chr(39)*2)}');"
        f"$s.TargetPath='{str(target).replace(chr(39), chr(39)*2)}';"
        f"$s.WorkingDirectory='{str(working).replace(chr(39), chr(39)*2)}';"
        "$s.Description='MinecraftRLLab';$s.Save()"
    )


def linux_desktop_entries(layout: InstallLayout, metadata: InstallMetadata, *, home: Path | None = None) -> dict[Path, str]:
    user_home = Path.home() if home is None else Path(home)
    apps = user_home / ".local/share/applications"
    executable = layout.app / metadata.executable
    helper = _helper_path(layout, "Linux")
    app_entry = f"""[Desktop Entry]\nType=Application\nName=MinecraftRLLab\nComment=Reinforcement learning for Minecraft\nExec=\"{executable}\"\nTerminal=false\nCategories=Education;Development;\n"""
    uninstall_entry = f"""[Desktop Entry]\nType=Application\nName=Uninstall MinecraftRLLab\nExec=\"{helper}\" --uninstall \"{layout.metadata}\"\nTerminal=true\nCategories=Settings;\n"""
    return {
        apps / "minecraftrllab.desktop": app_entry,
        apps / "minecraftrllab-uninstall.desktop": uninstall_entry,
    }


def install_platform_integration(layout: InstallLayout, metadata: InstallMetadata, *, platform_name: str | None = None) -> None:
    platform_name = platform_name or platform_module.system()
    if platform_name.lower() == "windows":
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, WINDOWS_UNINSTALL_KEY) as key:
                for name, value in windows_registry_values(layout, metadata).items():
                    kind = winreg.REG_DWORD if isinstance(value, int) else winreg.REG_SZ
                    winreg.SetValueEx(key, name, 0, kind, value)
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", windows_shortcut_script(layout, metadata)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (ImportError, OSError):
            pass
        return

    entries = linux_desktop_entries(layout, metadata)
    for path, content in entries.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        try:
            path.chmod(0o755)
        except OSError:
            pass


def remove_platform_integration(metadata: InstallMetadata, *, platform_name: str | None = None, home: Path | None = None) -> None:
    platform_name = platform_name or metadata.platform or platform_module.system()
    layout = InstallLayout.from_root(Path(metadata.root), data_root=Path(metadata.data_root))
    if platform_name.lower() == "windows":
        try:
            import winreg
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, WINDOWS_UNINSTALL_KEY)
            except FileNotFoundError:
                pass
            menu = Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming"))) / "Microsoft/Windows/Start Menu/Programs"
            try:
                (menu / "MinecraftRLLab.lnk").unlink()
            except FileNotFoundError:
                pass
        except (ImportError, OSError):
            pass
        return

    user_home = Path.home() if home is None else Path(home)
    for path in linux_desktop_entries(layout, metadata, home=user_home):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
