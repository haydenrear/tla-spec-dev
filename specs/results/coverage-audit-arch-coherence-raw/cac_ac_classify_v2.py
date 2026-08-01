#!/usr/bin/env python3
"""Re-classification pass against `representation_scope` (plan schedule_revision 4).

    python3 specs/results/coverage-audit-arch-coherence-raw/cac_ac_classify_v2.py

The ENUMERATIONS are unchanged and are NOT re-run: `sweep1-surface.txt` and every
`effects-*.txt` / `behavior-*.txt` file committed at b1fc5fe are reused byte for
byte. Only the scope classification changes, because only the scope declaration
changed (owner amendment fa5762a).

v1 (`cac_ac_classify.py`) read ticket `implementation_scope`, which the amended
plan now declares is edit-permission only and never a representation claim
(`ticket_plan.yaml:68-77`, `representation_scope_rule`). v2 reads
`ticket_plan.yaml:220-240`, `representation_scope`, and nothing else.

Classification is still the Step-0 closure rule: a glob covers what it writes.
`CP2:N` == amended `specs/desired_program_model/ticket_plan.yaml` line N.
Anything no line covers is ESCALATION -- never an inference.
"""
from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# --------------------------------------------------------------------------
# representation_scope, transcribed with plan line numbers. Ordered; first
# match wins. `IN` / `OUT` is the disposition class.
# --------------------------------------------------------------------------
RULES: list[tuple[str, str, str, str]] = [
    # (class, glob, plan-line citation, human label)
    ("OUT", "specs/.history/**",          "CP2:237", "sealed append-only snapshots"),
    ("OUT", "specs/*/tests/**",           "CP2:235", "spec-tree test harness"),
    ("OUT", "tests/**",                   "CP2:235", "repository test harness"),
    ("OUT", "test_graph/**",              "CP2:235", "Test Graph validation harness"),
    ("OUT", "examples/**",                "CP2:236", "fixtures / worked examples / eval subjects"),
    ("OUT", "spec_double_compiler/**",    "CP2:238", "harness plumbing"),
    ("OUT", "templates/**",               "CP2:238", "generator templates"),
    ("OUT", "skill-scripts/**",           "CP2:239", "installer shell"),
    ("OUT", "scripts/run_tlc.sh",         "CP2:239", "wrapper shell, named explicitly"),
    ("OUT", "prompts/**",                 "CP2:240", "sub-agent prompts"),
    ("OUT", "references/**",              "CP2:240", "documentation"),
    ("OUT", "*.md",                       "CP2:240", "documentation"),
    ("IN",  "scripts/**/*.py",            "CP2:231", "the shipped CLI toolchain"),
    ("IN",  "specs/current/spec_manifest.yaml",              "CP2:232", "effect port declarations"),
    ("IN",  "specs/desired_program_model/spec_manifest.yaml","CP2:232", "effect port declarations"),
    ("IN",  "specs/program_model/spec_manifest.yaml",        "CP2:232", "effect port declarations"),
    ("IN",  "specs/*/TlaSpecDevCli.tla",  "CP2:233", "the model itself"),
    ("IN",  "specs/*/MC*.cfg",            "CP2:233", "finite instances"),
]

# STATED READING of one loose entry. CP2:239 writes `skill-scripts/**, *.sh
# wrappers, run_tlc.sh`. A bare `*.sh` glob does not cross a path separator, so
# it matches nothing at repository root. Rather than widen it by inference to
# "any .sh anywhere" -- which would silently absorb five files under
# specs/results/ that no line names -- only the two paths the entry writes
# explicitly are treated as covered. The remainder escalates. Strictness here
# produces MORE escalations, which Step 0 says is the correct direction.


def _glob_re(glob: str) -> re.Pattern[str]:
    """Path-aware glob: `**` crosses separators, `*` and `?` do not."""
    out, i = [], 0
    while i < len(glob):
        c = glob[i]
        if glob.startswith("**/", i):
            out.append("(?:[^/]+/)*"); i += 3
        elif glob.startswith("**", i):
            out.append(".*"); i += 2
        elif c == "*":
            out.append("[^/]*"); i += 1
        elif c == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(c)); i += 1
    return re.compile("^" + "".join(out) + "$")


_COMPILED: dict[str, re.Pattern[str]] = {}


def _match(path: str, glob: str) -> bool:
    if glob not in _COMPILED:
        _COMPILED[glob] = _glob_re(glob)
    return _COMPILED[glob].match(path) is not None


def scope_v2(path: str) -> tuple[str, str, str]:
    """-> (IN | OUT | ESCALATION, plan-line citation, label)."""
    for cls, glob, cite, label in RULES:
        if _match(path, glob):
            return cls, cite, f"`{glob}` — {label}"
    return "ESCALATION", "none — no representation_scope line covers it", ""


# --------------------------------------------------------------------------
# Sweep 1 re-classification (row set unchanged: sweep1-surface.txt, N=596)
# --------------------------------------------------------------------------
def read_lines(name: str) -> list[str]:
    p = HERE / name
    if not p.exists():
        sys.exit(f"missing raw file: {p}")
    return [l.rstrip("\n") for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def sweep1_v2() -> None:
    from cac_ac_classify import REPRESENTED, scope_of as scope_v1
    files = read_lines("sweep1-surface.txt")
    rows, counts, moved = [], {"IN": 0, "OUT": 0, "ESCALATION": 0}, 0
    for i, f in enumerate(files, 1):
        cls, cite, label = scope_v2(f)
        counts[cls] += 1
        if scope_v1(f)[0] == "ESCALATION" and cls != "ESCALATION":
            moved += 1
        action, verdict, ev = REPRESENTED.get(f, ("none", "unrepresented", "-"))
        if cls == "OUT":
            verdict, disp = "unrepresented", "inventory it"
        elif cls == "IN":
            disp = "-" if verdict == "represented" else "model it / change the program"
        else:
            disp = "ESCALATE"
        rows.append(f"| {i} | `{f}` | {cls} | {cite} | {action} | `{verdict}` | {disp} | {ev} |")
    hdr = ("| # | Module (`path`) | In/Out of model | representation_scope line | Spec action(s) "
           "| Verdict | Disposition | Evidence (`file:line`) |\n|---|---|---|---|---|---|---|---|")
    (HERE / "sweep1-table-v2.md").write_text(hdr + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"SWEEP1-v2 N={len(files)} M={len(rows)} equal={len(files) == len(rows)}")
    print(f"  {counts}")
    print(f"  previously-ESCALATION rows that now carry a real disposition: {moved} of 187")


# --------------------------------------------------------------------------
# Sweep 1b -- the in-model surface representation_scope names that the v1
# language globs never enumerated (.yaml / .tla / .cfg). ESC-4 in reverse.
# --------------------------------------------------------------------------
def sweep1b() -> None:
    import subprocess
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.splitlines()
    hits = [p for p in tracked
            if scope_v2(p)[0] == "IN" and not p.endswith(".py")]
    (HERE / "sweep1b-in-model-nonsource.txt").write_text("\n".join(sorted(hits)) + "\n",
                                                         encoding="utf-8")
    print(f"SWEEP1b in-model non-source files = {len(hits)}")
    for h in sorted(hits):
        print(f"  {h}")


# --------------------------------------------------------------------------
# Sweeps 2 and 3 -- same groups, same raw files, re-columned IN/OUT/ESCALATION
# --------------------------------------------------------------------------
def regroup() -> None:
    from cac_ac_classify import EFFECT_RULES, BEHAVIOR_RULES, split_hit
    for prefix, ruleset in (("effects", EFFECT_RULES), ("behavior", BEHAVIOR_RULES)):
        for cat, rules in ruleset.items():
            hits = read_lines(f"{prefix}-{cat}.txt")
            buckets: dict[str, list] = {g: [] for g, _, _ in rules}
            for h in hits:
                path, ln, text = split_hit(h)
                for g, pat, _ in rules:
                    if re.search(pat, text):
                        buckets[g].append((path, ln, text))
                        break
            assert sum(len(v) for v in buckets.values()) == len(hits), cat
            lines = ["| Group | Distinct semantics | Raw | IN-MODEL | out-of-model | ESCALATION |",
                     "|---|---|---|---|---|---|"]
            summary = {}
            for g, _, desc in rules:
                b = buckets[g]
                c = {"IN": 0, "OUT": 0, "ESCALATION": 0}
                for p, _, _ in b:
                    c[scope_v2(p)[0]] += 1
                lines.append(f"| `{g}` | {desc} | {len(b)} | {c['IN']} | {c['OUT']} | {c['ESCALATION']} |")
                summary[g] = c
            (HERE / f"{prefix}-{cat}-groups-v2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            tot_in = sum(v["IN"] for v in summary.values())
            tot_esc = sum(v["ESCALATION"] for v in summary.values())
            print(f"{prefix} {cat}: raw={len(hits)} IN={tot_in} ESC={tot_esc}")
    # destructive sites, re-columned
    hits = read_lines("effects-filesystem.txt")
    pat = r"(rmtree|\.unlink\(|os\.remove\(|os\.rename\(|os\.replace\(|shutil\.move\(|replace_tree)"
    rows = []
    for h in hits:
        p, ln, text = split_hit(h)
        if re.search(pat, text):
            cls, cite, _ = scope_v2(p)
            rows.append(f"| {len(rows)+1} | `{p}:{ln}` | `{text.strip()[:100]}` | {cls} | {cite} |")
    (HERE / "effects-destructive-sites-v2.md").write_text(
        "| # | Site | Line | In/Out of model | representation_scope line |\n|---|---|---|---|---|\n"
        + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"destructive per-site rows = {len(rows)}")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sweep1_v2()
    sweep1b()
    regroup()
