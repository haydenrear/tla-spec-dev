#!/usr/bin/env python3
"""RD-03 probe. Per (tree, mutant, instrument). No aggregate kill rate.

Never mutates a tree in place: every mutant is applied to a fresh copy under
the scratch root. Nothing in the six artifact trees, the shared suite, the
catalogue or the model is written by this script.

Instruments, named so a zero can be attributed:

  own-tests            the tree's own hand-written tests, as shipped
  shared-suite         examples/validation/ab/tests/test_behavior.py, unchanged
  shared-suite-fake    the SAME file through a second composition point that
                       wires the in-memory adapter. Only meaningful on a tree
                       that HAS a second adapter; the four-line composition
                       point is written by this probe, outside the tree, and is
                       reported as an instrument I built rather than as
                       something the tree shipped.

Verdicts:

  KILLED / SURVIVED    the instrument ran and decided
  INEXPRESSIBLE        the tree has no surface the semantic applies to
  HOLE:<why>           the re-anchoring did not reproduce the declared
                       semantic on this tree; NOT a survivor
  N/A                  the instrument does not exist for this tree
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from anchors import ARCHITECTURE, INEXPRESSIBLE, OWN_TESTS, TREES, WITNESS_WIRING  # noqa: E402

REPO = Path("/Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-03")
PRISTINE = HERE / "trees"
SHARED_SUITE = REPO / "examples/validation/ab/tests/test_behavior.py"

MUTANTS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09",
           "M10", "PA-M11", "PA-M12", "PA-M13", "PA-M14", "FI-M15"]

FAKE_COMPOSITION = '''"""A second composition point, written by the RD-03 probe, OUTSIDE the tree.

The same domain wired to the in-memory adapter instead of the file one. It is
the `suite-fake` instrument of examples/validation/ab/seeded_faults.toml,
reconstructed for these trees. Four lines, exactly as the catalogue's
[pa_measured_swap_baseline] block claims.
"""
from quota_ledger import Ledger, MemoryJournal


class QuotaLedger(Ledger):
    def __init__(self, quotas, ledger_path):
        super().__init__(dict(quotas), MemoryJournal())
'''

WITNESS_DRIVER = '''
import sys, importlib, json
from pathlib import Path
tree, probe_dir, name, wiring, work = sys.argv[1:6]
sys.path.insert(0, probe_dir)
sys.path.insert(0, tree)
import wit
module = importlib.import_module("quota_ledger")
if wiring == "fake":
    make = lambda q, p: module.Ledger(dict(q), module.MemoryJournal())
else:
    make = lambda q, p: module.QuotaLedger(dict(q), p)
try:
    if name == "__moved__":
        print(json.dumps({"trace": wit.moved_observables(make, Path(work) / "ledger.txt")}))
    else:
        print(json.dumps({"value": bool(wit.WITNESSES[name](make, Path(work) / "ledger.txt"))}))
except Exception as error:
    print(json.dumps({"error": f"{type(error).__name__}: {error}"}))
'''


def moved_set(clean: dict, dirty: dict) -> dict:
    """Which observables differ, and at which step. Names only, no averaging."""
    if "trace" not in clean or "trace" not in dirty:
        return {"unavailable": {"pristine": clean, "mutated": dirty}}
    moved: dict[str, list[str]] = {}
    for before, after in zip(clean["trace"], dirty["trace"]):
        for field in ("status", "reason", "reservation_id", "available",
                      "committed", "closed", "outstanding", "ledger"):
            if before[field] != after[field]:
                moved.setdefault(field, []).append(before["step"])
    return {"moved_observables": moved,
            "port_region_committed_closed_ledger": sorted(
                set(moved) & {"committed", "closed", "ledger"})}


def purge(root: Path) -> None:
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def run_witness(tree_dir: Path, name: str, wiring: str, work: Path) -> dict:
    purge(tree_dir)
    work.mkdir(parents=True, exist_ok=True)
    driver = work / "_witness_driver.py"
    driver.write_text(WITNESS_DRIVER, encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(driver), str(tree_dir), str(HERE), name, wiring, str(work)],
        capture_output=True, text=True,
    )
    if done.returncode != 0:
        return {"error": done.stderr.strip().splitlines()[-1:] or ["nonzero exit"]}
    try:
        return json.loads(done.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": done.stdout.strip()[-300:]}


def run_pytest(targets: list[str], cwd: Path, env_extra: dict | None = None) -> dict:
    environment = dict(os.environ)
    environment.update(env_extra or {})
    done = subprocess.run(
        ["uv", "run", "--with", "pytest", "python", "-m", "pytest", *targets,
         "-q", "-p", "no:cacheprovider"],
        cwd=str(cwd), env=environment, capture_output=True, text=True,
    )
    tail = [line for line in done.stdout.splitlines() if line.strip()][-1:]
    return {"failed": done.returncode != 0, "tail": tail, "returncode": done.returncode}


def measure_tree(tree: str, out_dir: Path) -> dict:
    anchors = TREES[tree]
    source = PRISTINE / tree
    rows: dict[str, dict] = {}
    ports = ARCHITECTURE[tree] == "ports-and-adapters"

    with tempfile.TemporaryDirectory() as raw:
        work_root = Path(raw)
        # -- baseline, unmutated --------------------------------------------
        base = work_root / "baseline"
        shutil.copytree(source, base)
        if ports:
            (base / "quota_ledger_fake.py").write_text(FAKE_COMPOSITION, encoding="utf-8")
        purge(base)
        baseline = {
            "own-tests": run_pytest([str(base / t) for t in OWN_TESTS[tree]], base),
            "shared-suite": run_pytest(
                [str(SHARED_SUITE)], REPO,
                {"QUOTA_LEDGER_DIR": str(base), "QUOTA_LEDGER_IMPL": "quota_ledger"}),
        }
        if ports:
            baseline["shared-suite-fake"] = run_pytest(
                [str(SHARED_SUITE)], REPO,
                {"QUOTA_LEDGER_DIR": str(base), "QUOTA_LEDGER_IMPL": "quota_ledger_fake"})

        for mutant in MUTANTS:
            entry = anchors.get(mutant)
            if entry is INEXPRESSIBLE or entry is None:
                rows[mutant] = {
                    "verdict_kind": "INEXPRESSIBLE" if entry is INEXPRESSIBLE else "NOT_ANCHORED",
                    "cells": {
                        name: ("INEXPRESSIBLE" if entry is INEXPRESSIBLE else "NOT_ANCHORED")
                        for name in baseline
                    },
                }
                continue

            work = work_root / f"mut-{mutant}"
            shutil.copytree(source, work)
            if ports:
                (work / "quota_ledger_fake.py").write_text(FAKE_COMPOSITION, encoding="utf-8")

            # exactly-once, on every edit of the patch
            occurrences = []
            for relative, find, _ in entry:
                text = (work / relative).read_text(encoding="utf-8")
                occurrences.append({"path": relative, "count": text.count(find)})
            if any(item["count"] != 1 for item in occurrences):
                rows[mutant] = {
                    "verdict_kind": "HOLE",
                    "why": f"find string not exactly once: {occurrences}",
                    "cells": {name: "HOLE:anchor-not-unique" for name in baseline},
                }
                continue

            wiring = WITNESS_WIRING.get((tree, mutant), "real")
            clean = run_witness(work, mutant, wiring, work_root / f"w-clean-{mutant}")
            clean_trace = run_witness(work, "__moved__", wiring,
                                      work_root / f"t-clean-{mutant}")

            for relative, find, replace in entry:
                target = work / relative
                target.write_text(
                    target.read_text(encoding="utf-8").replace(find, replace, 1),
                    encoding="utf-8")
            purge(work)

            dirty = run_witness(work, mutant, wiring, work_root / f"w-dirty-{mutant}")
            dirty_trace = run_witness(work, "__moved__", wiring,
                                      work_root / f"t-dirty-{mutant}")
            separates = clean.get("value") is False and dirty.get("value") is True
            record = {
                "wiring": wiring,
                "witness_on_pristine": clean,
                "witness_on_mutated": dirty,
                "separates_the_trees": separates,
                "effect_on_observables": moved_set(clean_trace, dirty_trace),
                "edits": [{"path": r, "find": f, "replace": p} for r, f, p in entry],
            }
            if not separates:
                record["verdict_kind"] = "HOLE"
                record["why"] = "semantic not reproduced on this tree"
                record["cells"] = {name: "HOLE:semantic-not-reproduced" for name in baseline}
                rows[mutant] = record
                continue

            cells = {}
            observed = {
                "own-tests": run_pytest([str(work / t) for t in OWN_TESTS[tree]], work),
                "shared-suite": run_pytest(
                    [str(SHARED_SUITE)], REPO,
                    {"QUOTA_LEDGER_DIR": str(work), "QUOTA_LEDGER_IMPL": "quota_ledger"}),
            }
            if ports:
                observed["shared-suite-fake"] = run_pytest(
                    [str(SHARED_SUITE)], REPO,
                    {"QUOTA_LEDGER_DIR": str(work), "QUOTA_LEDGER_IMPL": "quota_ledger_fake"})
            for name, result in observed.items():
                if baseline[name]["failed"]:
                    cells[name] = "BASELINE_RED"
                else:
                    cells[name] = "KILLED" if result["failed"] else "SURVIVED"
            record["verdict_kind"] = "MEASURED"
            record["cells"] = cells
            record["raw"] = observed
            rows[mutant] = record
            purge(work)
            shutil.rmtree(work, ignore_errors=True)

    return {
        "tree": tree,
        "architecture": ARCHITECTURE[tree],
        "baseline_on_unmutated_code": baseline,
        "instruments": list(baseline),
        "per_mutant": rows,
    }


def main() -> int:
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    trees = sys.argv[2:] or list(TREES)
    for tree in trees:
        report = measure_tree(tree, out_dir)
        (out_dir / f"{tree}.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"== {tree} ({report['architecture']}) ==")
        for mutant, row in report["per_mutant"].items():
            cells = " ".join(f"{k}={v}" for k, v in sorted(row["cells"].items()))
            print(f"  {mutant:<8} {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
