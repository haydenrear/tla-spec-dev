#!/usr/bin/env python3
"""HP-06's kill table: per class, per instrument, PER ARM. Never one rate.

Descended from HP-03's `run_kill_table.py` and HP-05's
`run_mapping_kill_table.py` so the three tables are comparable cell for cell.
The assertions are the SHIPPED ones -- `assert_case_result_per_field` and
`call_adapter` are imported, never reimplemented -- and the content assertion is
the one `scripts/generate_python.py` GENERATED, imported from the generated
package. What is local to HP-06 is the loop and the per-arm binding, not the
oracle.

What differs from its two ancestors: an arm is a TREE, not a file. It is copied
whole into a scratch directory, one mutant is written into the file that mutant
names, and every instrument runs against the copy. Nothing under
`specs/results/scorecards/hexagonal-prompting/arms/` is ever written to.

FILE FINDINGS, FIX NOTHING. Nothing here repairs a mutant, retries a failure,
re-runs an instrument until a number improves, or reports the best of several
runs.
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
REPO_ROOT = HERE.parents[4]
for entry in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), str(HERE), str(HERE / "generated")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

from scripts.run_generated_case_adapters import assert_case_result_per_field  # noqa: E402
from spec_double_compiler.runtime import EffectProviderContext, call_adapter  # noqa: E402

_generated = importlib.import_module("quota_ledger_effects.effect_providers")

PORT = "LedgerAppendPort"
PORT_ACTIONS = ("Commit", "CloseTenant")

#: provider key -> (declared mapping file, provider bound by it)
PROVIDERS: dict[str, tuple[str, Any]] = {
    "none": ("case_adapters.map-none.toml", None),
    "silent": ("case_adapters.map-silent.toml", _generated.silent_ledger_append_port_provider),
    "checking": ("case_adapters.map-checking.toml", _generated.ledger_append_port_provider),
}

ARM_MODULE_PREFIXES = ("quota_ledger",)
LOCAL_MODULES = ("arm_adapter", "arm_a_binding", "arm_b_binding")


def load_catalogue(path: Path) -> list[dict[str, Any]]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["mutants"]


def load_cases(package_dir: Path) -> list[Any]:
    parent = str(package_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    module = importlib.import_module(f"{package_dir.name}.cases")
    importlib.reload(module)
    return list(module.CASES)


def _purge_modules() -> None:
    """Drop the arm and the instrument so a seeded mutant is the code under test."""
    for name in list(sys.modules):
        if name in LOCAL_MODULES or name.split(".")[0] in ARM_MODULE_PREFIXES:
            del sys.modules[name]


def run_corpus(
    cases: list[Any], impl_dir: Path, work_root: Path, binding: str,
    provider: Any, mapping_path: Path,
) -> tuple[int, int, int, list[str]]:
    """``(ran, skipped, failed, first failures)`` over one corpus + one mapping."""
    os.environ["QUOTA_LEDGER_DIR"] = str(impl_dir)
    os.environ["QUOTA_LEDGER_BINDING"] = binding
    os.environ["TLA_SPEC_DEV_MAPPING"] = str(mapping_path)
    _purge_modules()
    adapter_module = importlib.import_module("arm_adapter")

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
                        port_name=PORT, action=action, case=case, work_dir=work_dir,
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
    environment = dict(
        os.environ, QUOTA_LEDGER_DIR=str(impl_dir), QUOTA_LEDGER_IMPL="quota_ledger",
    )
    completed = subprocess.run(
        ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(suite), "-q"],
        cwd=REPO_ROOT, env=environment, capture_output=True, text=True,
    )
    return completed.returncode != 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True)
    parser.add_argument("--arm-root", type=Path, required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument(
        "--instrument", action="append", default=[], metavar="NAME=PACKAGE_DIR[:PROVIDER]",
        help="An instrument: a name, the generated case package it runs, and "
             "optionally which effect-provider mapping is bound (none/silent/checking).",
    )
    parser.add_argument("--suite", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()

    specs: list[tuple[str, Path, str]] = []
    for entry in arguments.instrument:
        name, _, rest = entry.partition("=")
        path, _, provider = rest.partition(":")
        specs.append((name, Path(path).resolve(), provider or "none"))

    corpora = {name: load_cases(path) for name, path, _ in specs}
    rows = load_catalogue(arguments.catalogue)

    instruments = [name for name, _, _ in specs] + (["suite"] if arguments.suite else [])
    table: dict[str, dict[str, str]] = {}
    controls: dict[str, Any] = {}

    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        impl_dir = root / "impl"
        work_root = root / "work"
        work_root.mkdir(parents=True)
        shutil.copytree(arguments.arm_root, impl_dir,
                        ignore=shutil.ignore_patterns("__pycache__", "tests", "*.md"))
        pristine = {
            row["path"]: (impl_dir / row["path"]).read_text(encoding="utf-8") for row in rows
        }

        def run_all() -> dict[str, Any]:
            outcome: dict[str, Any] = {}
            for name, _, provider_key in specs:
                mapping_name, provider = PROVIDERS[provider_key]
                ran, skipped, failed, failures = run_corpus(
                    corpora[name], impl_dir, work_root, arguments.binding,
                    provider, HERE / mapping_name,
                )
                outcome[name] = {
                    "mapping": mapping_name, "cases": len(corpora[name]), "ran": ran,
                    "skipped": skipped, "failed": failed, "failures": failures,
                }
            if arguments.suite:
                outcome["suite"] = {"failed": int(run_suite(impl_dir, arguments.suite))}
            return outcome

        # CONTROL FIRST. A red control makes every "kill" below unreadable.
        controls = run_all()
        for name in instruments:
            controls[name]["failed_on_green"] = controls[name].pop("failed")

        for row in rows:
            mutant = row["id"]
            source = pristine[row["path"]]
            occurrences = source.count(row["find"])
            if occurrences != 1:
                table[mutant] = {name: f"UNAPPLIED({occurrences})" for name in instruments}
                continue
            target = impl_dir / row["path"]
            target.write_text(source.replace(row["find"], row["replace"], 1), encoding="utf-8")
            try:
                observed = run_all()
                table[mutant] = {
                    name: (
                        "CONTROL_RED" if controls[name]["failed_on_green"]
                        else ("KILLED" if observed[name]["failed"] else "SURVIVED")
                    )
                    for name in instruments
                }
            finally:
                target.write_text(source, encoding="utf-8")

    by_class: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        fault_class = row.get("fault_class", "unclassified")
        for instrument in instruments:
            by_class[fault_class][instrument].append(table[row["id"]][instrument])

    report = {
        "arm": arguments.arm,
        "arm_root": str(arguments.arm_root),
        "catalogue": str(arguments.catalogue),
        "mutants_re_anchored": len(rows),
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
