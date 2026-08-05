"""A declared control's ROLE must be executed, not merely written down.

PA-04's first run reported `control_red: []` while `PA-M14` -- declared
"positive -- must die on every instrument that executes an accepted Reserve
against the reference_ports tree, under BOTH wirings" -- SURVIVED both port
columns, each of which had executed **294 accepting Reserve cases**. The role
was prose that nothing compared against the measured `ran_accepting`, so a
demonstrated control FAILURE did not raise, and the goal verdict turned on it.

This is `EVAL-SUPPRESS` in the other direction. EVAL-SUPPRESS closed "a
declaration can erase a demonstrated kill"; this was "a role string can fail to
raise a demonstrated control failure". Same hole, opposite sign, and nothing in
`SUPPRESSION_KEYS` reaches it because nothing was suppressed -- the check simply
was not wired.

Every test below is the `declaration_executability_rule` applied to the ticket
that had to respect it most.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DRIVER = (
    REPO_ROOT
    / "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/run_port_swap.py"
)


def _load_driver():
    """Import the measurement driver by path; it is evidence, not a package."""
    spec = importlib.util.spec_from_file_location("pa04_run_port_swap", DRIVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = _load_driver()

#: `PA-M14` as the sealed catalogue declares it, fields that matter only.
PA_M14 = {
    "id": "PA-M14-positive-control-accepted-hold-too-large",
    "control_role": (
        "positive -- must die on every instrument that executes an accepted Reserve "
        "against the reference_ports tree, under BOTH wirings, AND must be invisible "
        "until one does."
    ),
    "refine_action": "Reserve",
}

N01 = {
    "id": "N01-negative-control-outstanding-id-order",
    "control_role": "negative -- must survive every generated instrument",
    "refine_action": "Reserve",
}


def _controls(ran_accepting: int | None, action: str = "Reserve") -> dict:
    """One instrument's unmutated-run accounting."""
    if ran_accepting is None:
        return {"port-swap:fake": {"total_failed": 0}}  # a suite: no per_action block
    return {
        "port-swap:fake": {
            "total_failed": 0,
            "per_action": {action: {"ran": 357, "ran_accepting": ran_accepting}},
        }
    }


# -- THE REGRESSION -----------------------------------------------------------


def test_a_positive_control_that_survives_an_instrument_that_reached_it_is_RED():
    """THE MUTATION THE OWNER NAMED.

    PA-M14 SURVIVES a column whose own accounting records 294 accepting Reserve
    cases. Its role says it must die on every instrument that executes one. The
    run must call that RED. Before this check existed, `control_red` was `[]`.
    """
    controls = _controls(294)
    per_mutant = {
        PA_M14["id"]: {
            "cells": {"port-swap:fake": "SURVIVED"},
            "control_verdict": driver.control_verdict(
                PA_M14, {"port-swap:fake": "SURVIVED"}, controls
            ),
        }
    }
    verdict = per_mutant[PA_M14["id"]]["control_verdict"]
    assert verdict["green"] is False
    assert verdict["instruments_wrong"] == ["port-swap:fake"]

    red = driver.red_controls(per_mutant, controls)
    assert red, "control_red must not be empty when a control's own role was violated"
    assert red[0]["mutant"] == PA_M14["id"]
    assert red[0]["instrument"] == "port-swap:fake"
    assert red[0]["witness_ran_accepting"] == 294
    assert red[0]["must_be"] == "KILLED"
    assert red[0]["observed_cell"] == "SURVIVED"


def test_the_run_output_says_it_too_not_only_the_json():
    """A number a reader has to open a JSON file to find is a number nobody reads."""
    controls = _controls(294)
    cells = {"port-swap:fake": "SURVIVED"}
    report = {
        "control_red": None,
        "per_mutant": {
            PA_M14["id"]: {
                "cells": cells,
                "control_verdict": driver.control_verdict(PA_M14, cells, controls),
            }
        },
    }
    report["control_red"] = driver.red_controls(report["per_mutant"], controls)
    rendered = driver.render_controls(report)
    assert "RED" in rendered
    assert "294 accepting Reserve case(s) executed" in rendered
    assert "IS A FLOOR" in rendered


# -- the honest distinction the check must NOT lose ---------------------------


def test_a_positive_control_is_NOT_red_where_the_instrument_never_reached_it():
    """Silence is never a pass, but neither is it a failure.

    An instrument that executed ZERO accepting `Reserve` cases has not been
    shown to reach the accept path, so its SURVIVED cell is not evidence about
    the instrument. Calling that red would make the check fire on the very
    distinction PA-03-DF-02 was filed to preserve.
    """
    controls = _controls(0)
    verdict = driver.control_verdict(PA_M14, {"port-swap:fake": "SURVIVED"}, controls)
    assert verdict["instruments_wrong"] == []
    assert verdict["instruments_not_decidable"] == ["port-swap:fake"]
    # ...and with nothing decided, it is NOT green either. Silence is not a pass.
    assert verdict["green"] is False


def test_a_positive_control_that_dies_where_it_reached_is_green():
    controls = _controls(294)
    verdict = driver.control_verdict(PA_M14, {"port-swap:fake": "KILLED"}, controls)
    assert verdict["green"] is True
    assert verdict["instruments_wrong"] == []


def test_a_negative_control_is_red_when_an_instrument_KILLS_it():
    """A kill retracts a documented limit and is a finding, not a success."""
    controls = _controls(294)
    cells = {"port-swap:fake": "KILLED"}
    verdict = driver.control_verdict(N01, cells, controls)
    assert verdict["must_be"] == "SURVIVED"
    assert verdict["instruments_wrong"] == ["port-swap:fake"]
    assert verdict["green"] is False


def test_a_negative_control_is_not_made_undecidable_by_a_zero_witness():
    """The zero-witness escape is for POSITIVE controls only.

    For a negative control a kill IS the failure, so dropping it from the
    decided set on a zero witness would mask exactly what the control reports.
    """
    verdict = driver.control_verdict(N01, {"port-swap:fake": "KILLED"}, _controls(0))
    assert verdict["instruments_wrong"] == ["port-swap:fake"]


# -- a reworded role must fail ------------------------------------------------


def test_a_role_naming_a_DIFFERENT_action_than_its_row_is_flagged_inconsistent():
    """`declaration_executability_rule`. A role nothing can execute says so.

    The polarity comes from the prose and the witness action from the structured
    field. If a reword leaves those naming different actions, nothing can decide
    which the control meant, and the run reports that rather than silently
    picking one.
    """
    controls = {
        "i": {"per_action": {"Reserve": {"ran_accepting": 294},
                             "Commit": {"ran_accepting": 384}}}
    }
    reworded = dict(
        PA_M14,
        control_role="positive -- must die on every instrument that executes an accepted Commit",
    )
    verdict = driver.control_verdict(reworded, {"i": "KILLED"}, controls)
    assert verdict["role_scope"]["executable_as_written"] is False
    assert verdict["role_scope"]["scope"] == "inconsistent"
    rendered = driver.render_controls(
        {"control_red": [], "per_mutant": {"m": {"cells": {"i": "KILLED"}, "control_verdict": verdict}}}
    )
    assert "nothing can decide which the control means" in rendered


def test_a_universal_role_is_executable_and_gets_NO_zero_witness_escape():
    """"must die on every instrument" claims every instrument. No excuses.

    This is the case my first fix got wrong: it flagged a universal role as
    unexecutable merely for naming no action, which would have put a false
    warning beside two legitimate negative controls.
    """
    universal = dict(PA_M14, control_role="positive -- must die on every instrument")
    verdict = driver.control_verdict(universal, {"i": "SURVIVED"}, _controls(0))
    assert verdict["role_scope"]["scope"] == "universal"
    assert verdict["role_scope"]["executable_as_written"] is True
    # Zero witness, and STILL red: the role admits no scope to hide in.
    assert verdict["instruments_wrong"] == ["i"]


def test_the_sealed_role_string_IS_executable_as_written():
    """Pin the real catalogue entry, so a reword of it fails here."""
    verdict = driver.control_verdict(PA_M14, {"i": "KILLED"}, _controls(294))
    assert verdict["role_scope"]["executable_as_written"] is True
    assert verdict["role_scope"]["scope"] == "witness-scoped"
    assert verdict["witness_action"] == "Reserve"


# -- retirement, honoured as the shipped driver honours it --------------------


def test_a_RETIRED_control_decides_nothing_and_is_not_a_false_red():
    """Found by RUNNING the fix: my first version flagged retired M09 red.

    Retirement is the honest way to record that a control's own declaration was
    falsified. M09 reverses a SEQUENCE and this model represents its ledger as
    one, so ordering is expressible and every corpus sees it -- the kills are
    correct and the CONTROL was wrong. Reporting that as a red control corrupts
    the record exactly as badly as a false green does.
    """
    m09 = {
        "id": "M09-negative-control-ledger-order",
        "control_role": "negative -- predicted to survive every corpus instrument",
        "refine_action": "Commit",
    }
    retired = {m09["id"]: {"mutant": m09["id"], "was": "negative",
                           "reason": "ordering is expressible on this model",
                           "replaced_by": "N01-negative-control-outstanding-id-order"}}
    verdict = driver.control_verdict(m09, {"i": "KILLED"}, _controls(384, "Commit"), retired)
    assert verdict["decides_nothing"] is True
    assert verdict["green"] is True
    assert verdict["instruments_wrong"] == []
    assert verdict["replaced_by"] == "N01-negative-control-outstanding-id-order"
    assert driver.red_controls({m09["id"]: {"cells": {"i": "KILLED"},
                                            "control_verdict": verdict}}, {}) == []


def test_retirement_is_REPORTED_never_applied_silently():
    m09 = {"id": "M09", "control_role": "negative -- x", "refine_action": "Commit"}
    retired = {"M09": {"mutant": "M09", "was": "negative", "reason": "r", "replaced_by": "N01"}}
    verdict = driver.control_verdict(m09, {"i": "KILLED"}, {}, retired)
    rendered = driver.render_controls(
        {"control_red": [], "per_mutant": {"M09": {"cells": {"i": "KILLED"},
                                                   "control_verdict": verdict}}}
    )
    assert "RETIRED" in rendered and "decides nothing" in rendered


@pytest.mark.parametrize("role", ["", "unclear -- something", "POSITIVE"])
def test_a_row_with_no_recognised_polarity_is_not_treated_as_a_control(role):
    assert driver.control_verdict(dict(PA_M14, control_role=role), {"i": "SURVIVED"}, {}) == {}


# -- the witness itself must be measured, never defaulted ---------------------


def test_an_instrument_with_no_accounting_is_decided_on_its_cell_and_says_so():
    verdict = driver.control_verdict(PA_M14, {"port-swap:fake": "KILLED"}, _controls(None))
    witness = verdict["witnesses"]["port-swap:fake"]
    assert witness["observed"] is None
    assert witness["basis"] == "instrument keeps no executability accounting"
    assert verdict["instruments_decided"] == ["port-swap:fake"]


def test_an_action_absent_from_a_corpus_is_a_measured_zero_not_a_missing_key():
    """EVAL-RERUN-DF-04: a missing key and a measured zero are different claims."""
    observed, basis = driver.witness_count(
        {"per_action": {"Commit": {"ran_accepting": 3}}}, "Reserve"
    )
    assert observed == 0
    assert basis == "action absent from this instrument's corpus"
