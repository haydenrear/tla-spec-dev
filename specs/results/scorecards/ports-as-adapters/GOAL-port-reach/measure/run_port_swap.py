"""The fake/real swap, run as an instrument. PA-04's headline measurement.

One case list. Two implementations of one declared port. Every adapter-internal
mutant in the catalogue applied to a working copy of the ported reference, and
every instrument asked what it saw.

    corpus-port-swap:real    the generated port corpus, port-bound, FileJournal
    corpus-port-swap:fake    the SAME cases, port-bound, InMemoryJournal
    corpus-action-bound      the SAME cases, bound to ACTIONS -- the pre-PA-04
                             world, in which `--wiring fake` has nothing to swap
    suite-real / suite-fake  PA-01's hand-written columns, for contrast

WHAT THIS DOES NOT DO

It does not seed anything. Every mutant is read from the sealed catalogue with
its own `find`/`replace`, applied exactly once, and reverted. If a column is
zero it is reported as zero: a fault seeded to make a number is not a
measurement, and this epic prefers a measured miss to a flattering pass.

It runs each cell in a FRESH INTERPRETER. See `port_corpus_run.py` for why.

Two runs over an identical corpus must produce byte-identical output. The one
nondeterministic field either instrument produces -- pytest's elapsed time --
is removed rather than excused: an elapsed time is not evidence about a mutant.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[5]
AB = REPO_ROOT / "examples/validation/ab"
SUITE = AB / "tests/test_behavior.py"
TREE = "reference_ports"

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

KILLED = "KILLED"
SURVIVED = "SURVIVED"
CONTROL_RED = "CONTROL_RED"

RERUN = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun"
PA06 = REPO_ROOT / "specs/results/scorecards/ports-as-adapters"

#: What can be measured, and with what. Every field is here rather than on the
#: command line so that a run is reproducible from its own artifact.
#:
#:   source      the tree copied whole; mutants apply to the copy
#:   subdir      catalogue paths are relative to this, inside the copy
#:   binding     how the shared oracle reaches the tree's internals
#:   catalogues  read as declared; nothing is seeded by this script
#:   corpus      instrument name -> (mapping file, wiring)
#:   suites      instrument name -> composition point the suite imports
SUBJECTS: dict[str, dict[str, Any]] = {
    "reference_ports": {
        "source": AB / "reference_ports",
        "subdir": "reference_ports",
        "binding": "ports_binding",
        "catalogues": [AB / "seeded_faults.toml"],
        "corpus": {
            "corpus-port-swap:real": ("case_adapters.port-swap.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.port-swap.toml", "fake"),
            "corpus-action-bound:real": ("case_adapters.action-only.toml", "real"),
            "corpus-action-bound:fake": ("case_adapters.action-only.toml", "fake"),
        },
        "suites": {"suite-real": "quota_ledger", "suite-fake": "quota_ledger_fake"},
    },
    "arm_a": {
        "source": RERUN / "arms/arm_a",
        "subdir": ".",
        "binding": "rerun_arm_a_binding",
        "catalogues": [RERUN / "measure/catalogue_arm_a.toml", RERUN / "measure/controls_arm_a.toml"],
        "corpus": {
            "corpus-action-bound": ("case_adapters.arm-action.toml", "real"),
            "corpus-port-swap:real": ("case_adapters.arm-a-port.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.arm-a-port.toml", "fake"),
        },
        "suites": {},
    },
    "arm_b": {
        "source": RERUN / "arms/arm_b",
        "subdir": ".",
        "binding": "rerun_arm_b_binding",
        "catalogues": [RERUN / "measure/catalogue_arm_b.toml", RERUN / "measure/controls_arm_b.toml"],
        "corpus": {
            "corpus-action-bound": ("case_adapters.arm-action.toml", "real"),
            "corpus-port-swap:real": ("case_adapters.arm-b-port.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.arm-b-port.toml", "fake"),
        },
        "suites": {},
    },
    # ADDED AT PA-06. THE ONLY CHANGES TO THIS FILE ARE TWO ROWS in this table
    # -- this one and `reference_ports_prerepair` below -- rather than a line of
    # logic: no function, no verdict rule and no accounting differs
    # between PA-04's run and PA-06's. That matters, because PA-04-DF-02 and
    # PA-04-DF-04 record that this project already has TWO verdict-table drivers
    # and that "two drivers is how a number gets quoted against the wrong
    # instrument". PA-06 therefore re-runs ALL FOUR subjects on this one driver
    # at its own commit and diffs the three PA-04 subjects cell for cell against
    # PA-04's sealed output, so "the addition moved nothing" is measured rather
    # than assumed.
    #
    # `binding` lives in PA-06's own measure directory rather than beside the
    # other two, so the CALLER puts that directory on PYTHONPATH. Nothing here
    # reaches for it: an import path smuggled into a driver is how a run stops
    # being reproducible from its own command line.
    "arm_c": {
        "source": PA06 / "arms/arm_c",
        "subdir": ".",
        "binding": "pa06_arm_c_binding",
        "catalogues": [PA06 / "measure/catalogue_arm_c.toml", PA06 / "measure/controls_arm_c.toml"],
        "corpus": {
            "corpus-action-bound": ("case_adapters.arm-action.toml", "real"),
            "corpus-port-swap:real": ("case_adapters.arm-c-port.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.arm-c-port.toml", "fake"),
        },
        "suites": {},
    },
    # ADDED AT PA-06 to score ONE SEALED NEGATIVE PREDICTION, `N07`: "repairing
    # the positive control will move ZERO cells in the kill table ... on every
    # row including the control's own". Scoring it needs a BEFORE, and none
    # exists: the pre-repair `PA-M14` was authored and replaced without any
    # instrument executing it. UNMEASURED is not a pass, so it is measured.
    #
    # Identical to `reference_ports` in every field except the catalogue, which
    # is the pre-repair row extracted verbatim from `46c29c9^`. The before and
    # after therefore differ in exactly the thing the repair changed.
    "reference_ports_prerepair": {
        "source": AB / "reference_ports",
        "subdir": "reference_ports",
        "binding": "ports_binding",
        "catalogues": [PA06 / "measure/pa_m14_prerepair.toml"],
        "corpus": {
            "corpus-port-swap:real": ("case_adapters.port-swap.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.port-swap.toml", "fake"),
            "corpus-action-bound:real": ("case_adapters.action-only.toml", "real"),
            "corpus-action-bound:fake": ("case_adapters.action-only.toml", "fake"),
        },
        "suites": {"suite-real": "quota_ledger", "suite-fake": "quota_ledger_fake"},
    },
}


def run_corpus(tree: Path, cases: Path, mapping: str, wiring: str, binding: str) -> dict[str, Any]:
    import os

    environment = dict(os.environ, QUOTA_LEDGER_BINDING=binding)
    completed = subprocess.run(
        [
            sys.executable, str(HERE / "port_corpus_run.py"),
            "--cases", str(cases), "--tree", str(tree),
            "--mapping", str(HERE / mapping), "--wiring", wiring,
        ],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=environment,
    )
    if completed.returncode != 0:
        return {
            "total_ran": 0, "total_failed": 0, "harness_error": True,
            "failures": completed.stderr.strip().splitlines()[-3:],
        }
    return json.loads(completed.stdout)


def run_suite(tree: Path, impl: str) -> dict[str, Any]:
    import os

    environment = dict(os.environ, QUOTA_LEDGER_DIR=str(tree), QUOTA_LEDGER_IMPL=impl)
    completed = subprocess.run(
        ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(SUITE), "-q"],
        cwd=str(REPO_ROOT), env=environment, capture_output=True, text=True,
    )
    tail = [line for line in completed.stdout.splitlines() if line.strip()][-1:]
    tail = [re.sub(r" in \d+\.\d+s$", "", line) for line in tail]
    return {"total_failed": int(completed.returncode != 0), "failures": tail}


NOT_DECIDABLE = "NOT_DECIDABLE"


def witness_count(control_record: dict[str, Any], action: str | None) -> tuple[int | None, str]:
    """How many ACCEPTED cases of `action` this instrument executed, and on what basis.

    `None` means "not evaluable" and nothing is decided against it. A missing key
    and a measured zero are not the same claim: an action absent from an
    instrument's accounting is not an action that ran zero times, it is a name
    nobody counted (EVAL-RERUN-DF-04).
    """
    per_action = control_record.get("per_action")
    if per_action is None:
        return None, "instrument keeps no executability accounting"
    counts = per_action.get(action)
    if counts is None:
        return 0, "action absent from this instrument's corpus"
    return counts.get("ran_accepting", 0), "measured"


def known_actions(controls: dict[str, dict[str, Any]]) -> set[str]:
    """Every action name some instrument in THIS run actually accounted for.

    Derived from the run rather than hardcoded, so a model that grows an action
    does not silently fall outside the role reader.
    """
    return {
        action
        for record in controls.values()
        for action in (record.get("per_action") or {})
    }


def role_scope(prose: str, action: str | None, actions: set[str]) -> dict[str, Any]:
    """Read a declared role's SCOPE out of its own prose.

    Three outcomes, and the middle one is the reason this is not a substring
    test. A role reading "must die on every instrument" is UNIVERSAL: it names
    no action, so there is no witness to excuse a survival and every decided
    cell must match. A role reading "every instrument that executes an accepted
    Reserve" is WITNESS-SCOPED: an instrument that executed none of those has
    not been shown to reach the fault, and its cell decides nothing. A role
    naming a DIFFERENT action from the row's own `refine_action` is
    INCONSISTENT -- the declaration cannot be executed as written, and that is
    reported rather than resolved by picking one of the two.
    """
    named = sorted(name for name in actions if name.lower() in prose.lower())
    if named and action and action not in named:
        return {
            "scope": "inconsistent",
            "executable_as_written": False,
            "actions_named_in_prose": named,
            "why": (
                f"the role prose names {named} and the row's refine_action is {action!r}; "
                "nothing can decide which the control means"
            ),
        }
    if named:
        return {"scope": "witness-scoped", "executable_as_written": True,
                "actions_named_in_prose": named}
    return {"scope": "universal", "executable_as_written": True, "actions_named_in_prose": []}


def control_verdict(
    mutant: dict[str, Any], cells: dict[str, str], controls: dict[str, dict[str, Any]],
    retired: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """EXECUTE a control's declared role against this run's measured counts.

    THE BUG THIS EXISTS TO CLOSE. PA-04's first run reported `control_red: []`
    while `PA-M14` -- declared "positive -- must die on every instrument that
    executes an accepted Reserve ... under BOTH wirings" -- SURVIVED both port
    columns, each of which executed **294 accepted Reserve cases**. The role was
    prose that nothing compared against the measured `ran_accepting`, so a
    demonstrated control FAILURE did not raise.

    That is EVAL-SUPPRESS in the other direction. EVAL-SUPPRESS closed "a
    declaration can erase a demonstrated kill"; this was "a role string can fail
    to raise a demonstrated control failure". No suppression key reaches it,
    because nothing was suppressed -- the check simply was not wired.

    The rule is `run_controls.py`'s (`role` -> `must_be`, every decided cell must
    match, silence is never a pass) so the two drivers stay comparable, PLUS the
    measured witness the role's own sentence names:

      * positive, witness > 0, cell != KILLED -> RED
      * positive, witness == 0                -> NOT_DECIDABLE, and NOT red: the
        instrument provably never reached the accept path
      * negative, cell == KILLED              -> RED; a kill retracts a
        documented limit and is a finding
    """
    role = str(mutant.get("control_role", "")).split()[:1]
    if role not in (["positive"], ["negative"]):
        return {}
    polarity = role[0]
    prose = str(mutant.get("control_role", ""))

    # RETIREMENT, honoured exactly as `run_controls.py` honours it, and REPORTED
    # rather than applied silently. Retiring a control is the honest way to
    # record that its own declaration was falsified -- M09 reverses a SEQUENCE
    # and this model represents its ledger as one, so ordering is expressible
    # and every corpus sees it. That is a property of the MODEL, so the kills
    # below are correct and it is the control that was wrong. It still runs and
    # is still scored in its class row; what it stops doing is deciding whether
    # an instrument works. Not honouring this produces a FALSE RED, which
    # corrupts a control record exactly as badly as a false green.
    retirement = (retired or {}).get(str(mutant.get("id")))
    if retirement:
        return {
            "role": f"{retirement.get('was', polarity)} (RETIRED)",
            "decides_nothing": True,
            "green": True,
            "declared_role": prose,
            "retirement_reason": str(retirement.get("reason", "")).strip(),
            "replaced_by": retirement.get("replaced_by"),
            "measured_cells": dict(sorted(cells.items())),
            "instruments_wrong": [],
            "witnesses": {},
        }

    wanted = KILLED if polarity == "positive" else SURVIVED
    action = mutant.get("refine_action")
    scope = role_scope(prose, action, known_actions(controls))

    decided: dict[str, str] = {}
    undecidable: dict[str, str] = {}
    witnesses: dict[str, Any] = {}
    for name, cell in cells.items():
        observed, basis = witness_count(controls.get(name, {}), action)
        witnesses[name] = {"witness_action": action, "observed": observed, "basis": basis}
        # The zero-witness escape belongs ONLY to a positive control whose own
        # role scopes it to an action. A universal role claims every instrument,
        # and for a NEGATIVE control a kill IS the failure -- dropping it from
        # the decided set would mask what the control exists to report.
        if polarity == "positive" and scope["scope"] == "witness-scoped" and observed == 0:
            undecidable[name] = cell
        else:
            decided[name] = cell

    wrong = sorted(name for name, cell in decided.items() if cell != wanted)
    return {
        "role": polarity,
        "must_be": wanted,
        "declared_role": prose,
        "witness_action": action,
        "role_scope": scope,
        "witnesses": dict(sorted(witnesses.items())),
        "instruments_decided": sorted(decided),
        "instruments_not_decidable": sorted(undecidable),
        "instruments_wrong": wrong,
        "green": not wrong and bool(decided),
    }


def red_controls(
    per_mutant: dict[str, Any], controls: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Every <control, instrument> pair whose own declared role was violated."""
    red: list[dict[str, Any]] = []
    for mutant_id, record in sorted(per_mutant.items()):
        verdict = record.get("control_verdict") or {}
        for name in verdict.get("instruments_wrong", []):
            witness = verdict["witnesses"][name]
            red.append({
                "mutant": mutant_id,
                "instrument": name,
                "role": verdict["role"],
                "must_be": verdict["must_be"],
                "observed_cell": record["cells"][name],
                "witness_action": witness["witness_action"],
                "witness_ran_accepting": witness["observed"],
                "witness_basis": witness["basis"],
                "why": (
                    f"declared {verdict['role']} control; this instrument executed "
                    f"{witness['observed']} accepting {witness['witness_action']} case(s) "
                    f"and the cell is {record['cells'][name]}, not {verdict['must_be']}"
                ),
            })
    return red


def observe(subject: dict[str, Any], tree: Path, cases: Path) -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for name, (mapping, wiring) in subject["corpus"].items():
        observed[name] = run_corpus(tree, cases, mapping, wiring, subject["binding"])
    for name, impl in subject["suites"].items():
        observed[name] = run_suite(tree, impl)
    return observed


def render(report: dict[str, Any]) -> str:
    instruments = report["instruments"]
    rows = ["| mutant | " + " | ".join(instruments) + " |",
            "|---|" + "---|" * len(instruments)]
    for mutant in report["per_mutant"]:
        cells = [report["per_mutant"][mutant]["cells"][name] for name in instruments]
        rows.append(f"| {mutant} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def render_controls(report: dict[str, Any]) -> str:
    """Say the control state in the run output, not only in the JSON."""
    red = report["control_red"]
    lines = ["", "CONTROLS (role EXECUTED against this run's measured counts):"]
    for mutant_id, record in report["per_mutant"].items():
        verdict = record.get("control_verdict") or {}
        if not verdict:
            continue
        if verdict.get("decides_nothing"):
            lines.append(
                f"  RETIRED  {mutant_id} [{verdict['role']}] -- decides nothing; "
                f"replaced by {verdict.get('replaced_by')}. Still runs, still scored "
                "in its class row."
            )
            continue
        state = "GREEN" if verdict["green"] else "RED"
        lines.append(
            f"  {state}  {mutant_id} [{verdict['role']}, must_be {verdict['must_be']}, "
            f"scope {verdict['role_scope']['scope']}]"
        )
        if not verdict["role_scope"]["executable_as_written"]:
            lines.append(f"         ! {verdict['role_scope']['why']}")
        for name in verdict["instruments_wrong"]:
            witness = verdict["witnesses"][name]
            lines.append(
                f"         wrong on {name}: cell {record['cells'][name]}, "
                f"{witness['observed']} accepting {witness['witness_action']} case(s) executed"
            )
        for name in verdict["instruments_not_decidable"]:
            lines.append(
                f"         not decidable on {name}: 0 accepting "
                f"{verdict['witness_action']} case(s) executed"
            )
    if red:
        lines.append("")
        lines.append(
            f"  {len(red)} RED control/instrument pair(s). EVERY KILL NUMBER FROM THOSE "
            "INSTRUMENTS IS A FLOOR: a control that should have died there and did not "
            "means the column's zeros cannot be told apart from a broken instrument."
        )
    else:
        lines.append("")
        lines.append("  no control's declared role was violated on any instrument that reached it.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", choices=sorted(SUBJECTS), required=True)
    parser.add_argument("--cases", type=Path, required=True, help="Generated port corpus package")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    subject = SUBJECTS[args.subject]
    instruments = list(subject["corpus"]) + list(subject["suites"])
    prefix = subject["subdir"]

    mutants: list[dict[str, Any]] = []
    retired: dict[str, dict[str, Any]] = {}
    for path in subject["catalogues"]:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
        for entry in document.get("retired_control", []):
            retired[entry["mutant"]] = entry
        for entry in document.get("mutants", []):
            declared = str(entry.get("path", ""))
            if prefix == ".":
                mutants.append({**entry, "relative": declared})
            elif declared.startswith(f"{prefix}/"):
                mutants.append({**entry, "relative": declared[len(prefix) + 1:]})

    workspace = Path(tempfile.mkdtemp(prefix="pa04-swap-tree-"))
    tree = workspace / "tree"
    shutil.copytree(subject["source"], tree, ignore=shutil.ignore_patterns("__pycache__", "tests"))
    # The arm-B fake composition point is a MEASUREMENT artifact and must be
    # importable beside the arm without being written into it. The arm on disk
    # is never touched; only this throwaway copy gains a file.
    if args.subject == "arm_b":
        shutil.copy2(HERE / "arm_b_fake.py", tree / "arm_b_fake.py")
    pristine = {path: path.read_text(encoding="utf-8") for path in tree.rglob("*.py")}

    try:
        controls = observe(subject, tree, args.cases)
        control_failed = {
            name: bool(record.get("total_failed") or record.get("harness_error"))
            for name, record in controls.items()
        }

        per_mutant: dict[str, Any] = {}
        for mutant in mutants:
            target = tree / mutant["relative"]
            original = pristine[target]
            occurrences = original.count(mutant["find"])
            mutated = original.replace(mutant["find"], mutant["replace"], 1)
            target.write_text(mutated, encoding="utf-8")
            for cache in tree.rglob("__pycache__"):
                shutil.rmtree(cache, ignore_errors=True)
            try:
                observed = observe(subject, tree, args.cases)
            finally:
                target.write_text(original, encoding="utf-8")
                for cache in tree.rglob("__pycache__"):
                    shutil.rmtree(cache, ignore_errors=True)
            cells = {
                name: (
                    CONTROL_RED if control_failed[name]
                    else (KILLED if record.get("total_failed") else SURVIVED)
                )
                for name, record in observed.items()
            }
            per_mutant[mutant["id"]] = {
                "fault_class": mutant.get("fault_class"),
                "path": mutant["path"],
                "control_role": mutant.get("control_role"),
                "occurrences_of_find": occurrences,
                "applied_exactly_once": occurrences == 1 and mutated != original,
                "cells": cells,
                # The role, EXECUTED against this run's own measured counts.
                "control_verdict": control_verdict(mutant, cells, controls, retired),
                "evidence": {
                    name: {
                        key: record.get(key)
                        for key in ("total_ran", "total_failed", "total_skipped", "failures")
                        if key in record
                    }
                    for name, record in observed.items()
                },
            }

        report = {
            "instruments": instruments,
            "subject": args.subject,
            "tree": str(Path(subject["source"]).relative_to(REPO_ROOT)),
            "binding": subject["binding"],
            "cases": str(args.cases.name),
            "catalogues": [str(path.relative_to(REPO_ROOT)) for path in subject["catalogues"]],
            "controls_on_unmutated_code": controls,
            # TWO DIFFERENT FACTS, kept apart because conflating them is how the
            # first run of this driver reported no red control while one was red.
            #   unmutated_control_failed -- the instrument is broken before any
            #     mutant is applied; it makes every cell in that column CONTROL_RED.
            #   control_red -- a declared control's own ROLE was violated on an
            #     instrument that its own witness count proves reached it.
            "unmutated_control_failed": sorted(
                name for name, red in control_failed.items() if red
            ),
            "retired_controls": dict(sorted(retired.items())),
            "control_red": red_controls(per_mutant, controls),
            "per_mutant": dict(sorted(per_mutant.items())),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(render(report))
        print(render_controls(report))
        print(f"\nwrote {args.out}")
        return 0
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
