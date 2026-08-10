"""One case list, run against both implementations of the `Journal` port.

Every case asserts an expected value rather than asserting that the two
journals agree. Two wirings of the same domain agree with each other even when
the domain is wrong, so an agreement-only test could never fail for a reason
worth knowing. Agreement is still checked -- it falls out of the same expected
dict passing for both parametrisations -- but it is not what carries the test.

If a case here could only be written for one of the two journals, the port
would be leaking. None of them can be.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quota_ledger import FileJournal, Ledger, MemoryJournal  # noqa: E402

QUOTAS = {"acme": 10, "globex": 4}


def observe(ledger: Ledger) -> dict:
    return {
        "lines": ledger.ledger_lines(),
        "available": {t: ledger.available(t) for t in QUOTAS},
        "committed": {t: ledger.committed(t) for t in QUOTAS},
        "closed": {t: ledger.is_closed(t) for t in QUOTAS},
        "outstanding": ledger.outstanding_ids(),
    }


def _reserve_only(ledger):
    ledger.reserve("acme", 3)
    return observe(ledger)


def _commit_accumulates(ledger):
    first = ledger.reserve("acme", 3).reservation_id
    second = ledger.reserve("acme", 2).reservation_id
    ledger.commit(first)
    ledger.commit(second)
    return observe(ledger)


def _release_writes_nothing(ledger):
    ledger.release(ledger.reserve("acme", 3).reservation_id)
    return observe(ledger)


def _interleaved_tenants(ledger):
    acme = ledger.reserve("acme", 2).reservation_id
    globex = ledger.reserve("globex", 1).reservation_id
    ledger.commit(globex)
    ledger.commit(acme)
    ledger.close_tenant("globex")
    return observe(ledger)


def _close_with_nothing_committed(ledger):
    ledger.close_tenant("globex")
    return observe(ledger)


def _rejections_write_nothing(ledger):
    ledger.reserve("nobody", 1)
    ledger.reserve("acme", 0)
    ledger.reserve("acme", 99)
    ledger.commit("r99")
    ledger.release("r99")
    ledger.close_tenant("nobody")
    return observe(ledger)


CASES = [
    (
        "a reservation holds quota and writes no line",
        _reserve_only,
        {
            "lines": [],
            "available": {"acme": 7, "globex": 4},
            "committed": {"acme": 0, "globex": 0},
            "closed": {"acme": False, "globex": False},
            "outstanding": ["r1"],
        },
    ),
    (
        "each commit appends one line carrying the running total",
        _commit_accumulates,
        {
            "lines": ["COMMIT acme 3 3", "COMMIT acme 2 5"],
            "available": {"acme": 5, "globex": 4},
            "committed": {"acme": 5, "globex": 0},
            "closed": {"acme": False, "globex": False},
            "outstanding": [],
        },
    ),
    (
        "a release returns the hold and appends nothing",
        _release_writes_nothing,
        {
            "lines": [],
            "available": {"acme": 10, "globex": 4},
            "committed": {"acme": 0, "globex": 0},
            "closed": {"acme": False, "globex": False},
            "outstanding": [],
        },
    ),
    (
        "lines keep the order the accepting commands ran, across tenants",
        _interleaved_tenants,
        {
            "lines": ["COMMIT globex 1 1", "COMMIT acme 2 2", "CLOSE globex 1"],
            "available": {"acme": 8, "globex": 3},
            "committed": {"acme": 2, "globex": 1},
            "closed": {"acme": False, "globex": True},
            "outstanding": [],
        },
    ),
    (
        "closing an untouched tenant writes a zero total",
        _close_with_nothing_committed,
        {
            "lines": ["CLOSE globex 0"],
            "available": {"acme": 10, "globex": 4},
            "committed": {"acme": 0, "globex": 0},
            "closed": {"acme": False, "globex": True},
            "outstanding": [],
        },
    ),
    (
        "six rejections leave the journal and the memory untouched",
        _rejections_write_nothing,
        {
            "lines": [],
            "available": {"acme": 10, "globex": 4},
            "committed": {"acme": 0, "globex": 0},
            "closed": {"acme": False, "globex": False},
            "outstanding": [],
        },
    ),
]


def make_file_journal(tmp_path):
    return FileJournal(tmp_path / "ledger.txt")


def make_memory_journal(tmp_path):
    return MemoryJournal()


@pytest.mark.parametrize("make_journal", [make_file_journal, make_memory_journal], ids=["file", "memory"])
@pytest.mark.parametrize("script,expected", [(c[1], c[2]) for c in CASES], ids=[c[0] for c in CASES])
def test_the_same_case_holds_through_either_journal(tmp_path, make_journal, script, expected):
    ledger = Ledger(dict(QUOTAS), make_journal(tmp_path))
    assert script(ledger) == expected


# -- the port's own contract, asserted directly on both --------------------


@pytest.mark.parametrize("make_journal", [make_file_journal, make_memory_journal], ids=["file", "memory"])
def test_a_journal_starts_empty_and_keeps_what_it_is_given_in_order(tmp_path, make_journal):
    journal = make_journal(tmp_path)
    assert journal.lines() == []
    journal.append("CLOSE b 0")
    journal.append("COMMIT a 1 1")
    assert journal.lines() == ["CLOSE b 0", "COMMIT a 1 1"]


@pytest.mark.parametrize("make_journal", [make_file_journal, make_memory_journal], ids=["file", "memory"])
def test_reading_a_journal_twice_does_not_change_it(tmp_path, make_journal):
    journal = make_journal(tmp_path)
    journal.append("COMMIT a 1 1")
    first = journal.lines()
    first.append("COMMIT a 9 9")  # the caller's copy, not the journal's
    assert journal.lines() == ["COMMIT a 1 1"]
