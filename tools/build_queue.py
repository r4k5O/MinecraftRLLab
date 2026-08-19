#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any
from urllib.request import Request, urlopen

ACTIVE={"queued","in_progress","pending","waiting","requested"}


def active_builds(runs:list[dict[str,Any]])->list[dict[str,Any]]:
    return [run for run in runs if str(run.get("status","")) in ACTIVE]


def fetch(repo:str,workflow:str,token:str)->list[dict[str,Any]]:
    url=f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?per_page=100"
    req=Request(url,headers={"Accept":"application/vnd.github+json","Authorization":f"Bearer {token}","User-Agent":"MinecraftRLLab-Build-Priority"})
    with urlopen(req,timeout=20) as response:
        payload=json.loads(response.read().decode("utf-8"))
    return list(payload.get("workflow_runs",[]))


def main()->int:
    parser=argparse.ArgumentParser(description="Wait until the MinecraftRLLab build queue is empty before tests start.")
    parser.add_argument("--repo",default=os.getenv("GITHUB_REPOSITORY","")); parser.add_argument("--workflow",default="build.yml")
    parser.add_argument("--interval",type=int,default=20); parser.add_argument("--timeout",type=int,default=7200)
    parser.add_argument("--once-json",help="Offline test: JSON file containing workflow_runs")
    args=parser.parse_args()
    if args.once_json:
        payload=json.load(open(args.once_json,encoding="utf-8")); pending=active_builds(payload.get("workflow_runs",[])); print(len(pending)); return 0
    token=os.getenv("GITHUB_TOKEN","")
    if not args.repo or not token: raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN are required")
    started=time.monotonic()
    while True:
        pending=active_builds(fetch(args.repo,args.workflow,token))
        if not pending:
            print("BUILD QUEUE EMPTY — verification may start")
            return 0
        print(f"BUILD PRIORITY — {len(pending)} build(s) still queued/running; tests remain parked")
        for run in pending[:10]:print(f"  #{run.get('run_number')} {run.get('status')} {str(run.get('head_sha',''))[:10]}")
        if time.monotonic()-started>args.timeout:raise SystemExit("Timed out waiting for build queue")
        time.sleep(max(5,args.interval))


if __name__=="__main__":raise SystemExit(main())
