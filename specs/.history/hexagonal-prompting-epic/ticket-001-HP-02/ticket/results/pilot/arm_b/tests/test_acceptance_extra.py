"""Extra acceptance tests beyond the shared suite: rejection-order edge cases
that the shared suite doesn't hit directly, and `outstanding_ids()` ordering
under interleaved tenants. Uses the public `QuotaLedger` (the composition
root), i.e. the same surface `test_behavior.py` exercises.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quota_ledger import QuotaLedger

QUOTAS = {"acme": 10, "globex": 4}


def make(tmp_path):
    return QuotaLedger(dict(QUOTAS), tmp_path / "ledger.txt")


def test_closed_tenant_beats_bad_amount(tmp_path):
    """FEATURE.md fixes the rejection order for reserve: unknown_tenant,
    tenant_closed, amount_not_positive, quota_exceeded -- in that order. A
    closed tenant asked for a non-positive amount must reject as
    tenant_closed, not amount_not_positive."""
    ledger = make(tmp_path)
    ledger.close_tenant("globex")
    result = ledger.reserve("globex", 0)
    assert result.status == "rejected"
    assert result.reason == "tenant_closed"


def test_closed_tenant_beats_quota_exceeded(tmp_path):
    ledger = make(tmp_path)
    ledger.close_tenant("globex")
    result = ledger.reserve("globex", 999)
    assert result.reason == "tenant_closed"


def test_unknown_tenant_beats_every_other_reserve_reason(tmp_path):
    ledger = make(tmp_path)
    assert ledger.reserve("nobody", 0).reason == "unknown_tenant"
    assert ledger.reserve("nobody", 999).reason == "unknown_tenant"


def test_close_checks_unknown_tenant_before_already_closed(tmp_path):
    ledger = make(tmp_path)
    assert ledger.close_tenant("nobody").reason == "unknown_tenant"


def test_outstanding_ids_ascending_across_interleaved_tenants(tmp_path):
    ledger = make(tmp_path)
    a = ledger.reserve("acme", 1).reservation_id
    b = ledger.reserve("globex", 1).reservation_id
    c = ledger.reserve("acme", 1).reservation_id
    assert ledger.outstanding_ids() == [a, b, c] == ["r1", "r2", "r3"]
    ledger.commit(b)
    assert ledger.outstanding_ids() == [a, c]


def test_reservation_ids_are_never_reused_after_release(tmp_path):
    ledger = make(tmp_path)
    rid = ledger.reserve("acme", 1).reservation_id
    ledger.release(rid)
    next_rid = ledger.reserve("acme", 1).reservation_id
    assert {rid, next_rid} == {"r1", "r2"}
    assert next_rid != rid


def test_zero_quota_tenant_can_close_immediately(tmp_path):
    ledger = QuotaLedger({"empty": 0}, tmp_path / "ledger.txt")
    result = ledger.close_tenant("empty")
    assert result.status == "accepted"
    assert ledger.ledger_lines() == ["CLOSE empty 0"]


def test_ledger_file_on_disk_matches_ledger_lines(tmp_path):
    path = tmp_path / "ledger.txt"
    ledger = QuotaLedger(dict(QUOTAS), path)
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.commit(rid)
    ledger.close_tenant("acme")
    on_disk = [line for line in path.read_text().splitlines() if line]
    assert on_disk == ledger.ledger_lines() == ["COMMIT acme 3 3", "CLOSE acme 3"]
