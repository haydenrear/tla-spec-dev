#!/usr/bin/env python3
"""Run a seeded catalogue and DECIDE ITS CONTROLS. Per class, per instrument.

Descended from HP-06's `measure/run_arm_kill_table.py`, which is left exactly as
it ran. What this driver adds is the thing that makes a table readable rather
than merely printable:

**A CONTROL VERDICT IS COMPUTED, NOT LEFT TO THE READER.** A catalogue declares
`control_role = "positive"` or `"negative"`. A positive control must be KILLED
by every instrument it is declared against; a negative control must SURVIVE
every one. This driver checks that and exits nonzero when a control is red, so a
run whose instrument is broken cannot quietly ship a table of kills.

**A DECLARED LIMITATION IS NOT A KILL AND NOT A SURVIVAL.** A control may carry
`limitation_on = [...]`: instruments on which the catalogue states, with a
reason, that the mutant cannot be decided. Those cells are reported as
`NOT_DECIDABLE` with the reason attached, they are excluded from the control
verdict, and they are excluded from the class denominator. "Not seeded", "not
caught" and "not decidable" are three different claims and this file never
blurs them.

**EXECUTABILITY IS REPORTED.** Every run records, per instrument and per action,
how many cases ran, how many failed and how many were skipped under which named
rule. A `SURVIVED` cell over an action with `ran: 0` is not evidence and the
JSON says so in the same object.

**FILE FINDINGS, FIX NOTHING.** Nothing here repairs a mutant, retries a
failure, re-runs an instrument until a number improves, or reports the best of
several runs.

Reproducing, in full. The four corpora first -- write them outside the repo,
the whole-view one is 66 MB -- and note that `generate cases` exits NONZERO on
this fixture because 43,128 cases are over its declared cap. It writes the
corpus anyway and that refusal is HP-03-DF-02, still open::

    python3 scripts/tla_spec_dev.py --spec-root specs generate cases \\
      examples/validation/ab/model/QuotaLedger.tla \\
      examples/validation/ab/model/QuotaLedger.cfg \\
      --out <scratch>/specs/corpus-whole --package quota_whole --view internal
    # ... the same with `--negative-cases only` into corpus-neg, and the two
    # Aspect_*.tla slices with --module-path examples/validation/ab/model and
    # --state-projector aspect_projectors:project_reservations / project_ledger
    # (see specs/results/scorecards/.../GOAL-catch-bugs/README.md, unchanged).

Then, per tree::

    python3 examples/validation/ab/eval/run_controls.py --label EVAL-STABLE \\
      --tree examples/validation/ab --module-dir reference \\
      --binding reference_binding \\
      --catalogue examples/validation/ab/seeded_faults.toml \\
      --catalogue examples/validation/ab/eval/controls.toml \\
      --instrument corpus-whole=<scratch>/specs/corpus-whole/spec-unit/quota_whole \\
      --instrument corpus-neg=<scratch>/specs/corpus-neg/spec-unit/quota_neg \\
      --instrument corpus-slice-res=<scratch>/specs/corpus-slice-res/spec-unit/quota_slice_res \\
      --instrument corpus-slice-led=<scratch>/specs/corpus-slice-led/spec-unit/quota_slice_led \\
      --instrument map-silent=<scratch>/specs/corpus-whole/spec-unit/quota_whole:silent \\
      --instrument map-checking=<scratch>/specs/corpus-whole/spec-unit/quota_whole:checking \\
      --suite examples/validation/ab/tests/test_behavior.py \\
      --out <out>.json

For arm A, swap `--tree`/`--module-dir`/`--binding` for the arm and use
`measure/catalogue_arm_a.toml` with `eval/controls_arm_a.toml`.

`results/` holds five runs, with the scratch paths rewritten to `<scratch>` and
`<out>` so they diff clean: `A0-before-fix-clean.json` (the generator
unrepaired, M07 red, reproducing the shipped arm-A row cell for cell),
`final-run-1/2.json` (the reference) and `arm-a-run-1/2.json` (arm A). Each
pair is byte-identical, failing executions and all.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from contextlib import ExitStack
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
MEASURE = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting/measure"
for entry in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), str(HERE), str(MEASURE),
              str(MEASURE / "generated")):
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
LOCAL_MODULES = ("oracle", "reference_binding", "arm_a_binding", "arm_b_binding")

KILLED = "KILLED"
SURVIVED = "SURVIVED"
CONTROL_RED = "CONTROL_RED"
NOT_DECIDABLE = "NOT_DECIDABLE"


def load_catalogue(paths: list[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Every mutant, plus the control record that scopes and retires them."""
    mutants: list[dict[str, Any]] = []
    limitations: list[dict[str, Any]] = []
    retired: dict[str, dict[str, Any]] = {}
    for path in paths:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
        mutants.extend(document.get("mutants", []))
        limitations.extend(document.get("limitation", []))
        for entry in document.get("retired_control", []):
            retired[entry["mutant"]] = entry
    by_mutant: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for entry in limitations:
        by_mutant[entry["mutant"]][entry["instrument"]] = entry
    return mutants, {"limitations": dict(by_mutant), "retired": retired}


def verify_limitation(entry: dict[str, Any], control: dict[str, Any]) -> dict[str, Any]:
    """Check a declared limitation against the run's OWN executability counts.

    A limitation is a claim that an instrument cannot decide a mutant. Believing
    it on the catalogue's say-so would make it a suppression key with better
    manners, so it must name an action, a polarity and the count that must be
    zero, and the number is read off the control run rather than asserted.
    """
    action = entry.get("witness_action")
    polarity = entry.get("witness_polarity", "positive")
    expected = entry.get("witness_ran_must_be", 0)
    counts = control.get("per_action", {}).get(action, {})
    key = "ran_accepting" if polarity == "positive" else "ran_refusing"
    observed = counts.get(key, 0)
    return {
        "reason": entry.get("reason", "").strip(),
        "witness": f"{polarity} {action} cases executed",
        "witness_expected": expected,
        "witness_observed": observed,
        "verified": observed == expected,
    }


def run_reality_witness(spec: str, module_dir: Path, work_dir: Path) -> bool | str:
    """Does this tree exhibit the fault? Run in a subprocess so no import sticks."""
    module_name, _, function = spec.partition(":")
    program = (
        "import importlib, sys\n"
        f"sys.path.insert(0, {str(module_dir)!r})\n"
        f"sys.path.insert(0, {str(HERE)!r})\n"
        "quota_ledger = importlib.import_module('quota_ledger')\n"
        f"witnesses = importlib.import_module({module_name!r})\n"
        "from pathlib import Path\n"
        f"print(bool(getattr(witnesses, {function!r})(quota_ledger, Path({str(work_dir)!r}))))\n"
    )
    work_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True,
    )
    if completed.returncode != 0:
        return f"witness raised: {completed.stderr.strip().splitlines()[-1:]}"
    return completed.stdout.strip() == "True"


def load_cases(package_dir: Path) -> list[Any]:
    parent = str(package_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    module = importlib.import_module(f"{package_dir.name}.cases")
    importlib.reload(module)
    return list(module.CASES)


def _purge_modules() -> None:
    """Drop the tree and the instrument so a seeded mutant is the code under test."""
    for name in list(sys.modules):
        if name in LOCAL_MODULES or name.split(".")[0] in ARM_MODULE_PREFIXES:
            del sys.modules[name]


def _purge_bytecode(root: Path) -> None:
    """Delete every `__pycache__` under the impl tree between mutants.

    HP-06's adversarial channel rejected this as a finding on the argument that
    every mutant in the sealed catalogue happens to change its file's size, so
    CPython's `(mtime, size)` invalidation cannot serve a stale `.pyc` (its R2).
    It recorded that the harness is one whitespace-neutral mutant away from a
    silent survivor. This costs nothing and removes the dependency on that
    coincidence.
    """
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def run_corpus(
    cases: list[Any], module_dir: Path, work_root: Path, binding: str,
    provider: Any, mapping_path: Path,
) -> dict[str, Any]:
    """Run one corpus under one mapping and account for every case."""
    os.environ["QUOTA_LEDGER_DIR"] = str(module_dir)
    os.environ["QUOTA_LEDGER_BINDING"] = binding
    os.environ["TLA_SPEC_DEV_MAPPING"] = str(mapping_path)
    _purge_modules()
    oracle = importlib.import_module("oracle")

    negative = oracle.NegativeAdapter()
    positive = oracle.PositiveAdapter()
    ledger = oracle.Ledger()
    failures: list[str] = []
    for index, case in enumerate(cases):
        accepting = "negative" not in case.labels
        adapter = positive if accepting else negative
        action = case.input.action
        verdict = adapter.can_run(case)
        if verdict is not True and not (isinstance(verdict, tuple) and verdict[0]):
            reason = verdict[1] if isinstance(verdict, tuple) and len(verdict) > 1 else "unstated"
            ledger.skipped[action] += 1
            ledger.skipped_by_rule[reason] += 1
            continue
        work_dir = work_root / f"case-{index}"
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
            ledger.ran[action] += 1
            ledger.ran_positive[action] += int(accepting)
        except Exception as error:  # a failing case is the signal, not an incident
            ledger.ran[action] += 1
            ledger.ran_positive[action] += int(accepting)
            ledger.failed[action] += 1
            if len(failures) < 3:
                failures.append(f"{case.name}: {type(error).__name__}: {error}")
        finally:
            adapter.port = None
            shutil.rmtree(work_dir, ignore_errors=True)
    report = ledger.as_dict()
    report["cases"] = len(cases)
    report["failures"] = failures
    return report


def run_suite(module_dir: Path, suite: Path) -> dict[str, Any]:
    environment = dict(
        os.environ, QUOTA_LEDGER_DIR=str(module_dir), QUOTA_LEDGER_IMPL="quota_ledger",
    )
    completed = subprocess.run(
        ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(suite), "-q"],
        cwd=REPO_ROOT, env=environment, capture_output=True, text=True,
    )
    tail = [line for line in completed.stdout.splitlines() if line.strip()][-1:]
    # pytest's summary carries its own wall clock. Two runs of the same
    # measurement must be byte-identical INCLUDING the failing executions, so
    # the one nondeterministic field in this artifact is removed rather than
    # excused: an elapsed time is not evidence about a mutant.
    tail = [re.sub(r" in \d+\.\d+s$", "", line) for line in tail]
    return {"total_failed": int(completed.returncode != 0), "failures": tail}


def control_verdict(
    row: dict[str, Any],
    cells: dict[str, str],
    record: dict[str, Any],
    witness: dict[str, Any] | None,
) -> dict[str, Any]:
    """Decide a declared control. Silence is never a pass."""
    mutant = row["id"]
    role = str(row.get("control_role", "")).split()[0] if row.get("control_role") else ""
    if role not in ("positive", "negative"):
        return {}
    retired = record["retired"].get(mutant)
    if retired:
        return {
            "role": f"{retired.get('was', role)} (RETIRED)",
            "decides_nothing": True,
            "green": True,
            "retirement_reason": str(retired.get("reason", "")).strip(),
            "replaced_by": retired.get("replaced_by"),
            "measured_cells": dict(sorted(cells.items())),
        }
    wanted = KILLED if role == "positive" else SURVIVED
    verdict: dict[str, Any] = {"role": role, "must_be": wanted}
    if witness is not None:
        verdict["reality_witness"] = witness
        if not witness.get("separates_the_trees"):
            # No proof the mutant is a fault, so "survived" is not evidence
            # about any instrument and this row decides nothing.
            verdict.update({"green": False, "decides_nothing": True,
                            "instruments_wrong": ["reality witness"]})
            return verdict
    decided = {name: cell for name, cell in cells.items() if cell != NOT_DECIDABLE}
    wrong = sorted(name for name, cell in decided.items() if cell != wanted)
    verdict.update({
        "instruments_decided": sorted(decided),
        "instruments_not_decidable": sorted(name for name in cells if name not in decided),
        "green": not wrong and bool(decided),
        "instruments_wrong": wrong,
    })
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--tree", type=Path, required=True,
                        help="Directory copied whole; mutant `path` is relative to it.")
    parser.add_argument("--module-dir", default=".",
                        help="Where `quota_ledger` is importable inside the tree.")
    parser.add_argument("--binding", required=True)
    parser.add_argument("--catalogue", type=Path, action="append", required=True)
    parser.add_argument("--instrument", action="append", default=[],
                        metavar="NAME=PACKAGE_DIR[:PROVIDER]")
    parser.add_argument("--suite", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()

    specs: list[tuple[str, Path, str]] = []
    for entry in arguments.instrument:
        name, _, rest = entry.partition("=")
        path, _, provider = rest.partition(":")
        specs.append((name, Path(path).resolve(), provider or "none"))

    corpora = {name: load_cases(path) for name, path, _ in specs}
    rows, record = load_catalogue(arguments.catalogue)
    instruments = [name for name, _, _ in specs] + (["suite"] if arguments.suite else [])

    table: dict[str, dict[str, str]] = {}
    evidence: dict[str, dict[str, Any]] = {}
    witnesses: dict[str, dict[str, Any]] = {}

    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        impl_dir = root / "impl"
        work_root = root / "work"
        work_root.mkdir(parents=True)
        shutil.copytree(arguments.tree, impl_dir,
                        ignore=shutil.ignore_patterns("__pycache__", "tests", "*.md", "eval"))
        module_dir = (impl_dir / arguments.module_dir).resolve()
        pristine = {
            row["path"]: (impl_dir / row["path"]).read_text(encoding="utf-8") for row in rows
        }

        def run_all() -> dict[str, Any]:
            _purge_bytecode(impl_dir)
            outcome: dict[str, Any] = {}
            for name, _, provider_key in specs:
                mapping_name, provider = PROVIDERS[provider_key]
                outcome[name] = run_corpus(
                    corpora[name], module_dir, work_root, arguments.binding,
                    provider, MEASURE / mapping_name,
                )
                outcome[name]["mapping"] = mapping_name
            if arguments.suite:
                outcome["suite"] = run_suite(module_dir, arguments.suite)
            return outcome

        # CONTROL FIRST. A red control makes every "kill" below unreadable.
        controls = run_all()

        for row in rows:
            mutant = row["id"]
            source = pristine[row["path"]]
            occurrences = source.count(row["find"])
            if occurrences != 1:
                table[mutant] = {name: f"UNAPPLIED({occurrences})" for name in instruments}
                continue
            declared = record["limitations"].get(mutant, {})
            limitation = {
                name: verify_limitation(entry, controls.get(name, {}))
                for name, entry in declared.items()
                if name in instruments
            }
            not_decidable = {name for name, checked in limitation.items() if checked["verified"]}
            target = impl_dir / row["path"]
            if row.get("reality_witness"):
                # PRISTINE FIRST, while the tree is still unmutated.
                clean_witness = run_reality_witness(
                    row["reality_witness"], module_dir, work_root / "witness-clean",
                )
                witnesses[mutant] = {"spec": row["reality_witness"],
                                     "on_pristine_tree": clean_witness}
            target.write_text(source.replace(row["find"], row["replace"], 1), encoding="utf-8")
            try:
                if row.get("reality_witness"):
                    _purge_bytecode(impl_dir)
                    mutated_witness = run_reality_witness(
                        row["reality_witness"], module_dir, work_root / "witness-mutant",
                    )
                    witnesses[mutant]["on_mutated_tree"] = mutated_witness
                    witnesses[mutant]["separates_the_trees"] = (
                        witnesses[mutant]["on_pristine_tree"] is False
                        and mutated_witness is True
                    )
                observed = run_all()
                table[mutant] = {
                    name: (
                        NOT_DECIDABLE if name in not_decidable
                        else CONTROL_RED if controls[name]["total_failed"]
                        else (KILLED if observed[name]["total_failed"] else SURVIVED)
                    )
                    for name in instruments
                }
                evidence[mutant] = {
                    "declared_limitations": limitation,
                    "why": {
                        name: observed[name]["failures"]
                        for name in instruments
                        if observed[name]["failures"]
                    },
                    "executed": {
                        name: observed[name].get("per_action", {}) for name in instruments
                    },
                }
            finally:
                target.write_text(source, encoding="utf-8")
                _purge_bytecode(impl_dir)

    by_class: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        fault_class = row.get("fault_class", "unclassified")
        for instrument in instruments:
            by_class[fault_class][instrument].append(table[row["id"]][instrument])

    control_rows = {
        row["id"]: control_verdict(row, table[row["id"]], record, witnesses.get(row["id"]))
        for row in rows
        if row.get("control_role")
    }

    # An action nobody executed cannot support a SURVIVED cell. Named, not implied.
    unexecuted = {
        name: sorted(
            action
            for action, counts in controls[name].get("per_action", {}).items()
            if counts["ran"] == 0
        )
        for name in instruments
        if controls[name].get("per_action")
    }

    report = {
        "label": arguments.label,
        "tree": str(arguments.tree),
        "catalogues": [str(path) for path in arguments.catalogue],
        "mutants": len(rows),
        "instruments": instruments,
        "controls_on_unmutated_code": controls,
        "actions_with_zero_executed_cases": unexecuted,
        "control_verdicts": control_rows,
        "reality_witnesses": witnesses,
        "retired_controls": record["retired"],
        "per_mutant": table,
        "evidence": evidence,
        "per_class": {
            fault_class: {
                instrument: (
                    f"{verdicts.count(KILLED)} of "
                    f"{sum(1 for v in verdicts if v in (KILLED, SURVIVED))}"
                    + (
                        f" ({verdicts.count(NOT_DECIDABLE)} not decidable)"
                        if NOT_DECIDABLE in verdicts else ""
                    )
                )
                for instrument, verdicts in instruments_map.items()
            }
            for fault_class, instruments_map in by_class.items()
        },
    }
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    red = sorted(name for name, verdict in control_rows.items() if not verdict.get("green"))
    print(json.dumps({
        "label": arguments.label,
        "controls_red": red,
        "control_verdicts": control_rows,
        "actions_with_zero_executed_cases": unexecuted,
        "out": str(arguments.out),
    }, indent=2, sort_keys=True))
    return 1 if red else 0


if __name__ == "__main__":
    raise SystemExit(main())
