"""Run one generated corpus over one tree under one WIRING. One process, one answer.

Deliberately a subprocess worker rather than a function the driver calls in a
loop. `EVAL-RERUN-DF-01` is the reason: a purge keyed on a fixed list of binding
module names left a module holding `_impl = import_module("quota_ledger")` bound
to the PRISTINE tree, every mutant then executed against unmutated code, and the
run reported 11 of 11 SURVIVED with green controls. Its repair was to ask the
interpreter which modules hold a handle rather than to keep a list. This goes one
step further and asks a FRESH INTERPRETER, which cannot hold a stale handle at
all. The cost is process startup per cell; the benefit is that the class of bug
that produced a whole green sealed run is unreachable by construction.

THE BINDING UNDER TEST IS THE SHIPPED ONE. `load_mappings`, `apply_wiring` and
`adapter_for_case` are imported from `scripts/run_generated_case_adapters.py` and
not reimplemented here, so this measurement cannot pass while the shipped
resolution is broken, and a rename in the mapping schema breaks this too.

Output is one JSON object on stdout. Every field is a count or a name; nothing
here is a verdict. The driver decides KILLED/SURVIVED.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[5]

for entry in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), str(HERE)):
    if entry not in sys.path:
        sys.path.insert(0, entry)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="Generated case package directory")
    parser.add_argument("--tree", type=Path, required=True, help="Directory holding the composition points")
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--wiring", choices=["real", "fake"], required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    os.environ["QUOTA_LEDGER_DIR"] = str(args.tree)

    from run_generated_case_adapters import (  # noqa: E402
        adapter_for_case,
        apply_wiring,
        load_mappings,
        port_bindings,
    )
    from spec_double_compiler.runtime import call_adapter  # noqa: E402
    from run_generated_case_adapters import assert_case_result_per_field  # noqa: E402

    mappings = load_mappings(args.mapping)
    mappings, wiring_notes = apply_wiring(mappings, args.wiring)

    parent = str(args.cases.resolve().parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    cases = list(importlib.import_module(f"{args.cases.resolve().name}.cases").CASES)
    if args.limit is not None:
        cases = cases[: args.limit]

    adapters: dict[str, Any] = {}
    ran: Counter = Counter()
    ran_positive: Counter = Counter()
    failed: Counter = Counter()
    skipped: Counter = Counter()
    skipped_by_rule: Counter = Counter()
    bound_by: Counter = Counter()
    failures: list[str] = []

    work_root = Path(tempfile.mkdtemp(prefix="pa04-port-swap-"))
    try:
        for index, case in enumerate(cases):
            action = case.input.action
            mapping = adapter_for_case(case, mappings)
            if mapping is None or not mapping.adapter:
                skipped[action] += 1
                skipped_by_rule["no binding for this case's labels"] += 1
                continue
            bound_by[f"{mapping.label} ({mapping.binds}) -> {mapping.adapter}"] += 1
            adapter = adapters.get(mapping.adapter)
            if adapter is None:
                module_name, _, attribute = mapping.adapter.partition(":")
                adapter = getattr(importlib.import_module(module_name), attribute)()
                adapters[mapping.adapter] = adapter
            verdict = adapter.can_run(case)
            if verdict is not True and not (isinstance(verdict, tuple) and verdict[0]):
                reason = verdict[1] if isinstance(verdict, tuple) and len(verdict) > 1 else "unstated"
                skipped[action] += 1
                skipped_by_rule[reason] += 1
                continue
            accepting = "negative" not in set(case.labels)
            work_dir = work_root / f"case-{index}"
            try:
                result = call_adapter(adapter, case, work_dir)
                assert_case_result_per_field(case=case, result=result)
                ran[action] += 1
                ran_positive[action] += int(accepting)
            except Exception as error:  # a failing case is the signal, not an incident
                ran[action] += 1
                ran_positive[action] += int(accepting)
                failed[action] += 1
                if len(failures) < 3:
                    failures.append(f"{case.name}: {type(error).__name__}: {error}")
            finally:
                shutil.rmtree(work_dir, ignore_errors=True)
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    actions = sorted(set(ran) | set(skipped))
    print(json.dumps({
        "wiring": args.wiring,
        "cases": len(cases),
        "total_ran": sum(ran.values()),
        "total_failed": sum(failed.values()),
        "total_skipped": sum(skipped.values()),
        "per_action": {
            action: {
                "ran": ran.get(action, 0),
                "ran_accepting": ran_positive.get(action, 0),
                "ran_refusing": ran.get(action, 0) - ran_positive.get(action, 0),
                "failed": failed.get(action, 0),
                "skipped": skipped.get(action, 0),
            }
            for action in actions
        },
        "skipped_by_rule": dict(sorted(skipped_by_rule.items())),
        "bound_by": dict(sorted(bound_by.items())),
        "port_bindings": sorted(port_bindings(mappings)),
        "wiring_notes": wiring_notes,
        "failures": failures,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
