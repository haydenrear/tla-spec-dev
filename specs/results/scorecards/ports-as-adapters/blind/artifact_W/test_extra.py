"""Tests beyond the shared suite. Run with:

    uv run --with pytest python -m pytest \
      <results-path> -q

These target things the shared suite (deliberately, per its own docstring —
a competent hand-written suite, not an adversarial one) does not pin down but
the feature file does: rejection-order ties, the exact-boundary accept, the
double-digit id sort trap, and that the ledger file on disk (not just an
in-memory mirror) carries the written bytes.
"""

from __future__ import annotations

from quota_ledger import QuotaLedger


def make(tmp_path, quotas=None):
    return QuotaLedger(dict(quotas or {"acme": 10, "globex": 4}), tmp_path / "ledger.txt")


def test_reserve_at_exact_available_boundary_accepts(tmp_path):
    """FEATURE.md: rejects when amount is greater than available -- so equal
    to available must accept. reserve('acme', 10) against quota 10."""
    q = make(tmp_path)
    result = q.reserve("acme", 10)
    assert result.status == "accepted"
    assert q.available("acme") == 0


def test_reserve_one_over_boundary_rejects(tmp_path):
    q = make(tmp_path)
    assert q.reserve("acme", 11).reason == "quota_exceeded"


def test_reserve_order_tenant_closed_beats_amount_not_positive(tmp_path):
    """Both tenant_closed and amount_not_positive apply to
    reserve(closed_tenant, 0); the feature orders tenant_closed (2) before
    amount_not_positive (3), so that reason must win."""
    q = make(tmp_path)
    q.close_tenant("acme")
    result = q.reserve("acme", 0)
    assert result.reason == "tenant_closed"


def test_reserve_order_unknown_tenant_beats_amount_not_positive(tmp_path):
    q = make(tmp_path)
    result = q.reserve("nobody", 0)
    assert result.reason == "unknown_tenant"


def test_rejected_reserve_does_not_consume_an_id(tmp_path):
    """Ids are allocated 'in order of acceptance' -- a rejection must not
    burn one. reserve(nobody,1) rejects, then reserve(acme,1) must still get
    r1, not r2."""
    q = make(tmp_path)
    q.reserve("nobody", 1)
    q.reserve("acme", 0)
    q.reserve("acme", 999)
    result = q.reserve("acme", 1)
    assert result.reservation_id == "r1"


def test_outstanding_ids_sort_numerically_past_nine(tmp_path):
    """A plain string sort would put 'r10' before 'r2'. Reserve eleven times
    against a large quota and check the ascending order is numeric."""
    q = make(tmp_path, {"acme": 1000})
    for _ in range(11):
        q.reserve("acme", 1)
    assert q.outstanding_ids() == [f"r{i}" for i in range(1, 12)]


def test_release_then_reserve_does_not_reuse_the_released_id(tmp_path):
    """Ids are 'never reused'. reserve, reserve, release the second, reserve
    again -- the fourth call must get r3, not the freed r2."""
    q = make(tmp_path)
    q.reserve("acme", 1)
    second = q.reserve("acme", 1).reservation_id
    q.release(second)
    fourth = q.reserve("acme", 1)
    assert fourth.reservation_id == "r3"
    assert q.outstanding_ids() == ["r1", "r3"]


def test_ledger_file_on_disk_matches_ledger_lines(tmp_path):
    """R2/R5 talk about a 'durable' ledger. Read the bytes back independently
    of the QuotaLedger object, not just through its own query method."""
    path = tmp_path / "ledger.txt"
    q = QuotaLedger({"acme": 10}, path)
    rid = q.reserve("acme", 5).reservation_id
    q.commit(rid)
    q.close_tenant("acme")
    raw = path.read_text()
    assert raw == "COMMIT acme 5 5\nCLOSE acme 5\n"
    assert q.ledger_lines() == ["COMMIT acme 5 5", "CLOSE acme 5"]


def test_construction_truncates_an_existing_file(tmp_path):
    """'The ledger file starts empty' -- verified against a path that already
    has content on disk before the QuotaLedger is constructed."""
    path = tmp_path / "ledger.txt"
    path.write_text("leftover garbage\n")
    q = QuotaLedger({"acme": 10}, path)
    assert q.ledger_lines() == []
    assert path.read_text() == ""


def test_close_order_unknown_tenant_beats_outstanding_reservations(tmp_path):
    """unknown_tenant (1) is checked before outstanding_reservations (3) --
    trivially true since an unknown tenant can hold no reservations, but
    confirm the reason returned is the declared first one."""
    q = make(tmp_path)
    result = q.close_tenant("nobody")
    assert result.reason == "unknown_tenant"


def test_r3_close_is_singular_second_close_line_never_written(tmp_path):
    """R3: exactly one CLOSE line. Close, then try to close again; the
    ledger must still have only the one CLOSE line."""
    q = make(tmp_path)
    q.close_tenant("acme")
    q.close_tenant("acme")  # rejected: tenant_closed
    close_lines = [l for l in q.ledger_lines() if l.startswith("CLOSE")]
    assert close_lines == ["CLOSE acme 0"]
