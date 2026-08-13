"""The shared behavioral contract for BOTH arms. See ../FEATURE.md.

One file, run unchanged against arm A's code, arm B's code, and the reference.
Neither arm may edit it: a change here is a change to the requirement, and two
arms measured against two requirements are not an A/B.

It is a competent hand-written suite, not an adversarial one. That is
deliberate. This suite is one of the eval's INSTRUMENTS -- HP-06 reports
findings by channel, and "what does a normal test suite catch that a generated
corpus does not, and vice versa" is a question this file has to be honest
enough to answer. Writing it weaker to protect a prediction, or stronger to
flatter one, would be tuning an instrument to its own metric.

Point it at an implementation:

    QUOTA_LEDGER_DIR=<dir on sys.path> QUOTA_LEDGER_IMPL=<module name> \\
      uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

Both default to the reference implementation.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_DEFAULT_DIR = _HERE.parent / "reference"

sys.path.insert(0, os.environ.get("QUOTA_LEDGER_DIR", str(_DEFAULT_DIR)))
_module = importlib.import_module(os.environ.get("QUOTA_LEDGER_IMPL", "quota_ledger"))
QuotaLedger = _module.QuotaLedger

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def ledger(tmp_path):
    return QuotaLedger(dict(QUOTAS), tmp_path / "ledger.txt")


def snapshot(book):
    """Everything a reader can observe. R4 compares this across a rejection."""
    return (
        {tenant: book.available(tenant) for tenant in QUOTAS},
        {tenant: book.committed(tenant) for tenant in QUOTAS},
        {tenant: book.is_closed(tenant) for tenant in QUOTAS},
        list(book.outstanding_ids()),
        list(book.ledger_lines()),
    )


# -- reserve ---------------------------------------------------------------


def test_reserve_accepts_and_holds_the_amount(ledger):
    result = ledger.reserve("acme", 3)
    assert result.status == "accepted"
    assert result.reservation_id == "r1"
    assert ledger.available("acme") == 7
    assert ledger.outstanding_ids() == ["r1"]
    assert ledger.ledger_lines() == []


def test_reservation_ids_are_allocated_in_order(ledger):
    assert ledger.reserve("acme", 1).reservation_id == "r1"
    assert ledger.reserve("globex", 1).reservation_id == "r2"
    assert ledger.reserve("acme", 1).reservation_id == "r3"


@pytest.mark.parametrize(
    "tenant,amount,reason",
    [
        ("nobody", 1, "unknown_tenant"),
        ("acme", 0, "amount_not_positive"),
        ("acme", -2, "amount_not_positive"),
        ("acme", 11, "quota_exceeded"),
        ("globex", 5, "quota_exceeded"),
    ],
)
def test_reserve_rejects_and_changes_nothing(ledger, tenant, amount, reason):
    """R4: a rejection changes nothing and names one of the six reasons."""
    before = snapshot(ledger)
    result = ledger.reserve(tenant, amount)
    assert result.status == "rejected"
    assert result.reason == reason
    assert snapshot(ledger) == before


def test_reserve_rejects_a_closed_tenant(ledger):
    assert ledger.close_tenant("globex").status == "accepted"
    before = snapshot(ledger)
    result = ledger.reserve("globex", 1)
    assert result.status == "rejected"
    assert result.reason == "tenant_closed"
    assert snapshot(ledger) == before


def test_reserve_exhausts_the_quota_exactly(ledger):
    assert ledger.reserve("globex", 4).status == "accepted"
    assert ledger.available("globex") == 0
    assert ledger.reserve("globex", 1).reason == "quota_exceeded"


# -- commit ----------------------------------------------------------------


def test_commit_moves_the_hold_into_committed_and_writes_one_line(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    result = ledger.commit(rid)
    assert result.status == "accepted"
    assert ledger.committed("acme") == 3
    assert ledger.available("acme") == 7, "committing does not give the hold back"
    assert ledger.outstanding_ids() == []
    assert ledger.ledger_lines() == ["COMMIT acme 3 3"]


def test_commit_running_total_accumulates(ledger):
    """R2: the running total on each line is that tenant's sum to that point."""
    first = ledger.reserve("acme", 3).reservation_id
    second = ledger.reserve("acme", 2).reservation_id
    ledger.commit(first)
    ledger.commit(second)
    assert ledger.committed("acme") == 5
    assert ledger.ledger_lines() == ["COMMIT acme 3 3", "COMMIT acme 2 5"]


def test_commit_totals_are_per_tenant(ledger):
    acme = ledger.reserve("acme", 3).reservation_id
    globex = ledger.reserve("globex", 2).reservation_id
    ledger.commit(acme)
    ledger.commit(globex)
    assert ledger.ledger_lines() == ["COMMIT acme 3 3", "COMMIT globex 2 2"]


def test_commit_rejects_an_unknown_reservation(ledger):
    before = snapshot(ledger)
    result = ledger.commit("r99")
    assert result.status == "rejected"
    assert result.reason == "unknown_reservation"
    assert snapshot(ledger) == before


def test_commit_twice_rejects_the_second(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    assert ledger.commit(rid).status == "accepted"
    before = snapshot(ledger)
    assert ledger.commit(rid).reason == "unknown_reservation"
    assert snapshot(ledger) == before


# -- release ---------------------------------------------------------------


def test_release_returns_the_hold_and_writes_nothing(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    result = ledger.release(rid)
    assert result.status == "accepted"
    assert ledger.available("acme") == 10
    assert ledger.committed("acme") == 0
    assert ledger.outstanding_ids() == []
    assert ledger.ledger_lines() == []


def test_release_rejects_an_unknown_reservation(ledger):
    before = snapshot(ledger)
    result = ledger.release("r99")
    assert result.status == "rejected"
    assert result.reason == "unknown_reservation"
    assert snapshot(ledger) == before


def test_release_then_reserve_again_uses_the_returned_quota(ledger):
    rid = ledger.reserve("globex", 4).reservation_id
    ledger.release(rid)
    assert ledger.reserve("globex", 4).status == "accepted"


# -- close -----------------------------------------------------------------


def test_close_writes_the_final_total(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.commit(rid)
    result = ledger.close_tenant("acme")
    assert result.status == "accepted"
    assert ledger.is_closed("acme")
    assert ledger.ledger_lines() == ["COMMIT acme 3 3", "CLOSE acme 3"]


def test_close_with_nothing_committed_writes_zero(ledger):
    assert ledger.close_tenant("acme").status == "accepted"
    assert ledger.ledger_lines() == ["CLOSE acme 0"]


@pytest.mark.parametrize("tenant,reason", [("nobody", "unknown_tenant")])
def test_close_rejects_and_changes_nothing(ledger, tenant, reason):
    before = snapshot(ledger)
    result = ledger.close_tenant(tenant)
    assert result.status == "rejected"
    assert result.reason == reason
    assert snapshot(ledger) == before


def test_close_rejects_an_already_closed_tenant(ledger):
    ledger.close_tenant("acme")
    before = snapshot(ledger)
    result = ledger.close_tenant("acme")
    assert result.status == "rejected"
    assert result.reason == "tenant_closed"
    assert snapshot(ledger) == before


def test_close_rejects_while_a_reservation_is_outstanding(ledger):
    """R3, and the cross-aspect guard: the RESERVATIONS aspect forbids a
    LEDGER-aspect write."""
    ledger.reserve("acme", 3)
    before = snapshot(ledger)
    result = ledger.close_tenant("acme")
    assert result.status == "rejected"
    assert result.reason == "outstanding_reservations"
    assert snapshot(ledger) == before


def test_close_is_allowed_once_the_reservation_is_resolved(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    assert ledger.close_tenant("acme").reason == "outstanding_reservations"
    ledger.release(rid)
    assert ledger.close_tenant("acme").status == "accepted"


# -- the rules, end to end -------------------------------------------------


def test_r1_conservation_holds_through_a_mixed_sequence(ledger):
    first = ledger.reserve("acme", 4).reservation_id
    second = ledger.reserve("acme", 3).reservation_id
    third = ledger.reserve("globex", 2).reservation_id
    ledger.commit(first)
    ledger.release(second)
    ledger.commit(third)
    held = {"acme": 0, "globex": 0}
    assert ledger.outstanding_ids() == []
    for tenant, quota in QUOTAS.items():
        assert ledger.available(tenant) + held[tenant] + ledger.committed(tenant) == quota


def test_r1_conservation_holds_while_reservations_are_live(ledger):
    ledger.reserve("acme", 4)
    ledger.reserve("acme", 3)
    assert ledger.available("acme") + 7 + ledger.committed("acme") == QUOTAS["acme"]


def test_r2_the_durable_ledger_agrees_with_memory(ledger):
    for amount in (4, 3, 2):
        ledger.commit(ledger.reserve("acme", amount).reservation_id)
    amounts = [int(line.split()[2]) for line in ledger.ledger_lines() if line.startswith("COMMIT")]
    totals = [int(line.split()[3]) for line in ledger.ledger_lines() if line.startswith("COMMIT")]
    assert sum(amounts) == ledger.committed("acme")
    running = 0
    for amount, total in zip(amounts, totals):
        running += amount
        assert total == running


def test_r5_the_ledger_is_append_only_and_ordered(ledger):
    """The order the accepting commands ran, not any other order."""
    acme = ledger.reserve("acme", 2).reservation_id
    globex = ledger.reserve("globex", 1).reservation_id
    ledger.commit(globex)
    ledger.commit(acme)
    ledger.close_tenant("globex")
    assert ledger.ledger_lines() == [
        "COMMIT globex 1 1",
        "COMMIT acme 2 2",
        "CLOSE globex 1",
    ]


def test_rejection_reasons_come_from_the_declared_vocabulary(ledger):
    declared = {
        "unknown_tenant",
        "tenant_closed",
        "amount_not_positive",
        "quota_exceeded",
        "unknown_reservation",
        "outstanding_reservations",
    }
    observed = {
        ledger.reserve("nobody", 1).reason,
        ledger.reserve("acme", 0).reason,
        ledger.reserve("acme", 99).reason,
        ledger.commit("r99").reason,
        ledger.release("r99").reason,
        ledger.close_tenant("nobody").reason,
    }
    assert observed <= declared
