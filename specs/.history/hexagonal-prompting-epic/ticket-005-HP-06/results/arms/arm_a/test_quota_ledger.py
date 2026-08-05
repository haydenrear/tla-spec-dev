"""Arm A's own tests for quota_ledger.

These are deliberately aimed at what the shared behavioral suite does not
cover: id allocation past r9, the file on disk as opposed to ledger_lines(),
rejection precedence when several checks would fire, R1/R2/R3 as invariants
checked after every step of a long mixed sequence, and the free choices this
implementation made where FEATURE.md is silent.

    uv run --with pytest python -m pytest test_quota_ledger.py -q
"""

from __future__ import annotations

import pytest

from quota_ledger import REASONS, QuotaLedger

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def ledger(tmp_path):
    return QuotaLedger(dict(QUOTAS), tmp_path / "ledger.txt")


# -- construction ----------------------------------------------------------


def test_the_ledger_file_is_created_empty(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    assert path.exists()
    assert path.read_text() == ""
    assert book.ledger_lines() == []


def test_construction_truncates_a_pre_existing_file(tmp_path):
    path = tmp_path / "ledger.txt"
    path.write_text("COMMIT stale 1 1\n")
    book = QuotaLedger(dict(QUOTAS), path)
    assert book.ledger_lines() == []


def test_a_string_path_works_as_well_as_a_path(tmp_path):
    book = QuotaLedger(dict(QUOTAS), str(tmp_path / "ledger.txt"))
    book.commit(book.reserve("acme", 1).reservation_id)
    assert book.ledger_lines() == ["COMMIT acme 1 1"]


def test_the_ledger_starts_at_full_quota(ledger):
    for tenant, quota in QUOTAS.items():
        assert ledger.available(tenant) == quota
        assert ledger.committed(tenant) == 0
        assert ledger.is_closed(tenant) is False
    assert ledger.outstanding_ids() == []


def test_the_constructor_copies_the_quota_mapping(tmp_path):
    quotas = dict(QUOTAS)
    book = QuotaLedger(quotas, tmp_path / "ledger.txt")
    quotas["acme"] = 999
    quotas["newcomer"] = 5
    assert book.available("acme") == 10
    assert book.reserve("newcomer", 1).reason == "unknown_tenant"


# -- id allocation ---------------------------------------------------------


def test_ids_are_never_reused_after_commit_or_release(ledger):
    first = ledger.reserve("acme", 1).reservation_id
    ledger.commit(first)
    second = ledger.reserve("acme", 1).reservation_id
    ledger.release(second)
    third = ledger.reserve("acme", 1).reservation_id
    assert [first, second, third] == ["r1", "r2", "r3"]


def test_a_rejected_reserve_does_not_consume_an_id(ledger):
    assert ledger.reserve("acme", 1).reservation_id == "r1"
    assert ledger.reserve("acme", 0).status == "rejected"
    assert ledger.reserve("nobody", 1).status == "rejected"
    assert ledger.reserve("acme", 99).status == "rejected"
    assert ledger.reserve("acme", 1).reservation_id == "r2"


def test_outstanding_ids_are_ascending_past_the_first_ten(ledger):
    """r10 sorts before r2 as a string; 'ascending' has to mean by allocation."""
    for _ in range(10):
        ledger.reserve("acme", 1)
    assert ledger.outstanding_ids() == [f"r{n}" for n in range(1, 11)]


def test_outstanding_ids_keep_their_order_when_the_middle_is_removed(ledger):
    ids = [ledger.reserve("acme", 1).reservation_id for _ in range(4)]
    ledger.release(ids[1])
    ledger.commit(ids[2])
    assert ledger.outstanding_ids() == [ids[0], ids[3]]


def test_outstanding_ids_span_all_tenants(ledger):
    ledger.reserve("acme", 1)
    ledger.reserve("globex", 1)
    assert ledger.outstanding_ids() == ["r1", "r2"]


# -- rejection precedence --------------------------------------------------


@pytest.mark.parametrize(
    "tenant,amount,reason",
    [
        # unknown beats every later check, including a bad amount
        ("nobody", 0, "unknown_tenant"),
        ("nobody", 999, "unknown_tenant"),
        # closed beats a bad amount and an oversized amount
        ("globex", 0, "tenant_closed"),
        ("globex", 999, "tenant_closed"),
    ],
)
def test_reserve_reports_the_first_failing_check(ledger, tenant, amount, reason):
    ledger.close_tenant("globex")
    assert ledger.reserve(tenant, amount).reason == reason


def test_close_reports_the_first_failing_check(ledger):
    """Unknown beats everything; a live hold on this tenant beats acceptance.

    'closed beats outstanding' is unreachable through the public commands --
    a tenant cannot be closed while it holds a reservation -- so it is not
    asserted here.
    """
    assert ledger.close_tenant("nobody").reason == "unknown_tenant"
    ledger.reserve("acme", 1)
    assert ledger.close_tenant("acme").reason == "outstanding_reservations"
    assert ledger.close_tenant("globex").status == "accepted"
    assert ledger.close_tenant("globex").reason == "tenant_closed"


def test_amount_not_positive_beats_quota_exceeded(ledger):
    """A negative amount is never 'quota_exceeded' even at zero available."""
    ledger.reserve("globex", 4)
    assert ledger.available("globex") == 0
    assert ledger.reserve("globex", -1).reason == "amount_not_positive"


def test_only_the_reserving_tenants_availability_is_consulted(ledger):
    ledger.reserve("acme", 10)
    assert ledger.reserve("globex", 4).status == "accepted"


# -- rejections change nothing (R4) ----------------------------------------


def _snapshot(book, path):
    return (
        {t: book.available(t) for t in QUOTAS},
        {t: book.committed(t) for t in QUOTAS},
        {t: book.is_closed(t) for t in QUOTAS},
        list(book.outstanding_ids()),
        list(book.ledger_lines()),
        path.read_text(),
    )


def test_every_rejection_leaves_the_file_on_disk_untouched(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 2).reservation_id)
    book.reserve("acme", 1)
    book.close_tenant("globex")

    before = _snapshot(book, path)
    rejections = [
        book.reserve("nobody", 1),
        book.reserve("globex", 1),
        book.reserve("acme", 0),
        book.reserve("acme", 999),
        book.commit("r404"),
        book.release("r404"),
        book.close_tenant("nobody"),
        book.close_tenant("globex"),
        book.close_tenant("acme"),
    ]
    assert all(result.status == "rejected" for result in rejections)
    assert {result.reason for result in rejections} <= REASONS
    assert _snapshot(book, path) == before


def test_a_rejected_result_carries_no_reservation_id(ledger):
    assert ledger.reserve("nobody", 1).reservation_id is None


def test_an_accepted_result_carries_no_reason(ledger):
    accepted = ledger.reserve("acme", 1)
    assert accepted.reason is None
    assert ledger.commit(accepted.reservation_id).reason is None
    assert ledger.close_tenant("globex").reason is None


def test_commit_and_release_reject_ids_from_the_other_verb(ledger):
    committed = ledger.reserve("acme", 1).reservation_id
    ledger.commit(committed)
    released = ledger.reserve("acme", 1).reservation_id
    ledger.release(released)
    assert ledger.release(committed).reason == "unknown_reservation"
    assert ledger.commit(released).reason == "unknown_reservation"


def test_commit_of_a_released_reservation_writes_nothing(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.release(rid)
    assert ledger.commit(rid).reason == "unknown_reservation"
    assert ledger.ledger_lines() == []
    assert ledger.available("acme") == 10


# -- the durable file itself -----------------------------------------------


def test_lines_are_newline_terminated_on_disk(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 1).reservation_id)
    book.close_tenant("globex")
    assert path.read_text() == "COMMIT acme 1 1\nCLOSE globex 0\n"


def test_ledger_lines_reads_back_from_disk(tmp_path):
    """The query is a read of the durable side, not of a memory mirror."""
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 1).reservation_id)
    with path.open("a") as handle:
        handle.write("\n\n")  # blank lines must not surface
    assert book.ledger_lines() == ["COMMIT acme 1 1"]


def test_existing_lines_are_never_rewritten(tmp_path):
    """R5: each command only ever extends what was already on disk."""
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    previous = ""
    for amount in (1, 2, 3):
        book.commit(book.reserve("acme", amount).reservation_id)
        current = path.read_text()
        assert current.startswith(previous)
        previous = current
    book.close_tenant("acme")
    assert path.read_text().startswith(previous)


def test_two_ledgers_use_separate_files(tmp_path):
    one = QuotaLedger(dict(QUOTAS), tmp_path / "one.txt")
    two = QuotaLedger(dict(QUOTAS), tmp_path / "two.txt")
    one.commit(one.reserve("acme", 1).reservation_id)
    assert one.ledger_lines() == ["COMMIT acme 1 1"]
    assert two.ledger_lines() == []


def test_a_missing_parent_directory_is_created(tmp_path):
    book = QuotaLedger(dict(QUOTAS), tmp_path / "nested" / "deeper" / "ledger.txt")
    book.commit(book.reserve("acme", 1).reservation_id)
    assert book.ledger_lines() == ["COMMIT acme 1 1"]


# -- close -----------------------------------------------------------------


def test_close_is_singular_even_under_repeated_attempts(ledger):
    ledger.close_tenant("acme")
    for _ in range(3):
        assert ledger.close_tenant("acme").reason == "tenant_closed"
    assert ledger.ledger_lines().count("CLOSE acme 0") == 1


def test_closing_one_tenant_leaves_the_other_open(ledger):
    ledger.close_tenant("globex")
    assert ledger.is_closed("globex") is True
    assert ledger.is_closed("acme") is False
    assert ledger.reserve("acme", 1).status == "accepted"


def test_a_released_reservation_does_not_block_close(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.release(rid)
    assert ledger.close_tenant("acme").status == "accepted"
    assert ledger.ledger_lines() == ["CLOSE acme 0"]


def test_another_tenants_reservation_does_not_block_close(ledger):
    ledger.reserve("acme", 1)
    assert ledger.close_tenant("globex").status == "accepted"


def test_a_closed_tenant_accepts_no_further_reservations(ledger):
    ledger.close_tenant("globex")
    assert ledger.reserve("globex", 1).reason == "tenant_closed"
    assert ledger.available("globex") == 4
    assert ledger.outstanding_ids() == []


# -- queries on unknown tenants (a free choice) ----------------------------


@pytest.mark.parametrize("query", ["available", "committed", "is_closed"])
def test_queries_raise_for_an_unknown_tenant(ledger, query):
    with pytest.raises(KeyError):
        getattr(ledger, query)("nobody")


# -- invariants across a long mixed sequence -------------------------------


def _check_invariants(book, path):
    lines = book.ledger_lines()
    assert lines == [line for line in path.read_text().split("\n") if line]

    held = {tenant: 0 for tenant in QUOTAS}
    running = {tenant: 0 for tenant in QUOTAS}
    closes = {tenant: 0 for tenant in QUOTAS}
    for line in lines:
        parts = line.split()
        if parts[0] == "COMMIT":
            tenant, amount, total = parts[1], int(parts[2]), int(parts[3])
            running[tenant] += amount
            # R2: the running total on the line matches the sum to that point
            assert total == running[tenant]
            assert closes[tenant] == 0, "a COMMIT after CLOSE"
        else:
            assert parts[0] == "CLOSE"
            tenant, total = parts[1], int(parts[2])
            closes[tenant] += 1
            # R3: exactly one CLOSE, whose total is the committed total
            assert closes[tenant] == 1
            assert total == running[tenant]

    for tenant, quota in QUOTAS.items():
        # R2: the durable amounts sum to committed()
        assert running[tenant] == book.committed(tenant)
        # R1: conservation, with held derived from what the ledger cannot see
        held[tenant] = quota - book.available(tenant) - book.committed(tenant)
        assert held[tenant] >= 0
        assert book.available(tenant) + held[tenant] + book.committed(tenant) == quota
        # R3: a closed tenant has exactly one CLOSE and no live holds
        assert book.is_closed(tenant) == (closes[tenant] == 1)
        if book.is_closed(tenant):
            assert held[tenant] == 0


def test_invariants_hold_after_every_step_of_a_mixed_sequence(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    live: list[str] = []

    _check_invariants(book, path)
    for step, amount in enumerate([3, 2, 1, 4, 2, 1, 3, 1, 1, 2]):
        tenant = "acme" if step % 3 else "globex"
        result = book.reserve(tenant, amount)
        if result.status == "accepted":
            live.append(result.reservation_id)
        _check_invariants(book, path)

        if live and step % 2 == 0:
            book.commit(live.pop(0))
        elif live:
            book.release(live.pop())
        _check_invariants(book, path)

    for rid in list(live):
        book.release(rid)
        _check_invariants(book, path)

    for tenant in QUOTAS:
        assert book.close_tenant(tenant).status == "accepted"
        _check_invariants(book, path)


def test_the_quota_can_be_fully_committed_and_then_closed(ledger):
    for _ in range(4):
        ledger.commit(ledger.reserve("globex", 1).reservation_id)
    assert ledger.available("globex") == 0
    assert ledger.committed("globex") == 4
    assert ledger.reserve("globex", 1).reason == "quota_exceeded"
    assert ledger.close_tenant("globex").status == "accepted"
    assert ledger.ledger_lines() == [
        "COMMIT globex 1 1",
        "COMMIT globex 1 2",
        "COMMIT globex 1 3",
        "COMMIT globex 1 4",
        "CLOSE globex 4",
    ]


def test_a_zero_quota_tenant_can_only_be_closed(tmp_path):
    book = QuotaLedger({"empty": 0}, tmp_path / "ledger.txt")
    assert book.available("empty") == 0
    assert book.reserve("empty", 1).reason == "quota_exceeded"
    assert book.close_tenant("empty").status == "accepted"
    assert book.ledger_lines() == ["CLOSE empty 0"]
