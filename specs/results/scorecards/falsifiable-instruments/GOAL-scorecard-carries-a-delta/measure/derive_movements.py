#!/usr/bin/env python3
"""FI-03: the cross-round movement, re-derived from the cards.

`SELF-IMPROVEMENT.md` exists so the DELTA is the measurement. PA-06 re-scored
byte-identical trees and four dimension-points moved. This is the harness that
measures that directly instead of noticing it afterwards.

It reads a SEALED round's cards and a RE-SCORE round's cards for the same
example, pairs them, and prints the movement per artifact, per dimension, per
judge. Nothing here is typed in by hand: every number in `RESULT.md` and every
`[[movement]]` block in `INSTRUMENT-LOG.toml` comes out of this script, and
`score_tools.py audit` re-derives the same numbers from the same cards on every
run, so a stale row is a violation rather than a thing someone has to spot.

  python3 derive_movements.py --sealed ports-as-adapters \\
                              --rescore falsifiable-instruments-rescore-v1 \\
                              [--emit table|toml|summary]

**Two pairings are reported and both are wanted.**

`positional` pairs pass 1 with pass 1 and pass 2 with pass 2. It is what the
sealed baseline table means when it writes "arm A D4 2/2 -> 4/4", and it is
ARBITRARY: judge `p1` of one round is not the same agent as judge `p1` of
another, so a positional movement can be inflated or deflated by which of two
same-round cards happens to be listed first.

`to_band` is immune to that. It scores each new judge against the INTERVAL the
sealed pair spans: zero if the new score lands inside the sealed round's own
spread, otherwise the distance to the nearer end. A result that holds under both
is not an artifact of pairing, and a result that holds under only one has to say
which.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

DIMS = ("D1", "D2", "D3", "D4", "D5")
HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = HERE.parents[6]
SCORECARDS = REPO_ROOT / "specs/results/scorecards"


def load_round(round_dir: pathlib.Path, example: str) -> dict:
    """{(label, pass): card} for every filled card of one round."""
    out = {}
    for path in sorted(round_dir.rglob("scorecard.json")):
        card = json.loads(path.read_text())
        if card.get("example") != example or card.get("status") == "unfilled":
            continue
        out[(str(card.get("arm")), int(card["judge"]["pass"]))] = card
    return out


def practice_of(card: dict) -> str:
    p = card.get("judging_practice")
    if not isinstance(p, dict):
        return "unrecorded"
    if p.get("executed_own_faults") is True:
        return "executed"
    if p.get("executed_own_faults") is False:
        return "packet-only"
    return "unrecorded"


def key_of(root: pathlib.Path, card: dict, round_name: str) -> str:
    return f"{round_name}/{card['example']}/{card['run_id']}"


def band(scores: list[int], value: int) -> int:
    lo, hi = min(scores), max(scores)
    if lo <= value <= hi:
        return 0
    return value - hi if value > hi else value - lo


def measure(sealed_name: str, rescore_name: str, example: str,
            label_map: dict[str, str] | None = None) -> dict:
    """`label_map` maps a RE-SCORE label to the SEALED round's label for the same
    arm. Every round blinds under fresh labels, so two rounds that are not
    adjacent share none -- and pairing them means reading both unblinding keys,
    which is a deliberate act. It is passed on the command line and recorded in
    the result rather than inferred by this script."""
    sealed = load_round(SCORECARDS / sealed_name, example)
    rescore = load_round(SCORECARDS / rescore_name, example)
    if label_map:
        sealed = {(new, p): card for (old, p), card in sealed.items()
                  for new, want in label_map.items() if want == old}
    labels = sorted({label for label, _ in sealed} & {label for label, _ in rescore})
    if not labels:
        sys.exit(f"no artifact label appears in both {sealed_name} and {rescore_name}; "
                 f"sealed has {sorted({l for l, _ in sealed})}, re-score has "
                 f"{sorted({l for l, _ in rescore})}")
    rows = []
    for label in labels:
        passes = sorted({p for l, p in rescore if l == label})
        for dim in DIMS:
            sealed_scores = [sealed[(label, p)]["dimensions"][dim]["score"]
                             for l, p in sorted(sealed) if l == label]
            for p in passes:
                new = rescore[(label, p)]
                old = sealed.get((label, p))
                if old is None:
                    continue
                a = old["dimensions"][dim]["score"]
                b = new["dimensions"][dim]["score"]
                rows.append({
                    "label": label, "dim": dim, "pass": p,
                    "sealed": a, "rescore": b,
                    "positional": b - a,
                    "to_band": band(sealed_scores, b),
                    "sealed_band": (min(sealed_scores), max(sealed_scores)),
                    "from_key": key_of(SCORECARDS, old, sealed_name),
                    "to_key": key_of(SCORECARDS, new, rescore_name),
                    "from_practice": practice_of(old),
                    "to_practice": practice_of(new),
                })
    return {"sealed": sealed_name, "rescore": rescore_name, "example": example,
            "labels": labels, "rows": rows}


def emit_table(m: dict) -> str:
    out = [f"| artifact | dim | sealed ({m['sealed']}) | re-score ({m['rescore']}) "
           f"| positional | to band |", "|" + "---|" * 6]
    for label in m["labels"]:
        for dim in DIMS:
            rs = [r for r in m["rows"] if r["label"] == label and r["dim"] == dim]
            if not rs:
                continue
            sealed = " / ".join(str(r["sealed"]) for r in rs)
            new = " / ".join(str(r["rescore"]) for r in rs)
            pos = " / ".join(f"{r['positional']:+d}" for r in rs)
            bnd = " / ".join(f"{r['to_band']:+d}" for r in rs)
            worst = max(abs(r["positional"]) for r in rs)
            mark = "**" if worst >= 2 else ""
            out.append(f"| `{label}` | {mark}{dim}{mark} | {sealed} | {new} | {mark}{pos}{mark} "
                       f"| {bnd} |")
    return "\n".join(out)


def emit_summary(m: dict) -> str:
    out = []
    for dim in DIMS:
        rs = [r for r in m["rows"] if r["dim"] == dim]
        pos = max((abs(r["positional"]) for r in rs), default=0)
        bnd = max((abs(r["to_band"]) for r in rs), default=0)
        moved = sum(1 for r in rs if r["positional"] != 0)
        out.append(f"{dim}: worst positional {pos}, worst to-band {bnd}, "
                   f"{moved} of {len(rs)} judge-scores moved "
                   f"-- {'MISS' if pos > 1 else 'within target'}")
    total = sum(abs(r["positional"]) for r in m["rows"])
    worst = max((abs(r["positional"]) for r in m["rows"]), default=0)
    out.append("")
    out.append(f"TOTAL dimension-points moved (positional, summed): {total}")
    out.append(f"WORST single judge-dimension movement: {worst}")
    out.append(f"TARGET: at most 1 per judge on every dimension -- "
               f"{'MET' if worst <= 1 else 'MISSED'}")
    practices = sorted({r["to_practice"] for r in m["rows"]})
    out.append(f"re-score judging practice recorded as: {', '.join(practices)}")
    return "\n".join(out)


SHORT = {"ports-as-adapters": "pa06", "hexagonal-prompting-rerun": "rerun",
         "hexagonal-prompting": "hp06", "falsifiable-instruments-rescore-v1": "v1",
         "falsifiable-instruments-rescore-v2": "v2"}


def emit_toml(m: dict, nonzero_only: bool = False) -> str:
    out = []
    a, b = SHORT.get(m["sealed"], m["sealed"]), SHORT.get(m["rescore"], m["rescore"])
    for r in m["rows"]:
        if nonzero_only and r["positional"] == 0:
            continue
        unrecorded = "unrecorded" in (r["from_practice"], r["to_practice"])
        mid = f"fi03-{a}-to-{b}-{r['label']}-p{r['pass']}-{r['dim']}"
        out += [
            "", "[[movement]]",
            f'id = "{mid}"',
            f'example = "{m["example"]}"',
            f'dimension = "{r["dim"]}"',
            f'from_card = "{r["from_key"]}"',
            f'to_card = "{r["to_key"]}"',
            f"points = {r['positional']}",
            f"readable = {'false' if unrecorded else 'true'}",
            f'from_practice = "{r["from_practice"]}"',
            f'to_practice = "{r["to_practice"]}"',
        ]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sealed", default="ports-as-adapters")
    ap.add_argument("--rescore", default="falsifiable-instruments-rescore-v1")
    ap.add_argument("--example", default="ab_quota_ledger")
    ap.add_argument("--emit", default="summary", choices=["table", "toml", "summary", "all"])
    ap.add_argument("--nonzero", action="store_true",
                    help="emit only the movements that MOVED. The zeros are in RESULT.md "
                         "with their denominators; a ledger carrying eighty rows of `+0` is "
                         "a ledger nobody reads.")
    ap.add_argument("--label-map", default=None,
                    help="RESCORE=SEALED pairs, e.g. T=Q,U=P -- required when the two rounds "
                         "blinded under different labels")
    args = ap.parse_args(argv)
    label_map = None
    if args.label_map:
        label_map = dict(pair.split("=", 1) for pair in args.label_map.split(",") if pair)
    m = measure(args.sealed, args.rescore, args.example, label_map)
    if args.emit in ("table", "all"):
        print(emit_table(m))
        print()
    if args.emit in ("toml", "all"):
        print(emit_toml(m, args.nonzero))
        print()
    if args.emit in ("summary", "all"):
        print(emit_summary(m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
