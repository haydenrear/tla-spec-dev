"""Does this fixture's A/B CAN diverge -- read off the runs, never argued.

`PA-06-DF-08` is the finding this file answers: `GOAL-cases-drive-ports` could
not have been met by the experiment that measured it, because the null was
ENTAILED by the fixture. The entailment has two clauses and BOTH have to hold:

  E1  THE INSTRUMENT IS THE SAME ON BOTH ARMS. A corpus is a pure function of
      `(model, manifest, flags)`, and the A/B holds one model and one manifest
      across every arm by design, so no change confined to generation can make
      two arms' corpora differ. PA-03 reached this independently.

  E2  THE SUBJECTS ARE THE SAME UNDER THAT INSTRUMENT. `AD-F1`'s exhaustive
      observational fingerprint -- 28,561 command sequences, three arms, per
      mutant -- measured the arms' MUTATED trees identical on 10 of 11 rows.

E1 and E2 together entail the null: identical instrument on observationally
identical subjects returns identical verdicts. The 64 of 64 was arithmetic.

THE CRACK, AND IT IS THE ONLY ONE. `--wiring fake` does not read the model. It
resolves the arm's OWN `fake =` declaration to the arm's OWN second
implementation, and an arm that has none runs its real code instead. So the
swap columns are the one instrument in this fixture that is a function of the
ARM'S ARCHITECTURE rather than of the shared model, and E1 fails there. That is
where the one diverging cell in PA-06's whole three-arm table came from.

WHAT THIS FILE COMPUTES, all of it from measured artifacts:

  compositions_per_arm   MEASURED, not declared. Two wirings that produce a
                         byte-identical evidence block on every row are ONE
                         composition. This is `AD-F6`'s own test, mechanised,
                         so that "arm A has no fake" is a reading of the data
                         rather than a sentence in a comment.

  reachability           per column: `REACHABLE` where the arms' composition
                         counts differ or a row has no home on one arm;
                         `NOT_REACHABLE (E1+E2 entailed)` otherwise.

  divergence             per semantic, per column, the cells that actually
                         differ, and the arm that structurally cannot produce
                         the other's cell.

R2, WIRED IN. A `REACHABLE` claim with no measured divergence beside it is
reported `CLAIMED_REACHABLE_BUT_UNDEMONSTRATED` and the run exits nonzero. A
reachability analysis that cannot come out red is the fifth unfalsifiable
instrument in this repository, and this epic exists because of the other four.

    python3 examples/validation/ab/eval/divergence.py \
        --run arm_a=<swap-arm_a.json> --run arm_b=<swap-arm_b.json> \
        --run arm_c=<swap-arm_c.json> --out <path>.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

HERE = Path(__file__).resolve().parent

NOT_APPLICABLE = "NOT_APPLICABLE"

#: The evidence fields that decide whether two wirings are the same run. Chosen
#: to be exactly what `run_port_swap.py` records per instrument per mutant, so
#: the comparison cannot drift from what the driver actually measured.
EVIDENCE_KEYS = ("total_ran", "total_failed", "total_skipped", "failures")


def load_catalogue(path: Path) -> dict[str, dict[str, Any]]:
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in document.get("mutants", [])}


def _partner(column: str) -> str | None:
    """The unswapped column a swapped column is a SUBSTITUTION OF."""
    for swapped, plain in ((":fake", ":real"), ("-fake", "-real")):
        if column.endswith(swapped):
            return column[: -len(swapped)] + plain
    return None


def measured_compositions(report: dict[str, Any]) -> dict[str, Any]:
    """How many DISTINCT compositions each COLUMN ran on this arm.

    PER COLUMN, NOT PER PAIR, and the difference is load-bearing. A `:real`
    column runs the tree as the program itself composes it -- on every arm,
    whatever else that arm ships -- so it is ONE composition everywhere by
    construction, and an arm that happens to own a fake does not thereby make
    its `:real` column arm-specific. Only the SWAPPED column is a function of
    the arm's architecture: it names the arm's own second implementation where
    one exists and silently falls back to the real one where none does.

    THE FIRST VERSION ATTRIBUTED THE PAIR'S COUNT TO BOTH HALVES, which made
    `corpus-port-swap:real` and `suite-real` look reachable for divergence on
    three arms whose `:real` columns had all run the same thing, and the tool
    duly reported two CLAIMED_REACHABLE_BUT_UNDEMONSTRATED reds. The assertion
    is unchanged -- a reachability claim still goes red unless its own run
    demonstrates it, and `tests/test_fixture_can_diverge.py` feeds it an input
    where it must. What was wrong was WHICH COLUMNS CARRIED THE CLAIM.

    Not read from a mapping file either way. Two columns whose evidence block is
    byte-identical on every row ran the same program, whatever their names say.
    `AD-F6` measured that by hand for arms A and C; here the run decides it.
    """
    columns = report["instruments"]
    rows = report["per_mutant"]
    per_column: dict[str, Any] = {}
    for column in columns:
        partner = _partner(column)
        if partner is None:
            per_column[column] = {
                "distinct_compositions": 1,
                "substitutes_for": None,
                "why": (
                    "this column runs the tree as the program composes it, on every "
                    "arm. Nothing is substituted, so it is one composition by "
                    "construction and it cannot be arm-specific."
                ),
            }
            continue
        if partner not in columns:
            per_column[column] = {
                "distinct_compositions": None,
                "substitutes_for": partner,
                "why": f"declared without its {partner} partner; nothing to compare against",
            }
            continue
        if all("evidence" in rows[row] for row in rows):
            identical = all(
                {key: rows[row]["evidence"][partner].get(key) for key in EVIDENCE_KEYS}
                == {key: rows[row]["evidence"][column].get(key) for key in EVIDENCE_KEYS}
                for row in rows
            )
            basis = "evidence blocks"
        else:
            identical = all(
                rows[row]["cells"][partner] == rows[row]["cells"][column] for row in rows
            )
            basis = "verdict cells (this artifact keeps no evidence block)"
        per_column[column] = {
            "distinct_compositions": 1 if identical else 2,
            "substitutes_for": partner,
            "rows_compared": len(rows),
            "compared_on": basis,
            "identical_on_every_row": identical,
            "why": (
                f"identical to {partner} on every row: this arm declares no second "
                "implementation, so the swap ran the real one and this column is a "
                "duplicate (AD-F6)"
                if identical
                else f"differs from {partner} on at least one row: this arm really does "
                "have a second implementation and the swap composed it"
            ),
        }
    # A column that does not exist on an arm is not a zero; it is a name nobody
    # could ask. Recorded so `reachability` reports the absence rather than
    # inferring something from a missing key.
    for column in ("suite-fake", "corpus-port-swap:fake"):
        if column not in columns:
            per_column[column] = {
                "distinct_compositions": None,
                "substitutes_for": _partner(column),
                "why": (
                    "no second composition point exists on this arm, so this column "
                    "was not declared. Declaring it would silently re-run the real one."
                ),
            }
    return per_column


def executable_counts(report: dict[str, Any]) -> dict[str, Any]:
    """What each column actually EXECUTED on unmutated code, per action.

    Never a bare kill number. The epic's standing rule.
    """
    counts: dict[str, Any] = {}
    for name, record in report["controls_on_unmutated_code"].items():
        per_action = record.get("per_action")
        counts[name] = {
            "cases": record.get("cases"),
            "ran": record.get("total_ran"),
            "skipped": record.get("total_skipped"),
            "per_action": (
                {action: figures.get("ran_accepting") for action, figures in per_action.items()}
                if per_action
                else None
            ),
            "accounting": "measured" if per_action else "instrument keeps none",
        }
    return counts


def build(runs: dict[str, tuple[Path, Path]]) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for arm, (report_path, catalogue_path) in runs.items():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        catalogue = load_catalogue(catalogue_path)
        arms[arm] = {
            "report": report,
            "catalogue": catalogue,
            "compositions": measured_compositions(report),
            "executable": executable_counts(report),
        }

    # Rows are paired by SEMANTIC KEY, never by id and never by bytes. That is
    # PA-06-DF-08's own suggested fix: a mutant defined by WHERE IT SITS, with
    # the pair reported as a difference the way PA-M11/PA-M12 are.
    semantics: dict[str, dict[str, list[str]]] = {}
    for arm, data in arms.items():
        for row_id, row in data["catalogue"].items():
            key = row.get("semantic_key", row_id)
            semantics.setdefault(key, {}).setdefault(arm, []).append(row_id)

    all_columns = sorted({name for data in arms.values() for name in data["report"]["instruments"]})

    per_semantic: dict[str, Any] = {}
    divergences: list[dict[str, Any]] = []
    for key, by_arm in sorted(semantics.items()):
        cells: dict[str, dict[str, dict[str, str]]] = {}
        for arm, data in arms.items():
            rows = by_arm.get(arm, [])
            cells[arm] = {}
            for row_id in rows:
                report_row = data["report"]["per_mutant"].get(row_id)
                if report_row is None:
                    continue
                cells[arm][row_id] = {
                    column: report_row["cells"].get(column, NOT_APPLICABLE)
                    for column in all_columns
                }
            if not rows:
                cells[arm]["<no home on this arm>"] = {c: NOT_APPLICABLE for c in all_columns}
        per_semantic[key] = {
            "homes_per_arm": {arm: len(by_arm.get(arm, [])) for arm in arms},
            "cells": cells,
        }

        # A DIVERGENCE is two arms giving DIFFERENT ANSWERS TO THE SAME QUESTION.
        #
        # THE COMPARABLE ROW IS THE ONE THE DEFAULT COMPOSITION WIRES, and the
        # catalogue says which by `wired_by_default`, declared per row before any
        # of them ran. Arm B has two homes for this semantic; only one of them is
        # what an ordinary run of arm B executes, and that is the row arm A's and
        # arm C's single home is the counterpart of.
        #
        # THE FIRST VERSION OF THIS FUNCTION COMPARED SETS OF VERDICTS ACROSS ALL
        # ROWS AND WAS WRONG. It reported `corpus-action-bound` and `suite-real`
        # as divergent, because arm B contributed `{KILLED, SURVIVED}` from two
        # rows against arm A's `{KILLED}` from one -- conflating "arm B has an
        # extra row" with "the arms disagree". On the comparable row the arms
        # AGREE on those two columns, which is the whole point: the divergence is
        # confined to the columns that swap the composition. Recorded here rather
        # than quietly corrected, because a divergence count that is too large is
        # the failure mode this ticket exists to stop.
        comparable: dict[str, tuple[str, dict[str, str]]] = {}
        for arm, rows in cells.items():
            for row_id, verdicts in rows.items():
                row = arms[arm]["catalogue"].get(row_id, {})
                if row.get("wired_by_default"):
                    comparable[arm] = (row_id, verdicts)
        per_semantic[key]["comparable_row_per_arm"] = {
            arm: row_id for arm, (row_id, _) in sorted(comparable.items())
        }
        per_semantic[key]["rows_with_no_counterpart"] = sorted(
            row_id
            for arm, rows in cells.items()
            for row_id in rows
            if row_id in arms[arm]["catalogue"]
            and not arms[arm]["catalogue"][row_id].get("wired_by_default")
        )

        for column in all_columns:
            answers = {
                arm: verdicts[column]
                for arm, (_, verdicts) in comparable.items()
                if verdicts.get(column, NOT_APPLICABLE) != NOT_APPLICABLE
            }
            if len(set(answers.values())) > 1:
                divergences.append({
                    "semantic": key,
                    "column": column,
                    "compared_rows": {
                        arm: comparable[arm][0] for arm in sorted(answers)
                    },
                    "per_arm": dict(sorted(answers.items())),
                    "compositions_per_arm": {
                        arm: _composition_for(arms[arm]["compositions"], column)
                        for arm in sorted(answers)
                    },
                })

    # A row with a home on one arm and none on another is a STRUCTURAL fact,
    # reported as its own kind rather than folded into the divergence list.
    structural: list[dict[str, Any]] = []
    for key, record in per_semantic.items():
        homes = record["homes_per_arm"]
        if len(set(homes.values())) > 1:
            structural.append({
                "kind": "unequal homes for one semantic",
                "semantic": key,
                "homes_per_arm": homes,
                "rows_with_no_counterpart": record["rows_with_no_counterpart"],
                "why": (
                    "the arms do not agree on how many places this semantic can live. "
                    "An arm with fewer homes cannot host the extra rows at all, and "
                    "inventing a nearest-bytes stand-in there is the re-anchoring "
                    "artefact PA-06-DF-08 is about."
                ),
            })
    for column in all_columns:
        present = {arm for arm, data in arms.items() if column in data["report"]["instruments"]}
        if present != set(arms):
            structural.append({
                "kind": "column absent on some arms",
                "column": column,
                "present_on_arms": sorted(present),
                "absent_on_arms": sorted(set(arms) - present),
                "why": (
                    "this column needs a second composition point and those arms have "
                    "none. Declaring it anyway would silently re-run the real column "
                    "and report a duplicated cell as an independent measurement, which "
                    "is AD-F6."
                ),
            })

    reachability: dict[str, Any] = {}
    for column in all_columns:
        counts = {
            arm: _composition_for(arms[arm]["compositions"], column) for arm in arms
        }
        present = {arm for arm, data in arms.items() if column in data["report"]["instruments"]}
        demonstrated = [d for d in divergences if d["column"] == column]
        if present != set(arms):
            # THE COLUMN CANNOT EXIST ON EVERY ARM. That is not an undemonstrated
            # claim; the absence IS the demonstration, and it is the strongest
            # form of "one arm structurally cannot".
            verdict = "REACHABLE_BY_ABSENCE"
            why = (
                f"the column does not exist on {sorted(set(arms) - present)}: those arms "
                "have no second composition point for it to name. The arms cannot give "
                "the same answer because one of them cannot be asked."
            )
        elif len(set(counts.values())) > 1:
            verdict = "REACHABLE" if demonstrated else "CLAIMED_REACHABLE_BUT_UNDEMONSTRATED"
            why = (
                "the arms differ in how many distinct compositions this column runs. "
                "E1 fails: the instrument is a function of the arm's architecture "
                "rather than of the shared model."
            )
        else:
            verdict = "NOT_REACHABLE"
            why = (
                "E1 holds (one corpus, one model, one manifest across arms) and E2 holds "
                "(AD-F1 measured the mutated trees observationally identical). Identical "
                "instrument on identical subjects returns identical verdicts."
            )
        reachability[column] = {
            "verdict": verdict,
            "compositions_per_arm": counts,
            "present_on_arms": sorted(present),
            "demonstrated_divergences": len(demonstrated),
            "why": why,
        }

    red = sorted(
        column
        for column, record in reachability.items()
        if record["verdict"] == "CLAIMED_REACHABLE_BUT_UNDEMONSTRATED"
    )
    return {
        "arms": sorted(arms),
        "columns": all_columns,
        "compositions_per_arm": {arm: data["compositions"] for arm, data in arms.items()},
        "executable_counts_per_arm": {arm: data["executable"] for arm, data in arms.items()},
        "reachability": reachability,
        "per_semantic": per_semantic,
        "divergences": divergences,
        "structural_asymmetries": structural,
        "undemonstrated_reachability_claims": red,
        "verdict": (
            "FIXTURE CAN DIVERGE" if divergences else "NULL STILL ENTAILED -- no divergence measured"
        ),
    }


def _composition_for(compositions: dict[str, Any], column: str) -> int | None:
    """How many distinct compositions this arm ran behind `column`.

    `measured_compositions` is now keyed BY COLUMN, so this is a lookup rather
    than a prefix match. `None` means the column does not exist on this arm --
    a name nobody could ask, never a zero and never a one.
    """
    record = compositions.get(column)
    return None if record is None else record["distinct_compositions"]


def render(result: dict[str, Any]) -> str:
    lines = [f"VERDICT: {result['verdict']}", ""]
    lines.append(
        "COMPOSITIONS PER ARM PER COLUMN (measured from the runs, not read from a mapping).\n"
        "Only a SWAPPED column can be arm-specific; an unswapped one runs the tree as the\n"
        "program composes it and is one composition everywhere by construction:"
    )
    for arm, record in sorted(result["compositions_per_arm"].items()):
        for column, figures in sorted(record.items()):
            if figures.get("substitutes_for") is None:
                continue
            count = figures["distinct_compositions"]
            shown = "ABSENT" if count is None else f"{count} composition(s)"
            lines.append(f"  {arm:7s} {column:24s} {shown:17s} -- {figures['why']}")
    lines.append("")
    lines.append("REACHABILITY, per column:")
    for column, record in sorted(result["reachability"].items()):
        lines.append(
            f"  {record['verdict']:38s} {column:24s} "
            f"compositions={record['compositions_per_arm']} "
            f"demonstrated={record['demonstrated_divergences']}"
        )
    lines.append("")
    if result["divergences"]:
        lines.append("DEMONSTRATED DIVERGENCES (comparable row only -- the one the default")
        lines.append("composition wires on each arm):")
        for record in result["divergences"]:
            lines.append(f"  {record['semantic']} / {record['column']}")
            for arm, verdict in record["per_arm"].items():
                lines.append(
                    f"      {arm}: {verdict:9s} via {record['compared_rows'][arm]}   "
                    f"(compositions={record['compositions_per_arm'][arm]})"
                )
    else:
        lines.append("NO DIVERGENCE MEASURED. The null is still entailed and that is the report.")
    if result["structural_asymmetries"]:
        lines.append("")
        lines.append("STRUCTURAL ASYMMETRIES:")
        for record in result["structural_asymmetries"]:
            if record["kind"] == "unequal homes for one semantic":
                lines.append(
                    f"  {record['semantic']}: homes {record['homes_per_arm']}; "
                    f"no counterpart anywhere for {record['rows_with_no_counterpart']}"
                )
            else:
                lines.append(
                    f"  column {record['column']} exists on {record['present_on_arms']} "
                    f"and CANNOT exist on {record['absent_on_arms']}"
                )
    if result["undemonstrated_reachability_claims"]:
        lines.append("")
        lines.append(
            "RED -- reachability CLAIMED and NOT DEMONSTRATED on: "
            + ", ".join(result["undemonstrated_reachability_claims"])
            + ". R1: an instrument ships with a demonstrated failing input, and a "
            "reachability analysis that cannot be contradicted by its own run is the "
            "next unfalsifiable instrument."
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", action="append", required=True, metavar="ARM=REPORT.json",
        help="one per arm; the catalogue is taken from --catalogue with the same arm",
    )
    parser.add_argument(
        "--catalogue", action="append", required=True, metavar="ARM=CATALOGUE.toml",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    reports = dict(item.split("=", 1) for item in args.run)
    catalogues = dict(item.split("=", 1) for item in args.catalogue)
    if set(reports) != set(catalogues):
        parser.error(f"arms disagree: runs {sorted(reports)} vs catalogues {sorted(catalogues)}")

    runs = {arm: (Path(reports[arm]), Path(catalogues[arm])) for arm in reports}
    result = build(runs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(render(result))
    print(f"\nwrote {args.out}")
    return 1 if result["undemonstrated_reachability_claims"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
