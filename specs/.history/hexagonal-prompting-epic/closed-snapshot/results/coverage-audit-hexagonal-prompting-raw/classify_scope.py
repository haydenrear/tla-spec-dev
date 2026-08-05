#!/usr/bin/env python3
"""MF-026 coverage audit, hexagonal-prompting-epic: mechanical scope partition.

Reads `representation_scope` from specs/desired_program_model/ticket_plan.yaml
(lines 102-119) and partitions EVERY git-tracked file into in_model /
out_of_model / unclassified. The auditing agent does not choose the partition;
this script derives it from the plan's own globs.

Usage: python3 classify_scope.py <repo_root>
Writes: surface-in-model.txt, surface-out-of-model.txt, surface-unclassified.txt,
        surface-partition-counts.txt
"""
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

# --- verbatim from ticket_plan.yaml:108-112 (in_model) ---
IN_MODEL = [
    ("scripts/**/*.py", "ticket_plan.yaml:109"),
    ("specs/*/spec_manifest.yaml", "ticket_plan.yaml:110"),
    ("specs/*/TlaSpecDevCli.tla", "ticket_plan.yaml:111"),
    ("specs/*/MC*.cfg", "ticket_plan.yaml:111"),
    ("specs/*/production_adapters.py", "ticket_plan.yaml:112"),
    ("specs/*/adapter_case_runtime.py", "ticket_plan.yaml:112"),
]

# --- verbatim from ticket_plan.yaml:113-119 (out_of_model) ---
OUT_OF_MODEL = [
    ("tests/**", "ticket_plan.yaml:114"),
    ("specs/*/tests/**", "ticket_plan.yaml:114"),
    ("test_graph/**", "ticket_plan.yaml:114"),
    ("examples/**", "ticket_plan.yaml:115"),
    ("specs/.history/**", "ticket_plan.yaml:116"),
    ("specs/tickets/**", "ticket_plan.yaml:116"),
    ("specs/results/**", "ticket_plan.yaml:116"),
    ("spec_double_compiler/**", "ticket_plan.yaml:117"),
    ("templates/**", "ticket_plan.yaml:117"),
    ("skill-scripts/**", "ticket_plan.yaml:118"),
    ("*.sh", "ticket_plan.yaml:118"),
    ("prompts/**", "ticket_plan.yaml:119"),
    ("references/**", "ticket_plan.yaml:119"),
    ("*.md", "ticket_plan.yaml:119"),
]


def matches(path: str, glob: str) -> bool:
    """`**` crosses separators; `*` does not (POSIX globstar semantics).

    Implemented by splitting on `/` so that `specs/*/spec_manifest.yaml` does
    NOT match `specs/.history/a/b/spec_manifest.yaml`, while `specs/.history/**`
    does.
    """
    p = path.split("/")
    g = glob.split("/")

    def rec(pi: int, gi: int) -> bool:
        while gi < len(g):
            if g[gi] == "**":
                if gi == len(g) - 1:
                    return True  # trailing ** matches the rest, incl. nothing
                for k in range(pi, len(p) + 1):
                    if rec(k, gi + 1):
                        return True
                return False
            if pi >= len(p):
                return False
            if not fnmatch(p[pi], g[gi]):
                return False
            pi += 1
            gi += 1
        return pi == len(p)

    # A bare `*.md` style glob (no separator) applies at ANY depth: the plan
    # writes `*.md -- documentation` and `*.sh wrappers`, which plainly mean the
    # file kind, not only repo-root files. Recorded as an interpretation.
    if len(g) == 1 and "/" not in glob:
        return fnmatch(p[-1], glob)
    return rec(0, 0)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out = Path(__file__).parent
    files = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.split()

    in_model, out_model, unclassified = [], [], []
    for f in sorted(files):
        hit_in = [line for g, line in IN_MODEL if matches(f, g)]
        hit_out = [line for g, line in OUT_OF_MODEL if matches(f, g)]
        if hit_in and hit_out:
            # in_model wins ONLY where the plan's own text resolves it; anything
            # else is an escalation, never an inference.
            unclassified.append(f"{f}\tCONFLICT in={hit_in} out={hit_out}")
        elif hit_in:
            in_model.append(f"{f}\t{hit_in[0]}")
        elif hit_out:
            out_model.append(f"{f}\t{hit_out[0]}")
        else:
            unclassified.append(f"{f}\tNO-PLAN-LINE")

    (out / "surface-in-model.txt").write_text("\n".join(in_model) + "\n")
    (out / "surface-out-of-model.txt").write_text("\n".join(out_model) + "\n")
    (out / "surface-unclassified.txt").write_text("\n".join(unclassified) + "\n")
    counts = (
        f"tracked_total\t{len(files)}\n"
        f"in_model\t{len(in_model)}\n"
        f"out_of_model\t{len(out_model)}\n"
        f"unclassified\t{len(unclassified)}\n"
    )
    (out / "surface-partition-counts.txt").write_text(counts)
    print(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
