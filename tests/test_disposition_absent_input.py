"""SS-05. `disposition.py`'s THREE absent-input states, and the named half.

`CA-10-DF-22`. `CA-05-DF-06` earned a structural refusal for duplicate YAML keys
after seven real rows (`SM-05-DF-01`..`DF-07`) carried two `disposition_ticket`
keys and the checker read a value the author never wrote. The refusal shipped as
a LINE SCAN that only ever saw keys at EXACTLY four-space indent inside a
`  - id:` block, so **a duplicate at any other level stayed invisible** -- and
the important one is a duplicated TOP-LEVEL `findings:`, which is what
concatenating two ledgers produces. `yaml.safe_load` keeps the last block and
`DISPOSED <label>: N findings, all three clauses hold` printed at exit 0 over a
document half of which the parser had thrown away.

THE THREE STATES, each asserted separately and each answering in ITS OWN WORDS:

    absent      no ledger at that path and no close recording one -> exit 2
                (already correct before this ticket; pinned here so a later
                change cannot quietly take it away)
    unreadable  the file is there and will not parse         -> exit 2, NEW
    empty       it parses perfectly and declares no findings -> exit 2, and it
                used to exit 1, which reads as a clause verdict

`SS-01-DF-04` is why two states are not enough, and `SS-01-DF-05` is why all
three exit 2 rather than 1.

NON-VACUITY. The real ledger must still be readable and must still report
DISPOSED, or a refusal that refuses everything would satisfy every assertion
here and mean nothing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "scripts" / "disposition.py"
LIVE_LEDGER = ROOT / "specs" / "deferred_findings.yaml"

sys.path.insert(0, str(ROOT / "scripts"))
import disposition as D  # noqa: E402


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(DISPOSITION), *args],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )


# ---------------------------------------------------------------------------
# The named half: a duplicate at a level the line scan could not see
# ---------------------------------------------------------------------------


TWO_ROOTS = """\
findings:
  - id: XX-DF-01
    found_by: probe
    severity: low
    disposition: open
    summary: the row in the FIRST block, which yaml discards without a word
findings:
  - id: XX-DF-02
    found_by: probe
    severity: low
    disposition: repaired
    disposition_ticket: "#1"
    disposition_note: a note
    summary: the row in the second block, which is all that was ever reported
"""


def test_a_duplicated_TOP_LEVEL_findings_key_is_now_refused(tmp_path) -> None:
    """The exact input `CA-10-DF-22` names, and it used to report DISPOSED.

    Before: `DISPOSED epic XX: 1 findings, all three clauses hold`, exit 0, over
    a document declaring two rows in two blocks -- a confident PASS computed over
    input a parser had already thrown away, with no `STRUCTURAL` line at all.
    """
    ledger = tmp_path / "ledger.yaml"
    ledger.write_text(TWO_ROOTS, encoding="utf-8")

    done = run("--ledger", str(ledger), "--epic", "XX")
    combined = done.stdout + done.stderr

    assert done.returncode != 0, combined
    assert "STRUCTURAL the document root" in combined
    assert "`findings` appears 2x" in combined
    assert "DISPOSED" not in combined, (
        "a clause verdict was still printed over a half-discarded parse"
    )


def test_the_four_space_case_CA_05_DF_06_was_filed_about_still_refuses() -> None:
    """The half that already worked must not be traded for the half that did not.

    This is the shape of the real fault: `#188` above the note, `#169` below it,
    and every YAML parser keeping the second without a word.
    """
    text = (
        "findings:\n"
        "  - id: X-01-DF-01\n"
        "    disposition: carried\n"
        '    disposition_ticket: "#188"\n'
        "    disposition_note: >-\n"
        "      carried to #188\n"
        '    disposition_ticket: "#169"\n'
    )
    assert [(r, k) for r, k, _ in D.duplicate_keys(text)] == [
        ("X-01-DF-01", "disposition_ticket")
    ]


@pytest.mark.parametrize(
    "yaml_text,expected_label,expected_key",
    [
        # a duplicate two levels down, inside a nested mapping
        ("findings:\n  - id: A-DF-01\n    surface:\n      production: [a]\n"
         "      production: [b]\n", "<document>", "production"),
        # a duplicate in a mapping that has no `id` at all
        ("top:\n  a: 1\n  a: 2\n", "<document>", "a"),
    ],
)
def test_a_duplicate_at_any_depth_is_seen(yaml_text, expected_label, expected_key) -> None:
    """A level scan cannot be right about levels it does not visit.

    The `surface:` case is not hypothetical -- every row in this repository's own
    ledger carries a nested `surface` mapping with five keys in it, and the old
    scan could not see a collision in any of them.
    """
    found = D.duplicate_keys(yaml_text)
    assert [(label, key) for label, key, _ in found] == [(expected_label, expected_key)]


# ---------------------------------------------------------------------------
# The three states
# ---------------------------------------------------------------------------


def test_state_absent_refuses_with_exit_2(tmp_path) -> None:
    """`--ledger` names a path with no file at it, explicitly, so no archive is
    searched. Already correct; pinned so it cannot silently regress."""
    done = run("--ledger", str(tmp_path / "nope.yaml"), "--epic", "XX")
    assert done.returncode != 0
    assert "no such ledger" in done.stdout + done.stderr


def test_state_unreadable_refuses_with_exit_2_and_SAYS_UNREADABLE(tmp_path) -> None:
    """NEW. A ledger that is there and will not parse.

    Before this ticket `duplicate_keys` was a regex scan that could not fail, so
    an unparseable ledger fell through to `yaml.safe_load` and died with a raw
    parser traceback -- which is a crash, not a verdict, and says nothing about
    which of the three states was hit.
    """
    ledger = tmp_path / "ledger.yaml"
    ledger.write_text("findings:\n  - id: [unclosed\n", encoding="utf-8")

    done = run("--ledger", str(ledger), "--epic", "XX")
    combined = done.stdout + done.stderr
    assert done.returncode == 2, combined
    assert "UNDECIDED [unreadable]" in combined
    assert "is not an absent one and is not an empty one" in combined
    assert "DISPOSED" not in combined


def test_state_empty_refuses_with_exit_2_not_1(tmp_path) -> None:
    """It parses perfectly and names nothing.

    It already refused, and it refused with exit 1 -- the code a CLAUSE VERDICT
    uses. `SS-01-DF-05` established that a caller reading the code rather than
    the text then sees `REFUSED ... N of M undisposed` where the truth is that
    nothing was measured.
    """
    ledger = tmp_path / "ledger.yaml"
    ledger.write_text("findings: []\n", encoding="utf-8")

    done = run("--ledger", str(ledger), "--epic", "XX")
    combined = done.stdout + done.stderr
    assert done.returncode == 2, combined
    assert "UNDECIDED [empty]" in combined
    assert "never populated" in combined


def test_the_three_states_do_not_answer_in_the_same_words(tmp_path) -> None:
    """The property `SS-07-DF-08` and `SS-06-DF-05` are both instances of losing.

    Two absent-input states answering in identical words is the defect, even when
    both verdicts are refusals: `vacuity_probe.py` refused correctly while
    reporting "I was not allowed to look" in the words of "there is nothing
    there".
    """
    absent = run("--ledger", str(tmp_path / "nope.yaml"), "--epic", "XX")

    unreadable_path = tmp_path / "u.yaml"
    unreadable_path.write_text("findings:\n  - id: [unclosed\n", encoding="utf-8")
    unreadable = run("--ledger", str(unreadable_path), "--epic", "XX")

    empty_path = tmp_path / "e.yaml"
    empty_path.write_text("findings: []\n", encoding="utf-8")
    empty = run("--ledger", str(empty_path), "--epic", "XX")

    messages = [(d.stdout + d.stderr).replace(str(tmp_path), "<tmp>")
                for d in (absent, unreadable, empty)]
    assert len(set(messages)) == 3, messages


# ---------------------------------------------------------------------------
# Non-vacuity: the refusals must not have refused everything
# ---------------------------------------------------------------------------


def test_the_real_ledger_still_loads_and_still_has_no_duplicate_keys() -> None:
    """The guard on the guard. A duplicate-rejecting loader that rejects the
    repository's own 349-row ledger would satisfy every test above and destroy
    the instrument."""
    rows = D.load(LIVE_LEDGER)
    assert len(rows) > 200
    assert D.duplicate_keys(LIVE_LEDGER.read_text()) == []


def test_the_real_ledger_still_reports_a_verdict() -> None:
    """End to end on the real subject, because `load` returning rows is not the
    same as the tool printing a verdict."""
    done = run("--ledger", str(LIVE_LEDGER), "--epic", "SS")
    combined = done.stdout + done.stderr
    assert "DISPOSED" in combined or "REFUSED" in combined, combined
    assert "UNDECIDED" not in combined, combined
