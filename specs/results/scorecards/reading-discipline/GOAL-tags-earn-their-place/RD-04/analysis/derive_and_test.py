"""RD-04 RESEARCH ANALYSIS. Not production code. Nothing imports this.

Two questions, answered against the 49 sealed cards and the artifact trees they
were scored over:

  1. DERIVATION -- can the proposed architecture tag be COMPUTED from a tree,
     using only figures `scripts/code_complexity.py` already emits?
  2. EARN-ITS-PLACE -- for each (dimension, tag-pair), do two artifacts of the
     SAME EXAMPLE that carry different tag values score in DISJOINT ranges?

R-H2 is respected: every comparison below is WITHIN one example. Cross-example
rows are printed for context and are explicitly marked NOT-A-COMPARISON.

Run from the repository root:
    python3 specs/results/scorecards/reading-discipline/\\
        GOAL-tags-earn-their-place/RD-04/analysis/derive_and_test.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
CARDS = ROOT / "specs/results/scorecards"

# ---------------------------------------------------------------------------
# The subjects. `paths` is a DECLARED scope -- nothing can compute which part of
# a tree is under score. Where a subject was scored under several arm labels in
# several rounds, every label it ever carried is listed.
# ---------------------------------------------------------------------------
SUBJECTS = {
    "arm_b": {
        "example": "ab_quota_ledger",
        "paths": ["specs/results/scorecards/ports-as-adapters/blind/artifact_T"],
        "labels": [
            ("hexagonal-prompting", "X"),
            ("hexagonal-prompting-rerun", "Q"),
            ("ports-as-adapters", "T"),
            ("falsifiable-instruments-rescore-v1", "T"),
            ("falsifiable-instruments-rescore-v2", "T"),
        ],
        "declared": "ports-and-adapters",
    },
    "arm_a": {
        "example": "ab_quota_ledger",
        "paths": ["specs/results/scorecards/ports-as-adapters/blind/artifact_U"],
        "labels": [
            ("hexagonal-prompting", "Y"),
            ("hexagonal-prompting-rerun", "P"),
            ("ports-as-adapters", "U"),
            ("falsifiable-instruments-rescore-v1", "U"),
            ("falsifiable-instruments-rescore-v2", "U"),
            ("subtract-to-measure-sm04-rescore-v2", "H"),
            ("subtract-to-measure-sm04-rescore-v3", "R"),
            ("subtract-to-measure-sm05-greenfield", "S"),
        ],
        "declared": "effectful",
    },
    "arm_c": {
        "example": "ab_quota_ledger",
        "paths": ["specs/results/scorecards/ports-as-adapters/blind/artifact_W"],
        "labels": [
            ("ports-as-adapters", "W"),
            ("falsifiable-instruments-rescore-v1", "W"),
            ("falsifiable-instruments-rescore-v2", "W"),
        ],
        "declared": "effectful",
    },
    # toolchain_removal: ONE round, TWO subjects. The scope is what the judges
    # disagreed about, and it is the reason D3 came out 2, 2, 3, 4.
    "toolchain": {
        "example": "toolchain_removal",
        "paths": ["scripts"],
        "labels": [("subtract-to-measure-sm05", "K")],
        "declared": "effectful",
    },
    "toolchain_fixture": {
        "example": "toolchain_removal",
        "paths": ["examples/validation/ab/reference_ports"],
        "labels": [],
        "declared": "ports-and-adapters",
    },
    "ex1_scaffold_only": {
        "example": "ex1_scaffold_only",
        "paths": ["examples/validation/ex1_scaffold_only"],
        "labels": [("architectural-coherence", None)],
        "declared": "effectful",
    },
    "ex3_over_complex": {
        "example": "ex3_over_complex",
        "paths": ["examples/validation/ex3_over_complex"],
        "labels": [("architectural-coherence", None)],
        "declared": "effectful",
    },
    "ex4_pipeline_coherent": {
        "example": "ex4_pipeline_coherent",
        "paths": ["examples/validation/ex4_pipeline_coherent"],
        "labels": [("architectural-coherence", None)],
        "declared": "ports-and-adapters",
    },
    "ex5_pipeline_divergent": {
        "example": "ex5_pipeline_divergent",
        "paths": ["examples/validation/ex5_pipeline_divergent"],
        "labels": [("architectural-coherence", None)],
        "declared": "ports-and-adapters",
    },
    "ex6_jenga": {
        "example": "ex6_jenga",
        "paths": ["examples/validation/ex6_jenga"],
        "labels": [("architectural-coherence", None)],
        "declared": "effectful",
    },
}

DIMS = ["D1", "D2", "D3", "D4", "D5"]


# ---------------------------------------------------------------------------
# 1. DERIVATION
# ---------------------------------------------------------------------------
def measure(paths: list[str]) -> dict | None:
    """Run the SHIPPED complexity instrument. Nothing new is measured here."""
    args = [sys.executable, str(ROOT / "scripts/code_complexity.py")]
    args += [str(ROOT / p) for p in paths]
    args += ["--json"]
    out = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        return None
    return json.loads(out.stdout)


def derive(record: dict) -> tuple[str, dict]:
    """The proposed derivation predicate, over code-role modules only.

    Returns (value, facts). Values: `ports-and-adapters`, `effectful`,
    `UNDERIVABLE:no-effect-surface`, `UNDERIVABLE:unparsed`.

    Deliberately does NOT try to tell a FOLLOWED boundary from a DECLARED-and-
    DIVERGED one. That distinction is what D3 anchors 1 and 2 score, and a tag
    that could make it would be doing the dimension's job.
    """
    mods = [m for m in record["modules"] if m["role"] == "code"]
    facts: dict = {}
    parsed = record.get("completeness", {}).get("parsed_fraction")
    facts["parsed_fraction"] = parsed
    if parsed is not None and parsed < 1.0:
        facts["note"] = "not every module parsed"

    eff = [m for m in mods if m.get("effectful_calls", 0) > 0]
    ifaces = [m for m in mods if m.get("declared_interfaces", 0) > 0]
    stateful = [m for m in mods if m.get("instance_state", 0) > 0]

    total_state = sum(m.get("instance_state", 0) for m in mods)
    state_in_eff = sum(m.get("instance_state", 0) for m in eff)
    facts["code_modules"] = len(mods)
    facts["modules_with_effectful_calls"] = len(eff)
    facts["declared_interfaces"] = sum(m.get("declared_interfaces", 0) for m in mods)
    facts["instance_state"] = total_state
    facts["instance_state_in_effectful_modules"] = state_in_eff
    facts["state_colocation"] = (
        None if total_state == 0 else round(state_in_eff / total_state, 3)
    )
    facts["iface_modules_with_no_effects"] = sorted(
        m["path"] for m in ifaces if m.get("effectful_calls", 0) == 0
    )

    if not eff:
        # No outside world is touched anywhere in the code role, so D3's
        # anchor 3 has no referent here and neither value can be asserted.
        # (The anchor's wording lives in the card and is not restated here.)
        # This is the `pure` candidate, returned UNDERIVABLE rather than as a
        # third value, because nothing in the record demonstrates it changes a
        # score.
        return "UNDERIVABLE:no-effect-surface", facts

    # ports-and-adapters requires ALL THREE, and each one is a figure the
    # shipped instrument already prints:
    #   (a) at least one code module declares an interface AND makes no
    #       effectful call -- a seam declared away from the outside world;
    #   (b) the state does not live where the effects are -- strictly under
    #       half of instance_state sits in effectful modules;
    #   (c) at least two code modules behind the seam, one effectful and one
    #       not -- a second implementation exists rather than being promised.
    a = bool(facts["iface_modules_with_no_effects"])
    b = facts["state_colocation"] is not None and facts["state_colocation"] < 0.5
    non_eff_impl = [
        m
        for m in mods
        if m.get("effectful_calls", 0) == 0
        and m.get("instance_state", 0) > 0
        and m.get("declared_interfaces", 0) == 0
    ]
    c = bool(eff) and bool(non_eff_impl)
    facts["clause_a_seam_declared_off_the_effect_surface"] = a
    facts["clause_b_state_not_colocated_with_effects"] = b
    facts["clause_c_second_implementation_present"] = c
    if a and b and c:
        return "ports-and-adapters", facts
    return "effectful", facts


# ---------------------------------------------------------------------------
# 2. THE CARDS
# ---------------------------------------------------------------------------
def load_cards() -> list[dict]:
    rows = []
    for p in sorted(CARDS.glob("*/*/*/scorecard.json")):
        d = json.loads(p.read_text())
        parts = p.relative_to(CARDS).parts
        rows.append(
            {
                "epic": parts[0],
                "example": parts[1],
                "run": parts[2],
                "arm": d.get("arm"),
                "model": (d.get("judge") or {}).get("model"),
                "tier": "opus"
                if "opus" in ((d.get("judge") or {}).get("model") or "")
                else ("sonnet" if "sonnet" in ((d.get("judge") or {}).get("model") or "") else "?"),
                "version": d.get("scorecard_version"),
                "scores": {
                    k: (d.get("dimensions") or {}).get(k, {}).get("score") for k in DIMS
                },
            }
        )
    return rows


def subject_of(card: dict, subjects: dict) -> str | None:
    for name, s in subjects.items():
        if s["example"] != card["example"]:
            continue
        for epic, arm in s["labels"]:
            if card["epic"] == epic and (arm is None or card["arm"] == arm):
                return name
    return None


def main() -> int:
    print("=" * 78)
    print("RD-04 -- derivation over the trees the sealed cards were scored over")
    print("=" * 78)
    derived: dict[str, dict] = {}
    for name, s in SUBJECTS.items():
        rec = measure(s["paths"])
        if rec is None:
            print(f"{name:24s}  MEASUREMENT FAILED")
            continue
        value, facts = derive(rec)
        derived[name] = {"value": value, "declared": s["declared"], "facts": facts}
        agree = "agree" if value == s["declared"] else "*** DISAGREE ***"
        print(
            f"{name:24s} derived={value:32s} declared={s['declared']:20s} {agree}\n"
            f"{'':24s}   iface={facts['declared_interfaces']} "
            f"eff_mods={facts['modules_with_effectful_calls']}/{facts['code_modules']} "
            f"state_coloc={facts['state_colocation']}"
        )

    print()
    print("=" * 78)
    print("EARN-ITS-PLACE -- within one example, per dimension, per tag pair")
    print("R-H2 respected: no comparison below crosses an example boundary.")
    print("=" * 78)
    cards = load_cards()
    by_example: dict[str, dict[str, dict[str, list]]] = {}
    unmapped = []
    for c in cards:
        subj = subject_of(c, SUBJECTS)
        if subj is None:
            unmapped.append(c)
            continue
        tag = derived.get(subj, {}).get("value", "?")
        ex = by_example.setdefault(c["example"], {})
        t = ex.setdefault(tag, {})
        for d in DIMS:
            t.setdefault(d, []).append((c["scores"][d], subj, c["epic"], c["tier"]))

    results = []
    for ex, tags in sorted(by_example.items()):
        names = sorted(tags)
        if len(names) < 2:
            print(f"\n{ex}: only one tag value present ({names}) -- NO TEST POSSIBLE")
            continue
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                ta, tb = names[i], names[j]
                print(f"\n{ex}:  {ta}  vs  {tb}")
                for d in DIMS:
                    sa = [x[0] for x in tags[ta][d] if x[0] is not None]
                    sb = [x[0] for x in tags[tb][d] if x[0] is not None]
                    if not sa or not sb:
                        continue
                    disjoint = max(sa) < min(sb) or max(sb) < min(sa)
                    verdict = "SEPARATES" if disjoint else "overlaps"
                    print(
                        f"   {d}  {ta[:18]:18s} {sorted(sa)}  n={len(sa)}\n"
                        f"       {tb[:18]:18s} {sorted(sb)}  n={len(sb)}   -> {verdict}"
                    )
                    results.append(
                        {
                            "example": ex,
                            "dimension": d,
                            "tag_a": ta,
                            "tag_b": tb,
                            "scores_a": sorted(sa),
                            "scores_b": sorted(sb),
                            "n_a": len(sa),
                            "n_b": len(sb),
                            "separates": disjoint,
                        }
                    )

    # ---------------------------------------------------------------------
    # THE CONTROL the earn-its-place test needs and does not state.
    # Two subjects carrying the SAME tag, same example. If those separate too,
    # the separation above is not about the tag.
    # ---------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("SAME-TAG CONTROL -- two subjects, same example, SAME derived tag")
    print("=" * 78)
    by_subject: dict[str, dict[str, list]] = {}
    for c in cards:
        subj = subject_of(c, SUBJECTS)
        if subj is None:
            continue
        s = by_subject.setdefault(subj, {})
        for d in DIMS:
            s.setdefault(d, []).append((c["scores"][d], c["tier"]))
    names = sorted(by_subject)
    controls = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if SUBJECTS[a]["example"] != SUBJECTS[b]["example"]:
                continue
            if derived.get(a, {}).get("value") != derived.get(b, {}).get("value"):
                continue
            print(f"\n{SUBJECTS[a]['example']}: {a} vs {b} "
                  f"(both {derived.get(a, {}).get('value')})")
            for d in DIMS:
                sa = [x[0] for x in by_subject[a][d] if x[0] is not None]
                sb = [x[0] for x in by_subject[b][d] if x[0] is not None]
                if not sa or not sb:
                    continue
                disj = max(sa) < min(sb) or max(sb) < min(sa)
                print(f"   {d}  {sorted(sa)} vs {sorted(sb)} -> "
                      f"{'SEPARATES (control FAILS)' if disj else 'overlaps (control holds)'}")
                controls.append({"example": SUBJECTS[a]["example"], "a": a, "b": b,
                                 "dimension": d, "separates": disj})

    # ---------------------------------------------------------------------
    # TIER CHECK on every separation found. RD-01 measured three tier splits;
    # a separation that exists in only one tier is a fact about the tier.
    # ---------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("TIER CHECK on each SEPARATES result")
    print("=" * 78)
    for r in results:
        if not r["separates"]:
            continue
        ex, d, ta, tb = r["example"], r["dimension"], r["tag_a"], r["tag_b"]
        for tier in ("opus", "sonnet"):
            sa = [x[0] for x in by_example[ex][ta][d] if x[1] and x[3] == tier and x[0] is not None]
            sb = [x[0] for x in by_example[ex][tb][d] if x[1] and x[3] == tier and x[0] is not None]
            if not sa or not sb:
                print(f"  {ex} {d} {ta}/{tb} tier={tier}: NOT MEASURED "
                      f"(n_a={len(sa)}, n_b={len(sb)}) -- absent, not 'no separation'")
                continue
            disj = max(sa) < min(sb) or max(sb) < min(sa)
            print(f"  {ex} {d} {ta}/{tb} tier={tier}: {sorted(sa)} vs {sorted(sb)} -> "
                  f"{'SEPARATES' if disj else 'overlaps'}")

    # ---------------------------------------------------------------------
    # THE CONTESTED SPREAD, DECOMPOSED BY THE SCOPE EACH JUDGE CITED.
    # D3 came out 2, 2, 3, 4 on toolchain_removal and both judges said no new
    # evidence could settle it. Read each card's D3 citations and attribute it
    # to the scope it actually cites.
    # ---------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("toolchain_removal D3 == 2,2,3,4 -- decomposed by CITED SCOPE")
    print("=" * 78)
    SCOPES = {
        "scripts/": ["scripts"],
        "spec_double_compiler/": ["spec_double_compiler"],
        "examples/validation/ab/reference_ports/": [
            "examples/validation/ab/reference_ports"
        ],
    }
    scope_tag = {}
    for label, paths in SCOPES.items():
        rec = measure(paths)
        scope_tag[label] = derive(rec)[0] if rec else "MEASUREMENT FAILED"
    for p in sorted(
        (CARDS / "subtract-to-measure-sm05/toolchain_removal").glob("*/scorecard.json")
    ):
        d = json.loads(p.read_text())
        dim = d["dimensions"]["D3"]
        cites = " ".join(dim.get("citations") or [])
        hits = {}
        for label in SCOPES:
            key = label.rstrip("/").split("/")[-1]
            hits[label] = cites.count(key + "/")
        # the scope a card is attributed to is the one it cites most
        best = max(hits, key=lambda k: hits[k]) if any(hits.values()) else "?"
        print(
            f"  {p.parent.name}  tier="
            f"{'opus' if 'opus' in d['judge']['model'] else 'sonnet'}"
            f"  D3={dim['score']}  cites={hits}\n"
            f"      -> scope {best}  derived tag = {scope_tag.get(best)}"
        )

    print("\n" + "=" * 78)
    print("CARDS NOT MAPPED TO A SUBJECT (counted, never omitted)")
    print("=" * 78)
    for c in unmapped:
        print(f"  {c['epic']}/{c['example']}/{c['run']} arm={c['arm']}")
    print(f"  total unmapped: {len(unmapped)} of {len(cards)}")

    out = Path(__file__).resolve().parent / "result.json"
    out.write_text(
        json.dumps(
            {
                "cards_total": len(cards),
                "cards_unmapped": len(unmapped),
                "derived": derived,
                "separation_tests": results,
                "same_tag_controls": controls,
            },
            indent=2,
        )
    )
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
