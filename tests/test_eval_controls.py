"""EVAL-STABLE: the control logic, and above all that it cannot excuse itself.

`examples/validation/ab/seeded_faults.toml` bans suppression keys in the
strongest terms it has: *"`expected_to_survive`, `known_survivor`, `waiver` and
friends are scanned for by scripts/kill_test.py and reported loudly... A control
that excuses itself is not a control."*

The eval's control record introduces two constructs that could become exactly
that if they were trusted rather than checked:

* a **declared limitation**, which says an instrument cannot decide a mutant; and
* a **retirement**, which says a control's declaration was falsified.

So this file's job is not to confirm they work. It is to prove they cannot be
used to make a red control green:

* a limitation whose witness does not hold is REJECTED and the cell is decided
  normally (`test_a_limitation_whose_witness_fails_is_rejected`);
* a limitation cannot rescue a control from an instrument that DID execute the
  action and DID let the mutant live
  (`test_a_limitation_cannot_hide_a_real_survival`);
* a control every instrument declines to decide is NOT green
  (`test_a_control_no_instrument_decided_is_not_green`);
* a negative control whose reality witness does not separate the trees decides
  nothing, because an equivalent mutant survives everything for reasons that
  say nothing about any instrument
  (`test_an_unwitnessed_negative_control_decides_nothing`).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DRIVER = REPO_ROOT / "examples/validation/ab/eval/run_controls.py"

pytestmark = pytest.mark.skipif(
    not DRIVER.exists(), reason="the A/B eval fixture is not present in this tree"
)


@pytest.fixture(scope="module")
def driver():
    """Import the driver without running it.

    It reaches into HP-06's `measure/` tree for the generated effect providers,
    so it is imported by path rather than as a package.
    """
    measure = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting/measure"
    for entry in (str(REPO_ROOT), str(REPO_ROOT / "scripts"), str(DRIVER.parent),
                  str(measure), str(measure / "generated")):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    spec = importlib.util.spec_from_file_location("eval_run_controls", DRIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def control_run(accepting: int = 0, refusing: int = 0) -> dict:
    return {"per_action": {"Reserve": {
        "ran": accepting + refusing, "ran_accepting": accepting,
        "ran_refusing": refusing, "failed": 0, "skipped": 0,
    }}}


LIMITATION = {
    "mutant": "M07", "instrument": "corpus-neg", "reason": "no accepted Reserve here",
    "witness_action": "Reserve", "witness_polarity": "positive", "witness_ran_must_be": 0,
}


# ---------------------------------------------------------------------------
# A declared limitation is CHECKED, never believed
# ---------------------------------------------------------------------------


def test_a_limitation_is_verified_against_the_runs_own_counts(driver):
    checked = driver.verify_limitation(LIMITATION, control_run(accepting=0, refusing=64))
    assert checked["verified"] is True
    assert checked["witness_observed"] == 0
    assert checked["witness"] == "positive Reserve cases executed"


def test_a_limitation_whose_witness_fails_is_rejected(driver):
    """NEGATIVE CONTROL for this file. The claim is identical; the run is not."""
    checked = driver.verify_limitation(LIMITATION, control_run(accepting=294))
    assert checked["verified"] is False
    assert checked["witness_observed"] == 294


def test_an_instrument_that_never_ran_the_action_at_all_still_verifies(driver):
    assert driver.verify_limitation(LIMITATION, control_run())["verified"] is True


def test_a_limitation_cannot_hide_a_real_survival(driver):
    """The whole point: only a VERIFIED limitation removes a cell from the verdict.

    An unverified one leaves `SURVIVED` in place, and a positive control with a
    `SURVIVED` cell is red. This is the assertion that separates this construct
    from `expected_to_survive`.
    """
    row = {"id": "M07", "control_role": "positive -- must die on every instrument"}
    cells = {"corpus-whole": driver.SURVIVED, "corpus-neg": driver.NOT_DECIDABLE}
    verdict = driver.control_verdict(row, cells, {"retired": {}, "limitations": {}}, None)
    assert verdict["green"] is False
    assert verdict["instruments_wrong"] == ["corpus-whole"]
    assert verdict["instruments_not_decidable"] == ["corpus-neg"]


# ---------------------------------------------------------------------------
# Silence is never a pass
# ---------------------------------------------------------------------------


def test_a_positive_control_is_green_only_when_every_decider_killed_it(driver):
    row = {"id": "M07", "control_role": "positive"}
    record = {"retired": {}, "limitations": {}}
    green = driver.control_verdict(
        row, {"a": driver.KILLED, "b": driver.KILLED, "c": driver.NOT_DECIDABLE}, record, None
    )
    assert green["green"] is True
    assert green["instruments_decided"] == ["a", "b"]


def test_a_control_no_instrument_decided_is_not_green(driver):
    """Every cell not decidable means the run measured nothing about the control."""
    row = {"id": "M07", "control_role": "positive"}
    verdict = driver.control_verdict(
        row, {"a": driver.NOT_DECIDABLE}, {"retired": {}, "limitations": {}}, None
    )
    assert verdict["green"] is False


def test_a_negative_control_must_survive_every_decider(driver):
    row = {"id": "N01", "control_role": "negative"}
    record = {"retired": {}, "limitations": {}}
    witness = {"separates_the_trees": True}
    assert driver.control_verdict(
        row, {"a": driver.SURVIVED, "b": driver.SURVIVED}, record, witness
    )["green"] is True
    killed = driver.control_verdict(
        row, {"a": driver.SURVIVED, "b": driver.KILLED}, record, witness
    )
    assert killed["green"] is False
    assert killed["instruments_wrong"] == ["b"]


def test_a_control_red_verdict_survives_a_control_red_cell(driver):
    """`CONTROL_RED` is not `KILLED`, so it cannot pass a positive control."""
    row = {"id": "M07", "control_role": "positive"}
    verdict = driver.control_verdict(
        row, {"a": driver.CONTROL_RED}, {"retired": {}, "limitations": {}}, None
    )
    assert verdict["green"] is False


# ---------------------------------------------------------------------------
# An unwitnessed negative control is an equivalent mutant wearing a badge
# ---------------------------------------------------------------------------


def test_an_unwitnessed_negative_control_decides_nothing(driver):
    row = {"id": "N01", "control_role": "negative"}
    verdict = driver.control_verdict(
        row, {"a": driver.SURVIVED, "b": driver.SURVIVED},
        {"retired": {}, "limitations": {}},
        {"separates_the_trees": False, "on_pristine_tree": False, "on_mutated_tree": False},
    )
    assert verdict["green"] is False
    assert verdict["decides_nothing"] is True
    assert verdict["instruments_wrong"] == ["reality witness"]


# ---------------------------------------------------------------------------
# Retirement records a falsified declaration; it does not delete a measurement
# ---------------------------------------------------------------------------


def test_a_retired_control_decides_nothing_but_keeps_its_cells(driver):
    row = {"id": "M09", "control_role": "negative -- predicted to survive"}
    record = {"retired": {"M09": {"mutant": "M09", "was": "negative",
                                  "reason": "the ledger is a sequence in this model",
                                  "replaced_by": "N01"}},
              "limitations": {}}
    verdict = driver.control_verdict(row, {"a": driver.KILLED}, record, None)
    assert verdict["decides_nothing"] is True
    assert verdict["replaced_by"] == "N01"
    # The measurement is retained, not erased: M09 still died on `a`.
    assert verdict["measured_cells"] == {"a": driver.KILLED}
    assert verdict["retirement_reason"]


def test_retirement_requires_a_reason_recorded_in_the_verdict(driver):
    row = {"id": "M09", "control_role": "negative"}
    record = {"retired": {"M09": {"mutant": "M09"}}, "limitations": {}}
    assert driver.control_verdict(row, {"a": driver.KILLED}, record, None)["retirement_reason"] == ""


# ---------------------------------------------------------------------------
# The shipped control record itself
# ---------------------------------------------------------------------------


def test_the_shipped_control_record_declares_a_witness_for_every_limitation(driver):
    """A limitation with no checkable witness is a suppression key. None ship."""
    for name in ("controls.toml", "controls_arm_a.toml"):
        _, record = driver.load_catalogue([DRIVER.parent / name])
        limitations = [
            entry
            for per_instrument in record["limitations"].values()
            for entry in per_instrument.values()
        ]
        assert limitations, name
        for entry in limitations:
            assert entry.get("witness_action"), f"{name}: {entry}"
            assert "witness_ran_must_be" in entry, f"{name}: {entry}"
            assert entry.get("reason", "").strip(), f"{name}: {entry}"


def test_the_shipped_negative_control_declares_a_reality_witness(driver):
    for name in ("controls.toml", "controls_arm_a.toml"):
        mutants, _ = driver.load_catalogue([DRIVER.parent / name])
        negatives = [row for row in mutants
                     if str(row.get("control_role", "")).startswith("negative")]
        assert negatives, name
        for row in negatives:
            assert row.get("reality_witness"), f"{name}: {row['id']}"


def test_the_sealed_catalogue_is_still_the_sealed_catalogue(driver):
    """The control record ADDS; it does not amend. If this fails, something edited
    a sealed measurement instead of overlaying it."""
    mutants, record = driver.load_catalogue(
        [REPO_ROOT / "examples/validation/ab/seeded_faults.toml"]
    )
    assert [row["id"] for row in mutants][:3] == [
        "M01-guard-zero-amount", "M02-guard-over-quota", "M03-guard-close-with-outstanding",
    ]
    assert len(mutants) == 10
    # The sealed file carries no limitation and no retirement of its own.
    assert record["limitations"] == {}
    assert record["retired"] == {}
