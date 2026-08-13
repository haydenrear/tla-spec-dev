"""The disposition requirement, pinned by its own demonstration.

`CA-05`. The rule is `references/consumption.md`; the instrument is
`scripts/disposition.py`. **This is not a gate on anyone's code** -- it reads
this repository's own findings ledger and nothing else. Seven epics of static
checking caught zero bugs and this epic adds no gate.

Every slice below is SELECTED FROM THE REAL LEDGER AT RUN TIME rather than
hardcoded, so nothing here is fitted to a known answer (`MF-020`). If the
backlog is ever fully disposed -- the outcome the whole programme wants -- the
refusal test skips and says so instead of failing.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import disposition as D  # noqa: E402

LEDGER = ROOT / D.LEDGER


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    return D.load(LEDGER)


def test_the_real_ledger_loads_and_is_not_empty(rows):
    """`load` refuses a ledger with no findings rather than reporting 0 of 0.

    `CA-00-DF-01` destroyed this file once by writing `findings: []`; a checker
    that reported a clean 0-of-0 over the wreckage would have been worse than
    no checker.
    """
    assert len(rows) > 200
    assert all("id" in r for r in rows)


def test_every_row_carries_a_disposition_field(rows):
    """The FIELD has been on every row since before this ticket. What CA-05 adds
    is that `open` is no longer an acceptable value at close-out."""
    assert [r["id"] for r in rows if "disposition" not in r] == []


def test_it_refuses_a_real_slice_that_contains_an_undisposed_row(rows):
    """The `R1` half: a demonstrated refusal on a real input, not a fixture."""
    epics = sorted({D.epic_of(r) for r in rows})
    refused = [e for e in epics
               if any(D.violations(r) for r in rows if D.epic_of(r) == e)]
    if not refused:
        pytest.skip("every epic in the ledger is disposed -- the backlog is "
                    "clear and this demonstration has nothing left to refuse")
    for e in refused:
        sl = [r for r in rows if D.epic_of(r) == e]
        assert D.report(sl, e, False) == 1


def test_it_accepts_a_real_slice_whose_rows_are_all_disposed(rows):
    """The half that stops the rule being a constant.

    An instrument that refuses everything is the mirror of harvest class `D1` --
    a cell that is a floor rather than a measurement. At least one REAL slice of
    the sealed record must pass, or the rule carries no information.
    """
    epics = sorted({D.epic_of(r) for r in rows})
    passed = [e for e in epics
              if not any(D.violations(r) for r in rows if D.epic_of(r) == e)]
    assert passed, (
        "no epic in the ledger passes all three clauses -- the rule has become "
        "a constant and is no longer measuring anything"
    )
    for e in passed:
        sl = [r for r in rows if D.epic_of(r) == e]
        assert D.report(sl, e, False) == 0


def test_the_ticket_that_shipped_the_rule_obeys_it(rows):
    """`CA-05` disposed its own findings. A ticket that ships a requirement it
    does not meet is asking everyone else to go first."""
    mine = [r for r in rows if str(r["id"]).startswith("CA-05-")]
    assert mine, "CA-05 filed no findings -- which would itself be suspicious"
    assert [(r["id"], D.violations(r)) for r in mine if D.violations(r)] == []


# -- the three clauses, each shown to be able to fail ----------------------

def test_d1_refuses_open_and_refuses_a_word_outside_the_vocabulary():
    assert D.violations({"id": "X", "disposition": "open"})
    assert D.violations({"id": "X", "disposition": "handled"})
    assert D.violations({"id": "X"})


def test_d2_refuses_a_terminal_disposition_with_no_note():
    for word in sorted(D.TERMINAL):
        assert D.violations({"id": "X", "disposition": word})
        assert not D.violations({"id": "X", "disposition": word,
                                 "disposition_note": "what was done"})


def test_d3_refuses_a_deferral_that_names_no_successor():
    assert D.violations({"id": "X", "disposition": "carried"})
    assert not D.violations({"id": "X", "disposition": "carried",
                             "disposition_ticket": "#262"})


def test_whitespace_does_not_satisfy_a_clause():
    """`disposition_note: "   "` is not a record of what was done."""
    assert D.violations({"id": "X", "disposition": "wontfix", "disposition_note": "   "})
    assert D.violations({"id": "X", "disposition": "carried", "disposition_ticket": ""})


def test_the_vocabularies_do_not_overlap_and_exclude_open():
    assert not (D.TERMINAL & D.DEFERRAL)
    assert "open" not in D.TERMINAL | D.DEFERRAL
