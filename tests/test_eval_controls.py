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

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace

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
    return {"total_failed": 0, "per_action": {"Reserve": {
        "ran": accepting + refusing, "ran_accepting": accepting,
        "ran_refusing": refusing, "failed": 0, "skipped": 0,
    }}}


def corpus_without_reserve() -> dict:
    """`corpus-slice-led`'s shape: real accounting, no `Reserve` key at all."""
    return {"total_failed": 0, "per_action": {"CloseTenant": {
        "ran": 24, "ran_accepting": 24, "ran_refusing": 0, "failed": 0, "skipped": 0,
    }}}


def failed(*names: str) -> dict:
    return {"total_failed": 1 if names else 0, "failures": list(names)}


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


def test_an_instrument_that_ran_the_action_and_accepted_none_verifies(driver):
    checked = driver.verify_limitation(LIMITATION, control_run(), {"Reserve"})
    assert checked["verified"] is True
    assert checked["witness_basis"] == "measured"


# ---------------------------------------------------------------------------
# EVAL-RERUN-DF-04: a check that passes because it looked at nothing
#
# `verify_limitation` read `counts.get(key, 0)`, so a MISSING key and a MEASURED
# zero were the same number. Under that reading an action appearing nowhere in
# the model "verified", and `corpus-slice-led`'s limitation -- 100% of arm B's
# -- was verified by the absence of a count rather than by one.
# ---------------------------------------------------------------------------


def test_a_witness_naming_an_action_no_instrument_ever_saw_verifies_nothing(driver):
    """The adversarial channel's probe 2, as an assertion.

    `ThisActionDoesNotExist` appears nowhere in the model. Before the repair it
    "verified", erased two genuine kills, and collapsed a class denominator to
    `0 of 0` at exit 0.
    """
    entry = dict(LIMITATION, witness_action="ThisActionDoesNotExist")
    checked = driver.verify_limitation(entry, control_run(accepting=294), {"Reserve", "Commit"})
    assert checked["verified"] is False
    assert checked["witness_observed"] is None
    assert checked["witness_basis"] == "no action of this name ran anywhere in this run"


def test_an_action_absent_from_this_corpus_but_real_in_the_run_is_a_provable_zero(driver):
    """The honest half. `corpus-slice-led` really does contain no `Reserve` edge.

    That is a STRONGER zero than "every case skipped" -- but it has to be
    established from the run's own vocabulary rather than defaulted, and the
    artifact has to say which of the two it was.
    """
    checked = driver.verify_limitation(
        LIMITATION, corpus_without_reserve(), {"Reserve", "CloseTenant"},
    )
    assert checked["verified"] is True
    assert checked["witness_basis"] == "action absent from this instrument's corpus"


def test_an_instrument_with_no_executability_accounting_cannot_carry_a_limitation(driver):
    """The `suite` column keeps no per-action counts, so nothing about it is a
    witness. Before the repair `.get("per_action", {})` made every such
    limitation verify."""
    checked = driver.verify_limitation(LIMITATION, {"total_failed": 0}, {"Reserve"})
    assert checked["verified"] is False
    assert checked["witness_basis"] == "instrument keeps no executability accounting"


# ---------------------------------------------------------------------------
# EVAL-RERUN-DF-02: a declaration may not erase a demonstrated kill
# ---------------------------------------------------------------------------


def test_a_verified_limitation_cannot_convert_a_demonstrated_kill(driver):
    """THE severe one. The cell was decided before the mutated run was consulted,
    so an instrument that demonstrably KILLED the mutant reported
    `NOT_DECIDABLE`, `verified: true`, `green: true`, exit 0, and nothing in the
    artifact said a kill had been discarded."""
    instruments = ["corpus-neg", "corpus-whole"]
    controls = {"corpus-neg": control_run(refusing=64), "corpus-whole": control_run(accepting=294)}
    observed = {"corpus-neg": failed("case_0009: available"), "corpus-whole": failed("boom")}
    cells, checked = driver.decide_cells(
        instruments, controls, observed, {"corpus-neg": LIMITATION}, {"Reserve"},
    )
    assert cells["corpus-neg"] == driver.KILLED
    assert checked["corpus-neg"]["contradicted_by_evidence"]


def test_a_verified_limitation_still_scopes_a_survival(driver):
    """The construct's real job is untouched: an instrument that executed none of
    the cases and saw nothing is NOT_DECIDABLE, not a miss."""
    controls = {"corpus-neg": control_run(refusing=64), "corpus-whole": control_run(accepting=294)}
    observed = {"corpus-neg": failed(), "corpus-whole": failed("boom")}
    cells, checked = driver.decide_cells(
        ["corpus-neg", "corpus-whole"], controls, observed, {"corpus-neg": LIMITATION}, {"Reserve"},
    )
    assert cells == {"corpus-neg": driver.NOT_DECIDABLE, "corpus-whole": driver.KILLED}
    assert "contradicted_by_evidence" not in checked["corpus-neg"]


def test_a_limitation_does_not_scope_a_broken_instrument(driver):
    """`CONTROL_RED` says the instrument fails on UNMUTATED code. That is not a
    scope note about one mutant and must not be dressed as one."""
    controls = {"corpus-neg": dict(control_run(refusing=64), total_failed=3)}
    cells, checked = driver.decide_cells(
        ["corpus-neg"], controls, {"corpus-neg": failed()}, {"corpus-neg": LIMITATION}, {"Reserve"},
    )
    assert cells["corpus-neg"] == driver.CONTROL_RED
    assert checked["corpus-neg"]["not_applied"]


# ---------------------------------------------------------------------------
# EVAL-RERUN-DF-03: a limitation's scope is falsifiable by the run's own kills
# ---------------------------------------------------------------------------


def test_a_limitation_the_runs_own_kills_falsify_is_rejected(driver):
    """Arm B's shape, exactly. The limitation says a mutant needs a positive
    `Reserve` to be seen; `corpus-neg` executes none and kills it anyway, so the
    mutant is observable without one and the limitation scopes nothing.

    This is the whole of adversarial F1 as arithmetic on data already in hand --
    no `corpus-noreserve`, no second opinion, no reader noticing.
    """
    instruments = ["corpus-neg", "corpus-slice-led", "corpus-whole"]
    controls = {
        "corpus-neg": control_run(refusing=64),
        "corpus-slice-led": corpus_without_reserve(),
        "corpus-whole": control_run(accepting=294),
    }
    observed = {
        "corpus-neg": failed("case_0009_close_tenant: available"),
        "corpus-slice-led": failed(),
        "corpus-whole": failed("boom"),
    }
    declared = {"corpus-slice-led": dict(LIMITATION, instrument="corpus-slice-led")}
    cells, checked = driver.decide_cells(
        instruments, controls, observed, declared, {"Reserve", "CloseTenant"},
    )
    assert cells["corpus-slice-led"] == driver.SURVIVED
    assert checked["corpus-slice-led"]["verified"] is False
    assert checked["corpus-slice-led"]["scope_falsified_by"] == ["corpus-neg"]


def test_a_limitation_survives_kills_by_instruments_that_do_execute_the_action(driver):
    """Arm A's shape. Every instrument that kills M07 there executes accepted
    `Reserve` cases, so nothing falsifies the scope and the cell stays
    NOT_DECIDABLE. The check has to leave the sound declaration standing."""
    instruments = ["corpus-neg", "corpus-whole"]
    controls = {"corpus-neg": control_run(refusing=64), "corpus-whole": control_run(accepting=294)}
    observed = {"corpus-neg": failed(), "corpus-whole": failed("boom")}
    cells, checked = driver.decide_cells(
        instruments, controls, observed, {"corpus-neg": LIMITATION}, {"Reserve"},
    )
    assert cells["corpus-neg"] == driver.NOT_DECIDABLE
    assert "scope_falsified_by" not in checked["corpus-neg"]


def test_a_positive_control_killed_where_it_cannot_be_seen_is_not_green(driver):
    """An insensitive kill is not evidence about the instrument that scored it."""
    row = {"id": "M07", "control_role": "positive"}
    cells = {"corpus-neg": driver.KILLED, "corpus-slice-led": driver.SURVIVED,
             "corpus-whole": driver.KILLED}
    verdict = driver.control_verdict(
        row, cells, {"retired": {}, "limitations": {}}, None, ["corpus-neg"],
    )
    assert verdict["instruments_insensitive"] == ["corpus-neg"]
    assert "corpus-neg" not in verdict["instruments_decided"]
    assert verdict["green"] is False


def test_an_insensitive_kill_is_never_dropped_from_a_negative_control(driver):
    """For a negative control the KILL is the failure. Excluding it would be the
    one way this check could become the thing it exists to catch."""
    row = {"id": "N01", "control_role": "negative"}
    verdict = driver.control_verdict(
        row, {"a": driver.KILLED}, {"retired": {}, "limitations": {}},
        {"separates_the_trees": True}, ["a"],
    )
    assert verdict["green"] is False
    assert verdict["instruments_wrong"] == ["a"]
    assert "instruments_insensitive" not in verdict


def test_a_run_whose_only_positive_control_is_retired_has_no_positive_control(driver):
    """Retirement is honest and it is also how a run ends up with no control at
    all while every row on the page reads green. It has to be said out loud."""
    rows = [{"id": "M07", "control_role": "positive -- must die everywhere"},
            {"id": "M09", "control_role": "negative"},
            {"id": "N01", "control_role": "negative"}]
    verdicts = {
        "M07": {"green": True, "decides_nothing": True},
        "M09": {"green": True, "decides_nothing": True},
        "N01": {"green": True, "instruments_decided": ["a", "b"]},
    }
    coverage = driver.control_coverage(rows, verdicts)
    assert coverage["positive"] == {"declared": ["M07"], "deciding": [], "green": False}
    assert coverage["negative"]["deciding"] == ["N01"]
    assert coverage["negative"]["green"] is True


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


# ---------------------------------------------------------------------------
# EVAL-RERUN-DF-01: the purge was a list of NAMES, and a name is not a handle
# ---------------------------------------------------------------------------


@pytest.fixture
def stale_binding(tmp_path):
    """A binding module whose NAME is not on `LOCAL_MODULES`, holding the tree.

    This is EVAL-RERUN's own first arm-A run in eleven lines: a module-level
    `import quota_ledger` captured the pristine tree once, the name-keyed purge
    never dropped it, and 11 of 11 mutants executed against unmutated code and
    reported SURVIVED with green controls. Only the hand-written `suite` column
    disagreeing with all six corpus columns exposed it.
    """
    (tmp_path / "quota_ledger.py").write_text("VALUE = 'pristine'\n", encoding="utf-8")
    (tmp_path / "not_on_the_fixed_list.py").write_text(
        "import quota_ledger as _impl\n\n\ndef value():\n    return _impl.VALUE\n",
        encoding="utf-8",
    )
    saved = {
        name: sys.modules.pop(name, None)
        for name in ("not_on_the_fixed_list", "quota_ledger")
    }
    sys.path.insert(0, str(tmp_path))
    try:
        yield importlib.import_module("not_on_the_fixed_list")
    finally:
        for name, module in saved.items():
            sys.modules.pop(name, None)
            if module is not None:
                sys.modules[name] = module
        if str(tmp_path) in sys.path:
            sys.path.remove(str(tmp_path))


def test_the_purge_drops_a_module_holding_the_tree_whatever_it_is_called(driver, stale_binding):
    assert "not_on_the_fixed_list" not in driver.LOCAL_MODULES
    # The substantive assertion first: on the pre-repair driver this one fails,
    # and the module that survives it is the module that made 11 of 11 mutants
    # execute against pristine code.
    driver._purge_modules()
    assert "not_on_the_fixed_list" not in sys.modules
    assert "quota_ledger" not in sys.modules


def test_the_binding_named_on_the_command_line_is_purged_by_name_too(driver, stale_binding):
    """Belt and braces: the driver knows the binding's name, so it never has to
    depend on having noticed the handle."""
    driver._purge_modules("not_on_the_fixed_list")
    assert "not_on_the_fixed_list" not in sys.modules


def test_the_driver_leaves_modules_that_hold_no_handle_alone(driver, stale_binding):
    """A purge that dropped everything would be a different bug, not a fix."""
    holders = driver.tree_handle_holders()
    assert "not_on_the_fixed_list" in holders
    assert "json" not in holders
    assert "pytest" not in holders


# ---------------------------------------------------------------------------
# The suppression mechanism is auditable from the one place that enumerates them
# ---------------------------------------------------------------------------


def test_the_eval_suppression_constructs_are_on_the_projects_suppression_list():
    """`seeded_faults.toml` promises that suppression keys "are scanned for by
    scripts/kill_test.py and reported loudly". Until EVAL-SUPPRESS that list did
    not contain the one construct in this eval that could make a cell disappear,
    so nothing anywhere audited it."""
    from scripts.kill_test import SUPPRESSION_KEYS

    assert {"limitation", "retired_control", "not_decidable"} <= SUPPRESSION_KEYS


def test_every_run_artifact_enumerates_the_suppression_keys_its_catalogues_carry(driver):
    """Reported, never honored. A reader of the JSON can see the mechanism
    without reading the driver."""
    _, record = driver.load_catalogue([DRIVER.parent / "controls.toml"])
    keys = [key for entry in record["declared_suppression_keys"].values() for key in entry]
    assert "limitation" in keys
    assert "retired_control" in keys
    # Per INSTANCE, not merely per construct: two limitations are declared here
    # and the artifact names both.
    assert [key for key in keys if key.endswith("witness_ran_must_be")] == [
        "limitation[0].witness_ran_must_be", "limitation[1].witness_ran_must_be",
    ]


# ---------------------------------------------------------------------------
# A skip rule that misstates why it fires is the same class of defect
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def oracle_module():
    os.environ.setdefault("QUOTA_LEDGER_BINDING", "reference_binding")
    os.environ.setdefault("QUOTA_LEDGER_DIR", str(REPO_ROOT / "examples/validation/ab/reference"))
    if str(DRIVER.parent) not in sys.path:
        sys.path.insert(0, str(DRIVER.parent))
    return importlib.import_module("oracle")


def reserve_case(holder: dict, names: str):
    """A `Reserve` case naming id `names` from a before-state with `holder`."""
    return SimpleNamespace(
        name="synthetic",
        labels=(),
        before={"amt": {"r1": 0, "r2": 0}, "holder": holder},
        input=SimpleNamespace(action="Reserve", params={"t": "t1", "a": 1, "r": names}),
    )


def test_the_two_reasons_a_reserve_case_is_inexpressible_are_counted_apart(oracle_module):
    """EVAL-RERUN F4. One reason was reported for both populations and it is the
    wrong one for 266 of 294 skips.

    * `r2` is free and allocatable, the case names `r1`: the ARGUMENT is what the
      API cannot honour, which is what the old reason said.
    * both ids are taken, so the API's next id is `r3` -- outside `ResIds`
      entirely. No choice of `r` could have been expressible, and the mismatch
      is in the BEFORE-STATE, which the old reason did not say and 266 of 294
      cases needed it to.
    """
    adapter = oracle_module.PositiveAdapter()
    named_another_free_id = adapter.can_run(reserve_case({"r1": "t1", "r2": "none"}, "r1"))
    unreachable_before_state = adapter.can_run(reserve_case({"r1": "t1", "r2": "t1"}, "r1"))
    assert named_another_free_id == (False, oracle_module.ID_NOT_EXPRESSIBLE)
    assert unreachable_before_state == (False, oracle_module.STATE_NOT_EXPRESSIBLE)
    assert oracle_module.ID_NOT_EXPRESSIBLE != oracle_module.STATE_NOT_EXPRESSIBLE


def test_an_expressible_reserve_case_still_runs(oracle_module):
    """The negative control for the rule above: splitting a reason must not skip
    one more case than it did before."""
    adapter = oracle_module.PositiveAdapter()
    assert adapter.can_run(reserve_case({"r1": "none", "r2": "none"}, "r1")) is True


#: The ten rows HP-01 sealed, in file order. Named individually rather than
#: counted, because PA-01 was directed by the canonical plan to EXTEND this
#: catalogue and a bare `len(...) == 10` cannot tell an extension from an
#: amendment: it would have passed just as happily if a sealed row had been
#: deleted and a different one added in its place.
HP_SEALED_MUTANTS = (
    "M01-guard-zero-amount",
    "M02-guard-over-quota",
    "M03-guard-close-with-outstanding",
    "M04-durable-stale-total",
    "M05-durable-close-line-zero-and-swallowed",
    "M08-cross-aspect-commit-refunds-the-hold",
    "M06-wrong-status-on-release",
    "M10-apply-only-double-refund",
    "M07-positive-control-wrong-hold",
    "M09-negative-control-ledger-order",
)


def test_the_sealed_catalogue_is_still_the_sealed_catalogue(driver):
    """The control record ADDS; it does not amend. If this fails, something edited
    a sealed measurement instead of overlaying it."""
    mutants, record = driver.load_catalogue(
        [REPO_ROOT / "examples/validation/ab/seeded_faults.toml"]
    )
    ids = [row["id"] for row in mutants]
    assert ids[: len(HP_SEALED_MUTANTS)] == list(HP_SEALED_MUTANTS), (
        "a sealed HP-01 row was renamed, reordered or removed"
    )
    # Anything past the seal is an extension and must say which ticket added it.
    # PA-01 appended the adapter-internal class, anchored on a second reference
    # tree, because the flat reference contains no adapter to seed inside.
    for extra in ids[len(HP_SEALED_MUTANTS):]:
        assert extra.startswith("PA-"), (
            f"{extra!r} is neither a sealed HP-01 row nor a declared PA extension"
        )
    # The sealed file carries no limitation and no retirement of its own.
    assert record["limitations"] == {}
    assert record["retired"] == {}
