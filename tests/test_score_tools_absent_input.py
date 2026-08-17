"""SS-05. `audit` printed `0 violation(s)` about a tree it had not read.

`CA-10-DF-18` items 1, 2, 3 and the mechanism half of item 5. Four of the five
instances the sweep found in the instrument that EXECUTES THE READING RULES.
Item 4 -- `scope` over an absent card corpus -- was repaired by `SS-02`/`SS-04`
before this ticket started and is pinned here rather than re-repaired.

    1  `load_log` returned a fully-populated EMPTY SKELETON when
       `INSTRUMENT-LOG.toml` was absent under `--root`, so all six `R-H` checks
       iterated empty lists. MEASURED:
       `audit --root specs/results/scorecards/cut-the-apparatus`
       -> `# 0 card(s), 0 instrument change(s), 0 claim(s), 0 sealed digest(s)`
          ... `0 violation(s)`, exit 0.
    2  `audit_rh6` printed `OK  no judge group has a spread greater than 1 on any
       dimension` over ZERO CARDS -- an `OK` asserting a measured property of a
       corpus that was never read.
    3  `audit_rh1_architecture` printed NOTHING AT ALL over zero cards: it guards
       absent subjects and absent scope and had no guard for an empty card
       corpus. A clause that prints nothing is indistinguishable from a clause
       that passed, and unlike a skip it does not announce itself -- which is
       `CA-10-DF-14`'s vacuous-pass shape reappearing inside the instrument that
       executes the reading rules.
    5  `sweep_paths` never entered its loop body for a pattern matching zero
       files and said nothing about it. The NAMED HARM is already gone (`SS-01`
       added the relocated ledger to `DEFAULT_SWEEP` after 17 REFUTED figures
       went unswept); the MECHANISM was untouched.

WHAT THIS DELIBERATELY DOES NOT CHANGE, and it is the half `SS-02` handed
forward: `SS-02`'s registered contract for `scorecard-audit` declares
`exit_code_cannot_carry_the_answer` for the three LEDGER states and records that
making those exit non-zero *"is a change to what a violation MEANS, and that
belongs to SS-05"*. `SS-05` scoped it to "nothing was read at all". An
unresolvable ledger over a real corpus of cards still prints `UNVERIFIED` and
still exits 0, because an unverifiable fact genuinely is not a violation and 133
sealed digests were still checked. That decision is asserted below so it is a
choice on the record rather than an omission, and the remaining half is filed.

NON-VACUITY, which is the whole risk in a refusal: the real scorecard root must
still audit clean at exit 0, and `scope` must still reach its figures. Both are
asserted.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCORE_TOOLS = ROOT / "examples" / "validation" / "scorecards" / "score_tools.py"
REAL_ROOT = ROOT / "specs" / "results" / "scorecards"

sys.path.insert(0, str(SCORE_TOOLS.parent))
import score_tools as ST  # noqa: E402


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCORE_TOOLS), *args],
        capture_output=True, text=True, cwd=str(ROOT), timeout=900,
    )


# ---------------------------------------------------------------------------
# Item 1: the signature
# ---------------------------------------------------------------------------


def test_load_log_returns_None_when_there_is_no_log(tmp_path) -> None:
    """The repair is the type. `None` is "there is no log"; a dict is "there is
    one and here is what it records"."""
    assert ST.load_log(tmp_path) is None

    empty = ST.load_log_or_empty(tmp_path)
    assert empty["changes"] == [] and empty["sealed"] == []

    real = ST.load_log(REAL_ROOT)
    assert real is not None, "the real root has a log; this test is stale"
    assert real["changes"], "the real log records changes; this test is stale"


def test_audit_over_a_root_with_no_log_and_no_cards_is_UNDECIDED(tmp_path) -> None:
    """THE DEMONSTRATED ABSENT-INPUT CASE, on a real subject.

    `specs/results/scorecards/cut-the-apparatus` is a real per-round directory in
    this repository and is the natural thing to point `--root` at. Before:
    `0 violation(s)`, exit 0. After: `UNDECIDED [absent]`, exit 2.
    """
    subject = ROOT / "specs" / "results" / "scorecards" / "cut-the-apparatus"
    assert subject.is_dir(), "the real subject moved; re-point this test"

    done = run("audit", "--root", str(subject))
    combined = done.stdout + done.stderr
    assert done.returncode == ST.AUDIT_UNDECIDED, combined
    assert "UNDECIDED [absent]" in combined
    assert "nothing was checked" in combined
    # The refusal QUOTES `0 violation(s)` while explaining why it is not printing
    # one, so the check is that no line IS the verdict, not that the phrase is
    # absent from the page.
    assert not any(line.strip() == "0 violation(s)"
                   for line in combined.splitlines()), combined
    assert "## R-H1" not in combined, "the rules ran anyway"


def test_audit_over_a_path_that_does_not_exist_is_UNDECIDED_in_ITS_OWN_WORDS(tmp_path) -> None:
    """A root that is not there is not the same fact as a root with nothing in
    it, and the two must not answer identically (`SS-01-DF-04`)."""
    missing = run("audit", "--root", str(tmp_path / "nope"))
    empty_dir = tmp_path / "cards"
    (empty_dir / "sub").mkdir(parents=True)
    (empty_dir / "INSTRUMENT-LOG.toml").write_text("", encoding="utf-8")
    no_cards = run("audit", "--root", str(empty_dir))

    missing_out = (missing.stdout + missing.stderr).replace(str(tmp_path), "<tmp>")
    no_cards_out = (no_cards.stdout + no_cards.stderr).replace(str(tmp_path), "<tmp>")

    assert missing.returncode == ST.AUDIT_UNDECIDED, missing_out
    assert "no scorecard root at" in missing_out
    assert no_cards.returncode == ST.AUDIT_UNDECIDED, no_cards_out
    assert "UNDECIDED [empty]" in no_cards_out
    assert "ZERO CARDS" in no_cards_out
    assert missing_out != no_cards_out


# ---------------------------------------------------------------------------
# Items 2 and 3: the per-clause vacuity, reachable through run_audit directly
# ---------------------------------------------------------------------------


def test_rh6_says_UNVERIFIED_rather_than_OK_over_zero_cards(tmp_path) -> None:
    """`run_audit` is called directly by other code, so the clause-level repair
    has to hold independently of `cmd_audit`'s refusal."""
    (tmp_path / "INSTRUMENT-LOG.toml").write_text("", encoding="utf-8")
    results, ctx = ST.run_audit(tmp_path)
    assert ctx["rows"] == []

    rh6 = results["R-H6"]
    levels = {level for level, _ in rh6}
    assert ST.OK not in levels, rh6
    assert ST.UNVERIFIED in levels, rh6
    assert any("never read" in message for _, message in rh6), rh6


def test_rh1_no_longer_prints_nothing_at_all_over_zero_cards(tmp_path) -> None:
    """A clause that emits no line is indistinguishable from one that passed."""
    (tmp_path / "INSTRUMENT-LOG.toml").write_text("", encoding="utf-8")
    results, _ = ST.run_audit(tmp_path)

    rh1 = results["R-H1"]
    assert rh1, "R-H1 still emits nothing over an empty corpus"
    assert any(level == ST.UNVERIFIED for level, _ in rh1), rh1
    assert any("reads exactly like a clause that held" in message
               for _, message in rh1), rh1


# ---------------------------------------------------------------------------
# Item 5: a pattern that matched nothing
# ---------------------------------------------------------------------------


def test_a_sweep_pattern_matching_nothing_is_reported(tmp_path) -> None:
    """Reported, NOT refused. A `DEFAULT_SWEEP` entry can legitimately match zero
    files -- `specs/desired_program_model/*.yaml` matches three while a workflow is
    open and none after a close -- and the defect was that nothing said so."""
    (tmp_path / "a.md").write_text("hello\n", encoding="utf-8")
    files, barren = ST.sweep_paths_by_pattern(
        tmp_path, ("*.md", "no/such/dir/*.yaml", "*.toml")
    )
    assert [p.name for p in files] == ["a.md"]
    assert barren == ["no/such/dir/*.yaml", "*.toml"]

    # The old entry point keeps its old signature and its old answer.
    assert ST.sweep_paths(tmp_path, ("*.md",)) == files


def test_scope_prints_the_pattern_census_on_the_real_tree() -> None:
    """On the real repository, and NON-VACUITY for the whole item: `scope` must
    still reach its figures, not merely report its patterns."""
    done = run("scope")
    combined = done.stdout + done.stderr
    assert "patterns        swept" in combined, combined
    assert "files swept" in combined
    assert "REFUTED" in combined, "scope stopped reaching figures"


# ---------------------------------------------------------------------------
# What was already repaired, and what is deliberately left
# ---------------------------------------------------------------------------


def test_item_4_was_repaired_before_this_ticket_and_still_holds() -> None:
    """`CA-10-DF-18` item 4. `SS-02`/`SS-04` repaired it; `SS-05` re-measured it
    open-or-closed rather than assuming, and pins it rather than re-repairing."""
    done = run("scope", "--scorecards", "/nonexistent/scorecards")
    combined = done.stdout + done.stderr
    assert done.returncode == 2, combined
    assert "UNDECIDED: [absent]" in combined
    assert "82 UNREACHABLE" not in combined


def test_the_real_root_still_audits_and_still_exits_0() -> None:
    """NON-VACUITY. A refusal that refused the repository's own record would pass
    every test above and destroy the instrument that produced all four standing
    results."""
    done = run("audit", "--quiet-ok")
    combined = done.stdout + done.stderr
    assert done.returncode == 0, combined
    assert "0 violation(s)" in combined
    assert "UNDECIDED [" not in combined


def test_the_ledger_states_still_exit_0_and_that_is_FILED_NOT_FIXED() -> None:
    """WHAT SS-05 DID NOT DO, executed rather than remembered.

    `SS-02`'s register row for `scorecard-audit` declares three ledger states --
    absent, unreadable, empty -- each answering `UNDECIDED` in the text and
    exiting 0, with `exit_code_cannot_carry_the_answer` giving the reason and
    naming `SS-05` as the owner of the decision. `SS-05` declined it: repairing it
    means changing what a VIOLATION means for every caller, and it means amending
    another ticket's registered contract plus three tests that pin the register's
    literal text. Filed as `SS-05-DF-03`.

    This test asserts the state that WAS NOT REPAIRED, so the gap is executed. It
    reads the register rather than re-running six staged audits, which cost 2m41s.
    """
    import tomllib

    register = ROOT / "examples" / "validation" / "instruments" / "instruments.toml"
    data = tomllib.loads(register.read_text(encoding="utf-8"))
    rows = [r for r in data["instrument"] if r["id"] == "scorecard-audit"]
    assert len(rows) == 1
    contract = rows[0]["absent_input"]
    for state in ("absent", "unreadable", "empty"):
        spec = contract[state]
        assert spec["expect_exit"] == 0, (
            f"the {state} ledger state no longer exits 0 -- if SS-05-DF-03 has "
            f"been repaired, this test should become its regression pin"
        )
        assert str(spec.get("exit_code_cannot_carry_the_answer") or "").strip(), (
            f"the {state} state exits 0 answering undecided with no declared "
            f"reason, which the check itself refuses"
        )
