#!/usr/bin/env python3
"""Q2: is there ANY behavioural difference between a before tree and its after
tree? Per pair. Nothing here is averaged with anything else.

Three separate questions, answered separately:

  bytes      does the revision change any executable byte at all
  crossed    does each half pass the OTHER half's hand-written tests
  observed   does a differential walk over the public API ever separate them

A differential walk finding zero divergences does NOT prove equivalence. It
says this generator did not reach a distinguishing input, which is a weaker
claim, and the number of walks is reported with it.
"""

from __future__ import annotations

import importlib.util
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREES = HERE / "trees"
PAIRS = [("artifact_Z", "artifact_M"), ("artifact_E", "artifact_F"),
         ("artifact_N", "artifact_D")]
OWN = {"artifact_Z": "test_quota_ledger.py", "artifact_M": "test_quota_ledger.py",
       "artifact_N": "test_quota_ledger.py", "artifact_D": "test_quota_ledger.py",
       "artifact_E": "tests", "artifact_F": "tests"}

WALK = '''
import sys, json, random, importlib.util
from pathlib import Path

def load(directory, name):
    sys.path.insert(0, directory)
    import importlib
    for stale in [m for m in list(sys.modules) if m.split(".")[0] == "quota_ledger"]:
        del sys.modules[stale]
    module = importlib.import_module("quota_ledger")
    sys.path.pop(0)
    return module

before_dir, after_dir, work = sys.argv[1:4]
work = Path(work)
sys.path.insert(0, before_dir)
import importlib
before = importlib.import_module("quota_ledger")
sys.path.pop(0)
for stale in [m for m in list(sys.modules) if m.split(".")[0] == "quota_ledger"]:
    del sys.modules[stale]
sys.path.insert(0, after_dir)
after = importlib.import_module("quota_ledger")

def observe(book, tenants):
    return (
        [book.available(t) for t in tenants],
        [book.committed(t) for t in tenants],
        [book.is_closed(t) for t in tenants],
        list(book.outstanding_ids()),
        list(book.ledger_lines()),
    )

rng = random.Random(20260809)
WALKS, STEPS = 2000, 40
diverged = []
for walk in range(WALKS):
    quotas = {"acme": rng.randint(0, 14), "globex": rng.randint(0, 14)}
    a = before.QuotaLedger(dict(quotas), work / "a.txt")
    b = after.QuotaLedger(dict(quotas), work / "b.txt")
    tenants = list(quotas)
    for step in range(STEPS):
        op = rng.choice(["reserve", "reserve", "commit", "release", "close_tenant"])
        if op == "reserve":
            args = (rng.choice(["acme", "globex", "nobody"]), rng.randint(-2, 16))
        elif op == "close_tenant":
            args = (rng.choice(["acme", "globex", "nobody"]),)
        else:
            args = (f"r{rng.randint(1, 25)}",)
        first = getattr(a, op)(*args)
        second = getattr(b, op)(*args)
        key = lambda r: (r.status, getattr(r, "reason", None), getattr(r, "reservation_id", None))
        if key(first) != key(second) or observe(a, tenants) != observe(b, tenants):
            diverged.append({"walk": walk, "step": step, "op": op, "args": list(map(str, args)),
                             "before": key(first), "after": key(second)})
            break
print(json.dumps({"walks": WALKS, "steps_per_walk": STEPS,
                  "divergences": len(diverged), "first": diverged[:3]}))
'''


def bytes_diff(before: str, after: str) -> dict:
    done = subprocess.run(
        ["diff", "-r", "-x", "__pycache__", "-x", "*.md", "-x", ".pytest_cache",
         str(TREES / before), str(TREES / after)],
        capture_output=True, text=True)
    return {"identical_excluding_markdown": done.returncode == 0,
            "diff": done.stdout.strip()}


def run_tests(test_owner: str, against: str) -> dict:
    """Run `test_owner`'s hand-written tests against `against`'s code."""
    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw) / "tree"
        subprocess.run(["cp", "-R", str(TREES / against), str(work)], check=True)
        target = OWN[test_owner]
        source = TREES / test_owner / target
        destination = work / target
        subprocess.run(["rm", "-rf", str(destination)], check=True)
        subprocess.run(["cp", "-R", str(source), str(destination)], check=True)
        done = subprocess.run(
            ["uv", "run", "--with", "pytest", "python", "-m", "pytest",
             str(destination), "-q", "-p", "no:cacheprovider"],
            cwd=str(work), capture_output=True, text=True)
        tail = [line for line in done.stdout.splitlines() if line.strip()][-1:]
        return {"passed": done.returncode == 0, "tail": tail,
                "failures": [line for line in done.stdout.splitlines()
                             if line.startswith("FAILED")][:10]}


def main() -> int:
    report = {}
    for before, after in PAIRS:
        with tempfile.TemporaryDirectory() as raw:
            walk_script = Path(raw) / "walk.py"
            walk_script.write_text(WALK, encoding="utf-8")
            done = subprocess.run(
                [sys.executable, str(walk_script), str(TREES / before),
                 str(TREES / after), raw],
                capture_output=True, text=True)
            walk = (json.loads(done.stdout.strip().splitlines()[-1])
                    if done.returncode == 0 else {"error": done.stderr[-800:]})
        report[f"{before}->{after}"] = {
            "bytes": bytes_diff(before, after),
            "before_tests_on_after_code": run_tests(before, after),
            "after_tests_on_before_code": run_tests(after, before),
            "differential_walk": walk,
        }
        print(f"== {before} -> {after} ==")
        print(json.dumps(report[f"{before}->{after}"], indent=2)[:2400])
    (HERE / "out" / "pairs.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
