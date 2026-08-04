#!/usr/bin/env python3
"""Round-3 classification against representation_scope at schedule_revision 6.

    python3 specs/results/coverage-audit-arch-coherence-raw/round3/cac_ac_classify_v3.py

Round 3 RE-ENUMERATES (unlike round 2), because RC-01 changed the program: a new
CLI subcommand, two new actions, a new variable, four new ports and new files.
Sweeping it as a claim rather than as surface is exactly what this gate exists to
refuse. `CP3:N` == ticket_plan.yaml line N at 05acf8c.
"""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

RULES = [
    ("OUT", "specs/.history/**",          "CP3:277"), ("OUT", "specs/tickets/**",  "CP3:281"),
    ("OUT", "specs/results/**",           "CP3:282"), ("OUT", "specs/*/tests/**",  "CP3:275"),
    ("OUT", "tests/**",                   "CP3:275"), ("OUT", "test_graph/**",     "CP3:275"),
    ("OUT", "examples/**",                "CP3:276"), ("OUT", "spec_double_compiler/**", "CP3:278"),
    ("OUT", "templates/**",               "CP3:278"), ("OUT", "skill-scripts/**",  "CP3:279"),
    ("OUT", "scripts/run_tlc.sh",         "CP3:279"), ("OUT", "prompts/**",        "CP3:280"),
    ("OUT", "references/**",              "CP3:280"), ("OUT", "*.md",             "CP3:280"),
    ("IN",  "scripts/**/*.py",            "CP3:270"),
    ("IN",  "specs/current/spec_manifest.yaml",               "CP3:271"),
    ("IN",  "specs/desired_program_model/spec_manifest.yaml", "CP3:271"),
    ("IN",  "specs/program_model/spec_manifest.yaml",         "CP3:271"),
    ("IN",  "specs/*/TlaSpecDevCli.tla",  "CP3:272"), ("IN", "specs/*/MC*.cfg",   "CP3:272"),
    ("IN",  "specs/*/production_adapters.py",   "CP3:273"),
    ("IN",  "specs/*/adapter_case_runtime.py",  "CP3:273"),
]

def _re(g):
    out, i = [], 0
    while i < len(g):
        if g.startswith("**/", i): out.append("(?:[^/]+/)*"); i += 3
        elif g.startswith("**", i): out.append(".*"); i += 2
        elif g[i] == "*": out.append("[^/]*"); i += 1
        elif g[i] == "?": out.append("[^/]"); i += 1
        else: out.append(re.escape(g[i])); i += 1
    return re.compile("^" + "".join(out) + "$")

_C = {}
def scope(p):
    for cls, g, cite in RULES:
        if g not in _C: _C[g] = _re(g)
        if _C[g].match(p): return cls, cite
    return "ESCALATION", "none - no representation_scope line covers it"

def main():
    files = [l.strip() for l in (HERE/"sweep1-surface.txt").read_text().splitlines() if l.strip()]
    rows, counts = [], {"IN": 0, "OUT": 0, "ESCALATION": 0}
    for i, f in enumerate(files, 1):
        cls, cite = scope(f); counts[cls] += 1
        rows.append(f"| {i} | `{f}` | {cls} | {cite} |")
    (HERE/"sweep1-table-v3.md").write_text(
        "| # | Module | In/Out of model | representation_scope line |\n|---|---|---|---|\n"
        + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"SWEEP1-v3 N={len(files)} M={len(rows)} equal={len(files)==len(rows)}")
    print(f"  {counts}")
    if counts["ESCALATION"]:
        print("  ESCALATION rows:")
        for f in files:
            if scope(f)[0] == "ESCALATION": print(f"    {f}")
    tracked = subprocess.run(["git","ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    nonsrc = sorted(p for p in tracked if scope(p)[0]=="IN" and not p.endswith(".py"))
    (HERE/"sweep1b-in-model-nonsource.txt").write_text("\n".join(nonsrc)+"\n", encoding="utf-8")
    insrc = sorted(p for p in tracked if scope(p)[0]=="IN" and p.endswith(".py"))
    print(f"  IN-MODEL surface: {len(insrc)} .py + {len(nonsrc)} non-source = {len(insrc)+len(nonsrc)}")

if __name__ == "__main__": main()
