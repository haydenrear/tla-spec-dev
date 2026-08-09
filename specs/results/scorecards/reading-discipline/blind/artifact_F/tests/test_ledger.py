"""Behavior the shared suite does not pin down, plus the composition point.

These run on the fast in-memory journal where the case is about the rules, and
on the real `QuotaLedger` where the case is about the file actually on disk.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quota_ledger import Ledger, MemoryJournal, QuotaLedger, Result  # noqa: E402

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def ledger():
    return Ledger(dict(QUOTAS), MemoryJournal())


# -- id allocation ---------------------------------------------------------


def test_a_released_id_is_never_reused(ledger):
    ledger.release(ledger.reserve("acme", 3).reservation_id)
    assert ledger.reserve("acme", 3).reservation_id == "r2"


def test_a_committed_id_is_never_reused(ledger):
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    assert ledger.reserve("acme", 3).reservation_id == "r2"


def test_a_rejected_reserve_consumes_no_id(ledger):
    assert ledger.reserve("acme", 99).status == "rejected"
    assert ledger.reserve("nobody", 1).status == "rejected"
    assert ledger.reserve("acme", 0).status == "rejected"
    assert ledger.reserve("acme", 1).reservation_id == "r1"


def test_outstanding_ids_ascend_numerically_past_nine(ledger):
    for _ in range(10):
        ledger.reserve("acme", 1)
    assert ledger.outstanding_ids() == [f"r{n}" for n in range(1, 11)]


# -- the order the rejection reasons are checked in ------------------------


def test_an_unknown_tenant_outranks_a_bad_amount(ledger):
    assert ledger.reserve("nobody", 0).reason == "unknown_tenant"


def test_a_closed_tenant_outranks_a_bad_amount(ledger):
    ledger.close_tenant("globex")
    assert ledger.reserve("globex", 0).reason == "tenant_closed"


def test_a_bad_amount_outranks_an_exhausted_quota(ledger):
    ledger.reserve("globex", 4)
    assert ledger.available("globex") == 0
    assert ledger.reserve("globex", 0).reason == "amount_not_positive"


def test_a_closed_tenant_outranks_an_outstanding_reservation(ledger):
    ledger.close_tenant("acme")
    assert ledger.close_tenant("acme").reason == "tenant_closed"


# -- boundaries ------------------------------------------------------------


def test_a_reservation_for_exactly_what_is_left_is_accepted(ledger):
    ledger.reserve("acme", 6)
    assert ledger.reserve("acme", 4).status == "accepted"
    assert ledger.available("acme") == 0


def test_one_over_what_is_left_is_rejected(ledger):
    ledger.reserve("acme", 6)
    assert ledger.reserve("acme", 5).reason == "quota_exceeded"


def test_committing_does_not_free_quota_for_a_later_reservation(ledger):
    ledger.commit(ledger.reserve("acme", 10).reservation_id)
    assert ledger.reserve("acme", 1).reason == "quota_exceeded"


def test_a_committed_reservation_can_be_neither_committed_nor_released_again(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.commit(rid)
    assert ledger.commit(rid).reason == "unknown_reservation"
    assert ledger.release(rid).reason == "unknown_reservation"


def test_a_released_reservation_cannot_be_committed(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.release(rid)
    assert ledger.commit(rid).reason == "unknown_reservation"
    assert ledger.committed("acme") == 0


# -- tenants do not leak into one another ----------------------------------


def test_one_tenants_reservation_does_not_block_anothers_close(ledger):
    ledger.reserve("acme", 3)
    assert ledger.close_tenant("globex").status == "accepted"
    assert ledger.close_tenant("acme").reason == "outstanding_reservations"


def test_closing_one_tenant_leaves_the_other_working(ledger):
    ledger.close_tenant("globex")
    assert ledger.reserve("acme", 3).status == "accepted"
    assert ledger.available("acme") == 7
    assert ledger.available("globex") == 4


def test_conservation_holds_with_live_reservations_on_both_tenants(ledger):
    ledger.reserve("acme", 4)
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    ledger.reserve("globex", 2)
    held = {"acme": 4, "globex": 2}
    for tenant, quota in QUOTAS.items():
        assert ledger.available(tenant) + held[tenant] + ledger.committed(tenant) == quota


# -- the shape of a result -------------------------------------------------


def test_an_accepted_result_carries_no_reason(ledger):
    result = ledger.reserve("acme", 1)
    assert result.status == "accepted"
    assert result.reason is None


def test_a_rejected_result_carries_no_reservation_id(ledger):
    result = ledger.reserve("acme", 99)
    assert result.status == "rejected"
    assert result.reservation_id is None


def test_status_follows_the_reason_and_cannot_disagree_with_it():
    assert Result.accept("r1").status == "accepted"
    assert Result.reject("quota_exceeded").status == "rejected"


# -- the composition point and the file it wires up ------------------------


def test_the_wired_ledger_writes_the_lines_to_the_given_path(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    book.close_tenant("globex")
    assert path.read_text() == "COMMIT acme 3 3\nCLOSE globex 0\n"
    assert book.ledger_lines() == ["COMMIT acme 3 3", "CLOSE globex 0"]


def test_the_ledger_file_starts_empty(tmp_path):
    path = tmp_path / "ledger.txt"
    path.write_text("COMMIT stale 1 1\n")
    book = QuotaLedger(dict(QUOTAS), path)
    assert book.ledger_lines() == []


def test_the_wired_ledger_accepts_a_string_path(tmp_path):
    book = QuotaLedger(dict(QUOTAS), str(tmp_path / "ledger.txt"))
    book.close_tenant("acme")
    assert book.ledger_lines() == ["CLOSE acme 0"]


def test_the_domain_module_does_not_import_its_adapters():
    """The structural claim in NOTES.md, asserted rather than promised."""
    source = (Path(__file__).resolve().parents[1] / "quota_ledger" / "domain.py").read_text()
    assert "journal_" not in source
    assert "file_journal" not in source and "memory_journal" not in source
    assert "import os" not in source and "pathlib" not in source and "open(" not in source
