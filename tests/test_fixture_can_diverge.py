"""FI-04. The A/B fixture is an instrument; this is its demonstrated failing input.

`GOAL-fixture-can-diverge`'s baseline reads NULL ENTAILED: the arms are
identical on 10 of 11 mutated rows, so the experiment could only diverge where
re-anchoring FAILED, and the measured 64 of 64 was arithmetic that could not
have come out otherwise. `PA-06-DF-08` filed it and said either the fixture
changes or the goal does.

FI-04 changed the fixture. These tests hold the change to its own bar:

  * the one semantic really is one semantic, re-anchored by the property onto
    three arms whose `find` strings have nothing in common;
  * the arms really do disagree about it, on a column whose instrument is a
    function of the ARM'S ARCHITECTURE rather than of the shared model;
  * the row that has no counterpart really has none, and nothing invents one;
  * and `divergence.py`, which decides all of the above, GOES RED ON AN INPUT
    THAT SAYS IT SHOULD. That last one is R1 applied to the analysis, and it is
    the test that stops this from being the sixth instrument in this repository
    that cannot produce the result which would refute it.

Every cell asserted here was produced by `run_port_swap.py` -- PA-04's driver,
unmodified, a fresh interpreter per cell. `run_controls.py` is not used on any
ported subject: `FI-01-DF-01` is blocking and open, and that driver reports
15 of 15 false SURVIVED on a ported tree with no error at all.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL = REPO_ROOT / "examples/validation/ab/eval"
RESULTS = EVAL / "results/fi04"

ARM_TREES = {
    "arm_a": REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_a",
    "arm_b": REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_b",
    "arm_c": REPO_ROOT / "specs/results/scorecards/ports-as-adapters/arms/arm_c",
}
CATALOGUES = {arm: EVAL / f"adapter_faults_{arm}.toml" for arm in ARM_TREES}
SEMANTIC = "ledger-readback-drops-close-lines"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"fi04_{name}", EVAL / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


divergence = _load("divergence")
generator_vs_suite = _load("generator_vs_suite")


def catalogue(arm: str) -> dict:
    return divergence.load_catalogue(CATALOGUES[arm])


def report(arm: str) -> dict:
    return json.loads((RESULTS / f"swap-{arm}.json").read_text(encoding="utf-8"))


# -- the fixture change itself ---------------------------------------------


@pytest.mark.parametrize("arm", sorted(ARM_TREES))
def test_every_seeded_find_string_occurs_exactly_once_in_its_arm(arm):
    """A mutant that matches twice, or zero times, is not the mutant declared."""
    for row_id, row in catalogue(arm).items():
        target = ARM_TREES[arm] / row["path"]
        assert target.exists(), f"{row_id}: {target} does not exist"
        text = target.read_text(encoding="utf-8")
        assert text.count(row["find"]) == 1, f"{row_id}: find matched {text.count(row['find'])} times"


def test_one_semantic_re_anchored_by_the_property_not_by_the_bytes():
    """Three arms, one sentence, four `find` strings with nothing in common.

    If two arms shared a `find`, the row would be re-anchored by BYTES, and the
    whole result would be about the trees being similar rather than about their
    architecture. `AD-F1` measured the rival explanation false at the tree level;
    this keeps it false at the catalogue level.
    """
    finds = [
        row["find"]
        for arm in ARM_TREES
        for row in catalogue(arm).values()
    ]
    assert len(finds) == 4, finds
    assert len(set(finds)) == 4, "two rows share a find string; this is a byte re-anchoring"
    for arm in ARM_TREES:
        for row_id, row in catalogue(arm).items():
            assert row["semantic_key"] == SEMANTIC, row_id


def test_the_arms_do_not_agree_on_how_many_homes_the_semantic_has():
    """One on arm A, one on arm C, TWO on arm B. That asymmetry is the variable."""
    homes = {arm: len(catalogue(arm)) for arm in ARM_TREES}
    assert homes == {"arm_a": 1, "arm_b": 2, "arm_c": 1}, homes
    wired = {
        arm: [row_id for row_id, row in catalogue(arm).items() if row.get("wired_by_default")]
        for arm in ARM_TREES
    }
    assert all(len(rows) == 1 for rows in wired.values()), wired


# -- what was measured ------------------------------------------------------


def test_arm_b_carries_an_adapter_internal_fault_and_it_is_the_first_arm_that_does():
    """`PA-06-DF-04`: the class this work exists for had only ever been measured
    on `reference_ports/`, a tree the epic authored. `FI-M17` is that class on an
    artifact a prompt produced, and its cells are the PA-M11/PA-M12 shape."""
    cells = report("arm_b")["per_mutant"]
    real = cells["FI-M16-arm-b-real-adapter-drops-close-lines"]["cells"]
    fake = cells["FI-M17-arm-b-fake-adapter-drops-close-lines"]["cells"]
    assert real["corpus-port-swap:real"] == "KILLED"
    assert real["corpus-port-swap:fake"] == "SURVIVED"
    assert fake["corpus-port-swap:real"] == "SURVIVED"
    assert fake["corpus-port-swap:fake"] == "KILLED"
    # Read the difference between the rows, never a total. One semantic, two
    # sides of one port, and exactly one of them is on the executed path at a time.
    assert real["suite-real"] == "KILLED" and real["suite-fake"] == "SURVIVED"
    assert fake["suite-real"] == "SURVIVED" and fake["suite-fake"] == "KILLED"


@pytest.mark.parametrize("arm", ["arm_a", "arm_c"])
def test_an_arm_with_one_composition_cannot_take_the_fault_off_the_path(arm):
    """The sealed negative prediction. Arms A and C declare no fake, so `:fake`
    is a byte-identical rerun of `:real` (`AD-F6`) and CANNOT hide the fault."""
    row = next(iter(catalogue(arm)))
    cells = report(arm)["per_mutant"][row]["cells"]
    assert cells["corpus-port-swap:real"] == "KILLED"
    assert cells["corpus-port-swap:fake"] == "KILLED"
    assert cells["corpus-action-bound"] == "KILLED"
    assert cells["suite-real"] == "KILLED"
    assert "suite-fake" not in cells, (
        "arm A and arm C have no second composition point. A `suite-fake` column here "
        "would silently re-run `suite-real` and report a duplicated cell as an "
        "independent measurement -- AD-F6 with the sign flipped."
    )


@pytest.mark.parametrize("arm,expected", [("arm_a", 1), ("arm_b", 2), ("arm_c", 1)])
def test_composition_count_is_measured_from_the_run_not_read_from_a_mapping(arm, expected):
    """`AD-F6` mechanised: two columns with identical evidence on every row ran
    the same program, whatever the mapping file says they are."""
    measured = divergence.measured_compositions(report(arm))
    assert measured["corpus-port-swap:fake"]["distinct_compositions"] == expected
    # And the UNSWAPPED column is one composition on every arm by construction.
    assert measured["corpus-port-swap:real"]["distinct_compositions"] == 1
    assert measured["corpus-action-bound"]["distinct_compositions"] == 1


def test_every_reported_cell_sits_under_the_control_state_read_from_the_artifact():
    """`FI-02-DF-02`: `run_port_swap.py` prints a red control and exits 0. So the
    control state is read out of the JSON, never inferred from an exit code."""
    for arm in ARM_TREES:
        artifact = report(arm)
        assert artifact["control_red"] == [], f"{arm} has red controls: {artifact['control_red']}"
        assert artifact["unmutated_control_failed"] == [], arm
        declared = [
            row_id for row_id, row in artifact["per_mutant"].items() if row.get("control_role")
        ]
        assert declared, (
            f"{arm} declares NO control. 'No control was violated' is vacuous when there "
            "is no control, which is R2's own failure mode, and every kill number in that "
            "run would be a floor."
        )
    # Arm B is the only arm in this project with an in-region POSITIVE control,
    # and it is GREEN, so arm B's SURVIVED cells are counts rather than floors.
    verdict = report("arm_b")["per_mutant"][
        "FI-M15-positive-control-commit-total-too-large"
    ]["control_verdict"]
    assert verdict["role"] == "positive" and verdict["green"] is True


# -- the divergence, and the analysis that decides it -----------------------


def analysis() -> dict:
    return divergence.build(
        {arm: (RESULTS / f"swap-{arm}.json", CATALOGUES[arm]) for arm in ARM_TREES}
    )


def test_the_fixture_can_diverge_and_the_reason_is_the_architecture():
    result = analysis()
    assert result["verdict"] == "FIXTURE CAN DIVERGE"
    diverged = [d for d in result["divergences"]]
    assert len(diverged) == 1, diverged
    only = diverged[0]
    assert only["column"] == "corpus-port-swap:fake"
    assert only["semantic"] == SEMANTIC
    assert only["per_arm"] == {"arm_a": "KILLED", "arm_b": "SURVIVED", "arm_c": "KILLED"}
    # The variable that tracks the verdict is the composition count, not the
    # re-anchoring: arm C is a third independent re-anchoring and lands on arm A's
    # side, which is the check PA-04 asked for and PA-06 supplied for `M09`.
    assert only["compositions_per_arm"] == {"arm_a": 1, "arm_b": 2, "arm_c": 1}


def test_the_columns_that_swap_nothing_are_reported_not_reachable():
    """The entailment still holds everywhere the instrument is shared. A tool
    that called every column reachable would have proved nothing."""
    reachability = analysis()["reachability"]
    assert reachability["corpus-action-bound"]["verdict"] == "NOT_REACHABLE"
    assert reachability["corpus-port-swap:real"]["verdict"] == "NOT_REACHABLE"
    assert reachability["suite-real"]["verdict"] == "NOT_REACHABLE"
    assert reachability["corpus-port-swap:fake"]["verdict"] == "REACHABLE"
    assert reachability["suite-fake"]["verdict"] == "REACHABLE_BY_ABSENCE"


def test_the_row_with_no_counterpart_is_never_given_one():
    result = analysis()
    asymmetries = {record.get("kind"): record for record in result["structural_asymmetries"]}
    homes = asymmetries["unequal homes for one semantic"]
    assert homes["homes_per_arm"] == {"arm_a": 1, "arm_b": 2, "arm_c": 1}
    assert homes["rows_with_no_counterpart"] == [
        "FI-M17-arm-b-fake-adapter-drops-close-lines"
    ]
    absent = asymmetries["column absent on some arms"]
    assert absent["column"] == "suite-fake"
    assert absent["absent_on_arms"] == ["arm_a", "arm_c"]


def test_the_divergence_count_is_not_inflated_by_arm_b_having_an_extra_row():
    """The first version of `divergence.py` compared SETS of verdicts across all
    rows and reported four divergences instead of one, because arm B contributed
    `{KILLED, SURVIVED}` from two rows against arm A's `{KILLED}` from one. A
    divergence count that is too large is exactly the failure this ticket exists
    to stop, so the comparable row is declared per row in the catalogue and this
    test pins the count."""
    result = analysis()
    assert len(result["divergences"]) == 1
    per_semantic = result["per_semantic"][SEMANTIC]
    assert per_semantic["comparable_row_per_arm"] == {
        "arm_a": "FI-M18-arm-a-only-home-drops-close-lines",
        "arm_b": "FI-M16-arm-b-real-adapter-drops-close-lines",
        "arm_c": "FI-M19-arm-c-only-home-drops-close-lines",
    }


# -- R1: the analysis's OWN demonstrated failing input ----------------------


def _synthetic(arm_has_fake: bool, fake_differs: bool) -> dict:
    """A minimal `run_port_swap`-shaped report. Two columns, one row."""
    real = {"total_ran": 10, "total_failed": 0, "total_skipped": 0, "failures": []}
    fake = dict(real, total_failed=1, failures=["x"]) if fake_differs else dict(real)
    columns = ["corpus-port-swap:real"] + (["corpus-port-swap:fake"] if arm_has_fake else [])
    evidence = {"corpus-port-swap:real": real}
    cells = {"corpus-port-swap:real": "SURVIVED"}
    if arm_has_fake:
        evidence["corpus-port-swap:fake"] = fake
        cells["corpus-port-swap:fake"] = "SURVIVED"
    return {
        "instruments": columns,
        "per_mutant": {"ROW": {"cells": cells, "evidence": evidence}},
        "controls_on_unmutated_code": {name: {} for name in columns},
        "control_red": [],
        "unmutated_control_failed": [],
    }


def test_divergence_goes_RED_when_it_claims_reachability_its_own_run_cannot_show(tmp_path):
    """THE DEMONSTRATED FAILING INPUT, per R1.

    Two arms whose swapped columns ran DIFFERENT numbers of compositions -- so
    `E1` fails and divergence is reachable in principle -- and whose cells agree
    anyway. The analysis must say `CLAIMED_REACHABLE_BUT_UNDEMONSTRATED` and the
    command must exit nonzero. An analysis that reported this green would be the
    next instrument in this repository that cannot produce the result which
    would refute it, which is the defect the whole epic is about.
    """
    catalogue_text = (
        '[catalogue]\nid = "SYNTH"\n\n[[mutants]]\nid = "ROW"\n'
        'semantic_key = "s"\nwired_by_default = true\npath = "x.py"\n'
        'find = "a"\nreplace = "b"\n'
    )
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    left.write_text(json.dumps(_synthetic(arm_has_fake=True, fake_differs=True)))
    right.write_text(json.dumps(_synthetic(arm_has_fake=True, fake_differs=False)))
    cat = tmp_path / "c.toml"
    cat.write_text(catalogue_text)

    result = divergence.build({"left": (left, cat), "right": (right, cat)})
    assert result["reachability"]["corpus-port-swap:fake"]["verdict"] == (
        "CLAIMED_REACHABLE_BUT_UNDEMONSTRATED"
    )
    assert result["undemonstrated_reachability_claims"] == ["corpus-port-swap:fake"]
    assert result["verdict"] == "NULL STILL ENTAILED -- no divergence measured"


def test_divergence_reports_the_null_still_entailed_when_nothing_diverges(tmp_path):
    """The other half of R1: the PASSING input still has to be able to say no."""
    catalogue_text = (
        '[catalogue]\nid = "SYNTH"\n\n[[mutants]]\nid = "ROW"\n'
        'semantic_key = "s"\nwired_by_default = true\npath = "x.py"\n'
        'find = "a"\nreplace = "b"\n'
    )
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    left.write_text(json.dumps(_synthetic(arm_has_fake=False, fake_differs=False)))
    right.write_text(json.dumps(_synthetic(arm_has_fake=False, fake_differs=False)))
    cat = tmp_path / "c.toml"
    cat.write_text(catalogue_text)

    result = divergence.build({"left": (left, cat), "right": (right, cat)})
    assert result["verdict"] == "NULL STILL ENTAILED -- no divergence measured"
    assert result["undemonstrated_reachability_claims"] == []
    assert result["reachability"]["corpus-port-swap:real"]["verdict"] == "NOT_REACHABLE"


# -- generator against suite, as SETS ---------------------------------------


def test_the_dominance_result_is_a_property_of_who_wrote_the_catalogue():
    """Three epics have carried "the generated corpus is worse than a suite a
    competent engineer writes in an afternoon". It is measured on catalogues
    written by the author of the suite. On the only catalogues in this repository
    authored BLIND, neither dominates and each has a kill the other misses."""
    result = generator_vs_suite.build()
    blind_a = result["tables"]["blind/arm A"]["comparison"]
    blind_b = result["tables"]["blind/arm B"]["comparison"]
    for figures in (blind_a, blind_b):
        assert figures["verdict"].startswith("COMPLEMENTARY"), figures["verdict"]
        assert len(figures["generated_only"]) == 1
        assert len(figures["suite_only"]) == 1
    assert blind_a["generated_only"] == ["BA-P11"]
    assert blind_b["generated_only"] == ["BA-Q11"]

    for label in ("seeded/arm A", "seeded/arm B"):
        figures = result["tables"][label]["comparison"]
        assert figures["verdict"] == "IDENTICAL SETS", label
        assert figures["generated_only"] == [] and figures["suite_only"] == []

    # And the one place the suite really does dominate is the port machinery, on
    # the tree the epic authored. Both halves are reported; neither softens the other.
    ports = result["tables"]["ports/reference_ports"]["comparison"]
    assert ports["verdict"] == "SUITE STRICTLY DOMINATES"
    assert ports["generated_only"] == []
