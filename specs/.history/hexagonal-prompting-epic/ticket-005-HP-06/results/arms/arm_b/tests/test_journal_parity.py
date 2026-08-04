"""One case list, run against the real journal and against the fake.

Every case asserts an expected value, never "the two wirings agree" -- two
wirings of the same domain agree with each other even when the domain is
wrong, so an agreement-only test can never fail for a reason worth knowing.

If a case here can only be written for one of the two journals, the port is
leaking; that is the other thing this file is for.
"""

from __future__ import annotations

import pytest

from quota_ledger import InMemoryJournal, ReservationBook
from quota_ledger.journal_file import FileJournal

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture(params=["file", "fake"])
def book(request, tmp_path):
    journal = (
        FileJournal(tmp_path / "ledger.txt")
        if request.param == "file"
        else InMemoryJournal()
    )
    return ReservationBook(dict(QUOTAS), journal)


# -- the cases -------------------------------------------------------------


def case_nothing_committed_writes_nothing(book):
    book.reserve("acme", 3)
    book.release(book.reserve("globex", 1).reservation_id)
    assert book.ledger_lines() == []


def case_one_commit_writes_one_line(book):
    book.commit(book.reserve("acme", 3).reservation_id)
    assert book.ledger_lines() == ["COMMIT acme 3 3"]
    assert book.committed("acme") == 3


def case_running_total_accumulates_per_tenant(book):
    for tenant, amount in (("acme", 4), ("globex", 1), ("acme", 2)):
        book.commit(book.reserve(tenant, amount).reservation_id)
    assert book.ledger_lines() == [
        "COMMIT acme 4 4",
        "COMMIT globex 1 1",
        "COMMIT acme 2 6",
    ]


def case_close_appends_the_final_total(book):
    book.commit(book.reserve("globex", 2).reservation_id)
    book.close_tenant("globex")
    assert book.ledger_lines() == ["COMMIT globex 2 2", "CLOSE globex 2"]


def case_close_with_nothing_committed_writes_zero(book):
    book.close_tenant("acme")
    assert book.ledger_lines() == ["CLOSE acme 0"]


def case_a_rejected_command_writes_nothing(book):
    book.commit(book.reserve("acme", 1).reservation_id)
    book.reserve("acme", 5)
    assert book.close_tenant("acme").reason == "outstanding_reservations"
    assert book.commit("r404").reason == "unknown_reservation"
    assert book.reserve("acme", 99).reason == "quota_exceeded"
    assert book.ledger_lines() == ["COMMIT acme 1 1"]


def case_lines_are_in_the_order_the_commands_ran(book):
    acme = book.reserve("acme", 2).reservation_id
    globex = book.reserve("globex", 1).reservation_id
    book.commit(globex)
    book.close_tenant("globex")
    book.commit(acme)
    book.close_tenant("acme")
    assert book.ledger_lines() == [
        "COMMIT globex 1 1",
        "CLOSE globex 1",
        "COMMIT acme 2 2",
        "CLOSE acme 2",
    ]


def case_released_amount_is_never_journalled(book):
    first = book.reserve("acme", 6).reservation_id
    second = book.reserve("acme", 4).reservation_id
    book.release(first)
    book.commit(second)
    assert book.ledger_lines() == ["COMMIT acme 4 4"]
    assert book.available("acme") == 6
    assert book.committed("acme") == 4


CASES = [
    case_nothing_committed_writes_nothing,
    case_one_commit_writes_one_line,
    case_running_total_accumulates_per_tenant,
    case_close_appends_the_final_total,
    case_close_with_nothing_committed_writes_zero,
    case_a_rejected_command_writes_nothing,
    case_lines_are_in_the_order_the_commands_ran,
    case_released_amount_is_never_journalled,
]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.__name__[len("case_"):])
def test_journal_case(book, case):
    case(book)
