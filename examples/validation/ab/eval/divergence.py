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


def measured_compositions(report: dict[str, Any]) -> dict[str, Any]:
    """How many DISTINCT compositions this arm's swap columns actually ran.

    Not read from the mapping file. Two columns whose evidence block is
    byte-identical on the unmutated tree AND on every mutated row ran the same
    program twice, whatever their names say. `AD-F6` measured this by hand for
    arms A and C; here it is the run deciding it.
    """
    pairs: dict[str, Any] = {}
    columns = report["instruments"]
    real = [name for name in columns if name.endswith(":real")]
    for real_name in real:
        fake_name = real_name[: -len(":real")] + ":fake"
        if fake_name not in columns:
            continue
        rows = report["per_mutant"]
        identical = all(
            {key: rows[row]["evidence"][real_name].get(key) for key in EVIDENCE_KEYS}
            == {key: rows[row]["evidence"][fake_name].get(key) for key in EVIDENCE_KEYS}
            for row in rows
        )
        pairs[real_name[: -len(":real")]] = {
            "columns": [real_name, fake_name],
            "rows_compared": len(rows),
            "evidence_identical_on_every_row": identical,
            "distinct_compositions": 1 if identical else 2,
            "why": (
                "byte-identical evidence on every row: the two wirings ran the same "
                "program, so this arm has ONE composition of the port"
                if identical
                else "the two wirings differ on at least one row: this arm has TWO "
                "distinct compositions of the port"
            ),
        }
    # The suite pair is decided the same way, but its absence is also a fact.
    suite_real = "suite-real" in columns
    suite_fake = "suite-fake" in columns
    pairs["suite"] = {
        "columns": [name for name in ("suite-real", "suite-fake") if name in columns],
        "rows_compared": len(report["per_mutant"]),
        "evidence_identical_on_every_row": None if not (suite_real and suite_fake) else all(
            report["per_mutant"][row]["cells"]["suite-real"]
            == report["per_mutant"][row]["cells"]["suite-fake"]
            for row in report["per_mutant"]
        ),
        "distinct_compositions": 2 if (suite_real and suite_fake) else 1,
        "why": (
            "two composition points declared for the hand-written suite"
            if (suite_real and suite_fake)
            else "no second composition point exists on this arm, so no `suite-fake` "
            "column was declared. Declaring one would silently re-run `suite-real`."
        ),
    }
    return pairs


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

        # A DIVERGENCE is two arms giving different answers to the same column
        # about the same semantic. Where an arm has more than one home, the row
        # that the DEFAULT COMPOSITION wires is the comparable one -- the others
        # have no counterpart and are reported separately below.
        for column in all_columns:
            answers: dict[str, set[str]] = {}
            for arm, rows in cells.items():
                verdicts = {
                    verdict[column]
                    for verdict in rows.values()
                    if verdict[column] != NOT_APPLICABLE
                }
                if verdicts:
                    answers[arm] = verdicts
            distinct = {frozenset(v) for v in answers.values()}
            if len(distinct) > 1:
                divergences.append({
                    "semantic": key,
                    "column": column,
                    "per_arm": {arm: sorted(v) for arm, v in sorted(answers.items())},
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
                "semantic": key,
                "homes_per_arm": homes,
                "why": (
                    "the arms do not agree on how many places this semantic can live. "
                    "An arm with fewer homes cannot host the extra rows at all, and "
                    "inventing a nearest-bytes stand-in there is the re-anchoring "
                    "artefact PA-06-DF-08 is about."
                ),
            })

    reachability: dict[str, Any] = {}
    for column in all_columns:
        counts = {
            arm: _composition_for(arms[arm]["compositions"], column) for arm in arms
        }
        present = {arm for arm, data in arms.items() if column in data["report"]["instruments"]}
        differing = len(set(counts.values())) > 1 or present != set(arms)
        demonstrated = [d for d in divergences if d["column"] == column]
        if differing:
            verdict = "REACHABLE" if demonstrated else "CLAIMED_REACHABLE_BUT_UNDEMONSTRATED"
            why = (
                "the arms differ in how many distinct compositions this column runs, "
                "or the column does not exist on every arm. E1 fails: the instrument "
                "is a function of the arm's architecture."
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
    for prefix, record in compositions.items():
        if column == prefix or column.startswith(prefix + ":"):
            return record["distinct_compositions"]
    return None


def render(result: dict[str, Any]) -> str:
    lines = [f"VERDICT: {result['verdict']}", ""]
    lines.append("COMPOSITIONS PER ARM (measured from the runs, not read from a mapping):")
    for arm, record in sorted(result["compositions_per_arm"].items()):
        for prefix, figures in sorted(record.items()):
            lines.append(
                f"  {arm:7s} {prefix:22s} {figures['distinct_compositions']} composition(s) "
                f"-- {figures['why']}"
            )
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
        lines.append("DEMONSTRATED DIVERGENCES:")
        for record in result["divergences"]:
            lines.append(f"  {record['semantic']} / {record['column']}")
            for arm, verdicts in record["per_arm"].items():
                lines.append(
                    f"      {arm}: {', '.join(verdicts)}   "
                    f"(compositions={record['compositions_per_arm'][arm]})"
                )
    else:
        lines.append("NO DIVERGENCE MEASURED. The null is still entailed and that is the report.")
    if result["structural_asymmetries"]:
        lines.append("")
        lines.append("STRUCTURAL ASYMMETRIES (a semantic with different numbers of homes):")
        for record in result["structural_asymmetries"]:
            lines.append(f"  {record['semantic']}: homes {record['homes_per_arm']}")
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
