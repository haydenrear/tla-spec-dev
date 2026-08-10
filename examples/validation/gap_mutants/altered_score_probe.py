#!/usr/bin/env python3
"""SM-04-GM-T1, reproduced by something that is not SM-04-GM-T1.

    python3 examples/validation/gap_mutants/altered_score_probe.py --tree <staged tree>

WHAT IT ASKS
============

**A dimension score is altered in a scorecard after the card was written, and
nothing else is touched. Does the repository notice?**

That is the fault `SM-04` seeded when it removed `total`, a checksum over the
five dimension scores. It is the ONLY mutant in this project's history that
went `DIES` -> `SURVIVES`: on an unsealed card the arithmetic was the only
thing that noticed, and `total` was the arithmetic.

WHY A SECOND IMPLEMENTATION
===========================

`SM-04-GM-T1` lives inside `tests/test_score_tools.py` as an assertion, and it
reads before and after **in one process at one commit** by scaffolding a
version 2 card and a version 3 card side by side. That is a fine design and it
is the reason it worked. It also means the finding has only ever been produced
by the file that asserts it, using that file's own helpers.

This probe drives the tree's **shipped CLI** -- `scaffold` then `check` --
imports nothing from the test suite, and works against a staged tree at any
ref. So the before/after can be read from `6aac1ec~1` and `6aac1ec`
themselves, which is a replication rather than a re-reading.

HOW A KILL IS DECIDED
=====================

By SUBTRACTION, the same rule `run_gap_mutants.py` uses. `check` is run twice
against the same card, once unaltered and once with `D3` moved, and the kill is
the set of problems the second run reports that the first did not. A scaffolded
card that is already unclean therefore decides nothing by being unclean --
which matters, because the two trees do not agree about what a clean card is.

NOT A GATE. Nothing invokes it. It exits 2 if the tree's own `scaffold` refused
(so a broken setup cannot read as `UNCAUGHT`), 0 otherwise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(tree: Path, argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(tree / "examples/validation/scorecards/score_tools.py"), *argv],
        cwd=str(tree), capture_output=True, text=True,
    )


def problems(tree: Path, card_path: Path) -> set[str]:
    """Every `INVALID ...` line `check` prints, with the path stripped off."""
    done = run(tree, ["check", str(card_path)])
    found = set()
    for line in (done.stdout + done.stderr).splitlines():
        if line.startswith("INVALID "):
            found.add(line[len("INVALID "):].replace(str(card_path), "<card>").strip())
    return found


def fill(card: dict) -> dict:
    """Fill a scaffolded skeleton enough that `check` will look at its scores.

    Version-agnostic on purpose: it reads `scorecard_version` off the card the
    tree produced rather than being told which tree it is in. `total` is
    written only where the card carries one, because writing it on a version 3
    card is itself a refusal and would make the probe measure its own mistake.
    """
    version = card.get("scorecard_version", 1)
    card["status"] = "filled"
    card["commit"] = "0123456"
    card["judge"]["model"] = "claude-opus-5[1m]"
    card["verdict"] = "a verdict"
    if version >= 2:
        card["judging_practice"] = {
            "executed_own_faults": True,
            "what_was_run": ["seeded a fault in commit() and ran the suite"],
        }
    running = 0
    for dim in ("D1", "D2", "D3", "D4", "D5"):
        entry = card["dimensions"][dim]
        # D3 is the dimension that moves, and it starts HIGH and moves DOWN --
        # the same direction SM-04-GM-T1 uses, and the reason is a confound the
        # first version of this probe walked into and is recorded rather than
        # quietly fixed. Scoring D3 at 1 and raising it to 3 makes `check`
        # report `D3 scored 3 with NO citation -- rule 2 caps it at 1` at BOTH
        # trees, so the probe reads CAUGHT everywhere and the reason has
        # nothing to do with the checksum. Starting at 4 with a citation and
        # dropping to 2 leaves the citation rule satisfied at both ends, so the
        # ONLY thing that changes is the score and the sum over the scores.
        # Artifact of the confounded run: `sm04-gm-t1-*-confounded.json`.
        if dim == "D3":
            entry["score"] = 4
            entry["citations"] = ["quota_ledger/domain.py:22-43"]
            entry["refuses_to_claim"] = (
                "that anything but the durable side is behind a port"
            )
        else:
            entry["score"] = 1
        entry["rationale"] = "because the artifact says so and I ran it"
        running += entry["score"]
    if version < 3:
        card["total"] = running
    else:
        card.pop("total", None)
    return card


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    tree = args.tree.resolve()
    epic = tree / "specs/results/scorecards/rm01-probe"
    done = run(tree, [
        "scaffold", str(epic), "--example", "ab_quota_ledger", "--arms", "A",
        "--judges", "1", "--labels", "K", "--run-date", "20260101", "--run-tag", "rm01",
    ])
    if done.returncode != 0:
        print("REFUSED: the tree's own scaffold did not produce a card. "
              "Nothing here may be read as UNCAUGHT.", file=sys.stderr)
        print(done.stdout + done.stderr, file=sys.stderr)
        return 2

    cards = sorted(epic.rglob("scorecard.json"))
    if len(cards) != 1:
        print(f"REFUSED: scaffold produced {len(cards)} cards, want 1", file=sys.stderr)
        return 2
    card_path = cards[0]

    card = fill(json.loads(card_path.read_text(encoding="utf-8")))
    version = card.get("scorecard_version", 1)
    card_path.write_text(json.dumps(card, indent=2), encoding="utf-8")
    baseline = problems(tree, card_path)

    # THE FAULT: one dimension score moves and nothing else in the card does.
    # Not the sum, not a rationale, not a citation -- exactly what a hand edit
    # to a written card looks like.
    card["dimensions"]["D3"]["score"] = 2
    card_path.write_text(json.dumps(card, indent=2), encoding="utf-8")
    observed = problems(tree, card_path)

    new = sorted(observed - baseline)
    report = {
        "tree": str(tree),
        "scorecard_version": version,
        "baseline_problems": sorted(baseline),
        "problems_after_the_alteration": sorted(observed),
        "new_problems": new,
        "verdict": "CAUGHT" if new else "UNCAUGHT",
    }
    print(f"scorecard_version {version}: {report['verdict']}")
    for line in new:
        print(f"  new problem: {line}")
    if not new:
        print("  nothing in this tree reports a dimension score altered after the "
              "card was written, on an unsealed card.")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
