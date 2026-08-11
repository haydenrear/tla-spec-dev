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
# CL-02 -- EXTINCT, and the withdrawn headline made mechanical
# --------------------------------------------------------------------------
#
# `RM-05` withdrew `RM-03`'s "first PRICED removal in this project's history".
# The round's own control returned the headline verdict and its row was missing
# from the four-row output the report printed as three. The reason is structural:
# for every fault all of whose killing nodes lie inside a file the removal
# deletes, `ENTAILED-SURVIVES` follows from `git show` alone and no other verdict
# is reachable -- so the verdict carried no information about the removal.
#
# Every test below FAILS at `10cf11a`, this ticket's parent.

RM03_BEFORE = (REPO_ROOT / "specs/results/scorecards/portable-substrate"
               / "GOAL-dead-weight-gone/rm03-gap-mutants-before.json")
RUNNER = "RM03-GM-RUNNER-an-unapplied-mutant-reports-a-survival"
RM03_CTRL = "RM03-GM-CTRL-C-a-detector-that-no-longer-exists-is-reported-as-a-survival"
SM_BEFORE = (REPO_ROOT / "specs/results/scorecards/subtract-to-measure"
             / "before-state/gap-mutants-before.json")

#: Every published before-table, with a head the record actually names.
SEALED_TABLES = [
    (RM03_BEFORE, "6298eee"),
    (RM03_BEFORE, "1e6f691"),
    (SM_BEFORE, "0342a3a"),
    (SM_BEFORE, "bf0fb29"),
    (EVIDENCE / "residual-before-bf0fb29p.json", "bf0fb29"),
]


def _table(path: Path) -> dict:
    if not path.is_file():
        pytest.skip(f"{path.name} is not in the tree")
    return json.loads(path.read_text(encoding="utf-8"))


def test_extinct_is_distinguishable_from_entailed_survives_on_a_real_cut(pricer) -> None:
    """R1, ON A REAL CUT: the row RM-03 headlined and RM-05 withdrew.

    `RM03-GM-RUNNER` is seeded into `examples/validation/gap_mutants/
    run_gap_mutants.py`, which the removal at `6298eee` deletes whole. Its
    killing nodes are in `tests/test_gap_mutants.py`, which the same removal
    deletes whole -- so at the parent commit this row reads `ENTAILED-SURVIVES`,
    the verdict that was published as a price.

    IT IS NOT A PRICE. The removal did not take a detection away from a fault
    that still exists; it deleted the fault's habitat. There is no artifact
    after the cut into which this mutant could be seeded.
    """
    before = _table(RM03_BEFORE)
    row = pricer.entail(before, RUNNER, ["pytest-gap-mutants"], "6298eee")

    assert row["verdict"] == pricer.EXTINCT, row
    assert row["verdict"] != pricer.ENTAILED_SURVIVES
    assert not pricer.is_priced_result(row), "EXTINCT must never read as a price"
    assert row["habitat"] == ["examples/validation/gap_mutants/run_gap_mutants.py"]
    # The habitat really is gone at that head -- not a NOT-IN-TABLE in disguise.
    assert pricer._show("6298eee", row["habitat"][0]) is None
    # And the bound travels with the verdict, as ENTAILED-SURVIVES' does.
    assert "RENAMED" in row["why"], "the file-granular bound must be stated"


def test_extinct_is_a_property_of_the_head_and_not_a_blanket_downgrade(pricer) -> None:
    """THE SAME FAULT, THE OTHER RM-03 REMOVAL, AND IT IS NOT EXTINCT.

    RM-03 made two cuts. `card-dimensions-to-notes` lands at `1e6f691` and does
    not touch `run_gap_mutants.py`; `gap-mutant-catalogue-and-runner` lands at
    `6298eee` and deletes it. If `EXTINCT` were a way of quietly excusing awkward
    rows it would fire at both heads. It fires at one.
    """
    before = _table(RM03_BEFORE)
    assert pricer.entail(before, RUNNER, [], "1e6f691")["verdict"] == pricer.UNDECIDED
    assert pricer.entail(before, RUNNER, [], "6298eee")["verdict"] == pricer.EXTINCT


def test_a_mutant_that_creates_its_own_habitat_is_never_extinct(pricer) -> None:
    """THE GUARD THAT KEEPS `EXTINCT` FROM MAKING SM-03 LOOK CHEAPER.

    `SM-GM-I3` edits `scripts/gap_probe_instrument.py` with `op = "add_file"`,
    and that path is absent at `bf0fb29` **because the mutant creates it**.
    Absence there is the fault's PRECONDITION, not its extinction. A habitat rule
    that read the declared path list instead of the edit ops would call this row
    extinct and lower SM-03's price on a bookkeeping detail.
    """
    before = _table(SM_BEFORE)
    i3 = "SM-GM-I3-an-instrument-that-was-never-added-to-the-registry"
    record = before["per_mutant"][i3]
    assert [e["op"] for e in record["edits"]] == ["add_file"]
    assert pricer._show("bf0fb29", record["edits"][0]["path"]) is None, (
        "the premise: the path really is absent at the head"
    )
    assert pricer.habitat(record) == [], "an add_file edit declares no habitat"
    assert pricer.entail(before, i3, [], "bf0fb29")["verdict"] != pricer.EXTINCT


# --------------------------------------------------------------------------
# CL-02 -- a declared control is not a priceable row, in any mode
# --------------------------------------------------------------------------


def test_no_declared_control_in_any_sealed_table_can_be_a_priced_result(pricer) -> None:
    """THE ROW THAT WITHDREW AN EPIC'S HEADLINE, AND EVERY ONE LIKE IT.

    Swept over every published before-table and every head the record names, in
    BOTH modes. A control excluded by `entail` and priceable by `price` would be
    the same defect with one more step in front of it.
    """
    seen = 0
    for path, head in SEALED_TABLES:
        before = _table(path)
        for mutant, record in before["per_mutant"].items():
            if pricer.declared_control(record) is None:
                continue
            seen += 1
            row = pricer.entail(before, mutant, [], head)
            assert row["verdict"] == pricer.CONTROL_EXCLUDED, (path.name, mutant, row)
            assert not pricer.is_priced_result(row)
            # `price` reads the same row from the same table as its own after-table:
            # the most favourable input a control could be given, and still excluded.
            measured = pricer.price(before, before, mutant, head, [])
            assert measured["verdict"] == pricer.CONTROL_EXCLUDED, measured
            assert not pricer.is_priced_result(measured)
    assert seen >= 4, f"the sealed record declares four controls; found {seen}"


def test_the_control_that_returned_the_headline_verdict_is_excluded(pricer) -> None:
    """`RM03-GM-CTRL-C` by name: `is_control`, `removed_by` 'nothing',
    `gap` 'NONE, on purpose' -- and at the parent commit, `ENTAILED-SURVIVES`."""
    before = _table(RM03_BEFORE)
    record = before["per_mutant"][RM03_CTRL]
    assert record["is_control"] is True
    assert record["removed_by"] == "nothing"
    assert record["gap"].startswith("NONE, on purpose")
    row = pricer.entail(before, RM03_CTRL, ["pytest-gap-mutants"], "6298eee")
    assert row["verdict"] == pricer.CONTROL_EXCLUDED
    assert not pricer.is_priced_result(row)


def test_an_excluded_control_is_still_printed_and_in_no_denominator(pricer) -> None:
    """EXCLUDED IS NOT HIDDEN, AND THAT IS THE POINT OF RM-05's FINDING.

    RM-05's defect was a control row MISSING from the output, not a control row
    being scored. A renderer that dropped controls to keep the table tidy would
    reproduce the omission exactly. So the row is printed, in its own block,
    outside every denominator -- and the count of what was excluded is printed
    beside the denominator, because a control leaving it lowers the denominator
    without lowering any numerator, which is the direction that makes a price
    look LARGER.
    """
    before = _table(RM03_BEFORE)
    rows = [pricer.entail(before, m, [], "6298eee") for m in sorted(before["per_mutant"])]
    rendered = pricer.render_entail(rows, "6298eee")
    assert RM03_CTRL in rendered, "the control's row must not go missing again"
    assert "1 declared control(s) excluded" in rendered
    assert "0 of 3 subject(s) ENTAILED-SURVIVES" in rendered
    assert "1 EXTINCT (not a price)" in rendered


# --------------------------------------------------------------------------
# CL-02 -- `--head` is validated, because an unresolvable one priced everything
# --------------------------------------------------------------------------


def test_an_unresolvable_head_is_refused_instead_of_pricing_the_whole_table(
    pricer,
) -> None:
    """R1. THE DEMONSTRATED FAILING INPUT, ON THE SEALED RM-03 TABLE.

    `node_present` answers `False` when `git show <head>:<path>` fails, and it
    failed identically for a path the removal deleted and for a head that names
    nothing. At the parent commit this exact command printed four
    `ENTAILED-SURVIVES` rows and exited 0.
    """
    if not RM03_BEFORE.is_file():
        pytest.skip("RM-03's before-table is not in the tree")
    done = subprocess.run(
        [sys.executable, str(PRICER), "entail",
         "--before", str(RM03_BEFORE), "--head", "deadbeefdeadbeef"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert done.returncode == 2, done.stdout + done.stderr
    assert "ENTAILED-SURVIVES" not in done.stdout, done.stdout
    assert "does not name a commit" in done.stderr, done.stderr

    # And the same head that IS resolvable still produces a table.
    good = subprocess.run(
        [sys.executable, str(PRICER), "entail",
         "--before", str(RM03_BEFORE), "--head", "6298eee"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert good.returncode == 0, good.stdout + good.stderr
    assert pricer.EXTINCT in good.stdout


def test_the_api_refuses_an_unresolvable_head_too(pricer) -> None:
    """Validated in the functions, not only at the CLI, so an importer that
    skips `main` cannot skip the check."""
    before = _table(RM03_BEFORE)
    for call in (
        lambda: pricer.entail(before, RUNNER, [], "deadbeefdeadbeef"),
        lambda: pricer.price(before, before, RUNNER, "deadbeefdeadbeef", []),
    ):
        with pytest.raises(pricer.HeadNotResolvable):
            call()


# --------------------------------------------------------------------------
# CL-02 -- the re-priced history, and the known positives
# --------------------------------------------------------------------------


def test_rm03s_withdrawn_headline_re_prices_to_no_price_at_all(pricer) -> None:
    """THE RE-PRICED HISTORICAL REMOVAL, AND THE NUMBER IS ZERO.

    `gap-mutant-catalogue-and-runner` was the one removal in the census with a
    claimed non-zero price. Re-priced with the corrected instrument it has NO
    priced row: the control is excluded, the headline row is `EXTINCT`, and the
    two remaining subjects are `UNDECIDED` because their killing nodes are in
    `tests/test_score_tools.py`, which this removal does not delete.

    A ZERO IS NOT THE GOAL AND WAS NOT TUNED FOR. If a future round makes a
    historical removal come back non-zero, that is the informative outcome and
    this assertion is the thing that should be rewritten to say so.
    """
    before = _table(RM03_BEFORE)
    rows = [pricer.entail(before, m, ["pytest-gap-mutants"], "6298eee")
            for m in sorted(before["per_mutant"])]
    assert [r for r in rows if pricer.is_priced_result(r)] == []
    by_verdict = {r["mutant"]: r["verdict"] for r in rows}
    assert by_verdict[RM03_CTRL] == pricer.CONTROL_EXCLUDED
    assert by_verdict[RUNNER] == pricer.EXTINCT
    assert sorted(set(by_verdict.values())) == [
        pricer.CONTROL_EXCLUDED, pricer.EXTINCT, pricer.UNDECIDED,
    ]


def test_the_correction_does_not_move_the_sealed_audit_record(pricer) -> None:
    """`denominator_rule`, on the ten measured rows.

    Control exclusion and `EXTINCT` are additions, not re-readings: no control
    appears in any removal's `gap_mutants`, and no catalogue fault's habitat is
    deleted by the removal it is priced against. The ten rows are the same ten
    rows, with the same verdicts. If this moves, the numerator moved and the
    audit's `0 of 10 disagree` is no longer RM-01's number.
    """
    report = pricer.audit(
        tomllib.loads((CENSUS_DIR / "removals.toml").read_text(encoding="utf-8"))
    )
    assert len(report["rows"]) == 10
    assert all(row["agrees"] for row in report["rows"])
    assert [r for r in report["rows"] if r["measured"] == pricer.PRICED] == []
    assert pricer.CONTROL_EXCLUDED not in {r["measured"] for r in report["rows"]}
    assert pricer.EXTINCT not in {r["this_instrument"] for r in report["rows"]}


def test_rm01s_known_positive_still_prices_after_the_correction(
    pricer, rf_before, rf_after
) -> None:
    """KNOWN POSITIVE ONE. An instrument that cannot reproduce it is not working.

    `RM-01-RF-1` is a real `DIES` -> `SURVIVES` that survived a direct
    adversarial attempt to refute it. Its habitat is `instruments.toml`, which
    SM-03's removal does NOT delete -- so it is not extinct, it is not a control,
    and it is still `PRICED`.
    """
    row = pricer.price(rf_before, rf_after, RF1, "bf0fb29", [])
    assert row["verdict"] == pricer.PRICED, row
    assert pricer.is_priced_result(row)
    assert pricer.habitat(rf_before["per_mutant"][RF1]) == [
        "examples/validation/instruments/instruments.toml"
    ]
    assert pricer._show("bf0fb29", "examples/validation/instruments/instruments.toml")
    assert pricer.entail(rf_before, RF1, [], "bf0fb29")["verdict"] == pricer.UNDECIDED


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
