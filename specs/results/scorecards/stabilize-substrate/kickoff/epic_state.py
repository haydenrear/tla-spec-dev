#!/usr/bin/env python3
"""Compute the epic's own figures FROM THE REPOSITORY, at a named tree.

    uv run --with pyyaml python3 \
      specs/results/scorecards/stabilize-substrate/kickoff/epic_state.py [--json]

WHY THIS EXISTS. This epic's most repeated result is that a figure produced by
running a command re-derives, and a figure transcribed by hand into a second
document drifts. Measured on this epic: SS-04's `FINAL-FIGURES.txt` -- the file
it declared authoritative -- published a six-row table summing to 2,483 against
its own stated 2,496, while the sealed command output beside it was correct;
`instruments.toml`'s row, REWRITTEN TO CORRECT STALE FIGURES, shipped a fresh set
of stale ones; and the owner's own charter carried a cross-tab it had never run.

So the owner's status artifact is GENERATED. Nothing here is typed twice.

WHAT THIS IS NOT. It is not a gate, it decides no goal, and nothing consults it.
It exits 0 on every input including a tree with no epic at all. It reads; it
writes nothing. Every figure it prints carries the tree it was measured on,
because SS-01-DF-03 established that a figure is a joint property of the artifact
AND the tree it was measured in.

It REFUSES rather than guesses: an absent ledger, an unreadable plan or a plan
declaring no tickets is reported as UNDECIDED for that section, never as a zero.
An empty count and an unread count are different answers -- that is the class the
epic exists to close, and this script is an instrument like any other.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - reported, never guessed
    yaml = None

# parents: 0=kickoff 1=stabilize-substrate 2=scorecards 3=results 4=specs 5=repo.
# The first draft said [4] and resolved to `specs/`, so both loads missed. THE
# SCRIPT ANSWERED `UNDECIDED -- absent`, NOT ZERO, which is the whole point of it
# and is why the mistake was visible in one run instead of publishing 0 findings.
REPO = pathlib.Path(__file__).resolve().parents[5]
LEDGER = REPO / "specs/deferred_findings.yaml"
PLAN = REPO / "specs/desired_program_model/ticket_plan.yaml"
# 296 is the INHERITED count -- the closed cut-the-apparatus snapshot, moved
# byte-identical at kickoff. The kickoff RESULT quotes 299, which is the count
# AFTER the owner filed SS-00-DF-01/02/03, so it already contains three of this
# epic's own rows. The first draft of this script used 299 and printed
# `added_by_this_epic 36` beside `rows_with_ss_ids 39` -- two figures for one
# quantity, differing by exactly the rows the wrong base absorbed. The identity
# below is asserted rather than left for a reader to notice.
EPIC_INHERITED_LEDGER_ROWS = 296
TICKET_RE = re.compile(r"^(SS-\d+)-DF-\d+$")


def tree() -> dict:
    def git(*a: str) -> str | None:
        try:
            return subprocess.run(("git", "-C", str(REPO)) + a, capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            return None
    head = git("rev-parse", "HEAD")
    return {
        "head": head[:7] if head else None,
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
    }


def load(path: pathlib.Path) -> tuple[dict | None, str]:
    """(data, why). `None` means NOT READ -- never confused with read-and-empty."""
    if yaml is None:
        return None, "pyyaml is not importable in this interpreter"
    if not path.exists():
        return None, f"absent: {path.relative_to(REPO)}"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"unreadable: {type(exc).__name__}"
    if data is None:
        return None, "parsed to nothing"
    return data, "read"


def findings() -> dict:
    data, why = load(LEDGER)
    if data is None:
        return {"undecided": why}
    rows = data.get("findings")
    if rows is None:
        return {"undecided": "no `findings` key"}
    mine = [r for r in rows if TICKET_RE.match(str(r.get("id", "")))]
    reviewer = [r for r in mine
                if "review" in str(r.get("found_by", "")).lower()]
    return {
        "ledger_rows": len(rows),
        "inherited_rows": EPIC_INHERITED_LEDGER_ROWS,
        "added_by_this_epic": len(rows) - EPIC_INHERITED_LEDGER_ROWS,
        "rows_with_ss_ids": len(mine),
        "counts_agree": len(rows) - EPIC_INHERITED_LEDGER_ROWS == len(mine),
        "by_ticket": dict(sorted(collections.Counter(
            TICKET_RE.match(r["id"]).group(1) for r in mine).items())),
        "by_disposition": dict(sorted(collections.Counter(
            str(r.get("disposition")) for r in mine).items())),
        "by_severity": dict(sorted(collections.Counter(
            str(r.get("severity")) for r in mine).items())),
        "by_channel": dict(sorted(collections.Counter(
            str(r.get("channel")) for r in mine).items())),
        "found_by_independent_review": len(reviewer),
        "found_by_review_pct": round(100 * len(reviewer) / len(mine), 1) if mine else None,
    }


def schedule() -> dict:
    data, why = load(PLAN)
    if data is None:
        return {"undecided": why}
    tickets = data.get("tickets")
    if not tickets:
        return {"undecided": "the plan declares no tickets; empty is UNDECIDED, not satisfied"}
    return {
        "schedule_revision": data.get("schedule_revision"),
        "tickets": len(tickets),
        "by_status": dict(sorted(collections.Counter(
            str(t.get("status")) for t in tickets).items())),
        "goals": [g["id"] for g in data.get("epic_goals", [])],
        "closed": [t["id"] for t in tickets if t.get("status") == "closed"],
        "planned": [t["id"] for t in tickets if t.get("status") == "planned"],
    }


def merged_tickets() -> dict:
    try:
        log = subprocess.run(
            ("git", "-C", str(REPO), "log", "--oneline", "--merges", "436c78c..HEAD"),
            capture_output=True, text=True, check=True).stdout
    except Exception as exc:
        return {"undecided": f"git log failed: {type(exc).__name__}"}
    ids = sorted({m.group(1) for m in re.finditer(r"Merge (SS-\d+):", log)})
    return {"merged": ids, "count": len(ids)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    state = {"tree": tree(), "schedule": schedule(),
             "findings": findings(), "merges": merged_tickets()}

    if a.json:
        print(json.dumps(state, indent=2))
        return 0

    t = state["tree"]
    print(f"stabilize-substrate — state at {t['head']} on {t['branch']}"
          f"{'  (WORKING TREE DIRTY)' if t['dirty'] else ''}")
    print("=" * 78)
    for name, section in (("SCHEDULE", state["schedule"]),
                          ("MERGED", state["merges"]),
                          ("FINDINGS", state["findings"])):
        print(f"\n## {name}")
        if "undecided" in section:
            print(f"  UNDECIDED — {section['undecided']}")
            print("  (not zero: this section was not read, and that is a different answer)")
            continue
        for k, v in section.items():
            print(f"  {k:32} {v}")
    print("\nEvery figure above is about THIS tree. Nothing here is transcribed;")
    print("re-run rather than quote. This script decides nothing and gates nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
