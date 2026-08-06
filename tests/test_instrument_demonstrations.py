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
    """The ticket names eleven by hand. If a rename drops one out of the
    registry, this says which.

    IT IS A RENAME GUARD AND NOTHING MORE. `required <= enumerated` cannot catch
    an instrument that was NEVER ADDED, because a new one is not in `required`
    and the subset relation stays true either way -- FI-04 shipped
    `divergence.py` and this suite was fully green with it absent. FI-04-DF-04,
    confirmed and open; the rows below are added BY HAND by each ticket that
    ships an instrument, which is the workaround, not the fix.
    """

    required = {
        "scripts/run_generated_case_adapters.py",
        "scripts/effect_conformance.py",
        "scripts/analyze_complexity.py",
        "scripts/code_complexity.py",
        "examples/validation/ab/check_catalogue.py",
        "examples/validation/ab/eval/run_controls.py",
        "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/run_port_swap.py",
        "examples/validation/scorecards/score_tools.py",
        "specs/results/scorecards/ports-as-adapters/measure/make_blind_copies.py",
        "tests/test_code_complexity.py",
        # FI-04
        "examples/validation/ab/eval/divergence.py",
        # FI-05
        "examples/validation/ab/dispatch_record.py",
        "examples/validation/check_prediction_seal.py",
    }
    enumerated = {path for entry in registry["instrument"] for path in entry.get("paths", [])}
    assert required <= enumerated, sorted(required - enumerated)


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
