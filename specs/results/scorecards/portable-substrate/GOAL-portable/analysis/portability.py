#!/usr/bin/env python3
"""RM-02. Every figure in `PORTABILITY.md` is re-derived here.

Run from the repository root:

    python3 specs/results/scorecards/portable-substrate/GOAL-portable/analysis/portability.py

Reads only sealed cards under `specs/results/scorecards/` and the declared
scopes in `examples/validation/scorecards/subjects.toml`. Writes nothing.
NO production code -- nothing imports this file.

SCOPE (R3). Every figure printed names the population it was computed over.
59 of the 73 cards are `ab_quota_ledger`; a figure over "all cards" is a
figure about a corpus dominated by one example and says so.
"""
import collections
import glob
import json
import os
import re
import sys

CARDS = "specs/results/scorecards"

# Declared effect_boundary per (epic-dir, arm), transcribed from
# examples/validation/scorecards/subjects.toml. The DECLARED value is used
# because the derivation needs a tree on disk and four of these arms are
# fixtures; a declaration never refuses a comparison (architecture_tags.md
# 3.3) and here it is used only to group, never to suppress.
BOUNDARY = {
    ("hexagonal-prompting", "X"): "ports-and-adapters",
    ("hexagonal-prompting-rerun", "Q"): "ports-and-adapters",
    ("ports-as-adapters", "T"): "ports-and-adapters",
    ("falsifiable-instruments-rescore-v1", "T"): "ports-and-adapters",
    ("falsifiable-instruments-rescore-v2", "T"): "ports-and-adapters",
    ("hexagonal-prompting", "Y"): "effectful",
    ("hexagonal-prompting-rerun", "P"): "effectful",
    ("ports-as-adapters", "U"): "effectful",
    ("falsifiable-instruments-rescore-v1", "U"): "effectful",
    ("falsifiable-instruments-rescore-v2", "U"): "effectful",
    ("subtract-to-measure-sm04-rescore-v2", "H"): "effectful",
    ("subtract-to-measure-sm04-rescore-v3", "R"): "effectful",
    ("subtract-to-measure-sm05-greenfield", "S"): "effectful",
    ("ports-as-adapters", "W"): "effectful",
    ("falsifiable-instruments-rescore-v1", "W"): "effectful",
    ("falsifiable-instruments-rescore-v2", "W"): "effectful",
    ("subtract-to-measure-sm05", "K"): "effectful",
    ("reading-discipline", "Z"): "effectful",
    ("reading-discipline", "N"): "effectful",
    ("reading-discipline", "M"): "effectful",
    ("reading-discipline", "D"): "effectful",
    ("reading-discipline", "E"): "ports-and-adapters",
    ("reading-discipline", "F"): "ports-and-adapters",
}
EXAMPLE_BOUNDARY = {
    "ex1_scaffold_only": "effectful",
    "ex3_over_complex": "effectful",
    "ex6_jenga": "effectful",
    "ex4_pipeline_coherent": "ports-and-adapters",
    "ex5_pipeline_divergent": "ports-and-adapters",
}

DIMS = ["D1", "D2", "D3", "D4", "D5"]


def tier(model):
    m = model or ""
    return "opus" if "opus" in m else ("sonnet" if "sonnet" in m else "unknown")


def load():
    rows = []
    for p in sorted(glob.glob(os.path.join(CARDS, "**", "scorecard.json"), recursive=True)):
        d = json.load(open(p))
        rel = os.path.relpath(p, CARDS)
        epic_dir = rel.split(os.sep)[0]
        arm = d.get("arm")
        bnd = BOUNDARY.get((epic_dir, arm)) or EXAMPLE_BOUNDARY.get(d.get("example"))
        for dim, v in (d.get("dimensions") or {}).items():
            if not isinstance(v, dict):
                continue
            rows.append(dict(
                path=rel, epic_dir=epic_dir, example=d.get("example"), arm=arm,
                boundary=bnd, version=d.get("scorecard_version"),
                model=(d.get("judge") or {}).get("model"),
                tier=tier((d.get("judge") or {}).get("model")),
                dim=dim, score=v.get("score"),
                citations=v.get("citations") or [], rationale=v.get("rationale") or "",
            ))
    return rows


# ---------------------------------------------------------------- section 1
def cited_locality(rows):
    """Where do judges LOOK? Classify every citation path."""
    def klass(p):
        b = p.lower()
        if b.endswith(".tla") or b.endswith(".cfg") or "program_model" in b:
            return "FORMAL-MODEL"
        if "spec_double_compiler" in b:
            return "SDC-TOOLCHAIN"
        if b.startswith("scripts/") or "/scripts/" in b:
            return "REPO-SCRIPTS"
        if "examples/validation/scorecards" in b:
            return "CARD-TOOLING"
        if "examples/validation" in b:
            return "EVAL-HARNESS"
        if "references/" in b:
            return "REPO-DOCS"
        if ("specs/results" in b or "artifact_" in b
                or b.startswith("after/") or b.startswith("before/")):
            return "SUBJECT"
        if re.search(r"(quota_ledger|test_|notes\.md|evidence|revision-notes|readme|"
                     r"descriptor|mutation_check|order_hub|taskq|inbox|journal|queue)", b):
            return "SUBJECT"
        return "UNCLASSIFIED"

    per = collections.defaultdict(collections.Counter)
    for r in rows:
        for c in r["citations"]:
            per[r["dim"]][klass(c.split(":")[0])] += 1
    return per


# ---------------------------------------------------------------- section 2
LOCAL_TERMS = (r"TLC|TLA\+|\.tla\b|model-derived|derived from the model|"
               r"whole-view corpus|the corpus|corpora|generated corpus|"
               r"spec double|spec_double|projection|catalogue")
ANCHOR_DECISION = (r"anchor \d[^.;]{0,120}?(refus|not met|withheld|denied|cannot|is not|fails)"
                   r"|(refus|withheld|not met|cannot award|blocks?)[^.;]{0,80}?anchor \d"
                   r"|anchor \d is met|meets anchor \d|reaches anchor \d"
                   r"|not \d[:,]? (because|every|the)")


def anchor_rests_on_local(rows):
    """Does an ANCHOR DECISION cite local machinery in the same sentence?"""
    per = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        per[r["dim"]]["n"] += 1
        for s in re.split(r"(?<=[.;])\s+", r["rationale"]):
            if re.search(LOCAL_TERMS, s, re.I) and re.search(ANCHOR_DECISION, s, re.I):
                per[r["dim"]]["local"] += 1
                break
    return per


# ---------------------------------------------------------------- section 3
def tier_splits(rows):
    """A judge group is (round-dir, example, arm). A split is DISJOINT ranges."""
    g = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for r in rows:
        g[(r["epic_dir"], r["example"], r["arm"])][r["dim"]][r["tier"]].append(r["score"])
    out = []
    for key in sorted(g, key=str):
        for d in DIMS:
            o = sorted(g[key][d].get("opus", []))
            s = sorted(g[key][d].get("sonnet", []))
            if not o or not s:
                continue
            if max(o) < min(s):
                verdict, direction = "TIER-SPLIT", "sonnet higher"
            elif max(s) < min(o):
                verdict, direction = "TIER-SPLIT", "opus higher"
            else:
                verdict, direction = "", ""
            out.append((key, d, o, s, verdict, direction))
    return out


# ---------------------------------------------------------------- section 4
def d3_by_boundary(rows):
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r["dim"] != "D3" or r["boundary"] is None:
            continue
        per[r["example"]][r["boundary"]].append(r["score"])
    return per


def main():
    rows = load()
    ncards = len({r["path"] for r in rows})
    print(f"# RM-02 portability evidence — {ncards} sealed cards, {len(rows)} dimension-rows")
    ex = collections.Counter(r["example"] for r in rows if r["dim"] == "D1")
    print(f"\nSCOPE OF THE CORPUS (R3): {dict(ex)}")
    print("Every figure below is a figure about THAT population and no wider one.\n")

    print("## 1. Where judges look — citation targets per dimension "
          f"(population: all {ncards} cards)")
    per = cited_locality(rows)
    keys = ["SUBJECT", "EVAL-HARNESS", "FORMAL-MODEL", "REPO-SCRIPTS",
            "CARD-TOOLING", "SDC-TOOLCHAIN", "REPO-DOCS", "UNCLASSIFIED"]
    print(f"{'dim':4s}{'n':>6s}" + "".join(f"{k[:12]:>14s}" for k in keys))
    for d in DIMS:
        t = sum(per[d].values())
        print(f"{d:4s}{t:6d}" + "".join(f"{100*per[d][k]/t:13.0f}%" for k in keys))

    print(f"\n## 2. Anchor decisions resting on LOCAL machinery "
          f"(population: all {ncards} cards, per dimension)")
    a = anchor_rests_on_local(rows)
    print(f"{'dim':4s}{'n':>5s}{'rationales where an anchor decision cites local machinery':>60s}")
    for d in DIMS:
        print(f"{d:4s}{a[d]['n']:5d}{a[d]['local']:>48d} ({100*a[d]['local']/a[d]['n']:.0f}%)")

    print("\n## 3. Tier splits — judge groups scored by BOTH tiers")
    print(f"{'group':58s}{'dim':5s}{'opus':>10s}{'sonnet':>10s}  verdict")
    counts = collections.Counter()
    groups = collections.Counter()
    directions = collections.defaultdict(collections.Counter)
    for key, d, o, s, v, dirn in tier_splits(rows):
        groups[d] += 1
        if v:
            counts[d] += 1
            directions[d][dirn] += 1
        print(f"{str(key)[:58]:58s}{d:5s}{str(o):>10s}{str(s):>10s}  {v} {dirn}")
    print()
    for d in DIMS:
        n = groups[d]
        print(f"  {d}: {counts[d]} of {n} groups tier-split   directions={dict(directions[d])}")

    print("\n## 4. D3 by declared effect_boundary, PER EXAMPLE (R-H2: never averaged)")
    for exname, byb in sorted(d3_by_boundary(rows).items()):
        line = f"  {exname:22s}"
        for b in ("ports-and-adapters", "effectful"):
            v = sorted(byb.get(b, []))
            line += f"  {b}={v if v else '—'}"
        pa, ef = byb.get("ports-and-adapters", []), byb.get("effectful", [])
        if pa and ef:
            line += "   DISJOINT" if (min(pa) > max(ef) or min(ef) > max(pa)) else "   overlap"
        print(line)

    print("\n## 5. Score distribution per dimension (all cards — dominated by ab_quota_ledger)")
    for d in DIMS:
        c = collections.Counter(r["score"] for r in rows if r["dim"] == d)
        tot = sum(c.values())
        mode = c.most_common(1)[0]
        print(f"  {d}: {dict(sorted(c.items()))}  modal {mode[0]} on {mode[1]}/{tot} "
              f"({100*mode[1]/tot:.0f}%)")


if __name__ == "__main__":
    sys.exit(main())
