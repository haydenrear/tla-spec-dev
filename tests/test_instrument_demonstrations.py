"""FI-02. THE DEMONSTRATED FAILING INPUTS THAT ARE NOT COMMANDS.

Most of this ticket's product is `examples/validation/instruments/instruments.toml`
plus the runner beside it: an instrument, a subject broken on purpose, and the
verdict the instrument must return. This file carries the demonstrations that
cannot be a command line -- the ones that have to reach inside an instrument to
show what it can and cannot see -- and the guards that stop the enumeration
itself from going soft.

Four groups:

1. **The thermometer tripwire's own red, green and blind spot.**
   `PA-06-DF-05`: the tripwire was a substring grep, so a docstring mention
   failed it and a reader that never wrote the string passed it. Both
   directions are demonstrated here against the shipped scanner, and so is the
   blind spot the new one still has -- which is real, is not closed, and is
   counted.

2. **Two instruments shown to be UNABLE to report something true.**
   `run_controls.py` cannot measure a ported tree at all (`FI-01-DF-01`), and
   `run_port_swap.py`'s exit code cannot carry a red control. Per R2 these are
   demonstrated and reported, never quietly repaired.

3. **The enumeration's non-vacuity guards.** FI-01's lesson, generalised: a
   demonstration harness that passes whatever the instrument does is worth
   nothing. `test_the_demonstration_FAILS_if_the_probe_goes_soft` is the
   precedent; the equivalents here make the runner prove it can report a miss,
   and make the registry prove it did not silently drop a row.

4. **The fast demonstrations, executed.** So that the ticket's acceptance
   command runs them rather than trusting a table.
"""

from __future__ import annotations

import ast
import importlib.util
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_code_complexity import (  # noqa: E402
    GATING_SCAN_EXEMPT,
    executable_references,
    gating_uses,
)

INSTRUMENTS_DIR = REPO_ROOT / "examples" / "validation" / "instruments"
REGISTRY = INSTRUMENTS_DIR / "instruments.toml"
DEMONSTRATE = INSTRUMENTS_DIR / "demonstrate.py"
RUN_CONTROLS = REPO_ROOT / "examples" / "validation" / "ab" / "eval" / "run_controls.py"
RUN_PORT_SWAP = (
    REPO_ROOT
    / "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/run_port_swap.py"
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def demonstrate_module():
    """The enumerator, imported rather than shelled out to.

    Its discovery functions take the tree as an ARGUMENT, which is the whole
    reason they can be tested against a `tmp_path` instead of against whichever
    checkout the test happens to run in.
    """

    return _load(DEMONSTRATE, "sm03_demonstrate")


# ---------------------------------------------------------------------------
# 1. the thermometer tripwire
# ---------------------------------------------------------------------------


class TestThermometerTripwire:
    """`PA-06-DF-05`, both directions, against the shipped scanner.

    The old check was `if "code_complexity" in text`. It could not tell a
    sentence from an import and it could not tell a transcription from a gate,
    and it was RED on the epic branch because of the first of those. What
    replaced it is asserted here on inputs, not described in prose.
    """

    GATING = '''
"""A module that turned the thermometer into a thermostat."""

import subprocess
import sys

import scripts.code_complexity as cc


def refuse(tree):
    record = cc.analyze_tree(tree)
    if record["totals"]["branch_points"] > 50:
        sys.exit(1)
    return record


def refuse_by_command(tree):
    out = subprocess.run([sys.executable, "scripts/code_complexity.py", tree, "--json"])
    assert out.returncode == 0
    sys.exit(cc.analyze_tree(tree)["totals"]["branch_points"])
'''

    PROSE = '''
"""This module writes an evidence packet.

The complexity figures below are printed by `python3 scripts/code_complexity.py
<target>` and are transcribed into a MECHANICAL BLOCK that is never scored.
"""

import json
from pathlib import Path

# The definitions come from scripts/code_complexity.py and are not re-derived.
DEFINITIONS = (
    "Definitions are the instrument's own and are printed by "
    "`python3 scripts/code_complexity.py <target>`. `effectful_calls` UNDERCOUNTS."
)


def block(figures: dict) -> str:
    rows = [f"| `{name}` | {value} |" for name, value in sorted(figures.items())]
    return "\\n".join([DEFINITIONS, *rows])


def write(path, figures):
    Path(path).write_text(json.dumps(figures), encoding="utf-8")
'''

    BLIND = '''
"""A gate the scan cannot see: it never names the instrument."""

import json
import sys
from pathlib import Path


def refuse(scratch):
    figures = json.loads((Path(scratch) / "out/complexity-blind.json").read_text())
    if figures["totals"]["branch_points"] > 50:
        sys.exit(1)
    return figures
'''

    def test_it_reports_a_gate(self) -> None:
        """THE DEMONSTRATED FAILING INPUT. An ALIASED import -- the direction
        `PA-06-DF-05` says a substring grep gets wrong -- and a figure that
        reaches an if-test, a comparison and a `sys.exit`."""

        references = executable_references(self.GATING)
        assert references, "an aliased import of the instrument was not seen as a reference"
        kinds = " ".join(why for _, why in references)
        assert "import scripts.code_complexity" in kinds
        assert "scripts/code_complexity.py" in kinds

        gates = gating_uses(self.GATING)
        reasons = {why for _, why in gates}
        assert "reaches an if/while test" in reasons
        assert "is compared" in reasons
        assert "reaches exit()" in reasons

    def test_it_reports_no_gate_for_prose(self) -> None:
        """THE DEMONSTRATED PASSING INPUT, and it is the input that was FAILING.

        A module docstring, a comment, and a prose sentence naming the script
        that is written into a markdown block -- the exact shape of
        `specs/results/.../measure/build_evidence_packets.py`, which turned the
        old tripwire red while gating nothing.
        """

        assert executable_references(self.PROSE) == []
        assert gating_uses(self.PROSE) == []

    def test_the_real_consumer_is_no_longer_flagged(self) -> None:
        """The same thing, against the actual file, so this does not pass on a
        stand-in while the shipped tree still fails."""

        real = (
            REPO_ROOT
            / "specs/results/scorecards/ports-as-adapters/measure/build_evidence_packets.py"
        )
        text = real.read_text(encoding="utf-8")
        assert "code_complexity" in text, "the file that provoked PA-06-DF-05 has moved"
        assert executable_references(text) == []

    def test_the_blind_spot_is_real(self) -> None:
        """THE DEMONSTRATED INABILITY, per R2, reported rather than papered over.

        A consumer that loads a previously written complexity JSON and exits on
        it never names the instrument, so nothing textual can find it. This is
        not hypothetical: it is exactly the route the one real reader in this
        repository takes. The scan is a sufficient condition when it is empty
        and it is not a necessary one -- and a reader who does not know that
        will over-trust a green.
        """

        assert executable_references(self.BLIND) == [], (
            "if this now reports, the blind spot has been closed and this "
            "demonstration should be promoted to a failing input"
        )
        assert gating_uses(self.BLIND) == []

    def test_the_exemption_is_named_and_is_only_the_instruments_own_tests(self) -> None:
        """THE NEW TRIPWIRE'S OWN COST, stated rather than hidden.

        The gating scan skips exactly two files, and both of them are files
        whose SUBJECT is the instrument: its own tests, and this
        demonstration. A test asserting a property of the scanner compares the
        scanner's name and output by definition -- `assert
        "scripts/code_complexity.py" in kinds`, six lines above, is a genuine
        hit and it is not a thermostat.

        An exemption list nobody can see is how a scan goes quietly vacuous, so
        it is pinned here: two entries, both real files, both under `tests/`,
        and a third would have to break this test to arrive.
        """

        assert GATING_SCAN_EXEMPT == (
            "tests/test_code_complexity.py",
            "tests/test_instrument_demonstrations.py",
            "tests/test_produced_code_prompt.py",
        )
        for exempt in GATING_SCAN_EXEMPT:
            assert (REPO_ROOT / exempt).is_file()
            assert exempt.startswith("tests/")

    def test_the_third_exemption_never_reads_a_figure(self) -> None:
        """FI-05'S ENTRY, BOUNDED BY SOMETHING CHECKABLE RATHER THAN BY TRUST.

        The first two exemptions read the instrument's OUTPUT, because asserting
        a property of an instrument means running it. The third does not and may
        not: `test_produced_code_prompt.py` asserts things about the PROMPT, and
        it binds the prompt's figure names and quoted cells to
        `references/complexity_intuition.md` -- itself pinned to a live run by
        `test_documented_figures_match_shipped_output` and
        `test_recorded_figures_match_a_live_run` -- rather than measuring again.

        A figure cannot be reached without importing the module or invoking the
        script. So: every executable reference in that file must be a NAME
        token, never an import and never an invocation. That is the whole ground
        of its exemption, and adding a figure read to the file breaks this test
        instead of quietly widening the hole.
        """

        text = (REPO_ROOT / "tests/test_produced_code_prompt.py").read_text(encoding="utf-8")
        refs = executable_references(text)
        assert refs, "the file no longer names the instrument; drop its exemption"
        reads = [f"{lineno}: {why}" for lineno, why in refs if not why.startswith("path/module")]
        assert reads == [], (
            f"the third exemption now READS the instrument, not just its name: {reads}. "
            f"Bind the prompt to references/complexity_intuition.md instead, or move the "
            f"assertion into the instrument's own tests."
        )
        # The file DOES shell out once, to assert the instrument still exits 0
        # on the artifacts this ticket added. That is a read of an EXIT CODE,
        # not of a figure -- so the bound is that its output is never read.
        read_output = [s for s in (".stdout", ".stderr", "capture_output=False") if s in text]
        assert read_output == [], (
            f"the file reads the instrument's OUTPUT ({read_output}); only its exit code "
            f"is permitted here"
        )
        assert "--json" not in text, (
            "the file asks the instrument for machine-readable figures"
        )
        assert gating_uses(text), "the file no longer compares a token; drop its exemption"

    def test_the_exempt_files_are_exempt_because_they_WOULD_be_flagged(self) -> None:
        """And the exemption is load-bearing rather than defensive: run the
        scanner on this very file and confirm it reports, so a future reader can
        see what the exemption is paying for."""

        text = (REPO_ROOT / "tests/test_instrument_demonstrations.py").read_text(
            encoding="utf-8"
        )
        assert executable_references(text), "this file no longer names the instrument"
        assert gating_uses(text), "this file no longer compares a token; drop its exemption"


# ---------------------------------------------------------------------------
# 2. two instruments shown UNABLE to report something true
# ---------------------------------------------------------------------------


class TestRunControlsCannotMeasureAPortedTree:
    """`FI-01-DF-01`, blocking, owner-confirmed, and REPORTED rather than fixed.

    `run_controls.py` re-imports the tree between cells and purges what it
    believes the tree to be. That belief is the literal tuple
    `ARM_MODULE_PREFIXES = ("quota_ledger",)`. On the flat tree that is the
    whole program. On the PORTED tree the program is four modules and only the
    composition point matches, so a re-import picks the CACHED `domain` back up
    and every mutant seeded there runs against unmutated code -- 15 of 15 false
    SURVIVED, with no error and an artifact that looks like a clean run.

    Not repaired here. Repairing the driver that decides kill tables is a
    second instrument change in the ticket that is enumerating instruments, and
    the enumeration is worth more than the repair.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def driver(cls):
        return _load(RUN_CONTROLS, "fi02_run_controls")

    def test_the_ported_tree_is_not_recognised_as_the_tree(self, driver) -> None:
        assert driver.ARM_MODULE_PREFIXES == ("quota_ledger",)
        assert driver._is_tree_module("quota_ledger") is True
        # The three modules that carry the ported tree's actual behaviour.
        assert driver._is_tree_module("domain") is False
        assert driver._is_tree_module("journal_file") is False
        assert driver._is_tree_module("journal_memory") is False
        # And the fake composition point, which is not an exact first segment.
        assert driver._is_tree_module("quota_ledger_fake") is False

    def test_the_purge_leaves_the_ported_tree_cached(self, driver, tmp_path) -> None:
        """The mechanism, run rather than reasoned about."""

        ported = tmp_path / "reference_ports"
        shutil.copytree(
            REPO_ROOT / "examples/validation/ab/reference_ports",
            ported,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        sys.path.insert(0, str(ported))
        try:
            for name in ("quota_ledger", "domain", "journal_file", "journal_memory"):
                sys.modules.pop(name, None)
            import quota_ledger  # noqa: F401

            assert {"quota_ledger", "domain"} <= set(sys.modules)
            driver._purge_modules("ports_binding")
            assert "quota_ledger" not in sys.modules, "the composition point IS dropped"
            still_cached = sorted(
                name for name in ("domain", "journal_file") if name in sys.modules
            )
            assert still_cached == ["domain", "journal_file"], (
                "FI-01-DF-01 has been repaired; promote this demonstration to a "
                "failing input and close the finding"
            )
        finally:
            for name in ("quota_ledger", "domain", "journal_file", "journal_memory"):
                sys.modules.pop(name, None)
            sys.path.remove(str(ported))

    def test_the_shipped_purge_test_cannot_reach_the_defect(self) -> None:
        """Why it survived a test that looks like it covers it.

        `tests/test_eval_controls.py` does test the purge -- with a fixture
        that is a SINGLE MODULE NAMED `quota_ledger`. That is the flat shape,
        so the defect is out of the test's reach by construction. A green test
        beside a broken instrument is the shape this epic exists for.
        """

        text = (REPO_ROOT / "tests/test_eval_controls.py").read_text(encoding="utf-8")
        assert "test_the_purge_drops_a_module_holding_the_tree_whatever_it_is_called" in text
        assert "reference_ports" not in text


def test_port_swap_driver_has_no_nonzero_exit_path() -> None:
    """`run_port_swap.py` PRINTS a red control and EXITS 0 regardless.

    A run that finds every control violated on every instrument and a run that
    finds none are indistinguishable to anything reading the status. It has
    already happened:
    `examples/validation/ab/eval/results/fi01/swap-reference_ports.json`
    records PA-M14 as `control_red`, and that run exited 0.

    Asserted against the shipped source rather than by running it, because a
    run needs a generated port corpus and this fact does not.
    """

    tree = ast.parse(RUN_PORT_SWAP.read_text(encoding="utf-8"))
    main = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    returns = [
        node.value.value
        for node in ast.walk(main)
        if isinstance(node, ast.Return)
        and isinstance(node.value, ast.Constant)
    ]
    assert returns, "main() no longer returns a constant; re-derive this demonstration"
    assert set(returns) == {0}, (
        "run_port_swap.py has grown a nonzero exit; promote this to a failing "
        "input and settle FI-02-DF-02"
    )
    raises = [node for node in ast.walk(main) if isinstance(node, ast.Raise)]
    assert raises == [], "an explicit raise would change the verdict surface"


# ---------------------------------------------------------------------------
# 3. the enumeration's non-vacuity guards
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def registry() -> dict:
    return tomllib.loads(REGISTRY.read_text(encoding="utf-8"))


def test_every_row_is_classified_and_every_gap_carries_a_reason(registry) -> None:
    """The one thing the goal actually targets: NOTHING IS SILENTLY OMITTED.

    A row with no failing demonstration and no reason would be exactly the
    quiet omission this ticket exists to prevent, so it is a test rather than a
    convention.
    """

    valid = {
        "demonstrated-can-fail",
        "demonstrated-cannot-fail",
        "no-demonstration-constructible",
        "no-instrument-exists",
        "not-an-instrument",
    }
    problems: list[str] = []
    for entry in registry["instrument"]:
        if entry["classification"] not in valid:
            problems.append(f"{entry['id']}: unknown classification")
        if "failing" not in entry and not entry.get("no_failing_demonstration"):
            problems.append(f"{entry['id']}: no failing demonstration AND no reason")
        if entry["classification"] == "demonstrated-can-fail" and "failing" not in entry:
            problems.append(f"{entry['id']}: claims it can fail with nothing demonstrating it")
        if entry["classification"] == "not-an-instrument" and (
            "failing" in entry or "passing" in entry
        ):
            problems.append(f"{entry['id']}: classified not-an-instrument but demonstrates one")
    assert problems == []


def test_the_named_instruments_are_all_enumerated(registry) -> None:
    """SM-03. THE OMISSION, NOT ONLY THE RENAME.

    This test used to assert `required <= enumerated` over a literal of
    thirteen paths. That relation is ONE-DIRECTIONAL, its own docstring
    conceded it, and `FI-04-DF-04` was confirmed four times: a new instrument
    is not in `required`, so the subset stays true whether or not anyone
    registered it. FI-04 shipped `run_arm_swap.py` in the same reconcile as the
    finding about exactly this, and the suite was fully green with the row
    absent. `SM-GM-I3` is that failure seeded, and it survived every detector.

    THE REPAIR IS NOT A LONGER LITERAL. That shape was rejected at
    `EVAL-RERUN-DF-01` and again at `ARM_MODULE_PREFIXES`, and it is worse here
    than anywhere: the literal has to be edited by the same person who has just
    forgotten to register the instrument, so the check fails exactly when it is
    needed. The `required` set is deleted rather than extended.

    What replaces it DERIVES the set from the tree. `[registry.enumeration]`
    declares a SCOPE -- two roots and two excluded prefixes, each with a
    written reason -- and the members are discovered by walking it for
    executables: a `__main__` guard plus a nonzero exit path, which is the
    definition the registry's own preamble already uses. Adding a file cannot
    satisfy this; only adding a row can.

    THE PREDICATE OVER-APPROXIMATES ON PURPOSE. `raise SystemExit(main())`
    reads as a nonzero exit path even where `main()` only ever returns 0, so
    `generator_vs_suite.py` is flagged despite FI-06 correctly calling it not an
    instrument. That is the right direction to be wrong in: a false positive
    costs one row carrying `family = "not-an-instrument"` and a reason, which
    is what the preamble asks for anyway, while a false negative is the
    silent omission this registry exists to prevent.
    """

    missing = demonstrate_module().unregistered(REPO_ROOT, registry)
    assert missing == [], (
        f"{len(missing)} executable(s) under a declared instrument root have no row in "
        f"instruments.toml: {missing}. Add a row -- `family = \"not-an-instrument\"` with "
        f"a reason is a valid answer. Do NOT add the path to a list in this file; there "
        f"is no longer one to add it to."
    )


def test_the_enumeration_scope_is_declared_with_a_reason_for_every_exclusion(registry) -> None:
    """The derived check's own cost, pinned the way `GATING_SCAN_EXEMPT` is.

    A derived set is only as honest as its scope, and an exclusion list that
    can grow quietly is how a scan goes vacuous while still reporting. Both
    entries are named here, both carry prose, and a third has to break this
    test to arrive.
    """

    enumeration = registry["registry"]["enumeration"]
    assert enumeration["roots"] == ["scripts", "examples/validation"]
    excluded = enumeration["exclude"]
    assert [entry["path"] for entry in excluded] == [
        "examples/validation/runs",
        "examples/validation/ex1_scaffold_only",
    ]
    for entry in excluded:
        assert (REPO_ROOT / entry["path"]).is_dir(), f"{entry['path']} no longer exists"
        assert len(entry["reason"].split()) >= 20, (
            f"{entry['path']} is excluded without a reason anyone can argue with"
        )


def test_the_derived_check_finds_an_instrument_that_was_never_added(tmp_path) -> None:
    """SM-GM-I3, RUN. The demonstrated failing input for the repair.

    An executable under a declared root -- argparse, a `__main__`, a nonzero
    exit path -- and no row anywhere. The old subset check was green on exactly
    this; SM-01 measured it surviving `registry-enumeration` and the full
    suite.

    Measured against `tmp_path`, never against `REPO_ROOT`: SM-01 found the
    gap-mutant runner detecting itself because its catalogue check read anchors
    out of whichever tree it ran in, and anything that measures the registry
    inherits that risk unless it is told which tree to measure.
    """

    module = demonstrate_module()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "gap_probe_instrument.py").write_text(
        "import argparse, sys\n"
        "def main(argv=None):\n"
        "    argparse.ArgumentParser().parse_args(argv)\n"
        "    return 1\n"
        'if __name__ == "__main__":\n'
        "    sys.exit(main())\n",
        encoding="utf-8",
    )
    registry = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))

    assert module.unregistered(tmp_path, registry) == ["scripts/gap_probe_instrument.py"]

    # And the same tree WITHOUT the unregistered file is clean, so the red
    # above is the file's doing and not the staging's.
    (tmp_path / "scripts" / "gap_probe_instrument.py").unlink()
    assert module.unregistered(tmp_path, registry) == []


def test_the_derived_check_still_catches_the_rename_the_literal_caught(tmp_path) -> None:
    """The old check was a rename guard. Removing it must not lose that.

    A registered path that no longer exists is caught by
    `test_every_declared_path_exists`; a renamed FILE that still exists under a
    new name is caught here, because the new name is a discovered candidate
    with no row.
    """

    module = demonstrate_module()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "code_complexity_renamed.py").write_text(
        "import sys\n"
        "def main():\n"
        "    return 1\n"
        'if __name__ == "__main__":\n'
        "    sys.exit(main())\n",
        encoding="utf-8",
    )
    registry = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    assert module.unregistered(tmp_path, registry) == ["scripts/code_complexity_renamed.py"]


def test_the_derived_check_cannot_see_a_tripwire_that_is_a_test_file(tmp_path) -> None:
    """THE NEW CHECK'S DEMONSTRATED BLIND SPOT, per R2, reported not repaired.

    The predicate is a `__main__` guard plus a nonzero exit path. A repo
    tripwire that is a pytest FILE has neither: it has no `__main__` and it
    never calls `exit`. So the five rows this registry leans on hardest --
    `thermometer-tripwire`, `source-citation-tripwire`, `spec-yaml-tripwire`,
    `manifest-self-records-tripwire`, `port-declaration-tripwire` -- are
    exactly the five the derived check would never have asked anyone to add.

    Widening the predicate to "any file under `tests/`" was rejected: it makes
    every one of ~48 test files owe a row, which is a taxonomy nobody will
    maintain and a denominator that stops meaning anything. The hole is real,
    it is bounded, and it is counted rather than closed.
    """

    module = demonstrate_module()
    tripwire = REPO_ROOT / "tests" / "test_source_citations.py"
    assert tripwire.is_file()
    assert module.is_instrument_candidate(tripwire) is False, (
        "a pytest tripwire is now discoverable; promote this blind spot to a "
        "failing input and widen [registry.enumeration] roots to include tests/"
    )

    # And the shape it CAN see, side by side, so this is a statement about the
    # predicate rather than about the file happening to be uninteresting.
    (tmp_path / "scripts").mkdir()
    executable = tmp_path / "scripts" / "same_logic_but_executable.py"
    executable.write_text(
        tripwire.read_text(encoding="utf-8")
        + "\nimport sys\n"
        + 'if __name__ == "__main__":\n    sys.exit(1)\n',
        encoding="utf-8",
    )
    assert module.is_instrument_candidate(executable) is True


def test_a_cited_node_that_asserts_nothing_still_reports_ok(tmp_path) -> None:
    """THE ENUMERATOR'S REMAINING BLIND SPOT, after SM-03's repair.

    `expect_passed` closes the hole `SM-GM-I1` found: a slot whose cited node
    is collected and skipped now reports MISS instead of `ok`. It does NOT
    close the next one along. The runner judges that the cited test PASSED; it
    has no view on what the test asserted. A node whose body is `assert True`
    passes, counts, and satisfies an exact `expect_passed` at full strength.

    So the count proves a demonstration EXECUTED, not that it DEMONSTRATED --
    and a reader who reads `26 of 35` as "26 instruments were shown to catch
    something" is still over-trusting it, by less than before and not by zero.
    Written down here because the alternative is that the next sweep finds it
    and calls the repair hollow.
    """

    module = demonstrate_module()
    vacuous = tmp_path / "test_vacuous_demonstration.py"
    vacuous.write_text(
        "def test_it_asserts_nothing_at_all():\n    assert True\n", encoding="utf-8"
    )
    spec = {
        "kind": "pytest",
        "nodes": [str(vacuous)],
        "expect_exit": 0,
        "expect_passed": 1,
    }
    observed = module.run_pytest(spec, tmp_path)
    assert observed["counts"].get("passed") == 1
    assert module.judge(spec, observed) == [], (
        "the runner now reports a node that asserts nothing; promote this blind "
        "spot to a failing input"
    )


def test_every_pytest_slot_declares_an_executable_count(registry) -> None:
    """SM-03. THE HOLE FI-06 NAMED, AND THE ONE IT ACTUALLY HAD.

    `FI-06` reported twelve pytest failing slots asserting only
    `expect_exit = 0`, *"which pytest returns for a passing run and a fully
    skipped one"*. `SM-01` seeded both skip shapes and the sentence turned out
    to be right about the mechanism and wrong about its reach:

        pytest.skip(allow_module_level=True)   nothing collected, exit 5,
                                               the slot ALREADY went red
        pytestmark = pytest.mark.skip(...)     items collected then skipped,
                                               exit 0, the slot said `ok`

    So the blind spot is a demonstration that goes VACUOUS, not one that
    DISAPPEARS -- and a ticket that deleted these twelve rows on FI-06's
    sentence as written would have deleted twelve repairable instruments and
    improved its own ratio doing it.

    The count is what closes it, and it is mandatory rather than encouraged so
    that a slot added next year cannot arrive uncounted. This is the same
    requirement `SM-01-DF-01` asks for one layer down, where the port-swap
    driver's suite columns carry no executable count and are therefore
    structurally exempt from control checking -- and the same one
    `tests/test_gap_mutants.py::test_a_pytest_detector_reports_an_executable_count_not_only_an_exit_code`
    already imposes on the gap-mutant runner.
    """

    uncounted: list[str] = []
    for entry in registry["instrument"]:
        for slot in ("failing", "passing", "blind_spot"):
            spec = entry.get(slot)
            if not spec or spec.get("kind") != "pytest":
                continue
            if "expect_passed" not in spec and "expect_passed_at_least" not in spec:
                uncounted.append(f"{entry['id']}/{slot}")
    assert uncounted == [], (
        f"{len(uncounted)} pytest demonstration(s) assert only an exit code: {uncounted}. "
        f"pytest exits 0 for a collected-and-skipped run, so these report `ok` on a "
        f"demonstration that executed nothing. Declare expect_passed (exact, for node "
        f"ids) or expect_passed_at_least (a floor, for a whole file)."
    )


def test_no_pytest_slot_runs_the_same_command_as_its_own_passing_slot(registry) -> None:
    """`FI-06`'s other count: two rows whose `failing.nodes == passing.nodes`.

    `complexity-ledger` and `case-modules-validate` each ran
    `pytest <the whole file>` twice and reported it as two demonstrations. That
    is not a break and a control; it is one observation counted twice, and
    `expect_exit = 0` could not tell the difference. Both are repaired to cite
    the refusing and the accepting nodes separately, and this keeps a third
    from appearing.
    """

    def command(spec: dict | None) -> tuple | None:
        """What the slot actually RUNS -- the nodes AND the tree they run in.

        `spec-yaml-tripwire` cites the same file in both slots on purpose: the
        failing slot stages a tree and breaks a document in it, the passing
        slot runs the shipped tree untouched. Those are two different runs of
        one command, which is the correct shape. Comparing node lists alone
        would call that degenerate and comparing nothing would let the real
        thing back in, so the comparison is over the whole staged command.
        """

        if not spec or spec.get("kind") != "pytest":
            return None
        return (
            tuple(spec.get("nodes", [])),
            tuple(sorted((s["from"], s["to"]) for s in spec.get("stage", []))),
            tuple(sorted(str(sorted(m.items())) for m in spec.get("mutate", []))),
            spec.get("expect_exit"),
        )

    degenerate = [
        entry["id"]
        for entry in registry["instrument"]
        if command(entry.get("failing")) is not None
        and command(entry.get("failing")) == command(entry.get("passing"))
    ]
    assert degenerate == [], (
        f"{degenerate} demonstrate a failure and a pass with the SAME command against "
        f"the SAME tree. A row that runs one thing and reports two is false precision, "
        f"which reads as coverage."
    )


def test_every_declared_path_exists(registry) -> None:
    """A declaration that nothing executes will drift. This one is a path, so
    a rename breaks it here rather than silently in the table."""

    missing = [
        path
        for entry in registry["instrument"]
        for path in entry.get("paths", [])
        if not (REPO_ROOT / path).exists()
    ]
    assert missing == []


def _stage_sources(registry) -> list[tuple[str, str]]:
    """Every `from =` a slot stages, with the instrument it belongs to."""
    out: list[tuple[str, str]] = []
    for entry in registry["instrument"]:
        for slot in ("failing", "passing"):
            spec = entry.get(slot)
            if not isinstance(spec, dict):
                continue
            for stage in spec.get("stage", []) or []:
                source = stage.get("from")
                if source:
                    out.append((entry["id"], source))
    return out


def test_every_staged_source_exists(registry) -> None:
    """THE FIELD THE PATH CHECK DID NOT WALK.

    `test_every_declared_path_exists` walks `entry["paths"]` and stops there.
    A slot's `[[instrument.*.stage]] from` is also a path into this repository,
    and `demonstrate.py` raises `MALFORMED DEMONSTRATION: stage source does not
    exist` when it is missing -- but only in the SLOW tier, and the suite runs
    the fast one.

    So when the attribute-the-catch close removed `specs/desired_program_model`,
    `spec-yaml-tripwire`'s FAILING slot -- the demonstration that proves that
    instrument can go red -- staged a file that no longer existed, and nothing
    in the suite said so. The registry went on declaring
    `classification = "demonstrated-can-fail"` for an instrument whose
    demonstration was malformed. A blind review found it by running the tier
    by hand.

    This is the cheap half of that: the path is checked here, in the tier that
    always runs, so a rename or a removal breaks the table rather than the
    reader's trust in it.
    """
    missing = [
        f"{instrument}: {source}"
        for instrument, source in _stage_sources(registry)
        if not (REPO_ROOT / source).exists()
    ]
    assert missing == [], (
        "a demonstration stages a file that is not there, so the slot reports "
        "MALFORMED rather than the verdict the registry claims for it:\n  "
        + "\n  ".join(missing)
    )


def test_the_staged_source_check_is_not_vacuous(registry) -> None:
    """A sweep over nothing passes. This is the guard the other four carry."""
    sources = _stage_sources(registry)
    assert len(sources) >= 5, (
        f"only {len(sources)} staged sources found; the check above would pass "
        "on an empty sweep and prove nothing about the registry"
    )


def test_every_cited_pytest_node_exists(registry) -> None:
    """A demonstration citing a test id that does not exist would report `ok`
    on a run nobody made."""

    missing: list[str] = []
    for entry in registry["instrument"]:
        for slot in ("failing", "passing", "blind_spot"):
            spec = entry.get(slot)
            if not spec or spec.get("kind") != "pytest":
                continue
            for node in spec["nodes"]:
                path = REPO_ROOT / node.split("::")[0]
                if not path.is_file():
                    missing.append(f"{entry['id']}/{slot}: {node}")
                    continue
                text = path.read_text(encoding="utf-8")
                for part in node.split("::")[1:]:
                    if f"class {part}" not in text and f"def {part}" not in text:
                        missing.append(f"{entry['id']}/{slot}: {node}")
    assert missing == []


def test_the_runner_REPORTS_a_demonstration_that_stops_reproducing(tmp_path) -> None:
    """THE HARNESS'S OWN FAILING INPUT, and the reason it is here.

    FI-01's `test_the_demonstration_FAILS_if_the_probe_goes_soft` is the
    precedent: a demonstration harness that passes whatever it observes proves
    nothing, and the way to know is to hand it a declaration that is false.
    Here the declaration says a clean corpus run exits 1. It exits 0, and the
    runner must say so and exit non-zero.
    """

    registry_text = """
[registry]
id = "vacuity-probe"

[[instrument]]
id = "probe"
name = "a demonstration that does not reproduce"
family = "measurement"
watches = "nothing; this row exists to be wrong"
verdict_surface = "exit code"
classification = "demonstrated-can-fail"

  [instrument.failing]
  summary = "declares exit 1 for a run that exits 0"
  argv = ["{python}", "-c", "raise SystemExit(0)"]
  expect_exit = 1
"""
    probe = tmp_path / "probe.toml"
    probe.write_text(registry_text, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(DEMONSTRATE), "--registry", str(probe)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
    )
    assert completed.returncode == 1, completed.stdout
    assert "A DECLARED DEMONSTRATION DID NOT REPRODUCE" in completed.stdout
    assert "probe / failing: exit 0, declared 1" in completed.stdout


def test_the_runner_refuses_a_mutation_that_seeds_nothing(tmp_path) -> None:
    """`check_catalogue.py`'s rule, applied to this harness: a `find` that does
    not occur seeds nothing and reports a false green. A demonstration built on
    one would print `ok` while breaking nothing at all."""

    registry_text = """
[registry]
id = "stale-mutation-probe"

[[instrument]]
id = "probe"
name = "a mutation that has gone stale"
family = "measurement"
watches = "nothing"
verdict_surface = "exit code"
classification = "demonstrated-can-fail"

  [instrument.failing]
  summary = "a find string that is not in the file"
  argv = ["{python}", "-c", "raise SystemExit(1)"]
  expect_exit = 1

    [[instrument.failing.stage]]
    from = "examples/validation/ab/reference/quota_ledger.py"
    to = "subject.py"

    [[instrument.failing.mutate]]
    file = "subject.py"
    find = "a string that is certainly not in this file"
    replace = "nor is this"
"""
    probe = tmp_path / "probe.toml"
    probe.write_text(registry_text, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(DEMONSTRATE), "--registry", str(probe)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
    )
    assert completed.returncode == 1, completed.stdout
    assert "MALFORMED DEMONSTRATION" in completed.stdout
    assert "occurs 0 time(s)" in completed.stdout


def test_the_count_is_reported_and_is_not_a_ratio_target(registry) -> None:
    """The ticket's product is a NUMBER and its denominator. Assert both are
    derivable from the file rather than from a report someone wrote."""

    instruments = [e for e in registry["instrument"] if e["family"] != "not-an-instrument"]
    without = [e for e in instruments if "failing" not in e]
    assert instruments, "the registry is empty"
    assert all(e.get("no_failing_demonstration") for e in without)
    # No assertion on how many. Setting a floor here would be inventing the
    # answer, which is the one thing the goal explicitly forbids.


# ---------------------------------------------------------------------------
# 4. the fast demonstrations, executed
# ---------------------------------------------------------------------------


def test_every_fast_demonstration_reproduces() -> None:
    """S2 applied to ourselves, run rather than tabulated.

    The fast tier is every demonstration that is a command against a staged
    tree. The slow tier -- the ones that shell out to pytest -- is deliberately
    excluded: those tests are in this same suite already, and running them
    through a nested pytest would report a green twice and a red once.
    """

    completed = subprocess.run(
        [sys.executable, str(DEMONSTRATE), "--tier", "fast"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=1800,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Every declared demonstration reproduced." in completed.stdout
