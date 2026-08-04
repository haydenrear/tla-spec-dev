"""Additional tests beyond the shared behavioral suite.

These probe a few things the shared suite doesn't: durability across a fresh
read of the ledger file on disk, id allocation continuing to climb past
release/commit, and close_tenant leaving other tenants alone.
"""

from quota_ledger import QuotaLedger


def make_ledger(tmp_path, quotas=None):
    quotas = quotas or {"acme": 10, "globex": 4}
    return QuotaLedger(dict(quotas), tmp_path / "ledger.txt")


def test_ledger_file_on_disk_matches_ledger_lines(tmp_path):
    ledger = make_ledger(tmp_path)
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.commit(rid)
    ledger.close_tenant("acme")

    on_disk = (tmp_path / "ledger.txt").read_text().splitlines()
    assert on_disk == ledger.ledger_lines()
    assert on_disk == ["COMMIT acme 3 3", "CLOSE acme 3"]


def test_construction_truncates_a_preexisting_file(tmp_path):
    path = tmp_path / "ledger.txt"
    path.write_text("leftover junk\n")
    ledger = QuotaLedger({"acme": 10}, path)
    assert ledger.ledger_lines() == []
    assert path.read_text() == ""


def test_reservation_ids_keep_climbing_past_release_and_commit(tmp_path):
    ledger = make_ledger(tmp_path)
    r1 = ledger.reserve("acme", 1).reservation_id
    ledger.release(r1)
    r2 = ledger.reserve("acme", 1).reservation_id
    ledger.commit(r2)
    r3 = ledger.reserve("acme", 1).reservation_id
    assert (r1, r2, r3) == ("r1", "r2", "r3")


def test_outstanding_ids_sort_numerically_not_lexicographically(tmp_path):
    ledger = make_ledger(tmp_path, {"acme": 100})
    ids = [ledger.reserve("acme", 1).reservation_id for _ in range(11)]
    assert ledger.outstanding_ids() == ids  # r1..r11, not r1, r10, r11, r2...


def test_closing_one_tenant_does_not_affect_another(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.close_tenant("acme")
    assert ledger.is_closed("acme")
    assert not ledger.is_closed("globex")
    assert ledger.reserve("globex", 1).status == "accepted"


def test_rejected_reserve_does_not_advance_the_id_counter(tmp_path):
    ledger = make_ledger(tmp_path)
    assert ledger.reserve("acme", 0).status == "rejected"
    assert ledger.reserve("acme", 1).reservation_id == "r1"
