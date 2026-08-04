"""Apply each mutant in mutant_catalogue.toml, run every instrument, restore.

Green control runs first: if the unmutated tree does not pass every instrument,
"killed" means nothing and the script stops.

Restoration is by full-content backup taken before any mutation and rewritten
in a `finally`, plus a SHA-256 check of the whole `pipeline/` tree at the end.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tomllib
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
TOOLS = Path(
    "/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/"
    "b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/ev03/blind/toolchain"
)
RUNNER = TOOLS / "scripts" / "run_generated_case_adapters.py"

# name -> (corpus package dir, mapping file)
CORPUS_INSTRUMENTS = {
    "view_checking": ("out_view/spec-unit/Pipeline_cases", "case_adapters.toml"),
    "view_silent": ("out_view/spec-unit/Pipeline_cases", "case_adapters_corpus_only.toml"),
    "cm_durable_checking": (
        "out_cm/spec-unit/Scenario_DurableOutcome_cases",
        "case_adapters.toml",
    ),
    "cm_durable_silent": (
        "out_cm/spec-unit/Scenario_DurableOutcome_cases",
        "case_adapters_corpus_only.toml",
    ),
    "cm_intake_slice": (
        "out_cm/spec-unit/Scenario_IntakeToDelivery_cases",
        "case_adapters_slice.toml",
    ),
}


def tree_digest() -> str:
    h = hashlib.sha256()
    for p in sorted(ROOT.joinpath("pipeline").rglob("*.py")):
        h.update(p.relative_to(ROOT).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def run_corpus(corpus: str, mapping: str) -> tuple[bool, str]:
    proc = subprocess.run(
        [
            PY,
            str(RUNNER),
            str(ROOT / corpus),
            "--mapping",
            f"specs/program_model/{mapping}",
            "--spec-dir",
            "specs/program_model",
            "--view",
            "internal",
            "--batch",
            "--import-root",
            ".",
            "--import-root",
            "./generated",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip().splitlines()[-1:][0] if (
        proc.stdout + proc.stderr
    ).strip() else ""


def run_pytest() -> tuple[bool, str]:
    proc = subprocess.run(
        [PY, "-m", "pytest", "tests", "-q"], cwd=ROOT, capture_output=True, text=True
    )
    tail = [ln for ln in proc.stdout.splitlines() if ln.strip()][-1:]
    return proc.returncode == 0, tail[0] if tail else ""


def all_instruments() -> dict[str, tuple[bool, str]]:
    out = {name: run_corpus(*cfg) for name, cfg in CORPUS_INSTRUMENTS.items()}
    out["pytest"] = run_pytest()
    return out


@contextmanager
def mutated(entry: dict):
    path = ROOT / entry["path"]
    original = path.read_text(encoding="utf-8")
    count = original.count(entry["find"])
    if count != 1:
        raise SystemExit(
            f"{entry['id']}: `find` occurs {count} times in {entry['path']}, expected exactly 1"
        )
    try:
        path.write_text(original.replace(entry["find"], entry["replace"]), encoding="utf-8")
        yield
    finally:
        path.write_text(original, encoding="utf-8")


def main() -> int:
    before = tree_digest()
    catalogue = tomllib.loads((ROOT / "mutant_catalogue.toml").read_text())["mutant"]

    control = all_instruments()
    print("GREEN CONTROL (unmutated tree)")
    for name, (ok, line) in control.items():
        print(f"  {name:22} {'PASS' if ok else 'FAIL'}  {line}")
    if not all(ok for ok, _ in control.values()):
        print("control is not green; aborting -- kill numbers would be meaningless")
        return 1

    results = []
    for entry in catalogue:
        with mutated(entry):
            res = all_instruments()
        row = {"id": entry["id"], "class": entry["class"], "path": entry["path"]}
        row.update({name: ("KILLED" if not ok else "survived") for name, (ok, _) in res.items()})
        results.append(row)
        print(
            f"{entry['id']} {entry['class']:14} "
            + " ".join(
                f"{n}={'K' if not ok else '.'}" for n, (ok, _) in res.items()
            )
        )
        assert tree_digest() == before, f"{entry['id']}: tree not restored"

    (ROOT / "mutant_results.json").write_text(json.dumps(results, indent=2))
    after = tree_digest()
    print(f"\npipeline/ digest before={before[:16]} after={after[:16]} "
          f"{'RESTORED' if before == after else 'DRIFT'}")
    return 0 if before == after else 1


if __name__ == "__main__":
    raise SystemExit(main())
