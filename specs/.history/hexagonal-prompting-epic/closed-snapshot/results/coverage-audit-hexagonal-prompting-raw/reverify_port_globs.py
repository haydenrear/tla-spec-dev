#!/usr/bin/env python3
"""MF-026 re-verification at 0a05eed: do the two NEW ports match what they declare?

Reproduces (a) the exact program path `run_generated_case_adapters.py:1254-1255`
builds, (b) the exact target string `effect_conformance._command_target` records
for a spawn, and (c) the oracle's own matcher `_target_matches:513-524`, then
asks whether the declared glob accepts it.

    python3 reverify_port_globs.py
"""
import fnmatch
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
src = (ROOT / "scripts" / "run_generated_case_adapters.py").read_text(encoding="utf-8")
VER = eval(re.search(r"_WORK_PATH_KEY_VERSION\s*=\s*(.+)", src).group(1).strip())


def opaque(role: str, value: str) -> str:
    """run_generated_case_adapters._opaque_path_component, verbatim (:1358-1366)."""
    payload = json.dumps([VER, str(role), str(value)], ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")
    return f"{role}-{hashlib.sha256(payload).hexdigest()[:32]}"


def target_matches(pattern: str, target: str) -> bool:
    """effect_conformance._target_matches, verbatim (:513-524)."""
    normalized = target.replace(os.sep, "/")
    collapsed = pattern.replace(os.sep, "/").replace("**", "*")
    while "**" in collapsed:
        collapsed = collapsed.replace("**", "*")
    return fnmatch.fnmatch(normalized, collapsed)


WORK = "/var/folders/xy/T/spec-double-cases-abc123"
PY = "/opt/homebrew/opt/python@3.14/bin/python3.14"

print(f"_WORK_PATH_KEY_VERSION = {VER!r}\n")

print("=== G-2  case_program_process  target '*programs/case_*' ===")
print("    spawn site: run_generated_case_adapters.py:2178  subprocess.run([*python, str(program)])")
print("    program   : run_generated_case_adapters.py:1255  work_dir/'programs'/f'{case_component}.py'")
print("    component : run_generated_case_adapters.py:1358  f'{role}-{sha256[:32]}'   <-- HYPHEN\n")
any_hit = False
for case_name in ["case_0002_install_local_cli", "case_0004_record_budgets",
                  "case_0008_update_ticket_desired", "RunSpecUnitTests-0", "anything"]:
    comp = opaque("case", case_name)
    cmdline = f"{PY} {WORK}/programs/{comp}.py"
    hit = target_matches("*programs/case_*", cmdline)
    any_hit |= hit
    print(f"  case.name = {case_name!r}")
    print(f"    recorded target = {cmdline}")
    print(f"    matches '*programs/case_*' -> {hit}")
print(f"\n  ANY MATCH ACROSS ALL CASE NAMES: {any_hit}")
print("  The component is `case-<hex>`; the glob requires `case_`. The declared")
print("  port cannot accept the spawn it was written for, for ANY case name.\n")

print("  Globs that WOULD accept it:")
comp = opaque("case", "case_0002_install_local_cli")
cmdline = f"{PY} {WORK}/programs/{comp}.py"
for pat in ["*programs/case_*", "*programs/case-*", "*/programs/*", "*programs*"]:
    print(f"    {pat!r:24} -> {target_matches(pat, cmdline)}")

print("\n=== G-1  case_work_dir_delete  target '**' ===")
print("    '**' collapses to '*' at effect_conformance.py:521-523, and fnmatch '*'")
print("    crosses separators. So it accepts every string.\n")
for t in ["/anything/at/all", "/Users/me/important-project", "/", "relative/path",
          "/var/folders/T/x/case_0004", ""]:
    print(f"    delete target {t!r:34} -> {target_matches('**', t)}")

print("\n  What the code actually constrains (effect_conformance.py:1683-1687):")
print("    case_dir = Path(work_dir) / case_name   # exactly ONE level under work_dir")
print("    'Only the per-case subdirectory is removed, and only under a directory")
print("     the oracle owns.  ... leaving the parent alone' (docstring :1678-1681)")
print("  A glob expressing that is '**/*' at minimum, or '**/case_*' if case names")
print("  are prefixed. '**' expresses no constraint at all.\n")

print("=== G-1  does '**' subsume spec_tree_delete on the SAME action row? ===")
t = "/repo/specs/current/.effect-conformance-work/case_0004/x"
print(f"    observed delete: {t}")
print(f"      spec_tree_delete      '**/specs/**' -> {target_matches('**/specs/**', t)}")
print(f"      case_work_dir_delete  '**'          -> {target_matches('**', t)}")
print("    Both accept it. RunEffectConformance now declares two filesystem.delete")
print("    ports where the wider one accepts every target of the narrower one.")
