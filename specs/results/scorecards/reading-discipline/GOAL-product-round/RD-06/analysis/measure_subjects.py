#!/usr/bin/env python3
"""RD-06. Measure the produced subjects. SCORE NOTHING.

    python3 specs/results/scorecards/reading-discipline/GOAL-product-round/RD-06/analysis/measure_subjects.py

Run from the repository root. Re-runs in well under a minute and rewrites every
record in this directory from the trees on disk, so a reader can check the
figures rather than take them.

WHAT IT DOES

  * `scripts/code_complexity.py --json` over each produced tree, one record per
    tree, written as `complexity-artifact_<L>.json`;
  * RD-05's shipped derivation over each declared scope
    (`examples/validation/scorecards/architecture_tags.py`), written as
    `tags-rd06.json` with the derived value, the declared value, the agreement
    state and the clause facts behind it;
  * the shared behavioural suite, `examples/validation/ab/tests/test_behavior.py`,
    run unchanged against each tree, written as `suite-rd06.json`;
  * the three greenfield prompts **as dispatched**, measured with
    `check_catalogue.py`'s own `distinct_lines` / `unique_content`, written as
    `prompts-rd06.json`. This is here rather than in `--arms --dispatch-dir`
    because that path looks its rows up by the fixed arm names and this round's
    rows are opaque labels, so it silently falls back to the bytes on disk --
    filed as `RD-06-DF-01`. Reported under the labels: publishing the figures
    under `arm_a` / `arm_b` / `arm_c` would unblind the round, since the
    dispatched bytes carry the label in the working directory.

WHAT IT REFUSES TO DO, AND WHY EACH ONE

  * **No delta, no comparison, no direction.** `MF-020` -- a figure falling is
    not evidence the design improved. `scripts/code_complexity.py` ships no
    `--compare` mode for exactly that reason, and this script does not
    reintroduce one by arithmetic. Six records; read them.
  * **No score.** No D-number is assigned here and no artifact is ranked.
    RD-03 judges these blind, and `tests/test_rd06_subjects.py` scans this
    directory for score-shaped content with a demonstrated failing input.
  * **No refusal.** It exits 0 whatever it finds. A tree that will not parse, a
    suite that goes red, a tag that comes back `UNDERIVABLE` -- each is a fact
    written into a record, and none of them is this script's to decide.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[6]
TAGS_PY = REPO_ROOT / "examples/validation/scorecards/architecture_tags.py"
SUBJECTS_TOML = REPO_ROOT / "examples/validation/scorecards/subjects.toml"
COMPLEXITY = REPO_ROOT / "scripts/code_complexity.py"
SUITE = REPO_ROOT / "examples/validation/ab/tests/test_behavior.py"
BLIND = REPO_ROOT / "specs/results/scorecards/reading-discipline/blind"

GREENFIELD = ("Z", "E", "N")
PAIRS = {"M": "Z", "F": "E", "D": "N"}   # after -> before
LABELS = GREENFIELD + tuple(PAIRS)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def tree(label: str) -> Path:
    return BLIND / f"artifact_{label}"


def import_candidates(root: Path) -> list[str]:
    """Every top-level module or package in the tree that could be the entry.

    The arm names its module in its own notes; this looks instead, because a
    note is a claim about the code and the code is what gets measured.
    """
    out = []
    for child in sorted(root.iterdir()):
        if child.name.startswith((".", "_")):
            continue
        if child.is_dir() and (child / "__init__.py").is_file():
            out.append(child.name)
        elif child.suffix == ".py":
            out.append(child.stem)
    return out


def run_suite(label: str) -> dict:
    root = tree(label)
    for module in import_candidates(root):
        proc = subprocess.run(
            ["uv", "run", "--with", "pytest", "python", "-m", "pytest",
             str(SUITE), "-q", "--no-header", "-p", "no:cacheprovider"],
            cwd=str(REPO_ROOT), capture_output=True, text=True,
            env={**__import__("os").environ,
                 "QUOTA_LEDGER_DIR": str(root), "QUOTA_LEDGER_IMPL": module},
        )
        tail = proc.stdout.strip().splitlines()[-1:] or [""]
        if "error" in tail[0].lower() and "no tests ran" in proc.stdout.lower():
            continue
        if proc.returncode == 4 or "ModuleNotFoundError" in proc.stdout:
            continue
        return {"label": label, "module": module, "exit": proc.returncode,
                "summary": tail[0], "tree": str(root.relative_to(REPO_ROOT))}
    return {"label": label, "module": None, "exit": None,
            "summary": "no importable QuotaLedger module found",
            "tree": str(root.relative_to(REPO_ROOT))}


def measure_dispatched_prompts() -> dict:
    """The unique-content table over WHAT WAS SENT, under the opaque labels.

    Same measure as the sealed record's, imported rather than re-implemented:
    `distinct_lines` is "exactly the measure that produced the predecessor's
    sealed 6.6x", so these numbers are comparable with that record rather than
    merely similar to it.
    """
    check = load_module(REPO_ROOT / "examples/validation/ab/check_catalogue.py",
                        "rd06_check_catalogue")
    dispatch_dir = REPO_ROOT / "examples/validation/ab/dispatch/reading-discipline"
    paths = {label: dispatch_dir / f"artifact_{label}.dispatched.md"
             for label in GREENFIELD}
    rows = {}
    for label, path in paths.items():
        rows[label] = {
            "artifact": str(path.relative_to(REPO_ROOT)),
            "distinct_lines": len(check.distinct_lines(path)),
            "unique_vs": {other: len(check.unique_content(path, paths[other]))
                          for other in GREENFIELD if other != label},
            "architectural_vocabulary_hits": {
                other: len(check.architectural_hits(
                    check.unique_content(path, paths[other])))
                for other in GREENFIELD if other != label},
        }
    return {
        "note": "Measured on the PRESERVED DISPATCHED BYTES, not on the prompt "
                "sources. PA-06-DF-10. Labels are opaque; the label -> arm map "
                "is in UNBLINDING-rd06.md and is not published here.",
        "measure": "distinct non-blank whitespace-stripped lines, imported from "
                   "examples/validation/ab/check_catalogue.py",
        "arms": rows,
    }


def main() -> int:
    tags = load_module(TAGS_PY, "rd06_tags")
    declared = tomllib.loads(SUBJECTS_TOML.read_text())["subject"]

    tag_rows = []
    for label in LABELS:
        entry = declared[f"rd06_artifact_{label}"]
        proc = subprocess.run(
            [sys.executable, str(COMPLEXITY), str(REPO_ROOT / entry["scope"][0]),
             "--json"],
            cwd=str(REPO_ROOT), capture_output=True, text=True)
        record = json.loads(proc.stdout) if proc.stdout.strip() else {}
        (HERE.parent / f"complexity-artifact_{label}.json").write_text(
            json.dumps(record, indent=2) + "\n")

        value, facts = tags.derive(record)
        tag_rows.append({
            "label": label,
            "subject": f"rd06_artifact_{label}",
            "scope": entry["scope"],
            "derived_effect_boundary": value,
            "declared_effect_boundary": entry["declared_effect_boundary"],
            "agreement": tags.agreement_of(value, entry["declared_effect_boundary"]),
            "has_refusal_authority": tags.has_authority(value),
            "facts": facts,
        })

    (HERE.parent / "tags-rd06.json").write_text(json.dumps({
        "note": "RD-05's shipped derivation, USED. Declared before the trees "
                "existed; derived from them afterwards. A disagreement is "
                "TAG-DISPUTED, it fails open, and neither side is corrected.",
        "derivation": "examples/validation/scorecards/architecture_tags.py",
        "state_colocation_max": tags.STATE_COLOCATION_MAX,
        "subjects": tag_rows,
    }, indent=2) + "\n")

    suite_rows = [run_suite(label) for label in LABELS]
    (HERE.parent / "suite-rd06.json").write_text(json.dumps({
        "note": "The SHARED behavioural contract, unchanged, run against each "
                "produced tree. Recorded per tree with the tree named. This is "
                "not a score and it is not a quality measure -- FEATURE.md "
                "calls passing it a floor.",
        "suite": "examples/validation/ab/tests/test_behavior.py",
        "runs": suite_rows,
    }, indent=2) + "\n")

    prompts = measure_dispatched_prompts()
    (HERE.parent / "prompts-rd06.json").write_text(
        json.dumps(prompts, indent=2) + "\n")

    print("subject   derived                      declared            agreement")
    for row in tag_rows:
        print(f"  {row['label']:<6}  {row['derived_effect_boundary']:<27}"
              f"  {row['declared_effect_boundary']:<18}  {row['agreement']}")
    print("\nsubject   module                suite")
    for row in suite_rows:
        print(f"  {row['label']:<6}  {str(row['module']):<20}  {row['summary']}")
    print("\nComplexity: one record per tree in the parent directory. No delta is "
          "printed here and none may be computed from this script (MF-020).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
