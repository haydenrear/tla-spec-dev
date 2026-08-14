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


def ledger_path() -> pathlib.Path:
    """The one address every read below goes through. See `rows`."""
    return D.resolve_ledger(LEDGER, explicit=False)


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    """`CA-10-DF-06`. Resolve exactly as the script does, then load.

    This fixture used to call `D.load(LEDGER)` directly. `LEDGER` is inside
    `desired_program_model/`, which the workflow close REMOVES, so all eight
    tests below errored the moment the epic was actually closed -- `CA-09` gave
    the SCRIPT a read fallback and left the SUITE without one. Going through
    `resolve_ledger` means the demonstration reads the archived copy after a
    close for the same reason and by the same rule the instrument does, rather
    than being a second, more fragile opinion about where the ledger lives.
    """
    return D.load(ledger_path())


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


# -- the declared blind spot, demonstrated rather than asserted -----------

def test_self_routing_passes_d3_and_this_ticket_does_it(rows):
    """`CA-05-DF-03`, WIDENED after review. The dead case, kept executable.

    The first version of this test used `falsifiable-instruments` carrying rows
    to issues that closed the next day. The reviewer was right that that is the
    NORMAL signature of an epic closing, not a dead handoff. **The dead case is
    self-routing** -- an epic deferring a finding to its own ticket, which routes
    it precisely nowhere and passes D3 with full marks.

    **And this ticket does it.** All three of `CA-05`'s `carried` rows name
    `#262`, which is `CA-08`, *this epic's own evaluation ticket*. That is the
    right place for those findings to surface AND it is still self-routing, and
    the rule cannot tell the difference. Declared, rather than quietly re-pointed
    at an issue invented to look external.
    """
    same = {"id": "CA-05-DF-99", "disposition": "carried",
            "disposition_ticket": "https://github.com/haydenrear/tla-spec-dev/issues/262"}
    other = {"id": "CA-05-DF-98", "disposition": "carried",
             "disposition_ticket": "https://github.com/haydenrear/tla-spec-dev/issues/144"}
    assert D.violations(same) == D.violations(other) == [], (
        "D3 is satisfied identically by a successor inside the filing epic and "
        "one outside it -- that is the blindness, and it must stay visible"
    )

    mine = [r for r in rows if str(r["id"]).startswith("CA-05-")
            and r.get("disposition") == "carried"]
    assert mine, "CA-05 has no carried rows -- the example moved"
    assert all("262" in str(r.get("disposition_ticket")) for r in mine), (
        "CA-05's carried rows no longer point at CA-08; if they now name a "
        "successor outside this epic, update CA-05-DF-03 rather than this test"
    )


def test_a_successor_need_not_be_an_issue_or_resolve_to_anything():
    """Second face of `CA-05-DF-03`: `disposition_ticket` is any non-empty string.

    14 real rows name a bare ticket id (`PA-06`, `PA-01`) rather than a URL and
    pass. Nothing resolves the successor, so nothing distinguishes a live issue
    from a ticket that closed with the epic that named it.
    """
    assert D.violations({"id": "X", "disposition": "carried",
                         "disposition_ticket": "PA-06"}) == []
    assert D.violations({"id": "X", "disposition": "carried",
                         "disposition_ticket": "see the epic owner"}) == []


def test_a_deferral_needs_no_note_at_all(rows):
    """Third face of `CA-05-DF-03`: D2 binds terminal dispositions only.

    A `carried` row satisfies the rule with no `disposition_note` whatsoever,
    and real rows in the sealed ledger do exactly that.
    """
    assert D.violations({"id": "X", "disposition": "carried",
                         "disposition_ticket": "#1"}) == []
    noteless = [r["id"] for r in rows if r.get("disposition") == "carried"
                and not str(r.get("disposition_note") or "").strip()]
    assert noteless, "no noteless deferrals left -- retire this face of DF-03"


# -- the structural guard, on the real corruption that defeated the check --

def test_duplicate_keys_are_refused_structurally():
    """`CA-05-DF-06`. A clause verdict computed over silently-discarded input is
    not a verdict, so a duplicate key refuses BEFORE any clause is evaluated.

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
        ("X-01-DF-01", "disposition_ticket")]


def test_the_real_ledger_has_no_duplicate_keys(rows):
    """Regression pin on the repair of `SM-05-DF-01`..`DF-07`.

    `load` already refuses on duplicates, so `rows` existing proves the file is
    clean; asserted explicitly so the reason is on the record rather than
    implicit in a fixture that happens to load.
    """
    assert D.duplicate_keys(ledger_path().read_text()) == []
    assert len(rows) > 200
