#!/usr/bin/env python3
"""HP-05's kill table: one corpus, three mappings. Per class, per instrument.

Ticket-local measurement driver, built from HP-03's (`run_kill_table.py`) so
the two tables are comparable cell for cell. The assertions are the SHIPPED
ones -- `assert_case_result_per_field` and `call_adapter` are imported, never
reimplemented -- and the content assertion is the one
`scripts/generate_python.py` GENERATED, imported from the generated package.
What is ticket-local is the loop and the codec, not the oracle.

THE ONLY THING THAT VARIES BETWEEN THE THREE INSTRUMENTS IS ONE MAPPING LINE:

  map-none      no `[effect_providers.*]` table at all. This is HP-03's
                configuration and exists as a REPRODUCTION CONTROL: if its
                column does not match HP-03's `corpus-whole` column, the seam
                this instrument installs changed the baseline and every other
                number here is unreadable.
  map-silent    the port bound to the generated `silent_*_provider`.
  map-checking  the port bound to the generated content-asserting provider --
                which is what codegen now writes by default.

Same corpus, same cases, same adapter, same seam, same mutants, same order.

FILE FINDINGS, FIX NOTHING. Nothing here repairs a mutant, retries a failure,
or re-runs an instrument until a number improves.
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
from contextlib import ExitStack
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "generated"))

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

from scripts.run_generated_case_adapters import assert_case_result_per_field  # noqa: E402
from spec_double_compiler.runtime import EffectProviderContext, call_adapter  # noqa: E402

#: Read from the GENERATED package. If codegen stops emitting these, this
#: driver stops running -- which is the point of importing rather than copying.
_generated = importlib.import_module("quota_ledger_effects.effect_providers")

PORT = "LedgerAppendPort"
PORT_ACTIONS = ("Commit", "CloseTenant")

#: instrument name -> (declared mapping file, provider bound by it).
MAPPINGS: dict[str, tuple[Path, Any]] = {
    "map-none": (HERE / "case_adapters.map-none.toml", None),
    "map-silent": (HERE / "case_adapters.map-silent.toml", _generated.silent_ledger_append_port_provider),
    "map-checking": (HERE / "case_adapters.map-checking.toml", _generated.ledger_append_port_provider),
}


def load_catalogue(path: Path) -> list[dict[str, Any]]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["mutants"]


def load_cases(package_dir: Path) -> list[Any]:
    parent = str(package_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    module = importlib.import_module(f"{package_dir.name}.cases")
    importlib.reload(module)
    return list(module.CASES)


def run_corpus(
    cases: list[Any], impl_dir: Path, work_root: Path, provider: Any, mapping_path: Path
) -> tuple[int, int, int, list[str]]:
    """``(ran, skipped, failed, first failures)`` over one corpus + one mapping."""
    os.environ["QUOTA_LEDGER_DIR"] = str(impl_dir)
    os.environ["TLA_SPEC_DEV_MAPPING"] = str(mapping_path)
    for name in [key for key in sys.modules if key in ("quota_ledger", "quota_effect_adapter")]:
        del sys.modules[name]
    adapter_module = importlib.import_module("quota_effect_adapter")

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
        action = case.input.action
        try:
            with ExitStack() as scope:
                adapter.port = None
                if provider is not None and action in PORT_ACTIONS:
                    context = EffectProviderContext(
                        port_name=PORT,
                        action=action,
                        case=case,
                        work_dir=work_dir,
                    )
                    adapter.port = scope.enter_context(provider.bind(context))
                result = call_adapter(adapter, case, work_dir)
                assert_case_result_per_field(case=case, result=result)
            ran += 1
        except Exception as error:  # a failing case is the signal, not an incident
            ran += 1
            failed += 1
            if len(failures) < 3:
                failures.append(f"{case.name}: {type(error).__name__}: {error}")
        finally:
            adapter.port = None
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
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--suite", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()

    cases = load_cases(arguments.corpus.resolve())
    rows = load_catalogue(arguments.catalogue)
    pristine = (arguments.reference / "quota_ledger.py").read_text(encoding="utf-8")

    instruments = list(MAPPINGS) + (["suite"] if arguments.suite else [])
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
        for name, (mapping_path, provider) in MAPPINGS.items():
            ran, skipped, failed, failures = run_corpus(cases, impl_dir, work_root, provider, mapping_path)
            controls[name] = {
                "mapping": str(mapping_path),
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
                for name, (mapping_path, provider) in MAPPINGS.items():
                    if controls[name]["failed_on_green"]:
                        verdicts[name] = "CONTROL_RED"
                        continue
                    _, _, failed, _ = run_corpus(cases, impl_dir, work_root, provider, mapping_path)
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
        "corpus": str(arguments.corpus),
        "instruments": instruments,
        "mappings": {name: str(path) for name, (path, _) in MAPPINGS.items()},
        "mapping_note": (
            "Every column names its mapping. map-none and map-silent carry NO "
            "durable-write oracle: their kills are a floor, not a total."
        ),
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
