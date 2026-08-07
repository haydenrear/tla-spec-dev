#!/usr/bin/env python3
"""Write one neutrally-labelled evidence packet per blind artifact.

What a judge is given, and why each part is there:

* the artifact's own per-mutant per-instrument kill table, with `seeded_by`,
  because D1 is about what the cases CATCH and a class row without its diff
  shape cannot be read;
* the executability table beside it, because a zero from an instrument that ran
  nothing is not the same claim as a zero from one that ran 294 accepting
  cases (the plan's `known_gaps` requires executable counts beside every kill
  number);
* the CONTROL status, unabridged, including every red one -- a table under a red
  positive control is a FLOOR and a judge who is not told that is scoring a
  number nobody can interpret;
* the mechanical block for ALL THREE artifacts, neutrally labelled, because
  D2 anchor 3 reads a before/after and a judge with one column cannot reach it.
  This is EVAL-RERUN's rule carried forward unchanged.

Source code is still ONE artifact per judge.

Nothing in a packet names an arm, a prompt, a ticket or a prediction. Nothing in
a packet states one of the card's dimensions, anchors or scoring rules either:
those reach the judge through the rubric rendered into `scorecard.md`, under
`served_digest`, and a second copy here would be under nothing (SM-06).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
PA06 = REPO_ROOT / "specs/results/scorecards/ports-as-adapters"
SCRATCH = Path("/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/"
               "daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/pa06")

LABELS = {"T": "b", "U": "a", "W": "c"}  # opaque label -> kill-table suffix
OUT = PA06 / "blind"

INSTRUMENT_NOTE = """\
## What each instrument is

Every one of these is a set of executable cases run against this artifact with
exactly one seeded fault applied, then reverted. `KILLED` means at least one
case failed under the fault; `SURVIVED` means none did; `NOT_DECIDABLE` means a
declared limitation for that pair was verified against this run's own
executability counts and held, so the cell decides nothing.

| instrument | what it is |
|---|---|
| `corpus-whole` | every enabled edge of the model's state graph, replayed |
| `corpus-neg` | the DISABLED edges at each reachable state, each asserting a refusal plus inertness |
| `corpus-slice-res` | the same, projected onto the reservation aspect only |
| `corpus-slice-led` | the same, projected onto the ledger aspect only |
| `corpus-port` | cases generated PER DECLARED PORT rather than per action |
| `map-silent` | `corpus-whole` with an effect provider that records and asserts nothing about content |
| `map-checking` | `corpus-whole` with an effect provider that asserts durable content |
| `suite` | the shared hand-written behavioral suite, unchanged, the same for every artifact |
| `corpus-action-bound` | the port corpus bound to ACTIONS -- the pre-port-binding world |
| `corpus-port-swap:real` | the port corpus bound to the declared PORT, real implementation |
| `corpus-port-swap:fake` | the same cases, same binding, the port's FAKE implementation if one exists |

`corpus-port-swap:fake` on an artifact that ships no second implementation runs
its REAL one, and the runner says so on every such run. That is a fact about the
artifact, not a limitation of the instrument.

Every corpus here is generated from ONE model and ONE manifest shared by all
three artifacts. No artifact's corpus differs from another's by a byte, and the
`cases.py` sha1 is recorded below. So a difference between artifacts in this
table is a difference in the CODE, never in the cases.
"""

# SM-06: this note used to restate two of the card's numbered scoring rules and
# one of its dimension caveats, in prose written HERE. That is the worst place in
# the repository for a copy of the card: it is handed to a judge, and it is
# covered by no digest -- the rubric a judge is served carries its own
# `served_digest`, and this text is not in it. Inverted as gap mutant M2 it moved
# no verdict anywhere. Every rule a judge needs is in the card they are served,
# parsed out of the rubric; what belongs here is only what is true of THIS
# PACKET and of nothing else.
RULES_NOTE = """\
## How to use this packet

**The scoring rules are the ones in your scorecard, and they are not repeated
here.** They are rendered into `scorecard.md` out of
`references/eval_scorecard.md`, which is the one place any of them is stated.
Read them there. Two of them govern this packet directly — how to read the
mechanical block against your judgement, and whether a claim in an artifact's
own prose is evidence — and re-stating them in a packet is how a judge ends up
holding two versions of one rule.

What is true of this packet and of nothing else:

**A number under a RED control is a FLOOR.** Read the control section before
reading any kill number. A positive control that should have died on an
instrument and did not means that instrument's zeros cannot be told apart from a
broken instrument.

**The mechanical block covers all three artifacts, neutrally labelled**, because
one column is not a before and an after. Which column belongs to which arm is
not in this packet and is not for you to work out.
"""


def kill_table_markdown(table: dict, seeded_by: dict[str, str]) -> str:
    instruments = table["instruments"]
    lines = ["| mutant | class | seeded_by | " + " | ".join(instruments) + " |",
             "|---|---|---|" + "---|" * len(instruments)]
    for mutant in sorted(table["per_mutant"]):
        record = table["per_mutant"][mutant]
        cells = record.get("cells", record)
        klass = record.get("fault_class", "") if isinstance(record, dict) else ""
        lines.append(
            f"| `{mutant}` | {klass} | {seeded_by.get(mutant, '?')} | "
            + " | ".join(str(cells.get(i, "-")) for i in instruments) + " |"
        )
    return "\n".join(lines)


def executability_markdown(table: dict) -> str:
    controls = table["controls_on_unmutated_code"]
    lines = ["| instrument | cases | executed | skipped | failed on unmutated code | accepting `Reserve` executed |",
             "|---|---|---|---|---|---|"]
    for instrument in table["instruments"]:
        record = controls.get(instrument, {})
        per_action = record.get("per_action") or {}
        reserve = per_action.get("Reserve") or {}
        lines.append(
            f"| `{instrument}` | {record.get('cases', '-')} | {record.get('total_ran', '-')} | "
            f"{record.get('total_skipped', '-')} | {record.get('total_failed', '-')} | "
            f"{reserve.get('ran_accepting', '-')} |"
        )
    return "\n".join(lines)


def mechanical_markdown(complexity: dict) -> str:
    header = ("| figure | artifact T | artifact U | artifact W |\n|---|---|---|---|")
    by_label: dict[str, dict] = {}
    for report in complexity["reports"]:
        label = Path(report["target"]).name.replace("artifact_", "")
        by_label[label] = report
    figures = ["modules", "code_lines", "callables", "classes", "public_surface",
               "instance_state", "module_state", "branch_points",
               "max_branch_points_in_callable", "max_depth", "declared_interfaces",
               "declared_interface_methods", "internal_import_edges", "effectful_calls",
               "modules_with_effectful_calls", "branch_points_in_effectful_modules",
               "instance_state_in_effectful_modules"]
    rows = [header]
    for figure in figures:
        values = []
        for label in ("T", "U", "W"):
            totals = by_label[label]["totals_code_only"]
            values.append(str(totals.get(figure, "-")))
        rows.append(f"| `{figure}` | " + " | ".join(values) + " |")
    return "\n".join(rows)


def main() -> int:
    complexity = json.loads((SCRATCH / "out/complexity-blind.json").read_text())
    mechanical = mechanical_markdown(complexity)

    import tomllib
    seeded_by_per_arm = {}
    catalogues = {
        "a": [REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/measure/catalogue_arm_a.toml"],
        "b": [REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/measure/catalogue_arm_b.toml"],
        "c": [PA06 / "measure/catalogue_arm_c.toml"],
    }
    for arm, paths in catalogues.items():
        seeded_by_per_arm[arm] = {
            row["id"]: row.get("seeded_by", "?")
            for path in paths
            for row in tomllib.loads(path.read_text())["mutants"]
        }

    for label, arm in LABELS.items():
        table = json.loads((SCRATCH / f"out/kill-table-arm-{arm}.json").read_text())
        swap = json.loads((SCRATCH / f"swap/swap-arm_{arm}.json").read_text())
        packet = OUT / f"artifact_{label}" / "EVIDENCE.md"
        swap_instruments = sorted({i for r in swap["per_mutant"].values() for i in r["cells"]})
        swap_rows = ["| mutant | " + " | ".join(swap_instruments) + " |",
                     "|---|" + "---|" * len(swap_instruments)]
        for mutant in sorted(swap["per_mutant"]):
            cells = swap["per_mutant"][mutant]["cells"]
            swap_rows.append(f"| `{mutant}` | "
                             + " | ".join(str(cells.get(i, "-")) for i in swap_instruments) + " |")
        packet.write_text(f"""# Evidence packet — artifact {label}

This packet is measured evidence about **artifact {label} only**, except the
mechanical block, which covers all three artifacts because the scorecard's D2
anchor 3 reads a before/after and one column cannot reach it.

{RULES_NOTE}

{INSTRUMENT_NOTE}

## Shared behavioral suite

`examples/validation/ab/tests/test_behavior.py`, unchanged, the same file for
every artifact: **28 passed**, on unmutated code.

## Per-mutant, per-instrument kill table

Eleven seeded faults, each applied exactly once to a copy of this artifact,
proved to revert byte-identically, and reverted. Every cell is a measured run.

{kill_table_markdown(table, seeded_by_per_arm[arm])}

`seeded_by` is a fact about the DIFF, not about the artifact's quality:
`perturbation` = an existing statement changed; `addition` = a statement
invented and inserted, because the fault has no one-token form in this design.

### Per class

```
{json.dumps(table["per_class"], indent=2, sort_keys=True)}
```

## The port-binding columns

The same generated port corpus, bound three ways.

{chr(10).join(swap_rows)}

## Executability, beside every kill number

From this run's own control pass on **unmutated** code. A zero from an
instrument that executed nothing is not the same claim as a zero from one that
executed 294 accepting `Reserve` cases.

{executability_markdown(table)}

Generated corpus `cases.py` sha1 (the port corpus, identical for all three
artifacts): `08265aff0d81f27f4dfc9694d2a69c3c5b6e695c`.

## CONTROL STATUS — read this before any kill number

```
{json.dumps(table["control_verdicts"], indent=2, sort_keys=True)}
```

```
control coverage: {json.dumps(table["control_coverage"], sort_keys=True)}
polarities with no deciding control: {json.dumps(table.get("polarities_with_no_deciding_control", []))}
limitations rejected by this run's own evidence: {json.dumps(table.get("limitations_rejected", []), indent=2)}
```

Port-binding columns, control roles executed against this run's measured counts:

```
{json.dumps(swap.get("control_red", []), indent=2, sort_keys=True)}
```

## MECHANICAL BLOCK

Complexity of produced code, `role=code` only (implementation modules; test
modules excluded), over all three artifacts.

{mechanical}

Definitions are the instrument's own and are printed by
`python3 scripts/code_complexity.py <target>`. `effectful_calls` UNDERCOUNTS by
construction: 18 sink names are left out of the vocabulary for colliding with
in-memory operations, and the instrument says so on every run.

**This block is not a score and must not be converted into one.**
""", encoding="utf-8")
        print("wrote", packet.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
