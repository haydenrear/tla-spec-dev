#!/usr/bin/env python3
"""RM-04. IS `state_colocation < 0.5` MEASURED, OR IS THE INTERVAL EMPTY?

`RD-04-DF-04`: the constant was CHOSEN, not measured. Every subject ever
derived sits at 1.0 or at 0.0-0.167 -- a chasm -- so every threshold in
(0.167, 1.0) gives the same answer on every subject in the record and the
clause has never been asked a question it could get wrong.

This does not construct a fixture at 0.5. A fixture built to land on a boundary
tells you what the code does there, which is already readable from the source;
it tells you nothing about whether real code ever lands there. So the probe is a
CENSUS: run the shipped derivation over every directory in this repository that
the shipped instrument can parse, and report the distribution.

Run from the repository root:

    python3 specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/analysis/threshold_probe.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[7]

spec = importlib.util.spec_from_file_location(
    "_at", ROOT / "examples/validation/scorecards/architecture_tags.py")
at = importlib.util.module_from_spec(spec)
sys.modules["_at"] = at
spec.loader.exec_module(at)


def candidate_scopes(root: pathlib.Path) -> list[str]:
    """Every directory holding at least two Python files, excluding history."""
    # `.skill-manager` is the per-checkout Skill Manager home `wt new` creates.
    # It is a MIRROR of installed skills, not this repository's code, and every
    # scope in it appeared twice in the first run of this probe -- once as
    # `examples/...` and once as `.skill-manager/skills/spec-double-compiler/
    # examples/...`. Counting a tree twice because a tool copied it is the
    # denominator error this project keeps finding, so it is excluded and the
    # exclusion is named rather than silent.
    skip = {".git", "__pycache__", ".venv", "node_modules", ".history",
            ".skill-manager", "build"}
    out = []
    for d in sorted(root.rglob("*")):
        if not d.is_dir():
            continue
        rel = d.relative_to(root)
        parts = set(rel.parts)
        if parts & skip or ".history" in str(rel):
            continue
        if len([p for p in d.iterdir() if p.suffix == ".py"]) >= 2:
            out.append(str(rel))
    return out


def main() -> int:
    scopes = candidate_scopes(ROOT)
    rows = []
    for scope in scopes:
        record = at.measure([scope], ROOT)
        if record is None:
            rows.append({"scope": scope, "derived": "UNDERIVABLE:unmeasurable"})
            continue
        value, facts = at.derive(record)
        rows.append({"scope": scope, "derived": value,
                     "state_colocation": facts.get("state_colocation"),
                     "instance_state": facts.get("instance_state"),
                     "code_modules": facts.get("code_modules"),
                     "eff_modules": facts.get("modules_with_effectful_calls"),
                     "clause_a": facts.get("clause_a_seam_declared_off_the_effect_surface"),
                     "clause_b": facts.get("clause_b_state_not_colocated_with_effects"),
                     "clause_c": facts.get("clause_c_second_implementation_present")})

    measured = [r for r in rows if isinstance(r.get("state_colocation"), float)]
    print(f"# scopes walked: {len(rows)}; state_colocation defined on {len(measured)}")
    print(f"# threshold under test: {at.STATE_COLOCATION_MAX}\n")

    buckets = {"0.0": 0, "(0.0, 0.2)": 0, "[0.2, 0.4)": 0, "[0.4, 0.6)": 0,
               "[0.6, 0.8)": 0, "[0.8, 1.0)": 0, "1.0": 0}
    for r in measured:
        v = r["state_colocation"]
        if v == 0.0:
            buckets["0.0"] += 1
        elif v == 1.0:
            buckets["1.0"] += 1
        elif v < 0.2:
            buckets["(0.0, 0.2)"] += 1
        elif v < 0.4:
            buckets["[0.2, 0.4)"] += 1
        elif v < 0.6:
            buckets["[0.4, 0.6)"] += 1
        elif v < 0.8:
            buckets["[0.6, 0.8)"] += 1
        else:
            buckets["[0.8, 1.0)"] += 1
    print("## distribution of state_colocation over real scopes")
    for k, v in buckets.items():
        print(f"  {k:>12}  {v:>4}  {'#' * v}")

    near = sorted((r for r in measured if 0.3 <= r["state_colocation"] <= 0.7),
                  key=lambda r: abs(r["state_colocation"] - 0.5))
    print(f"\n## scopes within 0.2 of the threshold: {len(near)}")
    for r in near:
        print(f"  {r['state_colocation']:<6} {r['derived']:<34} {r['scope']}")

    # THE SENSITIVITY QUESTION, and it is the one that decides the clause.
    # How many scopes change their DERIVED VALUE as the threshold sweeps?
    print("\n## sweep: how many scopes change value as the threshold moves")
    print("   (only clause (b) moves; a and c are held at what the tree gives)")
    # ONLY over scopes the shipped derivation actually DECIDED. A scope that
    # returns `UNDERIVABLE:no-effect-surface` never reaches clause (b) at all,
    # so re-running clause (b) on it and calling the difference a flip counts
    # the guard, not the threshold. The first run of this probe did exactly
    # that and reported 93 flips AT THE SHIPPED THRESHOLD, which is the
    # arithmetic tell that the denominator was wrong.
    decided = [r for r in measured
               if r["derived"] in ("effectful", "ports-and-adapters")]
    print(f"   over the {len(decided)} scope(s) the shipped derivation decided")
    for t in [round(0.05 * i, 2) for i in range(1, 21)]:
        flipped = 0
        ported = 0
        for r in decided:
            b = r["state_colocation"] < t
            value = "ports-and-adapters" if (r["clause_a"] and b and r["clause_c"]) \
                else "effectful"
            if value == "ports-and-adapters":
                ported += 1
            if value != r["derived"]:
                flipped += 1
        mark = "   <- SHIPPED" if abs(t - at.STATE_COLOCATION_MAX) < 1e-9 else ""
        print(f"  threshold {t:<5} -> {ported:>3} ports-and-adapters, "
              f"{flipped:>3} differ from the shipped answer{mark}")

    out = HERE.parent / "threshold_probe.json"
    out.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
