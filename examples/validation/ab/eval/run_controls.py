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

**A DEMONSTRATED KILL IS NOT ERASABLE BY A DECLARATION** (EVAL-RERUN-DF-02).
Until EVAL-SUPPRESS this file computed `NOT_DECIDABLE` *before* the mutated run
was consulted, so a declared limitation converted a cell the instrument
demonstrably KILLED into `NOT_DECIDABLE`, with `verified: true`, `green: true`
and exit 0 -- a suppression key with better manners, which is the exact thing
the construct was introduced to avoid. The mutated run is now decided FIRST and
a limitation may only convert a `SURVIVED` cell. A limitation over a `KILLED`
cell is reported as **contradicted by evidence**, the kill stands, and the run
exits nonzero: a limitation that is not real is a defect in the record and is
never a quiet one.

Three further things a limitation must now survive, each of them a way a check
could pass by looking at nothing:

* **A missing count is not a measured zero** (EVAL-RERUN-DF-04). `.get(key, 0)`
  made an action that appears nowhere in the model "verify". The witness now
  carries a `witness_basis`, and an action no instrument in the run ever saw
  cannot verify anything.
* **A limitation's scope is falsifiable by the run's own data** (EVAL-RERUN-DF-03).
  A witness of the form "instrument X executes zero `<action, polarity>` cases"
  claims the mutant is only observable through that action. If some OTHER
  instrument satisfies the same condition and KILLS the mutant anyway, the run
  has proved the mutant observable without that action; the limitation is
  rejected and the cell decided normally.
* **A run with no positive control that decides anything is not green.**
  Retirement stops a control deciding; it must not thereby leave a run with no
  control at all and nobody saying so.

**SUPPRESSION-SHAPED KEYS ARE REPORTED.** Every catalogue is scanned with
`scripts/kill_test.py`'s own scanner and the keys it finds -- `limitation`,
`witness_ran_must_be`, `retired_control` among them -- are written into the run
artifact under `declared_suppression_keys`. They are checked, never honored on
their say-so, and now never invisible.

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

`results/eval-suppress/` holds EVAL-RERUN's own data re-decided by the repaired
driver. **Those five sealed runs are not edited and not restated.** What changed
under them, and what did not:

* `reference-repaired.json` and `arm-a-repaired.json` -- **not one cell moves.**
  Every key of `final-run-1.json` is reproduced except two, both intended:
  `skipped_by_rule` splits 294 into 28 + 266 (see `oracle.py`), and `evidence`
  gains `witness_basis`. Byte-identity with the sealed files no longer holds;
  per-cell identity does.
* `arm-b-repaired-sealed-catalogue.json` -- arm B against its sealed catalogues
  alone. **One cell moves**, `M07 / corpus-slice-led`
  `NOT_DECIDABLE -> SURVIVED`, because arm B's own `corpus-neg` kills M07 while
  executing zero accepted `Reserve` cases and so falsifies that limitation's
  scope. Arm B's positive control goes red and the run exits 1. It should have.
* `arm-b-repaired-with-P01.json` -- the same run plus
  `controls_rerun_arm_b.toml`, which retires M07 as a control and seeds P01 in
  its place. Exit 0, on a control that can fail.
* `arm-b-P01-noreserve-ablation.json` -- the proof of that last clause.
  `corpus-whole` with every `Reserve` case deleted, which is HP-06's regression:
  **M07 = KILLED, P01 = SURVIVED.** The old control stays green through its own
  failure mode; the replacement goes red, exit 1.
* `probe-DF02-{old,repaired}-driver.json` -- arm A's `corpus-neg` limitation
  copied verbatim onto arm B, where that cell is a demonstrated kill. OLD:
  `NOT_DECIDABLE`, `verified: true`, `green: true`, exit 0. REPAIRED: `KILLED`,
  `contradicted_by_evidence`, control red, exit 1.

Nothing here was re-run until a number improved, and no cell that moved moved
toward a better score: one `NOT_DECIDABLE` became a `SURVIVED`, one green
control became red, and one class denominator grew.
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
import types
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

from scripts.kill_test import scan_for_suppression  # noqa: E402
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
    suppression: dict[str, list[str]] = {}
    for path in paths:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
        mutants.extend(document.get("mutants", []))
        limitations.extend(document.get("limitation", []))
        for entry in document.get("retired_control", []):
            retired[entry["mutant"]] = entry
        # Reported, never honored on its say-so. `limitation`, `retired_control`
        # and `witness_ran_must_be` are on `scripts/kill_test.py`'s list, so
        # every run artifact now names the suppression-shaped keys its own
        # catalogues carry (EVAL-RERUN-DF-02).
        found = sorted(scan_for_suppression(document))
        if found:
            suppression[str(path)] = found
    by_mutant: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for entry in limitations:
        by_mutant[entry["mutant"]][entry["instrument"]] = entry
    return mutants, {
        "limitations": dict(by_mutant),
        "retired": retired,
        "declared_suppression_keys": suppression,
    }


def _actions_in_run(controls: dict[str, Any]) -> set[str]:
    """Every action name some instrument in THIS run actually accounted for."""
    return {
        action
        for record in controls.values()
        for action in (record.get("per_action") or {})
    }


def _witness_key(polarity: str) -> str:
    return "ran_accepting" if polarity == "positive" else "ran_refusing"


def _witness_count(
    control: dict[str, Any], action: Any, polarity: str, known_actions: set[str],
) -> tuple[int | None, str]:
    """The run's own count for one `<action, polarity>`, and WHAT it rests on.

    EVAL-RERUN-DF-04. The old reading was `counts.get(key, 0)`, under which a
    missing key and a measured zero were the same number. They are not the same
    claim: an action that appears nowhere in this run is not an action that ran
    zero times, it is a name nobody checked. `None` means "not evaluable" and
    nothing verifies against it.
    """
    per_action = control.get("per_action")
    if per_action is None:
        return None, "instrument keeps no executability accounting"
    counts = per_action.get(action)
    if counts is not None:
        return counts.get(_witness_key(polarity), 0), "measured"
    if action in known_actions:
        # Real action of this run, absent from THIS corpus: a provable zero,
        # and a stronger one than "every case skipped".
        return 0, "action absent from this instrument's corpus"
    return None, "no action of this name ran anywhere in this run"


def verify_limitation(
    entry: dict[str, Any],
    control: dict[str, Any],
    known_actions: set[str] | None = None,
) -> dict[str, Any]:
    """Check a declared limitation against the run's OWN executability counts.

    A limitation is a claim that an instrument cannot decide a mutant. Believing
    it on the catalogue's say-so would make it a suppression key with better
    manners, so it must name an action, a polarity and the count that must be
    zero, and the number is read off the control run rather than asserted --
    and the number has to have been READ rather than defaulted.
    """
    action = entry.get("witness_action")
    polarity = entry.get("witness_polarity", "positive")
    expected = entry.get("witness_ran_must_be", 0)
    observed, basis = _witness_count(control, action, polarity, known_actions or set())
    return {
        "reason": entry.get("reason", "").strip(),
        "witness": f"{polarity} {action} cases executed",
        "witness_expected": expected,
        "witness_observed": observed,
        "witness_basis": basis,
        "verified": observed is not None and observed == expected,
    }


def falsify_limitation_scope(
    entry: dict[str, Any],
    checked: dict[str, Any],
    cells: dict[str, str],
    controls: dict[str, Any],
    known_actions: set[str],
    target: str | None = None,
) -> dict[str, Any]:
    """Reject a limitation the run's own kills contradict (EVAL-RERUN-DF-03).

    ``witness_ran_must_be = 0`` on ``<action, polarity>`` asserts an IMPLICATION:
    an instrument that executes none of those cases cannot decide this mutant.
    That is falsifiable, and by data already in hand -- if another instrument
    executes none of them and KILLS the mutant, the mutant is observable without
    that action and the limitation is scoping the wrong thing.

    This is EVAL-RERUN's F1 stated mechanically. Arm B's M07 is killed by
    `corpus-neg`, whose control block records `Reserve: ran_accepting = 0`,
    which is the very condition arm A's identical limitation text calls
    undecidable. The same measured zero that scopes the control on one arm
    proves the scope wrong on the other.
    """
    if not checked.get("verified"):
        return checked
    polarity = entry.get("witness_polarity", "positive")
    action = entry.get("witness_action")
    expected = entry.get("witness_ran_must_be", 0)
    falsified = []
    for name, cell in cells.items():
        # The TARGET instrument killing it is DF-02's contradiction, reported
        # as that. This is about every OTHER instrument in the same run.
        if cell != KILLED or name == target:
            continue
        observed, _ = _witness_count(controls.get(name, {}), action, polarity, known_actions)
        if observed is not None and observed == expected:
            falsified.append(name)
    if falsified:
        checked = dict(checked)
        checked.update({
            "verified": False,
            "scope_falsified_by": sorted(falsified),
            "scope_falsified": (
                f"{sorted(falsified)} decided this mutant KILLED while itself executing "
                f"{expected} {polarity} {action} cases, so the mutant is observable "
                f"without them and this limitation does not scope it"
            ),
        })
    return checked


def decide_cells(
    instruments: list[str],
    controls: dict[str, Any],
    observed: dict[str, Any],
    declared: dict[str, dict[str, Any]],
    known_actions: set[str] | None = None,
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    """The mutated run first; a declaration may only ever downgrade a SURVIVAL.

    EVAL-RERUN-DF-02. A limitation exists so that an action an instrument never
    executed does not read as a fault it failed to catch. That is a statement
    about SURVIVALS. Over a `KILLED` cell it is not a scope note, it is an
    erasure, and over `CONTROL_RED` it would hide a broken instrument.
    """
    known_actions = known_actions or _actions_in_run(controls)
    raw = {
        name: (
            CONTROL_RED if controls[name]["total_failed"]
            else (KILLED if observed[name]["total_failed"] else SURVIVED)
        )
        for name in instruments
    }
    limitations = {
        name: falsify_limitation_scope(
            entry,
            verify_limitation(entry, controls.get(name, {}), known_actions),
            raw, controls, known_actions, name,
        )
        for name, entry in declared.items()
        if name in instruments
    }
    cells: dict[str, str] = {}
    for name in instruments:
        cell = raw[name]
        checked = limitations.get(name)
        if checked is not None and checked.get("verified"):
            if cell == SURVIVED:
                cell = NOT_DECIDABLE
            elif cell == KILLED:
                checked["contradicted_by_evidence"] = (
                    "this instrument KILLED the mutant; a demonstrated kill is not "
                    "erasable by a declaration, so the kill stands and the limitation "
                    "is false"
                )
            else:
                checked["not_applied"] = (
                    f"cell is {cell}; a limitation does not scope a broken instrument"
                )
        cells[name] = cell
    return cells, limitations


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


def _is_tree_module(name: str) -> bool:
    return name.split(".")[0] in ARM_MODULE_PREFIXES


def tree_handle_holders() -> set[str]:
    """Every imported module holding a handle on the tree under measurement.

    EVAL-RERUN-DF-01. The purge was a FIXED LIST of binding module names, so a
    binding whose name was not on the list kept a module-level
    `_impl = import_module("quota_ledger")` bound to the PRISTINE tree, every
    mutant then executed against unmutated code, and the run reported 11 of 11
    SURVIVED with green controls. It was caught only because the hand-written
    `suite` column in the same table disagreed with all six corpus columns --
    the first time in three rounds the suite caught anything, and not something
    to have to rely on twice.

    A list of names cannot be right, because the question is not what a module
    is called. It is whether it holds a handle, and the interpreter can answer
    that: any module-level value that IS a tree module, or whose `__module__`
    is one, survives a purge keyed on names and must not.
    """
    holders: set[str] = set()
    for name, module in list(sys.modules.items()):
        if module is None or _is_tree_module(name) or name in LOCAL_MODULES:
            continue
        origin = getattr(module, "__file__", None)
        if not origin or "site-packages" in origin or name in sys.stdlib_module_names:
            continue
        try:
            values = list(vars(module).values())
        except TypeError:  # pragma: no cover - exotic module objects
            continue
        for value in values:
            try:
                source = (
                    value.__name__ if isinstance(value, types.ModuleType)
                    else getattr(value, "__module__", None)
                )
            except Exception:  # pragma: no cover - properties that raise on access
                continue
            if isinstance(source, str) and _is_tree_module(source):
                holders.add(name)
                break
    return holders


def _purge_modules(*extra: str) -> None:
    """Drop the tree and everything holding a handle on it.

    `extra` is the binding named on the command line: a binding is by
    definition a handle on the tree, and naming it here means the driver no
    longer depends on it having been added to `LOCAL_MODULES` by hand.
    """
    doomed = set(LOCAL_MODULES) | {name for name in extra if name} | tree_handle_holders()
    for name in list(sys.modules):
        if name in doomed or _is_tree_module(name):
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
    _purge_modules(binding)
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


def control_coverage(rows: list[dict[str, Any]], verdicts: dict[str, Any]) -> dict[str, Any]:
    """Does this run still HAVE a control of each polarity it declares?

    EVAL-RERUN-DF-03's other half. Retirement is the honest way to record that a
    control's declaration was falsified, and it is also the way a run can end up
    with no working control of a polarity while every row on the page still
    reads green. A run that declares a positive control and has none that
    decides anything measured nothing about its instruments, and says so here.
    """
    coverage: dict[str, Any] = {}
    for polarity in ("positive", "negative"):
        declared = sorted(
            row["id"] for row in rows
            if str(row.get("control_role", "")).split()[:1] == [polarity]
        )
        if not declared:
            continue
        deciding = sorted(
            mutant for mutant in declared
            if verdicts.get(mutant, {}).get("green")
            and not verdicts[mutant].get("decides_nothing")
            and verdicts[mutant].get("instruments_decided")
        )
        coverage[polarity] = {
            "declared": declared, "deciding": deciding, "green": bool(deciding),
        }
    return coverage


def control_verdict(
    row: dict[str, Any],
    cells: dict[str, str],
    record: dict[str, Any],
    witness: dict[str, Any] | None,
    insensitive: list[str] | None = None,
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
    # An INSENSITIVE kill is a kill that says nothing about the instrument that
    # scored it: the control's own declared witness says the mutant needs an
    # action this instrument never executed, and it died anyway, so it died of
    # something else (EVAL-RERUN-DF-03 / F1). Applied to POSITIVE controls only.
    # For a negative control a kill is the failure itself, and dropping it from
    # the deciders would mask exactly what the control exists to report.
    blind = sorted(set(insensitive or ())) if role == "positive" else []
    if blind:
        verdict["instruments_insensitive"] = blind
        verdict["insensitivity"] = (
            "these instruments KILLED this control while executing none of the cases "
            "its own declared limitation says it needs, so their kill is not evidence "
            "that they reach the fault"
        )
    decided = {
        name: cell for name, cell in cells.items()
        if cell != NOT_DECIDABLE and name not in blind
    }
    wrong = sorted(name for name, cell in decided.items() if cell != wanted)
    verdict.update({
        "instruments_decided": sorted(decided),
        "instruments_not_decidable": sorted(
            name for name, cell in cells.items() if cell == NOT_DECIDABLE
        ),
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
        # The action vocabulary THIS run actually accounted for. A witness that
        # names anything else is checking a name, not a number (DF-04).
        known_actions = _actions_in_run(controls)

        for row in rows:
            mutant = row["id"]
            source = pristine[row["path"]]
            occurrences = source.count(row["find"])
            if occurrences != 1:
                table[mutant] = {name: f"UNAPPLIED({occurrences})" for name in instruments}
                continue
            declared = record["limitations"].get(mutant, {})
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
                # THE MUTATED RUN DECIDES FIRST; a declaration may only ever
                # downgrade a SURVIVAL (EVAL-RERUN-DF-02).
                table[mutant], limitation = decide_cells(
                    instruments, controls, observed, declared, known_actions,
                )
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

    # A limitation the run's own kills contradict or falsify. Both are findings
    # about the CATALOGUE -- somebody declared a limit that is not real -- and
    # both are loud rather than folded into a cell (EVAL-RERUN-DF-02/DF-03).
    contradicted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    insensitive_by_mutant: dict[str, list[str]] = {}
    for mutant, found in evidence.items():
        blind: set[str] = set()
        for instrument, checked in found["declared_limitations"].items():
            entry = {"mutant": mutant, "instrument": instrument,
                     "witness": checked["witness"], "reason": checked["reason"]}
            if checked.get("contradicted_by_evidence"):
                contradicted.append({**entry, "cell": table[mutant][instrument],
                                     "finding": checked["contradicted_by_evidence"]})
            elif not checked["verified"]:
                rejected.append({**entry, "cell": table[mutant][instrument],
                                 "witness_basis": checked["witness_basis"],
                                 "witness_observed": checked["witness_observed"],
                                 "finding": checked.get("scope_falsified",
                                                        "witness did not hold")})
            blind |= set(checked.get("scope_falsified_by", ()))
        if blind:
            insensitive_by_mutant[mutant] = sorted(blind)

    control_rows = {
        row["id"]: control_verdict(
            row, table[row["id"]], record, witnesses.get(row["id"]),
            insensitive_by_mutant.get(row["id"]),
        )
        for row in rows
        if row.get("control_role")
    }
    coverage = control_coverage(rows, control_rows)

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
        "control_coverage": coverage,
        "limitations_contradicted_by_evidence": contradicted,
        "limitations_rejected": rejected,
        "declared_suppression_keys": record["declared_suppression_keys"],
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
    without = sorted(polarity for polarity, block in coverage.items() if not block["green"])
    print(json.dumps({
        "label": arguments.label,
        "controls_red": red,
        "polarities_with_no_deciding_control": without,
        "limitations_contradicted_by_evidence": contradicted,
        "limitations_rejected": rejected,
        "declared_suppression_keys": record["declared_suppression_keys"],
        "control_verdicts": control_rows,
        "control_coverage": coverage,
        "actions_with_zero_executed_cases": unexecuted,
        "out": str(arguments.out),
    }, indent=2, sort_keys=True))
    # A false limitation is a defect in the record, and a run with no control of
    # a polarity it declares measured nothing about its instruments. Neither is
    # allowed to exit 0 (EVAL-RERUN-DF-02, DF-03).
    return 1 if red or without or contradicted else 0


if __name__ == "__main__":
    raise SystemExit(main())
