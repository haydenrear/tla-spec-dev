"""SM-01 -- the gap-mutant catalogue and the runner that prices a removal.

`removal_is_a_delta_rule`: every removal ships with a mutant seeded in its gap
BEFORE the cut. This file is the check that the seeds are real seeds -- that
each anchor is live in the shipped tree, that each mutant names the mechanism it
prices, and that the runner's verdict rule cannot report a survival it did not
observe.

The last part is the point. The three failures this project has already bought
all have the same shape -- a green reading produced by something that did not
run:

  * `FI-01-DF-01`   15 of 15 false SURVIVED, no error, cached modules.
  * `FI-02-DF-02`   a red control printed, exit 0.
  * `FI-06`         `expect_exit = 0`, which a fully skipped run satisfies.

So `verdict()` is tested against all three directly: nothing executed is INERT,
a detector that no longer exists is REMOVED, and neither is ever SURVIVES.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "examples/validation/gap_mutants/run_gap_mutants.py"
CATALOGUE = REPO_ROOT / "examples/validation/gap_mutants/gap_mutants.toml"

tomllib = pytest.importorskip("tomllib")


def _load_runner():
    """Import the SHIPPED runner by path. A rename must fail this file."""
    spec = importlib.util.spec_from_file_location("sm01_run_gap_mutants", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def runner():
    return _load_runner()


@pytest.fixture(scope="module")
def catalogue() -> dict:
    return tomllib.loads(CATALOGUE.read_text(encoding="utf-8"))


# -- 1. the seeds are live in the shipped tree -----------------------------


def test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree(catalogue) -> None:
    """A mutant whose anchor has drifted is a row that will report a survival
    it never measured. `apply_mutant` refuses at run time; this refuses at
    commit time, which is the only place the drift can still be cheap."""
    problems: list[str] = []
    for mutant in catalogue["mutant"] + catalogue["control"]:
        for edit in mutant["edit"]:
            target = REPO_ROOT / edit["path"]
            if "add_file" in edit:
                if target.exists():
                    problems.append(f"{mutant['id']}: add_file target {edit['path']} exists")
                continue
            if not target.is_file():
                problems.append(f"{mutant['id']}: {edit['path']} is missing")
                continue
            if "append" in edit:
                continue
            count = target.read_text(encoding="utf-8").count(edit["find"])
            if count != 1:
                problems.append(f"{mutant['id']}: anchor occurs {count}x in {edit['path']}")
    assert not problems, problems


def test_every_mutant_names_the_mechanism_it_prices_and_the_ticket_that_cuts_it(
    catalogue,
) -> None:
    for mutant in catalogue["mutant"]:
        for key in ("mechanism", "removed_by", "claims_to_catch", "gap"):
            assert mutant.get(key), f"{mutant['id']} has no {key}"
        assert mutant["removed_by"] in {"SM-02", "SM-03", "RM-03"}, mutant["id"]
        assert mutant.get("detector"), f"{mutant['id']} declares no detector"


def test_every_removal_that_declared_a_ticket_carries_at_least_one_gap_mutant(
    catalogue,
) -> None:
    """`GOAL-removal-is-measured` has a baseline of ZERO. No cut that declared a
    ticket here may be the one that stays there.

    RM-03 joins SM-02 and SM-03 rather than replacing them: its rows are seeded
    in the gaps of the mechanisms RM-03 itself removes, before the cut, which is
    what `removal_is_a_delta_rule` asks for and what makes the after-reading a
    measurement rather than an absence.
    """
    cut_by = {mutant["removed_by"] for mutant in catalogue["mutant"]}
    assert cut_by == {"SM-02", "SM-03", "RM-03"}, sorted(cut_by)
    for ticket in sorted(cut_by):
        seeded = [m["id"] for m in catalogue["mutant"] if m["removed_by"] == ticket]
        assert seeded, ticket


def test_every_detector_a_mutant_names_is_declared(catalogue) -> None:
    declared = {entry["id"] for entry in catalogue["detector"]}
    for mutant in catalogue["mutant"] + catalogue["control"]:
        for row in mutant["detector"]:
            assert row["id"] in declared, f"{mutant['id']} names undeclared {row['id']}"


# -- 1b. R2: the table carries positive controls, and they decide columns --


def test_every_detector_that_decides_a_gap_mutant_carries_a_positive_control(
    catalogue,
) -> None:
    """PA-04's first run printed `control_red: []` while a declared control had
    survived four columns that each executed 294 accepting cases. Without a
    control, a SURVIVES cannot be told apart from a detector that never reached
    the subject."""
    controlled = {d for control in catalogue["control"] for d in control["must_die_on"]}
    used = {row["id"] for mutant in catalogue["mutant"] for row in mutant["detector"]}
    uncontrolled = used - controlled
    assert uncontrolled <= {"registry-enumeration", "spec-yaml-tripwire",
                            "port-binding-report"}, sorted(uncontrolled)


def test_a_control_declares_the_detectors_it_must_die_on(catalogue) -> None:
    assert catalogue["control"], "R2: a table with no positive control decides nothing"
    for control in catalogue["control"]:
        assert control["must_die_on"], f"{control['id']} declares no must_die_on"
        assert control.get("control_role"), f"{control['id']} has no role"


def test_the_controls_run_through_the_same_code_path_as_the_gap_mutants() -> None:
    """A control measured by a second code path is not a control for the first."""
    source = RUNNER.read_text(encoding="utf-8")
    assert 'declared += [{**entry, "is_control": True} for entry in document.get("control", [])]' in source
    assert "def apply_control" not in source
    assert "def run_control_detector" not in source


def test_the_ports_mutants_are_measured_by_a_detector_that_outlives_the_cut(
    catalogue,
) -> None:
    """SM-05 has to re-run these AFTER `[ports.*]` is gone. A ports mutant whose
    only detectors use the binding would report REMOVED on every column and
    decide nothing, which is a row that cannot produce a result."""
    detectors = {entry["id"]: entry for entry in catalogue["detector"]}
    for mutant in catalogue["mutant"]:
        if mutant["mechanism"] != "ports-binding-machinery":
            continue
        survivors = [
            row["id"] for row in mutant["detector"]
            if not detectors[row["id"]].get("uses_ports_binding")
        ]
        assert survivors, f"{mutant['id']} has no detector that survives SM-02"


def test_every_cli_detector_declares_flags_its_entry_point_still_accepts(catalogue) -> None:
    """RD-02. A DETECTOR WHOSE ARGV ITS ENTRY POINT REJECTS IS NOT A COLUMN.

    `port-binding-report` passed `--port-manifest` to
    `run_generated_case_adapters.py`. SM-02 deleted that flag with the rest of
    the `[ports.*]` machinery, in the same epic, and from that moment the
    detector exited 2 with `unrecognized arguments`, executed nothing and
    reported `INERT` on every run for two epics. Nothing said so.

    The runner was never WRONG about it -- `INERT` decides nothing and is
    correctly not a survival. That is exactly why this needed a separate check:
    a column that has stopped being able to speak reads, in the table, almost
    the same as one that had nothing to say.

    DECLARED BLIND SPOT. This compares flag NAMES against the entry point's
    `add_argument` declarations. It cannot see a flag that is still accepted but
    now means something else, and it cannot see a positional that moved. It
    catches the failure that actually happened here and says so rather than
    implying more.
    """

    import re

    for detector in catalogue["detector"]:
        if detector["kind"] != "cli":
            continue
        entry = detector.get("entry_point")
        assert entry, f"{detector['id']} is a cli detector with no entry_point"
        source = (REPO_ROOT / entry).read_text(encoding="utf-8")
        declared = set(re.findall(r"""add_argument\(\s*["'](--[a-z0-9-]+)["']""", source))
        used = {token for token in detector["argv"] if token.startswith("--")}
        rejected = sorted(used - declared)
        assert not rejected, (
            f"detector {detector['id']!r} passes {rejected} to {entry}, which no longer "
            f"declares them. The column cannot execute: it exits 2 with `unrecognized "
            f"arguments` and the runner reports INERT. Either repair the argv or remove "
            f"the detector with a `[[not_seedable]]` row saying what it used to cover."
        )


# -- 2. R2: a mechanism with no seedable gap is REPORTED --------------------


def test_a_mechanism_with_no_seedable_gap_is_reported_with_its_reason(catalogue) -> None:
    rows = catalogue.get("not_seedable", [])
    assert rows, "R2: a row that cannot be seeded is reported, never omitted"
    for row in rows:
        assert row.get("mechanism") and row.get("reason") and row.get("removed_by")


def test_the_thermometer_is_named_as_not_a_removal_target(catalogue) -> None:
    """The produced-code descriptor correctly cannot fail. It must appear in the
    table as a declared non-target, not be silently absent from it.

    The module is identified through the catalogue's own text rather than by
    spelling its path here. `tests/test_code_complexity.py::
    test_no_reader_of_this_instrument_gates_on_its_output` scans every file that
    NAMES that module and flags any comparison in it as a possible gate, and it
    is right to: a consumer that reads its figures and asserts on them is
    exactly the thing that turns a thermometer into a thermostat. Naming it here
    would have been a false positive on a shipped tripwire, and the fix is to
    stop naming it, never to add this file to the tripwire's exemption list --
    that shape was rejected at `EVAL-RERUN-DF-01` and again at
    `ARM_MODULE_PREFIXES`.
    """
    thermometer = next(
        (row for row in catalogue["not_seedable"]
         if "thermometer" in row["reason"].lower()),
        None,
    )
    assert thermometer is not None, "the produced-code descriptor is not in the table"
    assert thermometer["mechanism"].endswith("the produced-code descriptor")
    assert "NOT a removal target" in thermometer["removed_by"]
    assert "no gap to seed because there is no claim" in thermometer["reason"]


# -- 3. the verdict rule cannot report a survival it did not observe --------


def test_nothing_executed_is_INERT_and_never_a_survival(runner) -> None:
    """`FI-06`: `expect_exit = 0` is satisfied by a FULLY SKIPPED run."""
    observed = {"present": True, "executed": 0, "red": False, "failing_nodes": []}
    assert runner.verdict({"failing_nodes": [], "red": False}, observed) == runner.INERT


def test_a_detector_that_no_longer_exists_is_REMOVED_and_never_a_survival(runner) -> None:
    """`MF-020` on the instrument itself: a deleted detector did not fail to
    catch anything, and recording it as a survival would price the cut at zero
    by construction."""
    observed = {"present": False, "executed": 0, "red": None, "failing_nodes": []}
    assert runner.verdict({}, observed) == runner.REMOVED


def test_a_new_failing_node_is_a_kill_even_when_the_baseline_was_already_red(
    runner,
) -> None:
    """The staged tree has nine git-history failures at the tip. A verdict rule
    keyed on the exit code would report BASELINE-RED for the whole suite and
    decide nothing; keyed on the failure SET it still decides."""
    baseline = {"failing_nodes": ["tests/test_score_tools.py::test_history"], "red": True}
    observed = {
        "present": True,
        "executed": 1300,
        "red": True,
        "failing_nodes": [
            "tests/test_score_tools.py::test_history",
            "tests/test_complexity_ledger.py::test_a_decrease_is_refused",
        ],
    }
    assert runner.verdict(baseline, observed) == runner.DIES


def test_this_runners_own_integrity_test_is_not_counted_as_a_repository_kill(
    runner,
) -> None:
    """THE INSTRUMENT WAS DETECTING ITSELF, and the first run was scored on it.

    `test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree` reads the
    catalogue's anchors out of whatever tree it runs in. During a measurement
    that tree is the mutated one, so it fires on every mutant -- and on five of
    the nine it was the ONLY new failure, which would have read as the
    repository catching a fault it does not catch. Excluded from the verdict,
    reported separately, never dropped."""
    node = runner.SELF_DETECTION[0]
    baseline = {"failing_nodes": [], "red": False}
    observed = {"present": True, "executed": 1300, "red": True, "failing_nodes": [node]}
    real, mine = runner.new_failures(baseline, observed)
    assert real == [] and mine == [node]
    assert runner.verdict(baseline, observed) == runner.DIES, (
        "the run still went red, so the cell is a kill on the exit code -- what "
        "the exclusion changes is that no node is CREDITED to the repository"
    )
    observed_green = {**observed, "red": False}
    assert runner.verdict(baseline, observed_green) == runner.SURVIVES


def test_the_exclusion_cannot_hide_a_node_that_is_not_this_runners_own(runner) -> None:
    """An exclusion that could grow is an exclusion that will."""
    assert len(runner.SELF_DETECTION) == 1
    assert all(node.startswith("tests/test_gap_mutants.py::") for node in runner.SELF_DETECTION)
    baseline = {"failing_nodes": [], "red": True}
    observed = {
        "present": True, "executed": 10, "red": True,
        "failing_nodes": [runner.SELF_DETECTION[0], "tests/test_other.py::test_real"],
    }
    real, mine = runner.new_failures(baseline, observed)
    assert real == ["tests/test_other.py::test_real"]
    assert runner.verdict(baseline, observed) == runner.DIES


def test_the_same_failures_as_the_baseline_is_a_survival(runner) -> None:
    baseline = {"failing_nodes": ["tests/test_score_tools.py::test_history"], "red": True}
    observed = {
        "present": True,
        "executed": 1300,
        "red": True,
        "failing_nodes": ["tests/test_score_tools.py::test_history"],
    }
    assert runner.verdict(baseline, observed) == runner.SURVIVES


# -- 4. an unapplied mutant is refused, loudly ------------------------------


def test_an_anchor_that_matches_twice_refuses_rather_than_mutating_one(runner, tmp_path) -> None:
    (tmp_path / "m.py").write_text("x = 1\nx = 1\n", encoding="utf-8")
    mutant = {"id": "T", "edit": [{"path": "m.py", "find": "x = 1", "replace": "x = 2"}]}
    with pytest.raises(runner.MutantNotApplied):
        runner.apply_mutant(tmp_path, mutant)


def test_an_edit_that_changes_nothing_refuses(runner, tmp_path) -> None:
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    mutant = {"id": "T", "edit": [{"path": "m.py", "find": "x = 1", "replace": "x = 1"}]}
    with pytest.raises(runner.MutantNotApplied):
        runner.apply_mutant(tmp_path, mutant)


def test_an_add_file_that_would_overwrite_refuses(runner, tmp_path) -> None:
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    mutant = {"id": "T", "edit": [{"path": "m.py", "add_file": "y = 2\n"}]}
    with pytest.raises(runner.MutantNotApplied):
        runner.apply_mutant(tmp_path, mutant)


def test_a_missing_target_refuses_rather_than_reporting_a_survival(runner, tmp_path) -> None:
    mutant = {"id": "T", "edit": [{"path": "nope.py", "find": "a", "replace": "b"}]}
    with pytest.raises(runner.MutantNotApplied):
        runner.apply_mutant(tmp_path, mutant)


def test_apply_then_restore_leaves_the_tree_byte_identical(runner, tmp_path) -> None:
    """A measurement that leaves the subject changed is not re-runnable, and the
    next mutant would be measured against the previous one's damage."""
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    before = (tmp_path / "m.py").read_bytes()
    mutant = {
        "id": "T",
        "edit": [
            {"path": "m.py", "find": "x = 1", "replace": "x = 2"},
            {"path": "new.py", "add_file": "z = 3\n"},
        ],
    }
    state = runner.apply_mutant(tmp_path, mutant)
    assert (tmp_path / "m.py").read_bytes() != before
    assert (tmp_path / "new.py").exists()
    runner.restore(state, tmp_path)
    assert (tmp_path / "m.py").read_bytes() == before
    assert not (tmp_path / "new.py").exists()


# -- 5. the detectors report what they DID, executed counts included -------


def _tiny_tree(tmp_path: Path) -> Path:
    tree = tmp_path / "tree"
    (tree / "tests").mkdir(parents=True)
    (tree / "src.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (tree / "tests" / "test_it.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
        "from src import value\n"
        "def test_value():\n"
        "    assert value() == 1\n",
        encoding="utf-8",
    )
    return tree


def test_a_pytest_detector_reports_an_executable_count_not_only_an_exit_code(
    runner, tmp_path
) -> None:
    tree = _tiny_tree(tmp_path)
    detector = {"id": "d", "kind": "pytest", "nodes": ["{tree}/tests"]}
    observed = runner.run_detector(detector, tree, [])
    assert observed["present"] and observed["executed"] == 1 and observed["red"] is False


def test_a_skipped_module_is_reported_as_zero_executed_so_the_verdict_is_INERT(
    runner, tmp_path
) -> None:
    """The FI-06 shape, end to end and in miniature: pytest exits 0, the
    detector reports 0 executed, and the verdict refuses to call it a survival."""
    tree = _tiny_tree(tmp_path)
    detector = {"id": "d", "kind": "pytest", "nodes": ["{tree}/tests"]}
    baseline = runner.run_detector(detector, tree, [])
    mutant = {
        "id": "skip",
        "edit": [{
            "path": "tests/test_it.py",
            "find": "import sys",
            "replace": 'import pytest\npytestmark = pytest.mark.skip("gap")\nimport sys',
        }],
    }
    state = runner.apply_mutant(tree, mutant)
    try:
        observed = runner.run_detector(detector, tree, [])
    finally:
        runner.restore(state, tree)
    assert observed["exit"] == 0, "pytest is green on a fully skipped run"
    assert observed["executed"] == 0
    assert runner.verdict(baseline, observed) == runner.INERT


def test_a_real_fault_dies_and_the_failing_node_is_named(runner, tmp_path) -> None:
    tree = _tiny_tree(tmp_path)
    detector = {"id": "d", "kind": "pytest", "nodes": ["{tree}/tests"]}
    baseline = runner.run_detector(detector, tree, [])
    mutant = {"id": "f", "edit": [{"path": "src.py", "find": "return 1", "replace": "return 2"}]}
    state = runner.apply_mutant(tree, mutant)
    try:
        observed = runner.run_detector(detector, tree, [])
    finally:
        runner.restore(state, tree)
    assert runner.verdict(baseline, observed) == runner.DIES
    assert any("test_value" in node for node in observed["failing_nodes"])


def test_a_detector_whose_entry_point_is_gone_is_present_false(runner, tmp_path) -> None:
    tree = _tiny_tree(tmp_path)
    detector = {"id": "d", "kind": "pytest", "nodes": ["{tree}/tests"], "entry_point": "gone.py"}
    observed = runner.run_detector(detector, tree, [])
    assert observed["present"] is False


def test_a_report_only_detector_is_red_on_its_printed_verdict_not_its_exit_code(
    runner, tmp_path
) -> None:
    """`FI-02-DF-02` in miniature. `render_port_binding_report` prints
    `BOUND BUT NOT DECLARED` and returns 0; a detector keyed on the exit code
    would call that clean."""
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "printer.py").write_text(
        'print("BOUND BUT NOT DECLARED: ledger.LedgerAppendPort")\n', encoding="utf-8"
    )
    detector = {
        "id": "d",
        "kind": "cli",
        "argv": ["{python}", "{tree}/printer.py"],
        "red_if_stdout_contains": ["BOUND BUT NOT DECLARED"],
    }
    observed = runner.run_detector(detector, tree, [])
    assert observed["exit"] == 0 and observed["red"] is True


# -- 6. the ports family never reads the port-swap driver's exit code -------


def test_the_ports_family_reads_control_red_from_json_and_not_an_exit_code() -> None:
    """`FI-02-DF-02`: `run_port_swap.py` prints a red control and exits 0. The
    driver's return value must not reach any verdict in this file."""
    source = RUNNER.read_text(encoding="utf-8")
    assert 'report["unmutated_control_failed"]' in source
    assert 'report["control_red"]' in source
    assert "= run_port_swap.main()" not in source
    assert "if run_port_swap.main()" not in source


def test_the_ports_family_swaps_only_the_catalogue_and_never_edits_the_driver() -> None:
    """`PA-04-DF-02`: two verdict-table drivers is how a number gets quoted
    against the wrong instrument. There is still only one."""
    source = RUNNER.read_text(encoding="utf-8")
    assert 'run_port_swap.SUBJECTS["reference_ports"]["catalogues"] = [catalogue]' in source
    assert "run_port_swap.control_verdict" not in source
    assert "run_port_swap.red_controls" not in source


# -- 7. it is not a gate ---------------------------------------------------


def test_the_runner_is_not_a_gate_and_nothing_in_the_repo_invokes_it() -> None:
    """`no_new_gates_rule`. Four epics of static checking caught zero bugs, and
    subtraction is not licence to add a refusal."""
    hits = subprocess.run(
        ["git", "grep", "-l", "run_gap_mutants"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    ).stdout.split()
    # Prose that NAMES it -- a results README, a predictions file, the plan --
    # is not an invocation. What would make it a gate is an executable on a
    # close, promotion or validation path reaching for it.
    forbidden = ("scripts/", "spec_double_compiler/", "test_graph/",
                 "specs/current/", "specs/program_model/", "skill-scripts/")
    invocations = [path for path in hits if path.startswith(forbidden)]
    assert not invocations, invocations
    assert "run_gap_mutants" not in (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_the_runner_exits_nonzero_only_when_a_mutant_did_not_apply() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "return 1 if unapplied else 0" in source
    assert source.count("return 1") == 1


# -- 8. the runner's own CLI answers --------------------------------------


def test_the_runner_reports_a_not_seedable_row_without_running_anything(tmp_path) -> None:
    """A mechanism with no seedable gap reaches the artifact even on a run that
    selects no mutant at all -- R2's whole point."""
    out = tmp_path / "report.json"
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--out", str(out), "--only", "nothing-matches-this"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=600,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["per_mutant"] == {}
    assert len(report["not_seedable"]) >= 4
    assert "NO SEEDABLE GAP" in completed.stdout
