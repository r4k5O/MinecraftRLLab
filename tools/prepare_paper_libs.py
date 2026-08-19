#!/usr/bin/env python3
"""Extract Paperclip's embedded Paper API/runtime libraries for an offline Gradle compile."""
from pathlib import Path
import shutil
import sys
import zipfile


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/prepare_paper_libs.py /path/to/paper-26.2-111.jar")
        return 2
    source = Path(sys.argv[1]).expanduser().resolve()
    if not source.is_file():
        print(f"Paper JAR not found: {source}")
        return 2
    root = Path(__file__).resolve().parents[1]
    target = root / "toolchain" / "paper-libs"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    count = 0
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            if info.filename.startswith("META-INF/libraries/") and info.filename.endswith(".jar"):
                relative = Path(info.filename).relative_to("META-INF/libraries")
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as src, destination.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                count += 1
    if not count:
        print("No embedded Paper libraries found. Is this a Paperclip server JAR?")
        return 1
    print(f"Extracted {count} libraries to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
