"""RM-01 -- the instrument that can return a non-zero price, and the shipped
classifier it catches.

`RD-02` measured that 0 of 9 gap mutants could have priced their removal, and
shipped `removal_census.py discriminate` to compute that condition up front.
The condition is computed over **detector names**, and this file is the
demonstration that reading a surviving detector name as a surviving kill is
unsound in the exact direction `discriminate` uses it in.

R1 -- THE DEMONSTRATED FAILING INPUT IS A REAL ONE. `test_the_shipped_
classifier_calls_a_real_priced_removal_entailed` runs the shipped classifier,
unmodified, over the sealed artifacts of a real removal that landed at
`bf0fb29`, and shows it reporting *"DIES after the cut was entailed before the
cut was made"* about a fault that measurably stopped being caught. Nothing in
this file is a synthetic fixture except the two unit cases that pin the
vocabulary, and those are marked as such.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GAP = REPO_ROOT / "examples/validation/gap_mutants"
PRICER = GAP / "price_removal.py"
CENSUS_DIR = REPO_ROOT / "examples/validation/removal_census"
EVIDENCE = (REPO_ROOT / "specs/results/scorecards/portable-substrate"
            / "GOAL-removal-can-be-priced/RM-01")

RF1 = "RM-01-RF-1-a-registered-instrument-outside-the-derived-scope-loses-its-row"
CTRL = "RM-01-RF-CTRL-a-registered-instrument-INSIDE-the-derived-scope-loses-its-row"

tomllib = pytest.importorskip("tomllib")


def _module(path: Path, name: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pricer():
    return _module(PRICER, "price_removal_under_test")


@pytest.fixture(scope="module")
def census():
    """The classifier that actually ships. Imported, never re-typed."""
    sys.path.insert(0, str(CENSUS_DIR))
    return _module(CENSUS_DIR / "removal_census.py", "removal_census_under_test")


def _load(name: str) -> dict:
    path = EVIDENCE / name
    if not path.is_file():
        pytest.skip(f"{name} is not in the tree; RM-01's measurement was not carried")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rf_before() -> dict:
    return _load("residual-before-bf0fb29p.json")


@pytest.fixture(scope="module")
def rf_after() -> dict:
    return _load("residual-after-bf0fb29.json")


# --------------------------------------------------------------------------
# R1: the failing input, on a real subject
# --------------------------------------------------------------------------


def test_the_shipped_classifier_calls_a_real_priced_removal_entailed(
    pricer, census, rf_before, rf_after
) -> None:
    """R1. THE DEMONSTRATED FAILING INPUT, AND IT IS NOT A FIXTURE.

    `removal_census.discriminating` decides whether a re-run could say anything
    by asking whether every killing DETECTOR is deleted by the removal. SM-03
    deleted no detector, so it answers `NON-DISCRIMINATING` for every fault
    with any kill at all, with the reason *"DIES after the cut was entailed
    before the cut was made"*.

    `RM-01-RF-1` is a fault on that removal that was measured at both trees.
    It dies at `bf0fb29~1` and survives at `bf0fb29`. The classifier says the
    opposite, from data alone, and would have told a removal ticket not to
    bother running it.
    """
    manifest = tomllib.loads((CENSUS_DIR / "removals.toml").read_text(encoding="utf-8"))
    removal = next(r for r in manifest["removal"] if r["id"] == "hardcoded-enumeration-literal")
    deleted = removal.get("deletes_detectors", [])
    assert deleted == [], "SM-03 deleted no detector; that is the premise of this test"

    shipped = census.discriminating(rf_before, RF1, deleted)
    assert shipped["verdict"] == "NON-DISCRIMINATING"
    assert "entailed" in shipped["why"]

    measured = pricer.price(rf_before, rf_after, RF1, "bf0fb29", deleted)
    assert measured["verdict"] == "PRICED", measured
    assert measured["kills_before"], "a PRICED fault must have had a kill to lose"
    assert measured["kills_after"] == []


def test_the_price_is_a_detector_that_survived_by_name_and_lost_the_kill(
    pricer, rf_before, rf_after
) -> None:
    """The loss reason, which is the thing no survivorship test can produce.

    `registry-enumeration` is one pytest node. Its file, its function name and
    its node id are identical at `bf0fb29~1` and `bf0fb29`. Its BODY is not:
    before the cut it asserts `required <= enumerated` over a literal of
    thirteen paths, after it walks two declared roots. The fault is on a path
    outside those roots, so the node survives and the kill does not.
    """
    row = pricer.price(rf_before, rf_after, RF1, "bf0fb29", [])
    reasons = {lost["reason"] for lost in row["lost_kills"]}
    assert pricer.DETECTOR_WEAKENED in reasons, row["lost_kills"]
    weakened = [l for l in row["lost_kills"] if l["reason"] == pricer.DETECTOR_WEAKENED]
    assert any(l["detector"] == "registry-enumeration" for l in weakened), weakened
    # And the node really is still there -- this is not a NODE-REMOVED in disguise.
    assert pricer.node_present(
        "bf0fb29",
        "tests/test_instrument_demonstrations.py::"
        "test_the_named_instruments_are_all_enumerated",
    )


def test_the_positive_control_died_at_both_trees(rf_before, rf_after) -> None:
    """R2. Without this, RM-01-RF-1's SURVIVES is undecided rather than a price.

    The control is the same fault class with ONE property changed: the path is
    inside the derived scope. If it did not die at `bf0fb29`, the after-tree's
    detector is dead for every input and the measurement decides nothing.
    """
    for table, where in ((rf_before, "bf0fb29~1"), (rf_after, "bf0fb29")):
        cell = table["per_mutant"][CTRL]["detectors"]["registry-enumeration"]
        assert cell["verdict"] == "DIES", f"control did not die at {where}: {cell}"
        assert cell["executed"] > 0, f"control executed nothing at {where}"
        assert table["control_red"] == [], table["control_red"]
        assert table["mutants_not_applied"] == [], table["mutants_not_applied"]


# --------------------------------------------------------------------------
# the asymmetry
# --------------------------------------------------------------------------


def test_entail_never_reports_that_a_DIES_was_entailed(pricer, rf_before) -> None:
    """The one-word correction, asserted so it cannot be undone quietly.

    Survivorship over a before-table is sound towards SURVIVES and unsound
    towards DIES. `entail` therefore has no verdict meaning "it will still
    die"; the strongest thing it may say about a surviving killing node is
    UNDECIDED.
    """
    row = pricer.entail(rf_before, RF1, [], "bf0fb29")
    assert row["verdict"] == "UNDECIDED"
    assert row["kills_that_survive_by_name"]
    source = PRICER.read_text(encoding="utf-8")
    assert "ENTAILED-DIES" not in source.replace("never emits `ENTAILED-DIES`", "")


def test_entail_proves_survives_when_every_killing_node_is_deleted(pricer) -> None:
    """SYNTHETIC, and marked as such: the sealed record contains no removal
    that deletes every killing node of any fault, so the sound direction has no
    real instance to be shown on. What is pinned here is the vocabulary."""
    before = {"per_mutant": {"F": {"detectors": {
        "gone": {"verdict": "DIES", "new_failing_nodes": []},
    }}}}
    row = pricer.entail(before, "F", ["gone"], None)
    assert row["verdict"] == "ENTAILED-SURVIVES"
    assert "ADDED" in row["why"], "the bound must travel with the verdict"


def test_a_column_that_decided_nothing_is_never_read_as_a_survival(pricer) -> None:
    """SYNTHETIC. `INERT`, `CONTROL_RED` and `NOT_RUN` are neither kills nor
    survivals -- `FI-06`, and `RD-02`'s dead `port-binding-report` column,
    which sat in two published tables reading almost like a detector."""
    for dead in ("INERT", "CONTROL_RED", "NOT_RUN"):
        record = {"detectors": {"d": {"verdict": dead, "new_failing_nodes": []}}}
        kills, undecided = pricer.kill_set(record)
        assert kills == set()
        assert undecided == ["d"]


# --------------------------------------------------------------------------
# the re-priced historical removals
# --------------------------------------------------------------------------


def test_node_granularity_does_not_rescue_the_nine_catalogue_mutants(pricer) -> None:
    """RD-02's `0 of 9` RE-PRICED at a finer granularity, and it survives.

    RD-02 computed it over detector names. This recomputes it over the kill
    SET -- a killing node counts as surviving only if the node still exists at
    the removal's head. If the finer reading had flipped a row, RD-02's
    headline would be wrong; it does not, and exactly one kill in the whole
    sealed table is lost to a removal.

    THIS IS THE HONEST HALF OF RM-01. The re-priced historical removals come
    back at zero, and the zero is now a measurement over kills rather than an
    artifact of a detector list.
    """
    report = pricer.audit(
        tomllib.loads((CENSUS_DIR / "removals.toml").read_text(encoding="utf-8"))
    )
    priced = [r for r in report["rows"] if r["measured"] == "PRICED"]
    assert priced == [], priced
    lost = [l for r in report["rows"] for l in r["lost_kills"]]
    by_reason: dict[str, list] = {}
    for entry in lost:
        by_reason.setdefault(entry["reason"], []).append(entry)
    # Two detectors were deleted outright by SM-02 and took their kills with
    # them, and EXACTLY ONE kill in the whole sealed table is lost at node
    # granularity -- which is the reading RD-02 did not take.
    assert sorted(by_reason) == [pricer.DETECTOR_REMOVED, pricer.NODE_REMOVED], by_reason
    assert len(by_reason[pricer.NODE_REMOVED]) == 1, by_reason[pricer.NODE_REMOVED]
    assert by_reason[pricer.NODE_REMOVED][0]["node"].startswith(
        "tests/test_port_adapter_binding.py::"
    )
    weakened = [l for l in lost if l["reason"] == pricer.DETECTOR_WEAKENED]
    assert weakened == [], (
        "the sealed record contains no DETECTOR-WEAKENED loss, which is why the "
        "shipped classifier has never been caught out by it"
    )


def test_the_shipped_classifier_agrees_with_every_measurement_in_the_sealed_record(
    pricer,
) -> None:
    """AND THE UNFLATTERING COMPANION TO THE R1 TEST.

    Over the ten published before/after rows, `discriminate` is right ten times.
    Its unsoundness is real and the sealed record does not exhibit it, because
    the record contains no fault of the weakening class. RM-01 had to construct
    one. Asserted so that a future round cannot read the R1 result as
    'discriminate is usually wrong'.
    """
    report = pricer.audit(
        tomllib.loads((CENSUS_DIR / "removals.toml").read_text(encoding="utf-8"))
    )
    assert len(report["rows"]) == 10
    assert all(row["agrees"] for row in report["rows"])


# --------------------------------------------------------------------------
# the known positive
# --------------------------------------------------------------------------


def test_sm04_gm_t1_reproduces_from_an_independent_implementation() -> None:
    """The known-positive. An instrument that cannot reproduce it is not working.

    `SM-04-GM-T1` lives in `tests/test_score_tools.py` and reads both sides in
    one process at one commit. `altered_score_probe.py` drives the tree's own
    shipped CLI, imports nothing from the suite, and was run against the two
    real trees `6aac1ec~1` and `6aac1ec`.
    """
    before = _load("sm04-gm-t1-before.json")
    after = _load("sm04-gm-t1-after.json")
    assert before["scorecard_version"] == 2 and after["scorecard_version"] == 3
    assert before["verdict"] == "CAUGHT"
    assert after["verdict"] == "UNCAUGHT"
    assert any("does not equal the sum" in p for p in before["new_problems"])
    assert after["new_problems"] == []


def test_the_probes_first_confounded_run_is_kept_on_the_record() -> None:
    """An instrument whose first design was wrong says so with the artifact.

    The first version of the probe raised D3 from 1 to 3, which trips a
    citation rule at BOTH trees and reads CAUGHT everywhere. The fix was to
    move D3 DOWN from a cited 4, which is what SM-04-GM-T1 does. Both runs are
    in the tree so the correction is inspectable rather than asserted.
    """
    confounded = _load("sm04-gm-t1-after-confounded.json")
    assert confounded["verdict"] == "CAUGHT"
    assert any("NO citation" in p for p in confounded["new_problems"])


# --------------------------------------------------------------------------
# the instrument is not a gate
# --------------------------------------------------------------------------


def test_nothing_in_the_repository_invokes_the_pricer() -> None:
    """No new gates. Five epics of static checking caught zero bugs."""
    hits = subprocess.run(
        ["git", "grep", "-l", "price_removal"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    ).stdout.split()
    if not hits:
        pytest.skip("no git history in this tree")
    allowed = {
        "examples/validation/gap_mutants/price_removal.py",   # itself
        "tests/test_price_removal.py",                        # its tests
        "examples/validation/instruments/instruments.toml",   # its registry row
        "examples/validation/gap_mutants/residual_faults.toml",  # names it in a comment
        # RM-03: `test_no_catalogue_mutant_could_have_priced_a_removal_and_it_says_so`
        # explains in a comment why RM-03's mutants read `NOT-IN-TABLE` there --
        # they were priced against their own before-table, with THIS file, over
        # kill sets. A mention, not a call: that test runs `removal_census.py`
        # and nothing else.
        "tests/test_removal_census.py",
        # RM-04: `subjects.toml` names the file in the comment that declares
        # `rm04_removal_pricer` -- the before/after this round scored D2 on was
        # 1209 lines of `gap_mutants.toml` + `run_gap_mutants.py` becoming 899
        # of `price_removal.py` + `altered_score_probe.py` +
        # `residual_faults.toml`, and a judge cannot check a declared scope
        # against a description that will not say what is in it. A mention in a
        # TOML comment; nothing in that file can call anything.
        "examples/validation/scorecards/subjects.toml",
    }
    unexpected = [h for h in hits if h not in allowed and not h.startswith("specs/")]
    assert unexpected == [], f"something consults the pricer: {unexpected}"
