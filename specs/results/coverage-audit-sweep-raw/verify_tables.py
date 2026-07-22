#!/usr/bin/env python3
"""Dependency-free structural verifier for this coverage-audit evidence.

This script verifies enumeration/accounting, formal verdict vocabularies, and
the total mapping from every scoped gap row to a disposition ID. It deliberately
does not infer semantic classifications: those remain the auditor's review
judgment recorded in the formal TSVs and report.
"""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent

EFFECT_COLLAPSED = {
    "clock": {105},
    "environment": set(),
    "filesystem": {224, 233, 234, 235, 419, 420, 423, 424},
    "network": {28, 29, 30, 31, 36, 37, 38},
    "notification": {35, 36, 41, 42, 45, 46, 54},
    "persistent_store": {
        94, 95, 96, 97, 98, 104, 105, 106, 107, 112,
        176, 177, 178, 179, 180, 181, 183, 184, 185, 186, 187, 189,
        191, 193, 194, 196, 197, 198, 200, 201, 203, 204, 205, 206,
    },
    "randomness": set(),
    "stdio": set(),
    "subprocess": set(),
}

BEHAVIOR_COLLAPSED = {
    "concurrency": set(),
    "config": set(),
    "errors": {284},
    "fallbacks": set(),
    "retries": set(),
    "timeouts": set(),
}

EFFECT_VERDICTS = {"declared", "undeclared", "partial"}
BEHAVIOR_VERDICTS = {"represented", "partial", "unrepresented"}
GAP_IDS = {
    "CA-01", "CA-02", "CA-03", "CA-04",
    "CH-01", "CH-02", "CH-03", "CH-04",
    "CR-01", "CR-02", "CR-03", "CR-04",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def verify_surface() -> None:
    raw = (HERE / "surface-all.txt").read_text(encoding="utf-8").splitlines()
    table = read_tsv(HERE / "program-surface-table.tsv")
    assert len(raw) == 3008 == len(table)
    assert [row["Module"] for row in table] == raw
    assert {row["Verdict"] for row in table} <= {"represented", "partial", "unrepresented"}
    for row in table:
        if row["In/Out"] == "in-scope" and row["Verdict"] in {"partial", "unrepresented"}:
            assert row["Disposition gap IDs"]


def verify_category(kind: str, collapsed_by_category: dict[str, set[int]]) -> None:
    verdicts = EFFECT_VERDICTS if kind == "effect" else BEHAVIOR_VERDICTS
    for category, collapsed in sorted(collapsed_by_category.items()):
        raw_path = HERE / f"{kind}-{category}.txt"
        table_path = HERE / f"{kind}-{category}-table.tsv"
        raw = raw_path.read_text(encoding="utf-8").splitlines()
        table = read_tsv(table_path)
        expected_indices = [index for index in range(1, len(raw) + 1) if index not in collapsed]
        actual_indices = [int(row["#"]) for row in table]
        assert actual_indices == expected_indices, (kind, category, len(raw), len(table))
        assert {row["Verdict"] for row in table} <= verdicts
        for row in table:
            if row["Classification"] == "excluded_mutant_behavior":
                assert row["In/Out"] == "out-of-scope behavior"
                assert row["Disposition gap ID"] == ""
            is_gap = row["In/Out"] == "in-scope" and row["Verdict"] in (
                {"partial", "undeclared"} if kind == "effect" else {"partial", "unrepresented"}
            )
            if is_gap:
                assert row["Disposition gap ID"] in GAP_IDS, (kind, category, row)


def derived_gap_rows() -> list[tuple[str, str, str, str, str]]:
    derived: list[tuple[str, str, str, str, str]] = []
    for row in read_tsv(HERE / "program-surface-table.tsv"):
        if row["In/Out"] != "in-scope" or row["Verdict"] not in {"partial", "unrepresented"}:
            continue
        for gap in row["Disposition gap IDs"].split(","):
            derived.append(("program-surface-table.tsv", row["#"], row["Module"], row["Verdict"], gap))
    for table_path in sorted(HERE.glob("effect-*-table.tsv")):
        for row in read_tsv(table_path):
            if row["In/Out"] == "in-scope" and row["Verdict"] in {"partial", "undeclared"}:
                derived.append((table_path.name, row["#"], row["Site"], row["Verdict"], row["Disposition gap ID"]))
    for table_path in sorted(HERE.glob("behavior-*-table.tsv")):
        for row in read_tsv(table_path):
            if row["In/Out"] == "in-scope" and row["Verdict"] in {"partial", "unrepresented"}:
                derived.append((table_path.name, row["#"], row["Trigger"], row["Verdict"], row["Disposition gap ID"]))
    return derived


def verify_gap_map() -> None:
    recorded = read_tsv(HERE / "gap-disposition-map.tsv")
    recorded_tuples = [
        (row["Source table"], row["Source row"], row["Surface/site/trigger"], row["Verdict"], row["Disposition gap ID"])
        for row in recorded
    ]
    derived = derived_gap_rows()
    assert recorded_tuples == derived
    assert len(derived) == 124
    assert {row[-1] for row in derived} == GAP_IDS


def verify_report() -> None:
    report = (RESULTS / "coverage_audit_report.md").read_text(encoding="utf-8")
    assert "@@SCOPE@@" not in report and "@@SURFACE_ROWS@@" not in report
    assert "- **Verdict:** `FAIL`" in report
    assert "- In-scope hard gaps: **12**" in report
    surface_section = report.split("| # | Module | In/Out", 1)[1].split("### Sweep-1 result", 1)[0]
    data_rows = [line for line in surface_section.splitlines() if line.startswith("| ")]
    assert len(data_rows) == 3008
    expected_rows = []
    for row in read_tsv(HERE / "program-surface-table.tsv"):
        values = [
            row["#"], row["Module"], row["In/Out"], row["Plan line"],
            row["Spec action(s)"], row["Verdict"], row["Evidence"],
            row["Disposition gap IDs"],
        ]
        expected_rows.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    assert data_rows == expected_rows

    quoted_scope = report.split(
        "# specs/desired_program_model/ticket_plan.yaml:538-663\n", 1
    )[1].split("\n```", 1)[0]
    plan_lines = (RESULTS.parent / "desired_program_model/ticket_plan.yaml").read_text(
        encoding="utf-8"
    ).splitlines()
    assert quoted_scope == "\n".join(plan_lines[537:663])


def main() -> None:
    verify_surface()
    verify_category("effect", EFFECT_COLLAPSED)
    verify_category("behavior", BEHAVIOR_COLLAPSED)
    verify_gap_map()
    verify_report()
    print("coverage audit evidence: PASS (structural verification of recorded FAIL verdict)")


if __name__ == "__main__":
    main()
