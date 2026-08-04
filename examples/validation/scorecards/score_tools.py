#!/usr/bin/env python3
"""Scorecard schema check and index builder (scorecard_version 1).

Deliberately lives under examples/validation/ rather than scripts/: scripts/**
is IN MODEL per the plan's representation_scope, and eval harness is not program
surface. Putting it here keeps the model's surface unchanged.

  python3 score_tools.py check <dir-or-file>...
  python3 score_tools.py index <epic-dir>

The check enforces the rules from references/eval_scorecard.md that can be
enforced mechanically. The ones that matter -- score artifacts not claims, prose
quality is never an input -- cannot be, which is why two blind judges exist.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

VERSION = 1
DIMS = ("D1", "D2", "D3", "D4", "D5")
NAMES = {
    "D1": "bug detection",
    "D2": "complexity",
    "D3": "modularity",
    "D4": "behavior preservation",
    "D5": "honesty",
}
CITE = re.compile(r"^[^\s:]+:\d+(-\d+)?$")


def check(card: dict, where: str) -> list[str]:
    bad: list[str] = []

    def err(msg: str) -> None:
        bad.append(f"{where}: {msg}")

    if card.get("scorecard_version") != VERSION:
        err(f"scorecard_version must be {VERSION}, got {card.get('scorecard_version')!r}")
    for field in ("epic", "example", "run_id", "commit", "judge", "dimensions", "verdict"):
        if not card.get(field):
            err(f"missing required field {field!r}")
    judge = card.get("judge") or {}
    for field in ("model", "pass"):
        if field not in judge:
            err(f"judge.{field} is required")

    dims = card.get("dimensions") or {}
    missing = [d for d in DIMS if d not in dims]
    if missing:
        err(f"missing dimensions: {', '.join(missing)}")
    extra = [d for d in dims if d not in DIMS]
    if extra:
        err(f"unknown dimensions: {', '.join(extra)}")

    running = 0
    for dim in DIMS:
        entry = dims.get(dim)
        if not isinstance(entry, dict):
            continue
        score = entry.get("score")
        if not isinstance(score, int) or not 0 <= score <= 4:
            err(f"{dim} score must be an int 0-4, got {score!r}")
            continue
        running += score
        cites = entry.get("citations") or []
        # Rule 2: every score >= 2 cites file:line, or is capped at 1.
        if score >= 2:
            if not cites:
                err(f"{dim} scored {score} with NO citation -- rule 2 caps it at 1")
            for c in cites:
                if not CITE.match(str(c)):
                    err(f"{dim} citation {c!r} is not file:line or file:line-line")
        # Rule 3: a 4 must name something the artifact refuses to claim.
        if score == 4 and not entry.get("refuses_to_claim"):
            err(f"{dim} scored 4 without refuses_to_claim -- rule 3")
        if not str(entry.get("rationale") or "").strip():
            err(f"{dim} has no rationale")

    total = card.get("total")
    if total != running:
        err(f"total {total!r} does not equal the sum of dimensions ({running})")
    return bad


def load(path: pathlib.Path) -> list[tuple[pathlib.Path, dict]]:
    if path.is_file():
        return [(path, json.loads(path.read_text()))]
    return [(p, json.loads(p.read_text())) for p in sorted(path.rglob("scorecard.json"))]


def cmd_check(args: list[str]) -> int:
    cards, problems = [], []
    for arg in args:
        cards.extend(load(pathlib.Path(arg)))
    if not cards:
        print("no scorecard.json found", file=sys.stderr)
        return 2
    for path, card in cards:
        problems.extend(check(card, str(path)))
    for line in problems:
        print(f"INVALID {line}")
    print(f"{len(cards)} scorecard(s) checked, {len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_index(args: list[str]) -> int:
    root = pathlib.Path(args[0])
    cards = load(root)
    by_example: dict[str, list[dict]] = {}
    for _, card in cards:
        by_example.setdefault(card["example"], []).append(card)

    out = [f"# Scorecards — {root.name}", ""]
    out.append("scorecard_version 1. See `references/eval_scorecard.md`.")
    out.append("")
    out.append("**Never average across examples.** `ex6_jenga` is a deliberately")
    out.append("incoherent fixture and is supposed to score low on D3; averaging it")
    out.append("with `ex4` produces a number about nothing.")
    out.append("")
    header = "| example | arm | " + " | ".join(f"D{i+1} {NAMES['D'+str(i+1)]}" for i in range(5)) + " | total | contested |"
    out.append(header)
    out.append("|" + "---|" * 9)
    for example in sorted(by_example):
        for card in sorted(by_example[example], key=lambda c: (str(c.get("arm")), c["run_id"])):
            d = card["dimensions"]
            row = [example, str(card.get("arm") or "—")]
            row += [str(d[k]["score"]) for k in DIMS]
            row.append(f"**{card['total']}**/20")
            row.append(", ".join(card.get("contested") or []) or "—")
            out.append("| " + " | ".join(row) + " |")
    out.append("")
    for example in sorted(by_example):
        for card in sorted(by_example[example], key=lambda c: c["run_id"]):
            out.append(f"- **{example}** ({card['run_id']}): {card['verdict']}")
    text = "\n".join(out) + "\n"
    (root / "INDEX.md").write_text(text)
    print(text)
    return 0


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in {"check", "index"}:
        print(__doc__)
        return 2
    return {"check": cmd_check, "index": cmd_index}[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())
