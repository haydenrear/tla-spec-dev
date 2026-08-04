#!/usr/bin/env python3
"""Merge the two runs that produced HP-06's kill table, and say which is which.

Two runs exist, and the reason is recorded rather than smoothed:

  run 1  every instrument. Its `corpus-slice-*` columns came back CONTROL_RED on
         BOTH arms on the UNMUTATED code, because the adapter returned all nine
         model fields against cases whose projection carries five. That is an
         instrument defect, filed as HP-06-DF-01.
  run 2  the two slice instruments only, after the adapter was corrected to
         compare exactly the fields the case's own projection carries.

The whole-view, negative and mapping columns are taken from run 1 UNCHANGED. The
correction cannot affect them: their cases carry all nine fields, so the filter
is the identity there, and their controls were green in run 1 already.

No column is taken from whichever run produced the better number. The rule is
one instrument, one run, named.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOAL = HERE.parent / "GOAL-catch-bugs"

ORDER = ["corpus-whole", "corpus-neg", "corpus-slice-res", "corpus-slice-led",
         "map-silent", "map-checking", "suite"]
FROM_RUN2 = {"corpus-slice-res", "corpus-slice-led"}


def merge(arm: str) -> dict:
    run1 = json.loads((GOAL / f"kill-table-arm-{arm}.json").read_text())
    run2 = json.loads((GOAL / f"kill-table-slices-arm-{arm}.json").read_text())
    merged = {
        "arm": run1["arm"],
        "catalogue": run1["catalogue"],
        "mutants_re_anchored": run1["mutants_re_anchored"],
        "instruments": ORDER,
        "provenance": {
            name: ("run2-corrected-slice-adapter" if name in FROM_RUN2 else "run1")
            for name in ORDER
        },
        "controls": {
            name: (run2 if name in FROM_RUN2 else run1)["controls"][name] for name in ORDER
        },
        "per_mutant": {},
    }
    for mutant in run1["per_mutant"]:
        merged["per_mutant"][mutant] = {
            name: (run2 if name in FROM_RUN2 else run1)["per_mutant"][mutant][name]
            for name in ORDER
        }
    classes = defaultdict(lambda: defaultdict(list))
    catalogue_rows = json.loads((GOAL / f"kill-table-arm-{arm}.json").read_text())["per_class"]
    # rebuild per-class from the merged per-mutant table using run1's class map
    import tomllib
    rows = tomllib.loads(Path(run1["catalogue"]).read_text())["mutants"]
    for row in rows:
        for name in ORDER:
            classes[row["fault_class"]][name].append(merged["per_mutant"][row["id"]][name])
    merged["per_class"] = {
        fault_class: {
            name: f"{verdicts.count('KILLED')} of {len(verdicts)}"
            for name, verdicts in by_instrument.items()
        }
        for fault_class, by_instrument in classes.items()
    }
    assert catalogue_rows  # run1 had one; kept only so the shape is documented
    return merged


def main() -> int:
    for arm in ("a", "b"):
        merged = merge(arm)
        out = GOAL / f"kill-table-arm-{arm}-merged.json"
        out.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
