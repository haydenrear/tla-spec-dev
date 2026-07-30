#!/usr/bin/env python3
"""RP-02: is there a rejected input anywhere in the 330-case corpus?

The guard-relaxation result is an assertion until this is counted. A guard can
only be caught by a case that supplies an argument the guard must REFUSE. This
walks the generated corpus and counts, per action, how many cases carry an
argument that the model's own guard would reject in that case's before-state.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
PKG = SCRATCH / "after-gen/spec-unit/pipeline_cases"

sys.path.insert(0, str(PKG.parent))
spec = importlib.util.spec_from_file_location("pipeline_cases", PKG / "__init__.py")
module = importlib.util.module_from_spec(spec)
sys.modules["pipeline_cases"] = module
spec.loader.exec_module(module)
CASES = module.CASES

ITEMS = {"i1", "i2"}


def enabled(action: str, i: str, s: dict) -> bool:
    """The TLA+ guard of each action, transcribed from Pipeline.tla."""
    b = {name: set(s[name]) for name in ("inbox", "accepted", "queue", "delivered", "failed", "ledger")}
    if action == "Accept":
        return i in b["inbox"]
    if action == "Enqueue":
        return i in b["accepted"] and i not in b["queue"]
    if action == "Deliver":
        return i in b["queue"] and i not in b["failed"]
    if action == "Fail":
        return i in b["delivered"] and i not in b["failed"]
    if action == "Record":
        return i in b["delivered"] and i not in b["ledger"]
    raise AssertionError(action)


by_action: dict[str, list[int]] = {}
statuses: dict[str, int] = {}
for case in CASES:
    action = case.input.action
    i = case.input.params["i"]
    counts = by_action.setdefault(action, [0, 0, 0])
    counts[0] += 1
    if enabled(action, i, case.before):
        counts[1] += 1
    else:
        counts[2] += 1
    statuses[case.output["status"]] = statuses.get(case.output["status"], 0) + 1

print(f"cases: {len(CASES)}")
print(f"expected output statuses: {statuses}")
print()
print(f"{'action':<10} {'cases':>6} {'arg ENABLED':>12} {'arg REJECTED':>13}")
for action in sorted(by_action):
    total, ok, bad = by_action[action]
    print(f"{action:<10} {total:>6} {ok:>12} {bad:>13}")
total = sum(v[0] for v in by_action.values())
rejected = sum(v[2] for v in by_action.values())
print(f"{'TOTAL':<10} {total:>6} {total - rejected:>12} {rejected:>13}")
print()

# How many arguments were even AVAILABLE to be rejected? For each case, how many
# elements of Items would the guard have refused in that before-state?
refusable = 0
for case in CASES:
    action = case.input.action
    refusable += sum(1 for i in ITEMS if not enabled(action, i, case.before))
print(
    f"argument/before-state pairs the model would REFUSE that a corpus COULD have "
    f"emitted: {refusable} (over {len(CASES)} cases x {len(ITEMS)} items)"
)
print("emitted by the generator: 0 -- a state graph has no edge for a refused argument.")
