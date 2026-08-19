#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import zipfile


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--platform",choices=("Windows","Linux"),required=True); p.add_argument("--client-dist",required=True); p.add_argument("--plugin",required=True); p.add_argument("--output",default="packages"); p.add_argument("--build",required=True)
    a=p.parse_args(); root=Path(a.output); root.mkdir(parents=True,exist_ok=True); stage=root/f"MinecraftRLLab-{a.build}-{a.platform}-x64"
    if stage.exists():shutil.rmtree(stage)
    shutil.copytree(a.client_dist,stage); sp=stage/"server-plugin"; sp.mkdir(exist_ok=True); shutil.copy2(a.plugin,sp/"MinecraftRLLab-Plugin.jar")
    info={"build":a.build,"platform":a.platform,"contains_plugin":True,"package_format":2,"self_update_payload":True}; (stage/"PACKAGE_INFO.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
    if a.platform=="Windows":
        archive=root/f"MinecraftRLLab-{a.build}-Windows-x64.zip"
        with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
            for path in stage.rglob("*"):
                if path.is_file():z.write(path,path.relative_to(stage.parent))
    else:
        archive=root/f"MinecraftRLLab-{a.build}-Linux-x64.tar.gz"
        with tarfile.open(archive,"w:gz") as tar:tar.add(stage,arcname=stage.name)
    (root/(archive.name+".sha256")).write_text(f"{sha256(archive)}  {archive.name}\n",encoding="utf-8")
    print(archive)
    return 0


if __name__=="__main__":raise SystemExit(main())
