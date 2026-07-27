#!/usr/bin/env python3
"""EV-02 aim-1 harness: seed each fault one at a time, run BOTH arms, restore.

Never fixes anything. Writes one log per (mutant, arm) plus a JSON matrix.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from contextlib import contextmanager
from pathlib import Path

FIXTURE = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
CORPUS = Path(sys.argv[3]).resolve()
OUT = Path(sys.argv[4]).resolve()
LABEL = sys.argv[5] if len(sys.argv) > 5 else "run1"

OUT.mkdir(parents=True, exist_ok=True)

ARMS = {
    "A": "specs/program_model/case_adapters_corpus_only.toml",
    "B": "specs/program_model/case_adapters.toml",
}


def run_arm(arm: str, tag: str) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{REPO}:{FIXTURE / 'generated'}"
    env["PATH"] = f"{Path.home()}/.skill-manager/bin/cli:" + env.get("PATH", "")
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "run_generated_case_adapters.py"),
        str(CORPUS),
        "--mapping",
        ARMS[arm],
        "--spec-dir",
        "specs/program_model",
        "--view",
        "internal",
        "--batch",
        "--import-root",
        ".",
    ]
    proc = subprocess.run(
        cmd, cwd=FIXTURE, env=env, capture_output=True, text=True, timeout=900
    )
    text = proc.stdout + ("\n--- STDERR ---\n" + proc.stderr if proc.stderr else "")
    (OUT / f"{tag}-arm{arm}.log").write_text(
        f"$ {' '.join(cmd)}\n(cwd={FIXTURE})\nEXIT={proc.returncode}\n\n{text}",
        encoding="utf-8",
    )
    return proc.returncode, text


@contextmanager
def seeded(mutant: dict):
    target = FIXTURE / mutant["path"]
    original = target.read_text(encoding="utf-8")
    find = mutant["find"]
    if find not in original:
        raise SystemExit(f"{mutant['id']}: find-text not present in {target}")
    if original.count(find) != 1:
        raise SystemExit(f"{mutant['id']}: find-text is not unique in {target}")
    target.write_text(original.replace(find, mutant["replace"], 1), encoding="utf-8")
    try:
        yield
    finally:
        target.write_text(original, encoding="utf-8")
        # kill stale bytecode so the next run cannot import a cached mutant
        for pyc in FIXTURE.rglob("__pycache__"):
            shutil.rmtree(pyc, ignore_errors=True)


def detector_of(text: str) -> list[str]:
    dets = []
    if "DETECTOR[provider_content_assertion]" in text:
        dets.append("provider_content_assertion")
    if "after-state mismatch" in text or "projected state mismatch" in text:
        dets.append("tla_projected_state")
    if "adapter output mismatch" in text or "semantic output mismatch" in text:
        dets.append("tla_output")
    return dets


def main() -> int:
    catalog = tomllib.loads(
        (FIXTURE / "seeded_faults.toml").read_text(encoding="utf-8")
    )
    results: dict = {"label": LABEL, "control": {}, "mutants": {}}

    # control first -- a red control voids every kill (MF-016)
    for arm in ("A", "B"):
        for pyc in FIXTURE.rglob("__pycache__"):
            shutil.rmtree(pyc, ignore_errors=True)
        code, text = run_arm(arm, "control")
        results["control"][arm] = {"exit": code, "green": code == 0}
        print(f"CONTROL arm {arm}: exit={code}")
    if not all(v["green"] for v in results["control"].values()):
        print("RED CONTROL -- every kill below is void")

    for mutant in catalog["mutants"]:
        mid = mutant["id"]
        results["mutants"][mid] = {
            "fault_class": mutant["fault_class"],
            "predicted_arm": mutant["predicted_arm"],
            "path": mutant["path"],
            "arms": {},
        }
        with seeded(mutant):
            for arm in ("A", "B"):
                for pyc in FIXTURE.rglob("__pycache__"):
                    shutil.rmtree(pyc, ignore_errors=True)
                code, text = run_arm(arm, mid)
                results["mutants"][mid]["arms"][arm] = {
                    "exit": code,
                    "killed": code != 0,
                    "detectors": detector_of(text),
                    "first_failure": next(
                        (
                            ln
                            for ln in text.splitlines()
                            if "FAIL" in ln or "AssertionError" in ln or "mismatch" in ln
                        ),
                        "",
                    )[:400],
                }
                print(
                    f"{mid} arm {arm}: exit={code} killed={code != 0} "
                    f"detectors={results['mutants'][mid]['arms'][arm]['detectors']}"
                )
    (OUT / "kill_matrix.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    # assert the fixture is restored
    subprocess.run(["git", "status", "--porcelain", str(FIXTURE)], cwd=REPO)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
