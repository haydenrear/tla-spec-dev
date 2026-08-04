#!/usr/bin/env python3
"""The HP-03 kill table: per class, per instrument. Never one rate.

Ticket-local measurement driver. It seeds one mutant at a time into an
implementation, runs each instrument over it, and records whether the mutant
DIED. The assertions are the SHIPPED ones -- ``assert_case_result_per_field``
and ``call_adapter`` are imported from ``scripts/run_generated_case_adapters.py``
and ``spec_double_compiler/runtime.py``, not reimplemented here -- so what is
ticket-local is the loop, not the oracle.

Why a loop of its own rather than the shipped CLI: the shipped runner's default
mode writes and executes ONE SUBPROCESS PER CASE, and the corpora here run to
tens of thousands of cases across a dozen mutants. The shipped CLI is exercised
separately, once, end to end, as evidence that it accepts this corpus
(``results/shipped-runner-negative.txt``).

FILE FINDINGS, FIX NOTHING. Nothing here repairs a mutant, retries a failure or
re-runs an instrument until a number improves.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

from scripts.run_generated_case_adapters import assert_case_result_per_field  # noqa: E402
from spec_double_compiler.runtime import call_adapter  # noqa: E402


def load_catalogue(path: Path) -> list[dict[str, Any]]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["mutants"]


def load_cases(package_dir: Path) -> list[Any]:
    parent = str(package_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    module = importlib.import_module(f"{package_dir.name}.cases")
    importlib.reload(module)
    return list(module.CASES)


def run_corpus(cases: list[Any], impl_dir: Path, work_root: Path) -> tuple[int, int, int, list[str]]:
    """``(ran, skipped, failed, first failures)`` over one corpus.

    A fresh adapter module is imported per implementation so a seeded mutant is
    actually the code under test.
    """
    os.environ["QUOTA_LEDGER_DIR"] = str(impl_dir)
    for name in [key for key in sys.modules if key in ("quota_ledger", "quota_ledger_adapter")]:
        del sys.modules[name]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    adapter_module = importlib.import_module("quota_ledger_adapter")

    negative = adapter_module.NegativeAdapter()
    positive = adapter_module.PositiveAdapter()
    ran = skipped = failed = 0
    failures: list[str] = []
    for index, case in enumerate(cases):
        adapter = negative if "negative" in case.labels else positive
        verdict = adapter.can_run(case)
        if verdict is not True and not (isinstance(verdict, tuple) and verdict[0]):
            skipped += 1
            continue
        work_dir = work_root / f"case-{index}"
        try:
            result = call_adapter(adapter, case, work_dir)
            assert_case_result_per_field(case=case, result=result)
            ran += 1
        except Exception as error:  # a failing case is the signal, not an incident
            ran += 1
            failed += 1
            if len(failures) < 3:
                failures.append(f"{case.name}: {type(error).__name__}: {error}")
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
    return ran, skipped, failed, failures


def run_suite(impl_dir: Path, suite: Path) -> bool:
    environment = dict(os.environ, QUOTA_LEDGER_DIR=str(impl_dir), QUOTA_LEDGER_IMPL="quota_ledger")
    completed = subprocess.run(
        ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(suite), "-q"],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    return completed.returncode != 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--suite", type=Path)
    parser.add_argument(
        "--corpus",
        action="append",
        default=[],
        metavar="NAME=PACKAGE_DIR",
        help="An instrument: a name and the generated case package it runs.",
    )
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()

    corpora: dict[str, list[Any]] = {}
    for entry in arguments.corpus:
        name, _, path = entry.partition("=")
        corpora[name] = load_cases(Path(path).resolve())

    rows = load_catalogue(arguments.catalogue)
    pristine = (arguments.reference / "quota_ledger.py").read_text(encoding="utf-8")

    instruments = list(corpora) + (["suite"] if arguments.suite else [])
    table: dict[str, dict[str, str]] = {}
    controls: dict[str, Any] = {}

    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        impl_dir = root / "impl"
        impl_dir.mkdir()
        work_root = root / "work"
        work_root.mkdir()
        target = impl_dir / "quota_ledger.py"

        # CONTROL FIRST. A red control means every "kill" below is noise.
        target.write_text(pristine, encoding="utf-8")
        for name, cases in corpora.items():
            ran, skipped, failed, failures = run_corpus(cases, impl_dir, work_root)
            controls[name] = {
                "cases": len(cases),
                "ran": ran,
                "skipped": skipped,
                "failed_on_green": failed,
                "failures": failures,
            }
        if arguments.suite:
            controls["suite"] = {"failed_on_green": int(run_suite(impl_dir, arguments.suite))}

        for row in rows:
            mutant = row["id"]
            occurrences = pristine.count(row["find"])
            if occurrences != 1:
                table[mutant] = {name: f"UNAPPLIED({occurrences})" for name in instruments}
                continue
            target.write_text(pristine.replace(row["find"], row["replace"], 1), encoding="utf-8")
            try:
                verdicts: dict[str, str] = {}
                for name, cases in corpora.items():
                    if controls[name]["failed_on_green"]:
                        # A red control makes every kill from that instrument
                        # unreadable: a case that fails on the unmutated
                        # reference fails on the mutated one too, and would be
                        # counted as a kill it did not earn.
                        verdicts[name] = "CONTROL_RED"
                        continue
                    _, _, failed, _ = run_corpus(cases, impl_dir, work_root)
                    verdicts[name] = "KILLED" if failed else "SURVIVED"
                if arguments.suite:
                    verdicts["suite"] = "KILLED" if run_suite(impl_dir, arguments.suite) else "SURVIVED"
                table[mutant] = verdicts
            finally:
                target.write_text(pristine, encoding="utf-8")

    by_class: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        fault_class = row.get("fault_class", "unclassified")
        for instrument in instruments:
            by_class[fault_class][instrument].append(table[row["id"]][instrument])

    report = {
        "catalogue": str(arguments.catalogue),
        "instruments": instruments,
        "controls": controls,
        "per_mutant": table,
        "per_class": {
            fault_class: {
                instrument: f"{verdicts.count('KILLED')} of {len(verdicts)}"
                for instrument, verdicts in instruments_map.items()
            }
            for fault_class, instruments_map in by_class.items()
        },
    }
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
