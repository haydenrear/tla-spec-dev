"""My own tests. Deliberately NOT a copy of the shared suite: each test here
covers something the shared suite leaves open, and the docstring says what.

    uv run --with pytest python -m pytest test_quota_ledger.py -q
"""

from __future__ import annotations

import random

import pytest

from quota_ledger import QuotaLedger

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def ledger(tmp_path):
    return QuotaLedger(dict(QUOTAS), tmp_path / "ledger.txt")


def snapshot(book, tenants=("acme", "globex")):
    return (
        {t: book.available(t) for t in tenants},
        {t: book.committed(t) for t in tenants},
        {t: book.is_closed(t) for t in tenants},
        list(book.outstanding_ids()),
        list(book.ledger_lines()),
    )


# -- rejection PRECEDENCE: inputs that violate more than one clause at once.
# The shared suite only uses inputs that violate exactly one, so it cannot tell
# a correct order from a shuffled one.


@pytest.mark.parametrize(
    "tenant,amount,reason",
    [
        ("nobody", 0, "unknown_tenant"),  # unknown beats not-positive
        ("nobody", 99, "unknown_tenant"),  # unknown beats exceeded
        ("nobody", -1, "unknown_tenant"),
        ("globex", 0, "tenant_closed"),  # closed beats not-positive
        ("globex", 99, "tenant_closed"),  # closed beats exceeded
    ],
)
def test_reserve_rejection_order(ledger, tenant, amount, reason):
    assert ledger.close_tenant("globex").status == "accepted"
    assert ledger.reserve(tenant, amount).reason == reason


def test_not_positive_beats_quota_exceeded(tmp_path):
    """On a quota-0 tenant, `reserve(t, 0)` violates clause 3 and clause 4."""
    book = QuotaLedger({"z": 0}, tmp_path / "l.txt")
    assert book.reserve("z", 0).reason == "amount_not_positive"


def test_close_rejection_order(ledger):
    """unknown_tenant is decided before anything about the tenant's state."""
    assert ledger.close_tenant("nobody").reason == "unknown_tenant"
    ledger.reserve("acme", 1)
    assert ledger.close_tenant("acme").reason == "outstanding_reservations"
    assert ledger.close_tenant("globex").status == "accepted"
    assert ledger.close_tenant("globex").reason == "tenant_closed"


# -- amount and quota edges -------------------------------------------------


@pytest.mark.parametrize("amount,status", [(1, "accepted"), (0, "rejected"), (-1, "rejected")])
def test_amount_boundary_at_one(ledger, amount, status):
    assert ledger.reserve("acme", amount).status == status


def test_reserve_of_exactly_available_is_accepted(ledger):
    """`quota_exceeded` is `amount > available`, not `>=`."""
    ledger.reserve("acme", 6)
    assert ledger.available("acme") == 4
    assert ledger.reserve("acme", 4).status == "accepted"
    assert ledger.available("acme") == 0


def test_committed_amount_keeps_eating_available(ledger):
    """R1: a commit does not return the amount to `available`."""
    ledger.commit(ledger.reserve("acme", 6).reservation_id)
    assert ledger.available("acme") == 4
    assert ledger.reserve("acme", 5).reason == "quota_exceeded"
    assert ledger.reserve("acme", 4).status == "accepted"


# -- ids --------------------------------------------------------------------


def test_ids_are_not_reused_after_release(ledger):
    first = ledger.reserve("acme", 1).reservation_id
    ledger.reserve("acme", 1)
    ledger.release(first)
    assert ledger.reserve("acme", 1).reservation_id == "r3"


def test_ids_are_not_reused_after_commit(ledger):
    first = ledger.reserve("acme", 1).reservation_id
    ledger.commit(first)
    assert ledger.reserve("acme", 1).reservation_id == "r2"


@pytest.mark.parametrize("resolve", ["release", "commit"])
def test_ids_advance_even_when_outstanding_returns_to_empty(ledger, resolve):
    """Ids count reserves ACCEPTED, not reservations LIVE.

    The two existing non-reuse tests never let `outstanding` drain to empty and
    refill, so an id derived from the live count agrees with them; this sequence
    is the one that tells them apart (`r3` vs a second `r2`).
    """
    ids = []
    for _ in range(3):
        rid = ledger.reserve("acme", 1).reservation_id
        ids.append(rid)
        assert getattr(ledger, resolve)(rid).status == "accepted"
    assert ids == ["r1", "r2", "r3"]


def test_a_rejected_reserve_does_not_consume_an_id(ledger):
    """Ids are allocated "in order of acceptance" -- a rejection is not one."""
    ledger.reserve("acme", 99)
    ledger.reserve("nobody", 1)
    assert ledger.reserve("acme", 1).reservation_id == "r1"


def test_outstanding_ids_are_numerically_ascending_past_nine(tmp_path):
    """"ascending" over r1..r12; a plain string sort puts r10 before r2."""
    book = QuotaLedger({"acme": 100}, tmp_path / "l.txt")
    for _ in range(12):
        book.reserve("acme", 1)
    assert book.outstanding_ids() == [f"r{n}" for n in range(1, 13)]


# -- the durable side -------------------------------------------------------


def test_release_writes_nothing_even_between_two_commits(ledger):
    first = ledger.reserve("acme", 3).reservation_id
    released = ledger.reserve("acme", 2).reservation_id
    second = ledger.reserve("acme", 1).reservation_id
    ledger.commit(first)
    ledger.release(released)
    ledger.commit(second)
    assert ledger.ledger_lines() == ["COMMIT acme 3 3", "COMMIT acme 1 4"]


def test_close_total_excludes_released_amounts(ledger):
    ledger.release(ledger.reserve("acme", 3).reservation_id)
    ledger.close_tenant("acme")
    assert ledger.ledger_lines() == ["CLOSE acme 0"]


def test_ledger_file_has_no_blank_lines_and_ends_with_a_newline(ledger, tmp_path):
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    ledger.close_tenant("globex")
    raw = (tmp_path / "ledger.txt").read_text()
    assert raw == "COMMIT acme 3 3\nCLOSE globex 0\n"
    assert "" not in ledger.ledger_lines()


def test_ledger_lines_comes_from_the_file_not_a_memory_mirror(ledger, tmp_path):
    """R2 is a claim about the durable side; an in-memory copy would make it
    true by construction, so a second reader of the same path must agree."""
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    assert (tmp_path / "ledger.txt").read_text().splitlines() == ledger.ledger_lines()


def test_the_ledger_prefix_never_changes(ledger):
    """R5: append-only. Every write leaves the earlier lines byte-identical."""
    seen: list[str] = []
    for _ in range(6):
        ledger.commit(ledger.reserve("acme", 1).reservation_id)
        lines = ledger.ledger_lines()
        assert lines[: len(seen)] == seen
        seen = lines
    ledger.close_tenant("globex")
    assert ledger.ledger_lines()[: len(seen)] == seen


def test_construction_starts_the_ledger_file_empty(tmp_path):
    path = tmp_path / "l.txt"
    path.write_text("COMMIT ghost 9 9\n")
    assert QuotaLedger({"acme": 1}, path).ledger_lines() == []


# -- R4, exhaustively over every rejection path ------------------------------

REJECTIONS = [
    ("reserve unknown_tenant", lambda b: b.reserve("nobody", 1), "unknown_tenant"),
    ("reserve tenant_closed", lambda b: b.reserve("globex", 1), "tenant_closed"),
    ("reserve amount_not_positive", lambda b: b.reserve("acme", 0), "amount_not_positive"),
    ("reserve negative", lambda b: b.reserve("acme", -5), "amount_not_positive"),
    ("reserve quota_exceeded", lambda b: b.reserve("acme", 999), "quota_exceeded"),
    ("commit unknown id", lambda b: b.commit("r99"), "unknown_reservation"),
    ("commit committed id", lambda b: b.commit("r1"), "unknown_reservation"),
    ("release unknown id", lambda b: b.release("r99"), "unknown_reservation"),
    ("release committed id", lambda b: b.release("r1"), "unknown_reservation"),
    ("close unknown_tenant", lambda b: b.close_tenant("nobody"), "unknown_tenant"),
    ("close tenant_closed", lambda b: b.close_tenant("globex"), "tenant_closed"),
    ("close outstanding", lambda b: b.close_tenant("acme"), "outstanding_reservations"),
]


@pytest.mark.parametrize("label,operation,reason", REJECTIONS, ids=[r[0] for r in REJECTIONS])
def test_r4_every_rejection_path_changes_nothing(ledger, label, operation, reason):
    """R4 from a NON-EMPTY state: the shared suite mostly rejects from a fresh
    book, where several ways of being wrong are indistinguishable from right."""
    ledger.commit(ledger.reserve("acme", 3).reservation_id)  # r1, committed
    ledger.reserve("acme", 2)  # r2, outstanding
    ledger.close_tenant("globex")

    before = snapshot(ledger)
    result = operation(ledger)
    assert result.status == "rejected"
    assert result.reason == reason
    assert snapshot(ledger) == before


def test_a_rejected_command_carries_no_reservation_id(ledger):
    assert ledger.reserve("nobody", 1).reservation_id is None


# -- the rules, over a random walk ------------------------------------------


def test_rules_hold_after_every_operation_of_a_random_walk(tmp_path):
    """R1/R2/R3 re-checked after EVERY operation, not just at the end, so a
    rule that is violated and then repaired still fails."""
    rng = random.Random(20260809)
    for trial in range(200):
        quotas = {"acme": rng.randint(0, 12), "globex": rng.randint(0, 12)}
        book = QuotaLedger(quotas, tmp_path / f"walk{trial}.txt")
        live: dict[str, tuple[str, int]] = {}

        for _ in range(40):
            operation = rng.choice(["reserve", "commit", "release", "close"])
            if operation == "reserve":
                tenant = rng.choice(["acme", "globex", "nobody"])
                amount = rng.randint(-2, 13)
                result = book.reserve(tenant, amount)
                if result.status == "accepted":
                    live[result.reservation_id] = (tenant, amount)
            elif operation in ("commit", "release"):
                rid = rng.choice([*live, "r99"]) if live else "r99"
                if getattr(book, operation)(rid).status == "accepted":
                    live.pop(rid, None)
            else:
                book.close_tenant(rng.choice(["acme", "globex", "nobody"]))

            lines = book.ledger_lines()
            for tenant, quota in quotas.items():
                held = sum(a for (t, a) in live.values() if t == tenant)
                # R1
                assert book.available(tenant) + held + book.committed(tenant) == quota

                # R2
                running = 0
                for line in lines:
                    fields = line.split()
                    if fields[0] == "COMMIT" and fields[1] == tenant:
                        running += int(fields[2])
                        assert int(fields[3]) == running
                assert running == book.committed(tenant)

                # R3
                closes = [ln for ln in lines if ln.startswith(f"CLOSE {tenant} ")]
                if book.is_closed(tenant):
                    assert len(closes) == 1
                    assert int(closes[0].split()[2]) == book.committed(tenant)
                    assert all(t != tenant for (t, _) in live.values())
                else:
                    assert closes == []

                # R4's vocabulary clause, structurally
                assert book.available(tenant) >= 0


def test_reasons_only_ever_come_from_the_six(ledger):
    declared = {
        "unknown_tenant",
        "tenant_closed",
        "amount_not_positive",
        "quota_exceeded",
        "unknown_reservation",
        "outstanding_reservations",
    }
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    ledger.reserve("acme", 2)
    ledger.close_tenant("globex")
    observed = {operation(ledger).reason for _, operation, _ in REJECTIONS}
    assert observed <= declared
    assert len(observed) == 6, "all six reasons are reachable"
