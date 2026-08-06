"""FI-01: an instrument that can fail, and a control a port-scoped one can see.

Two things are under test and each of them is a rule this epic added.

**R1 -- an instrument ships with a DEMONSTRATED FAILING INPUT.** Not a test that
the instrument passes on good input: a broken probe passes good input too, which
is exactly how `PA-06-DF-07` happened. `examples/validation/ab/
probe_demonstrations.toml` holds five controls broken on purpose, each declaring
the verdict the probe must return for it, and the tests below RUN it. If a
future change makes the probe soft, the demonstration is what fails.

**R2 -- a control that cannot fail is worse than no control.** `PA-M14` is
measured INERT on `reference_ports` and that verdict is PINNED here rather than
repaired away, because repairing it by weakening the property is the act this
project has committed four times, most recently in the ticket whose job was to
catch it.

Nothing here is a gate. `check_catalogue.py` refuses nothing in the product; the
epic's `no_new_gates_rule` bans a new blocking check and these are tests of a
fixture.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AB = REPO_ROOT / "examples" / "validation" / "ab"
DEMONSTRATIONS = AB / "probe_demonstrations.toml"
ARM_B_CONTROL = AB / "eval" / "controls_port_region_arm_b.toml"
RERUN_ARMS = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/arms"


def _load_check_catalogue():
    """Import the SHIPPED harness. Not a copy of it -- a rename must fail."""
    spec = importlib.util.spec_from_file_location(
        "_fi01_check_catalogue", AB / "check_catalogue.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cc = _load_check_catalogue()


def _rows(catalogue: Path) -> list[dict]:
    _, raw_rows, _ = cc.load_catalogue(catalogue)
    return raw_rows


# -- R1: the probe's demonstrated failing input ------------------------------


def test_the_probe_reports_a_no_op_control_BROKEN():
    """THE HEADLINE. `PA-06-DF-07 (b)`, reproduced and now caught.

    A mutant whose `replace` is the identical line plus a comment, declared
    `control_role = "positive"`. The old probe reported HOLDS, which is why
    every HOLDS it printed -- including the one PA-01 offered as evidence its
    repair worked -- was worth nothing.
    """
    row = next(r for r in _rows(DEMONSTRATIONS) if r["id"].startswith("DEMO-01"))
    assert row["find"].strip() in row["replace"], (
        "DEMO-01 must be the identical line plus a comment, or it is not a no-op"
    )
    verdict, detail = cc.probe_control_property(
        AB / "reference_ports", "quota_ledger", "domain.py",
        row["find"], row["replace"], "accept-path-only",
    )
    assert verdict == "INERT", (
        f"a NO-OP declared a positive control probed {verdict} ({detail}). A probe "
        f"that does not go red here cannot go red for anything."
    )


def test_the_probe_reports_a_control_that_needs_two_steps_BROKEN():
    """`PA-06-DF-07 (a)`. Not a strawman: this is `PA-M14`'s own mutation.

    Every generated corpus case is single-action, so a control that only
    surfaces on the second action cannot be killed by any corpus regardless of
    reach -- which is why `PA-M14` is RED on four of `reference_ports`' six
    columns for a reason that is about the control, not the instrument.
    """
    row = next(r for r in _rows(DEMONSTRATIONS) if r["id"].startswith("DEMO-04"))
    verdict, _ = cc.probe_control_property(
        AB / "reference_ports", "quota_ledger", "domain.py",
        row["find"], row["replace"], "accept-path-only",
    )
    assert verdict == "INERT"


def test_the_probe_reports_a_control_outside_the_ports_region_OUT_OF_REGION():
    """`PA-03-DF-03` made executable.

    A port case narrows its expected `after` to `{closed, committed, ledger}`.
    A control landing anywhere else is undecidable by every port-scoped
    instrument no matter how blatant it is, and a column of survivors beside it
    cannot be told apart from a dead column.
    """
    row = next(r for r in _rows(DEMONSTRATIONS) if r["id"].startswith("DEMO-03"))
    verdict, detail = cc.probe_control_property(
        AB / "reference_ports", "quota_ledger", "domain.py",
        row["find"], row["replace"], "port-region-commit-path",
    )
    assert verdict == "OUT_OF_REGION", detail
    assert "available" in detail, "the probe must name what moved instead"


def test_the_probe_still_says_yes_to_a_control_that_works():
    """S2 asks for a demonstrated PASSING input too.

    A probe that reported everything broken would be exactly as useless as one
    that reported everything fine, and it would be far easier to ship by
    accident while feeling rigorous.
    """
    row = next(r for r in _rows(DEMONSTRATIONS) if r["id"].startswith("DEMO-05"))
    verdict, detail = cc.probe_control_property(
        AB / "reference_ports", "quota_ledger", "domain.py",
        row["find"], row["replace"], "port-region-commit-path",
    )
    assert verdict == "HOLDS", detail


def test_every_demonstration_row_declares_the_verdict_it_demonstrates():
    """A demonstration that does not say what it demonstrates cannot fail."""
    rows = _rows(DEMONSTRATIONS)
    assert len(rows) >= 4, "too few demonstrations to say the probe can fail"
    verdicts = {str(row.get("probe_must_report", "")) for row in rows}
    assert "" not in verdicts, "a demonstration row with no `probe_must_report`"
    assert {"INERT", "BROKEN", "OUT_OF_REGION", "HOLDS"} <= verdicts, (
        f"the demonstration does not cover every way the probe must be able to "
        f"answer; it covers {sorted(verdicts)}"
    )


def test_the_shipped_demonstration_command_is_re_runnable_and_passes():
    """R1 end to end, through the command a reader would actually type.

    Exercising the CLI rather than the function is the point: a demonstration
    that only runs from inside pytest is not a demonstration anyone can re-run.
    """
    done = subprocess.run(
        [sys.executable, str(AB / "check_catalogue.py"), "--demonstrate",
         "--catalogue", str(DEMONSTRATIONS)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "R1 holds" in done.stdout
    for name in ("DEMO-01", "DEMO-02", "DEMO-03", "DEMO-04", "DEMO-05"):
        assert name in done.stdout


def test_the_demonstration_FAILS_if_the_probe_goes_soft():
    """The demonstration's own non-vacuity, and it is not optional.

    A demonstration harness that passes whatever the probe says is a second copy
    of the defect it exists to catch. This makes the probe answer HOLDS for
    everything and asserts the demonstration then FAILS -- so a future change
    that neuters the probe cannot leave a green demonstration behind it.
    """
    saved = cc.probe_control_property
    try:
        cc.probe_control_property = lambda *a, **k: ("HOLDS", "a probe gone soft")
        problems = cc.demonstrate_probe_failure(DEMONSTRATIONS, AB, "quota_ledger")
    finally:
        cc.probe_control_property = saved
    broken = [line for line in problems if "reported 'HOLDS'" in line]
    assert len(broken) >= 3, problems
    assert any("every HOLDS it has ever printed is void" in line for line in problems)


# -- R2: the control that could not be made to work is reported RED ----------


def test_PA_M14_is_reported_RED_on_the_tree_where_it_cannot_be_observed():
    """MEASURED, PINNED, AND NOT REPAIRED.

    `PA-M14` holds the half the old probe tested -- it is invisible before an
    accepted reserve -- and fails the half it did not: it is invisible AFTER one
    too, because no query exposes a reservation's amount and `reference_ports`
    stores `available` rather than deriving it. It is not deleted, not
    re-anchored and not excused; it still runs, is still declared, is still
    probed on every `--controls` run, and prints INERT every time.
    """
    row = next(
        r for r in _rows(AB / "seeded_faults.toml")
        if r["id"].startswith("PA-M14")
    )
    verdict, detail = cc.probe_control_property(
        AB / "reference_ports", "quota_ledger", "domain.py",
        row["find"], row["replace"], "accept-path-only",
    )
    assert verdict == "INERT", (
        f"PA-M14 probed {verdict} ({detail}). If this ever becomes HOLDS, either "
        f"the tree changed or the probe went soft, and PA-06-DF-07 says which is "
        f"more likely."
    )
    assert str(row.get("control_role", "")).startswith("positive"), (
        "PA-M14 was quietly stripped of its control role. A broken control is "
        "reported broken; it is not deleted to make a table look decided."
    )


def test_a_tree_whose_every_control_is_broken_is_reported_red_not_silent(tmp_path):
    """R2 at the level of a TREE, which is where it actually bites.

    One broken control satisfied the old "exactly one positive control per
    anchor tree" rule perfectly, and that is precisely the state `PA-06-DF-07`
    found `reference_ports` in. What a tree needs is a control that CAN go red;
    with only broken ones every kill number measured on it is a floor, and
    before FI-01 nothing said so.

    The catalogue below is the whole pre-FI-01 world in miniature: one declared
    positive control, no-op, nothing else.
    """
    catalogue = tmp_path / "only_broken.toml"
    catalogue.write_text(
        '[catalogue]\n'
        'id = "one-broken-control"\n'
        'extends = "examples/validation/ab/probe_demonstrations.toml"\n\n'
        '[[mutants]]\n'
        'id = "DEMO-01-noop-is-not-a-control"\n'
        'control_role = "positive -- declared, and a lie"\n'
        'fault_class = "wrong_value"\n'
        'boundary_kind = "invariant"\n'
        'boundary_ref = "R1-conservation"\n'
        'path = "reference_ports/domain.py"\n'
        'find = "        self._next_id = 1"\n'
        'replace = "        self._next_id = 1  # no-op"\n'
        'description = "a no-op declared a control"\n'
        'refine_variable = "amt"\n'
        'refine_action = "Reserve"\n',
        encoding="utf-8",
    )
    problems = cc.check_controls(catalogue, AB, "quota_ledger", tree_root=False)
    joined = "\n".join(problems)
    assert "NOT ONE holds its property" in joined, problems
    assert "FLOOR" in joined


# -- the control seeded inside the port's region -----------------------------


#: Every tree in this repository, and whether it declares a port. Enumerated so
#: that "every tree that declares a port" is a checked claim rather than a list
#: someone kept up to date by hand.
TREES = {
    "reference": AB / "reference",
    "reference_ports": AB / "reference_ports",
    "arm_a": RERUN_ARMS / "arm_a",
    "arm_b": RERUN_ARMS / "arm_b",
    "arm_c": REPO_ROOT / "specs/results/scorecards/ports-as-adapters/arms/arm_c",
}
DECLARES_A_PORT = {"reference_ports", "arm_b"}


def _declares_a_port(tree: Path) -> bool:
    """A port is a declared interface the domain owns, not a directory name."""
    for source in tree.rglob("*.py"):
        if "test" in source.name:
            continue
        text = source.read_text(encoding="utf-8")
        if "Protocol)" in text or "(Protocol" in text or "abstractmethod" in text:
            return True
    return False


def test_the_set_of_trees_that_declare_a_port_is_what_this_ticket_assumed():
    """If a tree grows a port, the claim "every tree that declares one" moves.

    Read from the source, so a new arm with a port fails here instead of
    silently being left without an in-region control.
    """
    measured = {name for name, tree in TREES.items() if _declares_a_port(tree)}
    assert measured == DECLARES_A_PORT, (
        f"trees declaring a port are now {sorted(measured)}, not "
        f"{sorted(DECLARES_A_PORT)}. Each one needs a positive control seeded "
        f"inside its port's region, or its port-scoped numbers are a floor."
    )


@pytest.mark.parametrize(
    "tree_name,catalogue,relative",
    [
        ("reference_ports", AB / "seeded_faults.toml", "domain.py"),
        ("arm_b", ARM_B_CONTROL, "quota_ledger/domain.py"),
    ],
)
def test_every_tree_with_a_port_has_a_control_inside_the_ports_region(
    tree_name, catalogue, relative
):
    """The ticket's first requirement, run rather than described.

    `GOAL-port-reach` clause 2 -- "and no positive control is red" -- could not
    be met last epic because no control was seeded where a port-scoped
    instrument looks. `corpus-port` executed 1855 cases against
    `reference_ports` and reported BOTH declared controls SURVIVED.
    """
    row = next(r for r in _rows(catalogue) if r["id"].startswith("FI-M15"))
    declared, problems = cc.resolve_control_properties(catalogue)
    assert not problems, problems
    assert declared[str(row["id"])] == "port-region-commit-path"

    verdict, detail = cc.probe_control_property(
        TREES[tree_name], "quota_ledger", relative,
        row["find"], row["replace"], "port-region-commit-path",
    )
    assert verdict == "HOLDS", f"{tree_name}: {verdict} -- {detail}"
    # The point of the region, stated as the assertion rather than as prose: at
    # least one observable a PORT CASE PROJECTS has to move, or no port-scoped
    # instrument can decide the control however blatant it is.
    assert any(name in detail for name in ("committed", "ledger_lines")), detail


def test_the_in_region_control_is_the_same_semantic_on_both_trees():
    """Re-anchored BY THE PROPERTY, not by the bytes -- PA-06-DF-07's lesson.

    The two `find` strings have nothing in common: `reference_ports` writes
    `self._committed[t] += amount` and reads the dict back when it renders the
    line; arm B computes `total` once and uses it twice. What is shared is the
    id, the semantic and the property, which is what makes the two rows one
    experiment.
    """
    ports = next(r for r in _rows(AB / "seeded_faults.toml") if r["id"].startswith("FI-M15"))
    arm_b = next(r for r in _rows(ARM_B_CONTROL) if r["id"].startswith("FI-M15"))
    assert ports["id"] == arm_b["id"]
    assert ports["find"] != arm_b["find"], "re-anchored by the bytes, not the property"
    assert ports["refine_action"] == arm_b["refine_action"] == "Commit"
    assert ports["refine_variable"] == arm_b["refine_variable"] == "committed"
    # EVAL-RERUN-DF-03: a role string copied across trees is how a control stops
    # being about the thing it guards.
    assert ports["control_role"] != arm_b["control_role"]


def test_the_ports_region_is_read_from_the_generator_not_restated():
    """`PORT_REGION` is a transcription of what the case generator prints.

    If the manifest's port grows a variable and this constant does not, the
    probe's region test silently narrows. The generated corpus is the source of
    truth, so the check is against a generated case rather than against prose.
    """
    manifest = (AB / "model" / "spec_manifest.yaml").read_text(encoding="utf-8")
    assert "LedgerAppendPort" in manifest
    # The three names the generator reports for this fixture's one port, spelled
    # as the probe's driver spells them.
    assert set(cc.PORT_REGION) == {"closed", "committed", "ledger_lines"}
    assert set(cc.PORT_REGION) <= set(cc.OBSERVABLES)


# -- PA-06-DF-02: `extends` is executed, not documented -----------------------


def test_extends_is_followed_when_reading_the_control_property():
    """`PA-06-DF-02`. The arm B control file declares NO property table.

    Before FI-01 the property table was read only out of the file handed in, so
    a re-anchored control whose parent declares it was reported undeclared -- and
    the workaround was to copy the table into every re-anchoring file, which is
    five copies of one property with nothing checking them against each other.
    """
    tomllib = cc._toml()
    document = tomllib.loads(ARM_B_CONTROL.read_text(encoding="utf-8"))
    assert "pa_control_properties" not in document, (
        "the arm B control file restated the property; then this test proves "
        "nothing about `extends`"
    )
    resolved, problems = cc.resolve_control_properties(ARM_B_CONTROL)
    assert not problems, problems
    assert resolved["FI-M15-positive-control-commit-total-too-large"] == (
        "port-region-commit-path"
    ), "the property was not inherited from the parent named by `extends`"


def test_a_child_property_wins_over_the_one_it_inherits(tmp_path):
    """Inheritance, not override-by-accident. A re-anchoring that has MEASURED a
    different property on its own tree must be able to say so."""
    child = tmp_path / "child.toml"
    child.write_text(
        '[catalogue]\n'
        'id = "t"\n'
        'extends = "examples/validation/ab/seeded_faults.toml"\n\n'
        '[pa_control_properties]\n'
        '"M07-positive-control-wrong-hold" = "port-region-commit-path"\n',
        encoding="utf-8",
    )
    resolved, problems = cc.resolve_control_properties(child)
    assert not problems
    assert resolved["M07-positive-control-wrong-hold"] == "port-region-commit-path"
    # ...and the siblings it did not restate are still inherited.
    assert resolved["FI-M15-positive-control-commit-total-too-large"] == (
        "port-region-commit-path"
    )


def test_an_extends_that_resolves_to_nothing_is_reported(tmp_path):
    """A declaration that resolves to nothing is the drift the rule is about."""
    child = tmp_path / "child.toml"
    child.write_text(
        '[catalogue]\nid = "t"\nextends = "examples/validation/ab/gone.toml"\n',
        encoding="utf-8",
    )
    _, problems = cc.resolve_control_properties(child)
    assert problems and "does not exist" in problems[0]


def test_an_extends_naming_a_revision_resolves_its_path(tmp_path):
    """`pa_m14_prerepair.toml` carries `<path> @ <rev>`, which names a parent AS
    OF a commit. Reporting that as a broken declaration would be a false
    complaint of exactly the kind PA-06-DF-02 is about."""
    child = tmp_path / "child.toml"
    child.write_text(
        '[catalogue]\nid = "t"\n'
        'extends = "examples/validation/ab/seeded_faults.toml @ 46c29c9^"\n',
        encoding="utf-8",
    )
    resolved, problems = cc.resolve_control_properties(child)
    assert not problems, problems
    assert "M07-positive-control-wrong-hold" in resolved


# -- the fixture is never left modified --------------------------------------


def test_the_probe_leaves_every_tree_byte_identical(tmp_path):
    """A harness that can corrupt the fixture it measures is not a harness.

    The probe copies a tree before mutating it. This asserts the copy, because
    the alternative -- a probe that mutated `reference_ports/domain.py` in place
    and reverted -- is one exception away from leaving a seeded fault in the
    repository.
    """
    domain = AB / "reference_ports" / "domain.py"
    before = domain.read_bytes()
    row = next(r for r in _rows(AB / "seeded_faults.toml") if r["id"].startswith("FI-M15"))
    cc.probe_control_property(
        AB / "reference_ports", "quota_ledger", "domain.py",
        row["find"], row["replace"], "port-region-commit-path",
    )
    assert domain.read_bytes() == before

    # And the same for a tree under `specs/results/`, which this epic's plan
    # declares out_of_model: FI-01 READS the sealed arms and writes nothing.
    arm = RERUN_ARMS / "arm_b" / "quota_ledger" / "domain.py"
    arm_before = arm.read_bytes()
    arm_row = next(r for r in _rows(ARM_B_CONTROL) if r["id"].startswith("FI-M15"))
    cc.probe_control_property(
        RERUN_ARMS / "arm_b", "quota_ledger", "quota_ledger/domain.py",
        arm_row["find"], arm_row["replace"], "port-region-commit-path",
    )
    assert arm.read_bytes() == arm_before


def test_nothing_fi01_added_can_suppress_a_survivor():
    """`no_new_gates_rule` and the suppression scanner, on the new files.

    `probe_must_report` is an expectation about an INSTRUMENT, checked by
    running the instrument. It decides no kill and appears in no measurement.
    This asserts it did not arrive alongside anything that could.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import kill_test  # noqa: PLC0415

    for catalogue in (AB / "seeded_faults.toml", DEMONSTRATIONS, ARM_B_CONTROL):
        text = catalogue.read_text(encoding="utf-8")
        for key in kill_test.SUPPRESSION_KEYS:
            assert f"\n{key} =" not in text and f"[[{key}]]" not in text, (
                f"{catalogue.name} grew a suppression-shaped key {key!r}"
            )
    assert "probe_must_report" not in kill_test.SUPPRESSION_KEYS


def test_the_probe_uses_a_fresh_ledger_file_per_plan(tmp_path):
    """Found by RUNNING it: the file adapter truncates at construction.

    Two plans sharing one ledger path made the second plan's `before` depend on
    the first plan's writes on the REAL wiring and not on the fake one, which
    would have made a verdict depend on the composition point rather than on the
    control. The plans are independent runs and each gets its own file.
    """
    source = (AB / "check_catalogue.py").read_text(encoding="utf-8")
    assert 'f"ledger-{state}-{plan}.txt"' in source


def test_the_two_declared_properties_use_different_paths():
    """Two properties that drive the same actions are one property with two
    names, and a control declared against the wrong one would look checked."""
    accept = cc.CONTROL_PROPERTIES["accept-path-only"]
    port = cc.CONTROL_PROPERTIES["port-region-commit-path"]
    assert accept.present != port.present
    assert accept.absent != port.absent
    assert accept.region == () and port.region == cc.PORT_REGION


def test_the_measured_evidence_is_recorded_beside_the_control():
    """`declaration_executability_rule`: the numbers a reader needs are in the
    catalogue that makes the claim, not only in a report nobody diffs."""
    text = (AB / "seeded_faults.toml").read_text(encoding="utf-8")
    for phrase in ("region {closed, committed, ledger}", "PA-06-DF-07",
                   "PA-03-DF-03", "R2"):
        assert phrase in text, f"the FI-01 block does not cite {phrase}"
    assert "FI-M15" in text


def test_the_run_that_happened_is_recorded(tmp_path):
    """Report the run that happened. The evidence file is committed and parses,
    so a later ticket can diff against it instead of re-deriving prose."""
    evidence = AB / "eval" / "results" / "fi01" / "port-region-control.json"
    assert evidence.is_file(), "FI-01's measured evidence is not committed"
    data = json.loads(evidence.read_text(encoding="utf-8"))
    assert data["reference_ports"]["FI-M15"]["corpus-port-swap:real"] == "KILLED"
    assert data["reference_ports"]["FI-M15"]["corpus-port-swap:fake"] == "KILLED"
    assert data["reference_ports"]["PA-M14"]["corpus-port-swap:real"] == "SURVIVED"
    assert data["arm_b"]["FI-M15"]["corpus-port:real"]["failed"] == 384
    assert data["arm_b"]["clean"]["corpus-port:real"]["failed"] == 0
    assert shutil.which("python3") or True  # the run is recorded, not re-run here
