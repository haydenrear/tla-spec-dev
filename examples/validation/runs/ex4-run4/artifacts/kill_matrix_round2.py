#!/usr/bin/env python3
"""EV-03 round-2 kill matrix: BOTH catalogs, BOTH arms, plus the pytest column.

Catalog 1  examples/validation/ex4_pipeline_coherent/seeded_faults.toml
           the EV-01 answer key (6 content faults, F1..F6) -- ARM A / ARM B.
Catalog 2  specs/.history/.../ticket-008-RP-02/ticket/results/harness/mutants.toml
           the reconstructed 12-mutant catalog (guard relaxation, wrong write,
           ordering, one equivalent) -- ARM A / ARM B / hand-written pytest.

Green control FIRST on every instrument (MF-016): a corpus that already fails
kills everything and reports 1.0.

Nothing is ever fixed. Every mutant is applied by verbatim find/replace with a
`finally` restore; `__pycache__` is purged around every execution and
PYTHONDONTWRITEBYTECODE is set, so no run can import a cached mutant.

usage: kill_matrix_round2.py FIXTURE REPO CORPUS OUT LABEL RP02_HARNESS
"""
from __future__ import annotations

import hashlib
import json
import os
import re
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
LABEL = sys.argv[5]
RP02 = Path(sys.argv[6]).resolve()

OUT.mkdir(parents=True, exist_ok=True)
LOGS = OUT / "logs"
LOGS.mkdir(exist_ok=True)

ARMS = {
    "A": "specs/program_model/case_adapters_corpus_only.toml",
    "B": "specs/program_model/case_adapters.toml",
}


def _env() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{REPO}:{FIXTURE / 'generated'}"
    env["PATH"] = f"{Path.home()}/.skill-manager/bin/cli:" + env.get("PATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def purge() -> None:
    for pyc in FIXTURE.rglob("__pycache__"):
        shutil.rmtree(pyc, ignore_errors=True)


def normalize(text: str) -> str:
    """Strip only the per-run varying parts: corpus path and temp directories."""
    text = text.replace(str(CORPUS), "<CORPUS>")
    text = text.replace(str(CORPUS.parent.parent), "<GEN>")
    text = re.sub(r"/(?:private/)?(?:var|tmp)/[^\s'\"]*", "<TMP>", text)
    text = re.sub(r"\b\d+\.\d+s\b", "<T>", text)
    return text


def run_arm(arm: str, tag: str) -> dict:
    purge()
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
        cmd, cwd=FIXTURE, env=_env(), capture_output=True, text=True, timeout=900
    )
    text = proc.stdout + ("\n--- STDERR ---\n" + proc.stderr if proc.stderr else "")
    (LOGS / f"{tag}-arm{arm}.log").write_text(
        f"$ {' '.join(cmd)}\n(cwd={FIXTURE})\nEXIT={proc.returncode}\n\n{text}",
        encoding="utf-8",
    )
    norm = normalize(text)
    m = re.search(r"ERROR: (\d+) batched case executions failed", text)
    return {
        "exit": proc.returncode,
        "killed": proc.returncode != 0,
        "points": int(m.group(1)) if m else 0,
        "detectors": detector_of(text),
        "stdout_sha256": hashlib.sha256(norm.encode()).hexdigest(),
        "failing_cases": sorted(set(re.findall(r"(case_\d+_[a-z]+)", text))),
    }


def run_pytest(tag: str) -> dict:
    purge()
    env = _env()
    env["PYTHONPATH"] = str(FIXTURE)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
        cwd=FIXTURE,
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
    )
    (LOGS / f"{tag}-pytest.log").write_text(
        f"EXIT={proc.returncode}\n\n{proc.stdout}{proc.stderr}", encoding="utf-8"
    )
    return {"exit": proc.returncode, "killed": proc.returncode != 0}


def detector_of(text: str) -> list[str]:
    dets = []
    if "DETECTOR[provider_content_assertion]" in text:
        dets.append("provider_content_assertion")
    if "after-state mismatch" in text or "projected state mismatch" in text:
        dets.append("tla_projected_state")
    if "adapter output mismatch" in text or "semantic output mismatch" in text:
        dets.append("tla_output")
    return dets


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
        purge()


def main() -> int:
    results: dict = {
        "label": LABEL,
        "interpreter": sys.version.split()[0],
        "corpus": str(CORPUS),
        "control": {},
        "seeded_faults": {},
        "catalog12": {},
    }

    print("=== CONTROL (unmutated) -- MF-016: without this every kill is void ===")
    for arm in ("A", "B"):
        r = run_arm(arm, "control")
        results["control"][f"arm{arm}"] = r
        print(f"  ARM {arm}: exit={r['exit']} {'GREEN' if r['exit'] == 0 else 'RED'}")
    p = run_pytest("control")
    results["control"]["pytest"] = p
    print(f"  pytest: exit={p['exit']} {'GREEN' if p['exit'] == 0 else 'RED'}")
    if any(v["exit"] != 0 for v in results["control"].values()):
        print("RED CONTROL -- every kill below is void")
        return 2

    print("\n=== CATALOG 1: seeded_faults.toml (the EV-01 answer key) ===")
    cat1 = tomllib.loads((FIXTURE / "seeded_faults.toml").read_text())["mutants"]
    for mutant in cat1:
        mid = mutant["id"]
        row = {
            "fault_class": mutant["fault_class"],
            "predicted_arm": mutant["predicted_arm"],
            "path": mutant["path"],
            "arms": {},
        }
        with seeded(mutant):
            for arm in ("A", "B"):
                row["arms"][arm] = run_arm(arm, mid)
        results["seeded_faults"][mid] = row
        a, b = row["arms"]["A"], row["arms"]["B"]
        print(
            f"  {mid:<26} ARM A {'KILLED ' if a['killed'] else 'SURVIVED'} "
            f"({a['points']:>3} pts, {','.join(a['detectors']) or '-'})   "
            f"ARM B {'KILLED ' if b['killed'] else 'SURVIVED'} "
            f"({b['points']:>3} pts, {','.join(b['detectors']) or '-'})"
        )

    print("\n=== CATALOG 2: the reconstructed 12-mutant catalog (RP-02 harness) ===")
    cat2 = tomllib.loads((RP02 / "mutants.toml").read_text())["mutants"]
    for mutant in cat2:
        mid = mutant["id"]
        row = {"fault_class": mutant["fault_class"], "path": mutant["path"], "arms": {}}
        with seeded(mutant):
            for arm in ("A", "B"):
                row["arms"][arm] = run_arm(arm, mid)
            row["pytest"] = run_pytest(mid)
        results["catalog12"][mid] = row
        print(
            f"  {mid:>4} {row['fault_class']:<26} "
            f"ARM A {'KILLED  ' if row['arms']['A']['killed'] else 'SURVIVED'} "
            f"ARM B {'KILLED  ' if row['arms']['B']['killed'] else 'SURVIVED'} "
            f"pytest {'KILLED' if row['pytest']['killed'] else 'SURVIVED'}"
        )

    (OUT / "kill_matrix.json").write_text(json.dumps(results, indent=2))

    status = subprocess.run(
        ["git", "status", "--porcelain", "examples/validation/"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    dirty = [
        ln
        for ln in status.stdout.splitlines()
        if "/runs/" not in ln  # this run's own records
    ]
    print("\nfixture restored -- git status on examples/validation/ (runs/ excluded):")
    print("  " + (repr(dirty) if dirty else "clean"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
