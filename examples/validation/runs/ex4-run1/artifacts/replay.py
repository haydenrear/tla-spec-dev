#!/usr/bin/env python3
"""EV-02 aim-3: replay a SEEDED failure from the runner's own replay command.

For each chosen mutant/arm: reseed the fault, take the first EFFECT_FUZZ_FAILURE
record from the batch log, run its `replay` command verbatim TWICE, and compare.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

FIXTURE = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
LOGDIR = Path(sys.argv[3]).resolve()
OUT = Path(sys.argv[4]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [("F1-wrong-value", "A"), ("F3-off-by-one-durable", "B"), ("F4-wrong-status", "A")]

catalog = {
    m["id"]: m
    for m in tomllib.loads((FIXTURE / "seeded_faults.toml").read_text())["mutants"]
}

results = []
for mid, arm in TARGETS:
    log = (LOGDIR / f"{mid}-arm{arm}.log").read_text()
    rec = json.loads(
        next(l for l in log.splitlines() if l.startswith("EFFECT_FUZZ_FAILURE")).split(
            " ", 1
        )[1]
    )
    cmd = shlex.split(rec["replay"])
    mutant = catalog[mid]
    target = FIXTURE / mutant["path"]
    original = target.read_text()
    target.write_text(original.replace(mutant["find"], mutant["replace"], 1))
    runs = []
    try:
        for i in (1, 2):
            for pyc in FIXTURE.rglob("__pycache__"):
                shutil.rmtree(pyc, ignore_errors=True)
            env = dict(os.environ)
            env["PYTHONPATH"] = f"{REPO}:{FIXTURE / 'generated'}"
            p = subprocess.run(
                cmd, cwd=FIXTURE, env=env, capture_output=True, text=True, timeout=600
            )
            text = p.stdout + p.stderr
            (OUT / f"{mid}-arm{arm}-replay{i}.log").write_text(
                f"$ {rec['replay']}\nEXIT={p.returncode}\n\n{text}"
            )
            runs.append((p.returncode, text))
    finally:
        target.write_text(original)
        for pyc in FIXTURE.rglob("__pycache__"):
            shutil.rmtree(pyc, ignore_errors=True)

    # the failure the batch saw, as reported by the single-case replay
    def err(t: str) -> str:
        for ln in t.splitlines():
            if ln.startswith("EFFECT_FUZZ_FAILURE"):
                return json.loads(ln.split(" ", 1)[1])["error"]
        return ""

    results.append(
        {
            "mutant": mid,
            "arm": arm,
            "case": rec["case"],
            "batch_error": rec["error"],
            "replay1_exit": runs[0][0],
            "replay2_exit": runs[1][0],
            "replay1_error": err(runs[0][1]),
            "replay2_error": err(runs[1][1]),
            "replay_reproduces_batch_failure": err(runs[0][1]) == rec["error"],
            "replay_identical_across_two_runs": runs[0] == runs[1],
        }
    )
    r = results[-1]
    print(
        f"{mid} arm {arm} case={rec['case']}: exits {r['replay1_exit']}/{r['replay2_exit']} "
        f"reproduces={r['replay_reproduces_batch_failure']} "
        f"identical={r['replay_identical_across_two_runs']}"
    )

(OUT / "replay.json").write_text(json.dumps(results, indent=2))
