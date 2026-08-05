"""Rules the shared suite does not pin down, checked through the fake.

These run against the domain with an InMemoryJournal because none of them is
about durability; the parity file is where the journal itself is on trial.
"""

from __future__ import annotations

import pytest

from quota_ledger import InMemoryJournal, ReservationBook

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def book():
    return ReservationBook(dict(QUOTAS), InMemoryJournal())


# -- the order the reserve rejections are checked in -----------------------


def test_closed_beats_amount_not_positive(book):
    book.close_tenant("globex")
    assert book.reserve("globex", 0).reason == "tenant_closed"


def test_closed_beats_quota_exceeded(book):
    book.close_tenant("globex")
    assert book.reserve("globex", 99).reason == "tenant_closed"


def test_amount_not_positive_beats_quota_exceeded(book):
    book.reserve("globex", 4)
    assert book.available("globex") == 0
    assert book.reserve("globex", 0).reason == "amount_not_positive"


def test_unknown_tenant_beats_everything(book):
    assert book.reserve("nobody", 0).reason == "unknown_tenant"


def test_close_checks_unknown_before_outstanding(book):
    book.reserve("acme", 1)
    assert book.close_tenant("nobody").reason == "unknown_tenant"


def test_close_checks_closed_before_outstanding(book):
    """A closed tenant cannot acquire reservations, so this pair can only be
    reached by asking about a tenant that is closed while another is holding."""
    book.close_tenant("globex")
    book.reserve("acme", 1)
    assert book.close_tenant("globex").reason == "tenant_closed"


# -- ids -------------------------------------------------------------------


def test_ids_are_never_reused_after_release_or_commit(book):
    first = book.reserve("acme", 1).reservation_id
    book.release(first)
    second = book.reserve("acme", 1).reservation_id
    book.commit(second)
    third = book.reserve("acme", 1).reservation_id
    assert [first, second, third] == ["r1", "r2", "r3"]


def test_a_rejected_reserve_does_not_consume_an_id(book):
    assert book.reserve("acme", 0).status == "rejected"
    assert book.reserve("nobody", 1).status == "rejected"
    assert book.reserve("acme", 1).reservation_id == "r1"


def test_outstanding_ids_are_numerically_ascending_past_nine(book):
    for _ in range(10):
        book.reserve("acme", 1)
    assert book.outstanding_ids() == [f"r{n}" for n in range(1, 11)]


def test_outstanding_ids_stay_ascending_after_a_gap(book):
    ids = [book.reserve("acme", 1).reservation_id for _ in range(3)]
    book.commit(ids[1])
    assert book.outstanding_ids() == ["r1", "r3"]


def test_release_then_commit_the_same_id_rejects(book):
    rid = book.reserve("acme", 2).reservation_id
    assert book.release(rid).status == "accepted"
    assert book.commit(rid).reason == "unknown_reservation"
    assert book.available("acme") == 10
    assert book.ledger_lines() == []


# -- conservation and isolation --------------------------------------------


def conserved(book, tenant, held):
    return book.available(tenant) + held + book.committed(tenant) == QUOTAS[tenant]


def test_conservation_holds_at_every_step_of_a_mixed_sequence(book):
    first = book.reserve("acme", 5).reservation_id
    assert conserved(book, "acme", 5)
    second = book.reserve("acme", 3).reservation_id
    assert conserved(book, "acme", 8)
    book.commit(first)
    assert conserved(book, "acme", 3)
    book.release(second)
    assert conserved(book, "acme", 0)
    assert book.available("acme") == 5 and book.committed("acme") == 5


def test_one_tenant_does_not_spend_anothers_quota(book):
    book.commit(book.reserve("globex", 4).reservation_id)
    assert book.available("acme") == 10
    assert book.committed("acme") == 0
    assert book.available("globex") == 0


def test_closing_one_tenant_leaves_the_other_open(book):
    book.reserve("acme", 1)
    assert book.close_tenant("globex").status == "accepted"
    assert book.is_closed("globex") is True
    assert book.is_closed("acme") is False
    assert book.reserve("acme", 1).status == "accepted"


def test_a_closed_tenants_committed_total_is_frozen(book):
    book.commit(book.reserve("acme", 4).reservation_id)
    book.close_tenant("acme")
    assert book.reserve("acme", 1).reason == "tenant_closed"
    assert book.committed("acme") == 4
    assert book.ledger_lines() == ["COMMIT acme 4 4", "CLOSE acme 4"]


def test_quota_can_be_fully_committed_then_closed(book):
    for _ in range(4):
        book.commit(book.reserve("globex", 1).reservation_id)
    assert book.available("globex") == 0
    assert book.close_tenant("globex").status == "accepted"
    assert book.ledger_lines()[-1] == "CLOSE globex 4"


def test_a_tenant_with_zero_quota_can_only_be_closed():
    book = ReservationBook({"nil": 0}, InMemoryJournal())
    assert book.reserve("nil", 1).reason == "quota_exceeded"
    assert book.close_tenant("nil").status == "accepted"
    assert book.ledger_lines() == ["CLOSE nil 0"]


# -- results ---------------------------------------------------------------


def test_accepted_results_carry_no_reason(book):
    rid = book.reserve("acme", 1).reservation_id
    assert book.commit(rid).reason is None
    assert book.close_tenant("globex").reason is None


def test_commit_and_release_echo_the_reservation_id(book):
    first = book.reserve("acme", 1).reservation_id
    second = book.reserve("acme", 1).reservation_id
    assert book.commit(first).reservation_id == first
    assert book.release(second).reservation_id == second


def test_the_constructor_copies_the_quota_mapping():
    quotas = {"acme": 10}
    book = ReservationBook(quotas, InMemoryJournal())
    quotas["acme"] = 1
    assert book.available("acme") == 10
