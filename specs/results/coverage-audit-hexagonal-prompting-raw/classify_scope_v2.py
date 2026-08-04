#!/usr/bin/env python3
"""MF-026 re-verification at 0a05eed: scope partition against the AMENDED block.

`classify_scope.py` (round 1) encoded `representation_scope` at
schedule_revision 2 and produced 19 ESCALATION rows. This is the same
instrument re-pointed at schedule_revision 3 (`ticket_plan.yaml:102-146`,
commit 475bc9a). Round 1's script is left untouched: it is committed evidence
of the previous measurement.

Two readings are computed, because the amendment introduces an OVERLAP the plan
does not adjudicate:

  SPECIFIC-WINS  the named out_of_model carve-out for
                 `scripts/run_generated_case_adapters.py` and
                 `scripts/generate_python.py` beats the general
                 `scripts/**/*.py` in_model glob.
  IN-WINS        the in_model directory glob beats the named carve-out.

Reported separately rather than resolved, per the closure rule.

Usage: python3 classify_scope_v2.py <repo_root>
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_scope import matches  # noqa: E402  -- same glob engine as round 1

# --- ticket_plan.yaml:108-121 (in_model) @ schedule_revision 3 ---
IN_MODEL = [
    ("scripts/**/*.py", "ticket_plan.yaml:122"),
    ("specs/*/spec_manifest.yaml", "ticket_plan.yaml:123"),
    ("specs/*/TlaSpecDevCli.tla", "ticket_plan.yaml:124"),
    ("specs/*/MC*.cfg", "ticket_plan.yaml:124"),
    ("specs/*/production_adapters.py", "ticket_plan.yaml:125"),
    ("specs/*/adapter_case_runtime.py", "ticket_plan.yaml:125"),
    ("specs/*/case_adapters.toml", "ticket_plan.yaml:126 (NEW, ESC-1)"),
    ("specs/*/kill_mutants.toml", "ticket_plan.yaml:127 (NEW, ESC-1)"),
    ("specs/*/tlc_projection.py", "ticket_plan.yaml:128 (NEW, ESC-1)"),
]

# --- ticket_plan.yaml:129-144 (out_of_model) @ schedule_revision 3 ---
OUT_OF_MODEL = [
    ("tests/**", "ticket_plan.yaml:130"),
    ("specs/*/tests/**", "ticket_plan.yaml:130"),
    ("test_graph/**", "ticket_plan.yaml:130"),
    ("examples/**", "ticket_plan.yaml:131"),
    ("specs/.history/**", "ticket_plan.yaml:132"),
    ("specs/tickets/**", "ticket_plan.yaml:132"),
    ("specs/results/**", "ticket_plan.yaml:132"),
    ("spec_double_compiler/**", "ticket_plan.yaml:133"),
    ("templates/**", "ticket_plan.yaml:133"),
    ("skill-scripts/**", "ticket_plan.yaml:134"),
    ("*.sh", "ticket_plan.yaml:134"),
    ("prompts/**", "ticket_plan.yaml:135"),
    ("references/**", "ticket_plan.yaml:135"),
    ("*.md", "ticket_plan.yaml:135"),
    ("specs/*/architecture_components.yaml", "ticket_plan.yaml:142 (NEW, ESC-1)"),
    ("specs/*/architecture_map.yaml", "ticket_plan.yaml:142 (NEW, ESC-1)"),
    ("specs/desired_program_model/ticket_plan.yaml", "ticket_plan.yaml:143 (NEW, ESC-1)"),
    ("specs/desired_program_model/deferred_findings.yaml", "ticket_plan.yaml:143 (NEW, ESC-1)"),
    ("specs/desired_program_model/desired_state.yaml", "ticket_plan.yaml:143 (NEW, ESC-1)"),
    (".gitignore", "ticket_plan.yaml:144 (NEW, ESC-1)"),
    (".DS_Store", "ticket_plan.yaml:144 (NEW, ESC-1)"),
    ("skill-manager.toml", "ticket_plan.yaml:144 (NEW, ESC-1)"),
]

# The ESC-3 carve-out, applied only under the SPECIFIC-WINS reading.
CARVE_OUT = [
    ("scripts/run_generated_case_adapters.py", "ticket_plan.yaml:145 (RESTORED, ESC-3)"),
    ("scripts/generate_python.py", "ticket_plan.yaml:145 (RESTORED, ESC-3)"),
]


def classify(f, out_rules):
    hit_in = [c for g, c in IN_MODEL if matches(f, g)]
    hit_out = [c for g, c in out_rules if matches(f, g)]
    if hit_in and hit_out:
        return "CONFLICT", f"in={hit_in[0]} out={hit_out[0]}"
    if hit_in:
        return "IN", hit_in[0]
    if hit_out:
        return "OUT", hit_out[0]
    return "ESCALATION", "no representation_scope line covers it"


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    here = Path(__file__).resolve().parent
    files = sorted(subprocess.run(["git", "ls-files"], cwd=root, capture_output=True,
                                  text=True, check=True).stdout.split())

    for label, out_rules in (("specific-wins", CARVE_OUT + OUT_OF_MODEL),
                             ("in-wins", OUT_OF_MODEL)):
        counts = {"IN": 0, "OUT": 0, "CONFLICT": 0, "ESCALATION": 0}
        rows, flagged = [], []
        for i, f in enumerate(files, 1):
            cls, cite = classify(f, out_rules)
            counts[cls] += 1
            rows.append(f"| {i} | `{f}` | {cls} | {cite} |")
            if cls in ("ESCALATION", "CONFLICT"):
                flagged.append(f"{f}\t{cls}\t{cite}")
        (here / f"reverify-sweep1-table-{label}.md").write_text(
            "| # | Module | In/Out of model | representation_scope line |\n|---|---|---|---|\n"
            + "\n".join(rows) + "\n", encoding="utf-8")
        (here / f"reverify-flagged-{label}.txt").write_text("\n".join(flagged) + "\n", encoding="utf-8")
        print(f"[{label}] N={len(files)} M={len(rows)} equal={len(files) == len(rows)}  {counts}")
        for line in flagged:
            print("   ", line.replace("\t", "  "))

    # Round 1's 19 escalation rows, re-checked one by one.
    prev = [l.split("\t")[0] for l in
            (here / "surface-unclassified.txt").read_text().splitlines() if l.strip()]
    print(f"\nRound-1 ESCALATION rows re-checked ({len(prev)}):")
    unresolved = []
    for f in prev:
        cls, cite = classify(f, CARVE_OUT + OUT_OF_MODEL)
        print(f"   {cls:11} {f:60} {cite}")
        if cls in ("ESCALATION", "CONFLICT"):
            unresolved.append(f)
    print(f"\nStill unclassified from round 1: {len(unresolved)} {unresolved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
