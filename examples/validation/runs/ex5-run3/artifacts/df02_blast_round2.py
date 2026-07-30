#!/usr/bin/env python3
"""EV-03 round-2 rerun of EV-02's blast-radius sweep.

Identical enumeration and identical module-map derivation to
`../../ex4-run1/artifacts/df02_blast.py` -- so the 203 rows are like-for-like --
plus the fields RP-01 added: `basis.clean_result_supportable`,
`basis.unsupported_clean_reasons`, `basis_limits`, and the two digests DP-1
scoring now compares.

MEASUREMENT ONLY. Nothing in the fixture is modified; generated YAML lives in
the scratch dir and is passed with --components/--map.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURE = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

VARS = ["inbox", "accepted", "queue", "delivered", "failed", "ledger"]
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
    dexit, desc = run("analyze_architecture.py", ["--components", str(cpath)])
    rexit, refl = run(
        "architecture_reflexion.py",
        ["--components", str(cpath), "--code", "pipeline", "--map", str(mpath)],
    )
    part = desc.get("measured", {}).get("partition", {})
    crit = part.get("criteria") or []
    decomposes = bool(part.get("decomposes"))
    verdict = refl.get("verdict", {}).get("architecture_scan", "ERROR")
    basis = refl.get("basis") or {}
    rows.append(
        {
            "n_components": len(groups),
            "partition": [sorted(g) for g in groups],
            "decomposes": decomposes,
            "failed_criteria": [c["name"] for c in crit if not c["met"]],
            "verdict": verdict,
            "reflexion_exit": rexit,
            "divergences": len(refl.get("divergences") or []),
            "absences": len(refl.get("absences") or []),
            "unrealized": len(refl.get("unrealized_components") or []),
            "blind_spots": [b.get("kind") for b in (refl.get("blind_spots") or [])],
            "basis_limits": [b.get("kind") for b in (refl.get("basis_limits") or [])],
            "clean_result_supportable": basis.get("clean_result_supportable"),
            "unsupported_clean_reasons": basis.get("unsupported_clean_reasons"),
            "partition_decomposes_in_basis": basis.get("partition_decomposes"),
            "divergence_detectable": basis.get("divergence_detectable"),
            "comparison_ran": basis.get("comparison_ran"),
        }
    )
    if (idx + 1) % 25 == 0:
        print(f"  {idx + 1}/{len(allp)}", flush=True)

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
print(f"other verdicts                       : {sorted({r['verdict'] for r in rows} - {'coherent','divergent','unmappable'})}")
print()
print("basis_limits kinds seen (count of partitions):")
kinds: dict[str, int] = {}
for r in rows:
    for k in r["basis_limits"]:
        kinds[k] = kinds.get(k, 0) + 1
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print(f"  {k}: {v}")
print("blind_spots kinds seen (count of partitions):")
kinds = {}
for r in rows:
    for k in r["blind_spots"]:
        kinds[k] = kinds.get(k, 0) + 1
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print(f"  {k}: {v}")
print()
print("CROSS-TAB verdict x decomposes")
for verdict in ("coherent", "divergent", "unmappable"):
    d = sum(1 for r in rows if r["verdict"] == verdict and r["decomposes"])
    nd = sum(1 for r in rows if r["verdict"] == verdict and not r["decomposes"])
    print(f"  {verdict:11s}  decomposes={d:4d}  does NOT={nd:4d}")
print()
print(f"divergent verdicts retained (round-1 was 71): {sum(1 for r in rows if r['verdict'] == 'divergent')}")
for r in false_clean[:12]:
    print(
        f"  FALSE CLEAN  n={r['n_components']} failed={r['failed_criteria']} "
        f"parts={r['partition']}"
    )
