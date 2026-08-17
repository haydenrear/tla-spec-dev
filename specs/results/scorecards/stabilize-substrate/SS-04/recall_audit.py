#!/usr/bin/env python3
"""What FORM P MISSES, measured against a deliberately over-broad superset.

`MF-020` defence, mechanical half. A recogniser's author is the worst possible
judge of its recall, because the shapes they think of are the shapes they built
for. So the denominator here is produced by a SEPARATE scanner that was written
to over-match on purpose -- any two numbers joined by a partitive-looking
connector, spelled or not, across a line break or not -- and every occurrence
FORM P did not take is bucketed by a rule, so the answer is a numerator and a
denominator rather than an impression.

    python3 recall_audit.py [--doc PATH ...] [--show N]
    python3 recall_audit.py --precision-sample N [--seed S]

It reports, per document: SUPERSET, TAKEN, MISSED, and the missed rows grouped
by which declared category defeated them. The categories come from
`PROSE-FORM-SPEC.md` S5, which was sealed BEFORE any of this ran.

`--precision-sample` is the OTHER half and it exists because the first version of
this file ADVERTISED A `--sample N` FLAG THAT WAS NEVER IMPLEMENTED, while the
write-up published a hand-audited `38 of 40` whose sample lived only in a
throwaway shell heredoc. A precision figure a reviewer cannot regenerate is a
figure nobody can check -- which is the whole complaint this ticket is about,
committed by the ticket. It draws a seeded sample of FORM P matches over the
default sweep and prints each with its source line, so the adjudication can be
repeated by someone who does not trust the adjudicator. Found by the reviewer of
PR #285.
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]
                       / "examples/validation/scorecards"))
import score_tools as st  # noqa: E402

# DELIBERATELY OVER-BROAD. It matches things that are not counted figures at
# all -- that is the point: a superset that only contained real figures would be
# a second recogniser with the same blind spots as the first.
_WORDS = (r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
          r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
          r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|"
          r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-"
          r"(?:one|two|three|four|five|six|seven|eight|nine)")
_N = rf"(?:\d[\d,]*|{_WORDS})"
SUPERSET = re.compile(
    rf"(?<![\w.,-])(?P<n>{_N})\s*(?:\n\s*)?"
    rf"(?:out\s+of|of|in|/|:|\bin\s+every\b)\s*(?:\n\s*)?"
    rf"(?:(?:the|a|an|its|their|our|my|these|those|all|every|first|last)\s+)?"
    rf"(?P<m>{_N})(?![\w-])",
    re.I)


def categorise(text: str, start: int, end: int, n: str, m: str) -> str:
    """Which DECLARED miss category this occurrence falls into."""
    frag = text[start:end]
    if "\n" in frag:
        return "split across a line break"
    if "/" in frag:
        return "ratio or movement notation `n/m`"
    if re.search(r"\s(?:in)\s", frag, re.I):
        return "`n in m` rather than `n of m`"
    if re.search(r":", frag):
        return "`n:m` colon form"
    for tok in (n, m):
        t = tok.strip().lower().replace(",", "")
        if not t.isdigit() and t not in st._NUMBER_WORDS:
            return "spelled-out number above twenty"
    before = text[max(0, start - 40):start]
    if re.search(r"(?:\b(?:every|each|any|neither)\s+)$", before, re.I):
        return "distributive `every one of the N` (deliberately refused)"
    det = re.search(rf"{re.escape(n)}\s+(?:out\s+of|of)\s+(\w+)\s+", frag, re.I)
    if det and det.group(1).lower() not in (
            "the", "a", "an", "its", "their", "our", "my", "these", "those",
            "all", "every"):
        return "more than one word between `of` and the denominator"
    return "unclassified — inspect"


def audit(paths: list[pathlib.Path], root: pathlib.Path) -> dict:
    out = {}
    for p in paths:
        try:
            lines = st.read_document(p)
        except st.ScopeUndecided as exc:
            out[str(p)] = {"state": exc.state, "detail": str(exc)}
            continue
        text = "\n".join(lines)
        taken = {(c["line"], c["n"], c["m"])
                 for c in st.find_claims(p, root, lines)}
        # Re-derive each superset hit's line number from the offset.
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln) + 1)
        sup, missed = 0, []
        for mt in SUPERSET.finditer(text):
            sup += 1
            nn, mm = st._as_count(mt.group("n")), st._as_count(mt.group("m"))
            lineno = max(i for i, s in enumerate(starts, 1) if s <= mt.start())
            if nn is not None and mm is not None and (lineno, nn, mm) in taken:
                continue
            missed.append({
                "line": lineno,
                "text": " ".join(mt.group(0).split())[:70],
                "why": categorise(text, mt.start(), mt.end(),
                                  mt.group("n"), mt.group("m")),
            })
        out[str(p)] = {"superset": sup, "taken": sup - len(missed),
                       "missed": missed}
    return out


def precision_sample(root: pathlib.Path, size: int, seed: int) -> list[dict]:
    """A seeded sample of FORM P matches, each with the line it was read from.

    Deterministic given (tree, size, seed): `sweep_paths` sorts, `find_claims`
    walks lines in order, so the population is ordered before it is sampled.
    THE POPULATION IS A PROPERTY OF THE TREE, so a sample drawn at one commit
    does not regenerate at another -- which is why the figure this produces is
    published WITH ITS COMMIT, per `SS-01-DF-03`.
    """
    import random

    population, sources = [], {}
    for path in st.sweep_paths(root):
        try:
            lines = st.read_document(path)
        except st.ScopeUndecided:
            continue
        for claim in st.find_claims(path, root, lines):
            if claim["form"] != "P":
                continue
            population.append(claim)
            sources[(claim["file"], claim["line"])] = lines[claim["line"] - 1]
    rng = random.Random(seed)
    picked = rng.sample(population, min(size, len(population)))
    return [dict(c, source=sources[(c["file"], c["line"])].strip()) for c in picked]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(st.REPO_ROOT))
    ap.add_argument("--doc", action="append", default=[])
    ap.add_argument("--show", type=int, default=8)
    ap.add_argument("--precision-sample", type=int, default=0,
                    help="draw N FORM P matches for hand adjudication and stop")
    ap.add_argument("--seed", type=int, default=277)
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    if args.precision_sample:
        rows = precision_sample(root, args.precision_sample, args.seed)
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True)
        print(f"# PRECISION SAMPLE -- {len(rows)} FORM P matches, seed {args.seed}")
        print(f"# root {root.resolve()}")
        print(f"# HEAD {head.stdout.strip() or 'NOT A GIT CHECKOUT'}")
        print("# Adjudicate each: is it a COUNTED FIGURE -- a numerator over a")
        print("# denominator counting a population -- or is it not?\n")
        for i, r in enumerate(rows, 1):
            print(f"{i:>3}. {r['file']}:{r['line']}  match={r['span']!r}")
            print(f"     noun={r['noun']!r}")
            print(f"     LINE: {r['source'][:180]}")
        return 0
    paths = ([pathlib.Path(d) for d in args.doc]
             if args.doc else st.sweep_paths(root))
    res = audit(paths, root)
    tot_sup = tot_taken = 0
    reasons: collections.Counter = collections.Counter()
    for path, r in sorted(res.items()):
        if "state" in r:
            print(f"{path}: UNDECIDED [{r['state']}] {r['detail']}")
            continue
        tot_sup += r["superset"]
        tot_taken += r["taken"]
        reasons.update(x["why"] for x in r["missed"])
        if args.doc:
            print(f"\n## {path}")
            print(f"   superset {r['superset']}  taken {r['taken']}  "
                  f"missed {len(r['missed'])}")
            for x in r["missed"][:args.show]:
                print(f"     :{x['line']:<5} [{x['why']}] {x['text']!r}")
            if len(r["missed"]) > args.show:
                print(f"     ... and {len(r['missed']) - args.show} more")
    pct = 100.0 * tot_taken / tot_sup if tot_sup else 0.0
    print(f"\nSUPERSET {tot_sup}   TAKEN BY FORM P + THE BOUND FORMS {tot_taken} "
          f"({pct:.1f}%)   MISSED {tot_sup - tot_taken}")
    print("missed, by declared category:")
    for why, k in reasons.most_common():
        print(f"  {k:>6}  {why}")
    print("\nA superset hit is NOT a counted figure -- this scanner over-matches "
          "on purpose. The denominator is 'shapes a reader might have to check', "
          "and the numerator is 'shapes the recogniser reaches'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
