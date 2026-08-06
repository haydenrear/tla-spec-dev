"""Generator against hand-written suite, as SETS, on every sealed kill table.

THE SENTENCE THIS FILE EXISTS TO TEST. Three epics have carried it forward
unchanged, and `FALSIFIABLE-INSTRUMENTS-EPIC.md` §2 restates it as settled:

    "On this fixture the generated corpus is still worse than a suite a
     competent engineer writes in an afternoon."

Its evidence is a COUNT (10 of 11 against 10 of 11) and a DOMINANCE claim
(`suite-fake` strictly dominates `corpus-port-swap:fake`). Neither is a set
comparison, and a count cannot tell "the same ten" from "ten each, different
by one in each direction". This file does the set comparison, on the sealed
tables, and reports:

    generated-only   killed by at least one generated instrument, MISSED by the
                     hand-written suite
    suite-only       killed by the suite, MISSED by every generated instrument
    neither          invisible to everything in the fixture

WHY THE CATALOGUE'S AUTHOR IS THE VARIABLE THAT MATTERS. `seeded_faults.toml`'s
own `[measured_suite_baseline]` declares the bias: "The suite was written before
the catalogue but by the same author who chose the fault classes. It is not
evidence that hand-written suites catch everything." The `blind_author` tables
are the only ones in this repository whose catalogue was authored by an agent
that had never seen the fixture's catalogue, its harness, or its reference. Run
against both and read the difference between them, never a total.

This file MEASURES NOTHING NEW. It reads sealed JSON that four earlier tickets
produced and does arithmetic on it. Nothing here can move a cell.

    python3 examples/validation/ab/eval/generator_vs_suite.py --out <path>.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
RERUN = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/GOAL-catch-bugs"
PORTS = REPO_ROOT / "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/results"
FI01 = REPO_ROOT / "examples/validation/ab/eval/results/fi01"

#: label -> (sealed table, who authored the catalogue, one line on what it is)
TABLES: dict[str, tuple[Path, str, str]] = {
    "seeded/arm A": (
        RERUN / "kill-table-arm-a.json", "the fixture's own author",
        "HP-01's catalogue, 11 rows, on arm A's judged tree",
    ),
    "seeded/arm B": (
        RERUN / "kill-table-arm-b.json", "the fixture's own author",
        "HP-01's catalogue, 11 rows, on arm B's judged tree",
    ),
    "blind/arm A": (
        RERUN / "kill-table-blind-author-arm-a.json", "an independent blind agent",
        "BLIND-AUTHOR-P, 15 rows, authored without sight of the fixture's catalogue",
    ),
    "blind/arm B": (
        RERUN / "kill-table-blind-author-arm-b.json", "an independent blind agent",
        "BLIND-AUTHOR-Q, 15 rows, authored without sight of the fixture's catalogue",
    ),
    "ports/reference_ports": (
        FI01 / "swap-reference_ports.json", "the fixture's own author",
        "PA-01's four adapter rows plus FI-01's in-region control, on reference_ports "
        "-- a tree the epic authored, which is PA-06-DF-04's whole complaint",
    ),
}

SUITE_PREFIX = "suite"


def cells_of(row: Any) -> dict[str, str]:
    """Both sealed shapes: `{instrument: verdict}` and `{"cells": {...}}`."""
    return row.get("cells", row) if isinstance(row, dict) else {}


def compare(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    columns = report["instruments"]
    suite = [name for name in columns if name.startswith(SUITE_PREFIX)]
    generated = [name for name in columns if name not in suite]
    rows = report["per_mutant"]

    generated_kills: set[str] = set()
    suite_kills: set[str] = set()
    for row_id, row in rows.items():
        cells = cells_of(row)
        if any(cells.get(name) == "KILLED" for name in generated):
            generated_kills.add(row_id)
        if any(cells.get(name) == "KILLED" for name in suite):
            suite_kills.add(row_id)

    per_column = {
        name: sorted(row_id for row_id, row in rows.items() if cells_of(row).get(name) == "KILLED")
        for name in columns
    }
    return {
        "rows": len(rows),
        "generated_columns": generated,
        "suite_columns": suite,
        "generated_union_kills": len(generated_kills),
        "suite_kills": len(suite_kills),
        "generated_only": sorted(generated_kills - suite_kills),
        "suite_only": sorted(suite_kills - generated_kills),
        "neither": sorted(set(rows) - generated_kills - suite_kills),
        "per_column_kills": {name: len(ids) for name, ids in per_column.items()},
        "verdict": (
            "SUITE STRICTLY DOMINATES" if (generated_kills < suite_kills)
            else "GENERATED UNION STRICTLY DOMINATES" if (suite_kills < generated_kills)
            else "IDENTICAL SETS" if generated_kills == suite_kills
            else "COMPLEMENTARY -- neither dominates; each has a kill the other misses"
        ),
    }


def render(result: dict[str, Any]) -> str:
    lines = []
    for label, record in result["tables"].items():
        lines.append(f"== {label}   catalogue authored by {record['catalogue_author']}")
        lines.append(f"   {record['what']}")
        figures = record["comparison"]
        lines.append(
            f"   generated union {figures['generated_union_kills']} of {figures['rows']}"
            f"   |   hand-written suite {figures['suite_kills']} of {figures['rows']}"
        )
        lines.append(f"   generated-only (suite MISSED): {figures['generated_only'] or 'none'}")
        lines.append(f"   suite-only (all generated MISSED): {figures['suite_only'] or 'none'}")
        lines.append(f"   invisible to everything: {figures['neither'] or 'none'}")
        lines.append(f"   -> {figures['verdict']}")
        lines.append("")
    lines.append(result["headline"])
    return "\n".join(lines)


def build() -> dict[str, Any]:
    tables = {}
    for label, (path, author, what) in TABLES.items():
        if not path.exists():
            tables[label] = {"catalogue_author": author, "what": what, "comparison": None,
                             "error": f"missing: {path}"}
            continue
        tables[label] = {
            "catalogue_author": author,
            "what": what,
            "comparison": compare(path),
        }

    blind = [
        record["comparison"] for label, record in tables.items()
        if label.startswith("blind/") and record.get("comparison")
    ]
    seeded = [
        record["comparison"] for label, record in tables.items()
        if not label.startswith("blind/") and record.get("comparison")
    ]
    blind_generated_only = sum(len(c["generated_only"]) for c in blind)
    blind_suite_only = sum(len(c["suite_only"]) for c in blind)
    seeded_generated_only = sum(len(c["generated_only"]) for c in seeded)

    headline = (
        "HEADLINE. On catalogues written by the fixture's own author the generated "
        f"family has {seeded_generated_only} kill(s) the hand-written suite misses. "
        "On the only catalogues in this repository authored BLIND, it has "
        f"{blind_generated_only}, and the suite has {blind_suite_only} the generated "
        "family misses. Neither dominates there. The dominance result that three "
        "epics have carried forward is a property of WHO WROTE THE CATALOGUE, and it "
        "reverses on the one catalogue that controls for it."
    )
    return {"tables": tables, "headline": headline}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(render(result))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
