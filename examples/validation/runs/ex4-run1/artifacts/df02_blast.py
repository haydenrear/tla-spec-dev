#!/usr/bin/env python3
"""EV-01-DF-02 blast radius.

How easily can a project obtain a FALSE `coherent` on the DIVERGENT twin by
declaring a partition that the descriptor itself says DOES NOT DECOMPOSE?

Enumerates every set partition of ex5's six model variables (Bell(6) = 203),
derives the natural module map from variable ownership, and records for each:
  * does the descriptor say the partition decomposes?
  * what does the reflexion check report?
MEASUREMENT ONLY. Nothing in the fixture is modified; the generated YAML lives
in the scratch dir and is passed with --components/--map.
"""
from __future__ import annotations

import itertools
import json
import subprocess
import sys
from pathlib import Path

FIXTURE = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

VARS = ["inbox", "accepted", "queue", "delivered", "failed", "ledger"]
# leaf module -> the variable whose state it holds; __init__ follows its sibling
MODULE_VAR = {
    "ingest/__init__.py": "inbox",
    "ingest/inbox.py": "inbox",
    "ingest/queue.py": "queue",
    "dispatch/__init__.py": "delivered",
    "dispatch/delivery.py": "delivered",
    "dispatch/failures.py": "failed",
    "ledger/__init__.py": "ledger",
    "ledger/journal.py": "ledger",
}


def partitions(collection):
    if len(collection) == 1:
        yield [collection]
        return
    first, rest = collection[0], collection[1:]
    for smaller in partitions(rest):
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[first] + subset] + smaller[n + 1 :]
        yield [[first]] + smaller


def yaml_components(groups):
    lines = ["architecture:", "  components:"]
    for i, g in enumerate(groups):
        lines.append(f"    - name: c{i}")
        lines.append(f"      variables: [{', '.join(sorted(g))}]")
    return "\n".join(lines) + "\n"


def yaml_map(groups):
    var_comp = {v: f"c{i}" for i, g in enumerate(groups) for v in g}
    by_comp: dict[str, list[str]] = {}
    for mod, var in MODULE_VAR.items():
        by_comp.setdefault(var_comp[var], []).append(mod)
    lines = ["architecture_map:", "  language: python", "  components:"]
    for comp in sorted(by_comp):
        lines.append(f"    - component: {comp}")
        lines.append(f"      modules: [{', '.join(sorted(by_comp[comp]))}]")
    return "\n".join(lines) + "\n"


def run(script, extra):
    cmd = [
        sys.executable,
        str(REPO / "scripts" / script),
        "specs/program_model/Pipeline.tla",
        "specs/program_model/Pipeline.cfg",
        "--format",
        "json",
    ] + extra
    p = subprocess.run(cmd, cwd=FIXTURE, capture_output=True, text=True, timeout=300)
    try:
        return p.returncode, json.loads(p.stdout)
    except json.JSONDecodeError:
        return p.returncode, {"_stdout": p.stdout[-400:], "_stderr": p.stderr[-400:]}


rows = []
cpath, mpath = OUT / "components.yaml", OUT / "map.yaml"
allp = list(partitions(VARS))
print(f"enumerating {len(allp)} partitions of {len(VARS)} variables")
for idx, groups in enumerate(allp):
    cpath.write_text(yaml_components(groups))
    mpath.write_text(yaml_map(groups))
    _, desc = run("analyze_architecture.py", ["--components", str(cpath)])
    _, refl = run(
        "architecture_reflexion.py",
        ["--components", str(cpath), "--code", "pipeline", "--map", str(mpath)],
    )
    part = desc.get("measured", {}).get("partition", {})
    crit = part.get("criteria") or []
    decomposes = bool(part.get("decomposes"))
    verdict = refl.get("verdict", {}).get("architecture_scan", "ERROR")
    rows.append(
        {
            "n_components": len(groups),
            "partition": [sorted(g) for g in groups],
            "decomposes": decomposes,
            "failed_criteria": [c["name"] for c in crit if not c["met"]],
            "verdict": verdict,
            "divergences": len(refl.get("divergences", [])),
            "absences": len(refl.get("absences", [])),
            "unrealized": len(refl.get("unrealized_components", [])),
            "blind_spots": [b.get("kind") for b in refl.get("blind_spots", [])],
        }
    )
    if (idx + 1) % 25 == 0:
        print(f"  {idx + 1}/{len(allp)}")

(OUT / "blast.json").write_text(json.dumps(rows, indent=2))

coherent = [r for r in rows if r["verdict"] == "coherent"]
false_clean = [r for r in coherent if not r["decomposes"]]
honest_clean = [r for r in coherent if r["decomposes"]]
print()
print(f"total partitions enumerated          : {len(rows)}")
print(f"verdict == coherent                  : {len(coherent)}")
print(f"  of which the descriptor says DOES  : {len(honest_clean)} (decomposes)")
print(f"  of which DOES NOT DECOMPOSE        : {len(false_clean)}  <-- EV-01-DF-02")
print(f"verdict == divergent                 : {sum(1 for r in rows if r['verdict'] == 'divergent')}")
print(f"verdict == unmappable                : {sum(1 for r in rows if r['verdict'] == 'unmappable')}")
print()
for r in false_clean[:12]:
    print(
        f"  FALSE CLEAN  n={r['n_components']} failed={r['failed_criteria']} "
        f"parts={r['partition']}"
    )
