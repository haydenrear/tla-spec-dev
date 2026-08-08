#!/usr/bin/env python3
"""Removal census: what a removal cost to prove safe, priced PER REMOVAL.

    python3 examples/validation/removal_census/removal_census.py census
    python3 examples/validation/removal_census/removal_census.py check
    python3 examples/validation/removal_census/removal_census.py discriminate

WHY THIS FILE EXISTS
--------------------

`subtract-to-measure` set out to simplify and came out **net +1677 code_lines**,
because every removal shipped new instruments, new tests and new demonstrations
to prove the removal was safe. Nobody counted that as a cost, and the epic
called itself the great simplification throughout.

This file counts it. Per removal: **lines removed, lines added to prove it
safe, and the ratio.**

WHAT IT IS NOT
--------------

**Not a gate.** Nothing invokes it on a close path and its exit code refuses
nothing about the design. It exits non-zero for exactly three reasons, all of
them about the CENSUS being wrong rather than the code:

  1. a declared region no longer measures what the manifest recorded (`check`),
  2. a removal declares neither a gap mutant nor a reason it has none, and
  3. **somebody asked it for a total.**

(3) IS THE POINT AND IT IS DELIBERATE. A total over removals hides which
removals paid for themselves; `subtract-to-measure`'s one published figure was
a total and it is the reason this ticket exists. `--total` is accepted by the
parser only so that it can be REFUSED with a reason.

THE DENOMINATOR RULE IS WIRED IN
--------------------------------

`denominator_rule`: if a count moves, say whether the numerator rose or the
denominator fell. A removal's denominator -- "lines removed" -- is trivially
inflatable by counting the removed mechanism's own test file, which is real
deletion but is not the mechanism. So every removal reports **two** cut figures,
`cut_production` and `cut_tests`, and **two** ratios. A single ratio over their
sum is not emitted, because the two are not the same claim.

EVERY FIGURE CARRIES ITS SCOPE (R3)
-----------------------------------

No row prints a number without the commit range and the path it was measured
over. `scope` is a field of the record, not a sentence in a report someone may
quote without it.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tomllib
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
DEFAULT_MANIFEST = HERE / "removals.toml"

EXIT_OK = 0
EXIT_REFUSED = 2

ROLES = ("cut_production", "cut_tests", "cut_prose", "replacement", "proof")
CUT_ROLES = ("cut_production", "cut_tests", "cut_prose")


class CensusRefusal(Exception):
    """The census cannot be produced honestly. Never a verdict about the code."""


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------


def git(*args: str, root: pathlib.Path = REPO_ROOT) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise CensusRefusal(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def diff_lines(base: str, head: str, path: str, pattern: str | None) -> tuple[int, int]:
    """Added and deleted lines for one path, optionally filtered by a regex.

    `-U0` so context never counts. The regex, when given, is applied to the
    diff line itself, which is how a removal embedded in a larger commit is
    attributed without hand-copying numbers into the manifest.
    """

    out = git("diff", "-U0", f"{base}", f"{head}", "--", path)
    rx = re.compile(pattern) if pattern else None
    added = deleted = 0
    for line in out.split("\n"):
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith("+"):
            if rx is None or rx.search(line[1:]):
                added += 1
        elif line.startswith("-"):
            if rx is None or rx.search(line[1:]):
                deleted += 1
    return added, deleted


def span_lines(commit: str, path: str, start: str, end: str) -> int:
    """Lines from the first line containing `start` up to but NOT including the
    first later line containing `end`, in `path` at `commit`.

    Markers rather than line numbers, so a manifest does not rot the first time
    anything above the region moves. Half-open because the natural end marker
    for a region is the first line of the NEXT one; a region therefore carries
    whatever blank or banner lines trail it, which is stated here rather than
    silently absorbed.
    """

    text = git("show", f"{commit}:{path}").split("\n")
    first = next((i for i, line in enumerate(text) if start in line), None)
    if first is None:
        raise CensusRefusal(f"start marker {start!r} not in {path} at {commit}")
    last = next((i for i in range(first + 1, len(text)) if end in text[i]), None)
    if last is None:
        raise CensusRefusal(f"end marker {end!r} not in {path} at {commit} after {start!r}")
    return last - first


# --------------------------------------------------------------------------
# measuring a declared region
# --------------------------------------------------------------------------


def measure_region(region: dict, removal: dict) -> dict:
    kind = region["kind"]
    base = region.get("base", removal.get("base"))
    head = region.get("head", removal.get("head"))
    if region["role"] not in ROLES:
        raise CensusRefusal(f"unknown role {region['role']!r}; roles are {ROLES}")

    if kind == "diff":
        added, deleted = diff_lines(base, head, region["path"], region.get("match"))
        count = added if region["count"] == "added" else deleted
        scope = f"git diff -U0 {base}..{head} -- {region['path']}"
        if region.get("match"):
            scope += f" | lines matching /{region['match']}/"
        scope += f" | {region['count']} only"
    elif kind == "span":
        commit = region.get("commit", base)
        count = span_lines(commit, region["path"], region["start"], region["end"])
        scope = (
            f"{region['path']}@{commit} lines {region['start']!r}..{region['end']!r} inclusive"
        )
    else:
        raise CensusRefusal(f"unknown region kind {kind!r}")

    return {
        "role": region["role"],
        "lines": count,
        "scope": scope,
        "reason": region["reason"],
    }


def measure_removal(removal: dict) -> dict:
    if not removal.get("gap_mutants") and not removal.get("no_gap_reason"):
        raise CensusRefusal(
            f"{removal['id']}: declares no gap mutant and no reason it has none. "
            "`removal_is_a_delta_rule`: a removal with no mutant in its gap is not a "
            "measurement, and four such removals were NAMED rather than omitted last "
            "epic. Name this one too."
        )

    regions = [measure_region(r, removal) for r in removal.get("region", [])]
    by_role = {role: sum(r["lines"] for r in regions if r["role"] == role) for role in ROLES}
    cut_all = sum(by_role[role] for role in CUT_ROLES)

    def ratio(denominator: int) -> float | None:
        return round(by_role["proof"] / denominator, 2) if denominator else None

    return {
        "id": removal["id"],
        "ticket": removal["ticket"],
        "name": removal["name"],
        "scope": f"{removal['base']}..{removal['head']}",
        "gap_mutants": removal.get("gap_mutants", []),
        "no_gap_reason": removal.get("no_gap_reason"),
        "deletes_detectors": removal.get("deletes_detectors", []),
        "lines": by_role,
        "cut_all": cut_all,
        "ratio_proof_over_production": ratio(by_role["cut_production"]),
        "ratio_proof_over_all_cut": ratio(cut_all),
        "regions": regions,
    }


# --------------------------------------------------------------------------
# discriminating power -- could the after re-run have said anything?
# --------------------------------------------------------------------------


def discriminating(before: dict, mutant_id: str, deleted_detectors: list[str]) -> dict:
    """Could this mutant have gone DIES -> SURVIVES when the removal landed?

    A mutant can only report that a removal cost something if EVERY detector
    that killed it is a detector the removal deletes. If one surviving detector
    already kills it, the after-verdict is entailed by the before-table and the
    re-run measures nothing about the removal.

    Reported per mutant, never averaged.
    """

    record = before["per_mutant"].get(mutant_id)
    if record is None:
        return {"mutant": mutant_id, "verdict": "NOT-IN-TABLE"}
    kills = sorted(
        did for did, cell in record.get("detectors", {}).items()
        if cell.get("verdict") == "DIES"
    )
    if not kills:
        return {
            "mutant": mutant_id, "kills_before": [], "verdict": "NO-KILL-TO-LOSE",
            "why": "it survived every detector before the cut, so it can only move upward",
        }
    surviving = [d for d in kills if d not in deleted_detectors]
    if surviving:
        return {
            "mutant": mutant_id, "kills_before": kills, "kills_that_outlive": surviving,
            "verdict": "NON-DISCRIMINATING",
            "why": (
                "killed by a detector the removal does not touch, so DIES after the cut "
                "was entailed before the cut was made"
            ),
        }
    return {
        "mutant": mutant_id, "kills_before": kills, "kills_that_outlive": [],
        "verdict": "DISCRIMINATING",
        "why": "every kill depends on code the removal deletes; the re-run could say something",
    }


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def render(rows: list[dict]) -> str:
    out = [
        "| removal | ticket | scope | cut (production) | cut (its own tests) | cut (prose) "
        "| replacement | **proof** | proof / production | proof / all cut |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines = row["lines"]
        out.append(
            f"| `{row['id']}` | {row['ticket']} | `{row['scope']}` "
            f"| {lines['cut_production']} | {lines['cut_tests']} | {lines['cut_prose']} "
            f"| {lines['replacement']} | **{lines['proof']}** "
            f"| {row['ratio_proof_over_production'] if row['ratio_proof_over_production'] is not None else '—'} "
            f"| {row['ratio_proof_over_all_cut'] if row['ratio_proof_over_all_cut'] is not None else '—'} |"
        )
    out.append("")
    out.append(
        "**No total row, and there will not be one.** A total over removals hides which "
        "removals paid for themselves, which is the defect this census exists to correct."
    )
    return "\n".join(out)


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------


def load_manifest(path: pathlib.Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def cmd_census(args) -> int:
    manifest = load_manifest(args.manifest)
    if args.total or manifest.get("report_total"):
        raise CensusRefusal(
            "REFUSED: this census does not emit a total over removals. A total is what "
            "`subtract-to-measure` reported (-225 lines from scripts/) and it was true "
            "and it hid that the same epic added 1677 net across the trees it touched. "
            "Read the rows."
        )
    rows = [measure_removal(r) for r in manifest["removal"]]
    shared = []
    for entry in manifest.get("shared_apparatus", []):
        measured = measure_region({**entry, "role": "proof"}, entry)
        shared.append({**measured, "id": entry["id"], "serves": entry["serves"],
                       "reason": entry["reason"]})
    payload = {
        "schema_version": manifest["schema_version"],
        "measured_at": git("rev-parse", "HEAD").strip(),
        "instrument": "examples/validation/removal_census/removal_census.py",
        "removals": rows,
        "shared_apparatus": shared,
        "shared_apparatus_note": (
            "NOT allocated to any removal. Splitting a shared runner across the removals "
            "it serves would require a weighting the data does not supply, and an invented "
            "weighting is how a per-removal figure becomes a total in disguise."
        ),
    }
    if args.json:
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(render(rows))
    if shared:
        print()
        print("**Shared apparatus, unallocated** — serves more than one removal:")
        print()
        print("| apparatus | lines | serves | scope |")
        print("|---|---|---|---|")
        for entry in shared:
            print(f"| `{entry['id']}` | {entry['lines']} | "
                  f"{', '.join(entry['serves'])} | `{entry['scope']}` |")
    return EXIT_OK


def cmd_check(args) -> int:
    """Re-measure every declared region and compare to what the manifest recorded.

    A census whose manifest can drift from the tree is a census that reports
    whatever its author last believed.
    """

    manifest = load_manifest(args.manifest)
    problems: list[str] = []
    for removal in manifest["removal"]:
        for region in removal.get("region", []):
            expected = region.get("expect_lines")
            if expected is None:
                problems.append(
                    f"{removal['id']}: region {region.get('path')} declares no `expect_lines`"
                )
                continue
            measured = measure_region(region, removal)["lines"]
            if measured != expected:
                problems.append(
                    f"{removal['id']}: {region['path']} ({region['role']}) measures "
                    f"{measured}, manifest says {expected}"
                )
    for entry in manifest.get("shared_apparatus", []):
        measured = measure_region({**entry, "role": "proof"}, entry)["lines"]
        if measured != entry.get("expect_lines"):
            problems.append(
                f"{entry['id']}: measures {measured}, manifest says {entry.get('expect_lines')}"
            )
    if problems:
        for problem in problems:
            print(f"CENSUS-DRIFT: {problem}", file=sys.stderr)
        print(f"\n{len(problems)} declared region(s) no longer measure what the manifest "
              f"recorded.", file=sys.stderr)
        return EXIT_REFUSED
    print("every declared region measures what the manifest recorded")
    return EXIT_OK


def cmd_discriminate(args) -> int:
    manifest = load_manifest(args.manifest)
    before = json.loads(pathlib.Path(manifest["gap_mutant_before_table"]).read_text())
    print("| removal | mutant | kills before the cut | kills that outlive it | verdict |")
    print("|---|---|---|---|---|")
    rows: list[dict] = []
    for removal in manifest["removal"]:
        deleted = removal.get("deletes_detectors", [])
        for mutant in removal.get("gap_mutants", []):
            row = discriminating(before, mutant, deleted)
            row["removal"] = removal["id"]
            rows.append(row)
            short = mutant.split("-", 3)
            print(
                f"| `{removal['id']}` | `{'-'.join(short[:3])}` "
                f"| {', '.join(row.get('kills_before', [])) or '—'} "
                f"| {', '.join(row.get('kills_that_outlive', [])) or '—'} "
                f"| **{row['verdict']}** |"
            )
    if args.json:
        args.json.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    n = sum(1 for r in rows if r["verdict"] == "DISCRIMINATING")
    print()
    print(f"**{n} of {len(rows)}** mutants in this table could have gone `DIES` -> `SURVIVES`. "
          f"Scope: the mutants declared in `{args.manifest.name}` against the before-table at "
          f"`{manifest['gap_mutant_before_table']}`. It is NOT a statement about every mutant "
          f"ever seeded under `removal_is_a_delta_rule` -- see the manifest's "
          f"`[[mutant_outside_this_table]]` rows, which are counted separately and not here.")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=pathlib.Path, default=DEFAULT_MANIFEST)
    sub = parser.add_subparsers(dest="command", required=True)

    census = sub.add_parser("census", help="per-removal cost table")
    census.add_argument("--json", type=pathlib.Path)
    census.add_argument(
        "--total", action="store_true",
        help="REFUSED. Accepted by the parser so the refusal has somewhere to happen.",
    )
    census.set_defaults(func=cmd_census)

    check = sub.add_parser("check", help="re-measure every region against the manifest")
    check.set_defaults(func=cmd_check)

    disc = sub.add_parser("discriminate", help="which mutants could have priced a removal")
    disc.add_argument("--json", type=pathlib.Path)
    disc.set_defaults(func=cmd_discriminate)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CensusRefusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
