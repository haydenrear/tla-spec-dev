"""this artifact's own tests, on top of the shared behavioral contract.

The shared suite (examples/validation/ab/tests/test_behavior.py) is the floor.
These cover what it does not:

  * the DURABLE side really being durable -- assertions read the file from
    disk, not the ledger_lines() accessor;
  * construction (the file starting empty, an existing file, a str path, the
    quotas mapping being copied);
  * id allocation across rejections, releases and commits;
  * R1/R2/R3 under a long randomized command sequence checked against an
    independent model.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from quota_ledger import QuotaLedger

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def path(tmp_path):
    return tmp_path / "ledger.txt"


@pytest.fixture()
def ledger(path):
    return QuotaLedger(dict(QUOTAS), path)


def file_lines(path: Path) -> list[str]:
    """The ledger as it exists on disk, read independently of the ledger."""
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# -- construction ----------------------------------------------------------


def test_the_ledger_file_starts_empty_and_exists(path):
    QuotaLedger(dict(QUOTAS), path)
    assert path.exists()
    assert path.read_text(encoding="utf-8") == ""


def test_construction_starts_empty_even_over_an_existing_file(path):
    path.write_text("COMMIT stale 5 5\n", encoding="utf-8")
    book = QuotaLedger(dict(QUOTAS), path)
    assert book.ledger_lines() == []
    assert file_lines(path) == []


def test_a_str_path_works(tmp_path):
    book = QuotaLedger(dict(QUOTAS), str(tmp_path / "ledger.txt"))
    book.commit(book.reserve("acme", 1).reservation_id)
    assert book.ledger_lines() == ["COMMIT acme 1 1"]


def test_the_quotas_mapping_is_copied(path):
    quotas = {"acme": 10}
    book = QuotaLedger(quotas, path)
    quotas["acme"] = 999
    quotas["intruder"] = 5
    assert book.available("acme") == 10
    assert book.reserve("intruder", 1).reason == "unknown_tenant"


def test_initial_state(ledger):
    for tenant, quota in QUOTAS.items():
        assert ledger.available(tenant) == quota
        assert ledger.committed(tenant) == 0
        assert ledger.is_closed(tenant) is False
    assert ledger.outstanding_ids() == []
    assert ledger.ledger_lines() == []


# -- durability ------------------------------------------------------------


def test_commit_lines_reach_the_file_itself(ledger, path):
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    ledger.commit(ledger.reserve("acme", 2).reservation_id)
    assert file_lines(path) == ["COMMIT acme 3 3", "COMMIT acme 2 5"]


def test_close_line_reaches_the_file_itself(ledger, path):
    ledger.commit(ledger.reserve("globex", 4).reservation_id)
    ledger.close_tenant("globex")
    assert file_lines(path) == ["COMMIT globex 4 4", "CLOSE globex 4"]


def test_each_line_is_newline_terminated_and_no_blanks_are_produced(ledger, path):
    ledger.commit(ledger.reserve("acme", 1).reservation_id)
    ledger.close_tenant("globex")
    text = path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert "\n\n" not in text
    assert "" not in ledger.ledger_lines()
    assert len(ledger.ledger_lines()) == 2


def test_reserve_and_release_write_nothing_durably(ledger, path):
    first = ledger.reserve("acme", 3).reservation_id
    ledger.reserve("globex", 1)
    ledger.release(first)
    assert path.read_text(encoding="utf-8") == ""


@pytest.mark.parametrize(
    "command",
    [
        lambda book: book.reserve("nobody", 1),
        lambda book: book.reserve("acme", 0),
        lambda book: book.reserve("acme", 500),
        lambda book: book.commit("r99"),
        lambda book: book.release("r99"),
        lambda book: book.close_tenant("nobody"),
    ],
)
def test_a_rejected_command_writes_nothing_durably(ledger, path, command):
    """R4, checked against the file rather than the accessor."""
    ledger.commit(ledger.reserve("acme", 1).reservation_id)
    before = path.read_text(encoding="utf-8")
    assert command(ledger).status == "rejected"
    assert path.read_text(encoding="utf-8") == before


def test_the_ledger_is_append_only_across_many_writes(ledger, path):
    """R5: every earlier line is still there, unchanged, in place."""
    seen: list[str] = []
    for amount in (1, 1, 2, 1):
        ledger.commit(ledger.reserve("acme", amount).reservation_id)
        seen.append(file_lines(path)[-1])
        assert file_lines(path) == seen


# -- reservation ids -------------------------------------------------------


def test_ids_are_not_reused_after_commit_or_release(ledger):
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


def test_outstanding_ids_are_ascending_past_ten(path):
    """Ascending by allocation order: r2 comes before r10, not after it."""
    book = QuotaLedger({"acme": 100}, path)
    ids = [book.reserve("acme", 1).reservation_id for _ in range(12)]
    assert ids[-1] == "r12"
    assert book.outstanding_ids() == ids
    book.release("r1")
    book.commit("r3")
    assert book.outstanding_ids() == [i for i in ids if i not in {"r1", "r3"}]


def test_outstanding_ids_span_tenants(ledger):
    ledger.reserve("acme", 1)
    ledger.reserve("globex", 1)
    assert ledger.outstanding_ids() == ["r1", "r2"]


# -- accepted results ------------------------------------------------------


def test_accepted_results_carry_no_reason(ledger):
    reserved = ledger.reserve("acme", 1)
    assert reserved.reason is None
    assert ledger.commit(reserved.reservation_id).reason is None
    assert ledger.close_tenant("globex").reason is None


def test_rejected_results_carry_no_reservation_id(ledger):
    assert ledger.reserve("nobody", 1).reservation_id is None
    assert ledger.commit("r99").reservation_id is None


# -- rules across whole sequences ------------------------------------------


def test_release_after_commit_rejects_and_leaves_the_total_alone(ledger):
    rid = ledger.reserve("acme", 4).reservation_id
    ledger.commit(rid)
    assert ledger.release(rid).reason == "unknown_reservation"
    assert ledger.committed("acme") == 4
    assert ledger.available("acme") == 6


def test_commit_after_release_rejects_and_writes_nothing(ledger):
    rid = ledger.reserve("acme", 4).reservation_id
    ledger.release(rid)
    assert ledger.commit(rid).reason == "unknown_reservation"
    assert ledger.committed("acme") == 0
    assert ledger.ledger_lines() == []


def test_closing_one_tenant_leaves_the_other_alone(ledger):
    ledger.close_tenant("globex")
    assert ledger.is_closed("globex") is True
    assert ledger.is_closed("acme") is False
    assert ledger.reserve("acme", 10).status == "accepted"


def test_a_closed_tenant_has_exactly_one_close_line(ledger):
    ledger.close_tenant("acme")
    for _ in range(3):
        assert ledger.close_tenant("acme").reason == "tenant_closed"
    assert [line for line in ledger.ledger_lines() if line.startswith("CLOSE")] == [
        "CLOSE acme 0"
    ]


def test_close_total_matches_committed_after_commits_and_releases(ledger):
    first = ledger.reserve("acme", 4).reservation_id
    second = ledger.reserve("acme", 3).reservation_id
    third = ledger.reserve("acme", 2).reservation_id
    ledger.commit(first)
    ledger.release(second)
    ledger.commit(third)
    ledger.close_tenant("acme")
    assert ledger.committed("acme") == 6
    assert ledger.ledger_lines()[-1] == "CLOSE acme 6"


def test_quota_can_be_fully_committed(ledger):
    ledger.commit(ledger.reserve("globex", 4).reservation_id)
    assert ledger.available("globex") == 0
    assert ledger.committed("globex") == 4
    assert ledger.reserve("globex", 1).reason == "quota_exceeded"


def test_a_zero_quota_tenant_can_only_be_closed(path):
    book = QuotaLedger({"empty": 0}, path)
    assert book.reserve("empty", 1).reason == "quota_exceeded"
    assert book.close_tenant("empty").status == "accepted"
    assert book.ledger_lines() == ["CLOSE empty 0"]


def test_reserve_rejection_order_is_the_declared_one(path):
    """Closed beats not-positive beats exceeded; unknown beats everything."""
    book = QuotaLedger({"acme": 1}, path)
    assert book.reserve("nobody", -5).reason == "unknown_tenant"
    assert book.reserve("acme", 500).reason == "quota_exceeded"
    book.close_tenant("acme")
    assert book.reserve("acme", 0).reason == "tenant_closed"
    assert book.reserve("acme", 500).reason == "tenant_closed"


def test_close_rejection_order_is_the_declared_one(ledger):
    ledger.reserve("acme", 1)
    assert ledger.close_tenant("nobody").reason == "unknown_tenant"
    assert ledger.close_tenant("acme").reason == "outstanding_reservations"
    ledger.release("r1")
    ledger.close_tenant("acme")
    ledger.reserve("globex", 1)
    # closed already, and it cannot have outstanding reservations anyway
    assert ledger.close_tenant("acme").reason == "tenant_closed"


# -- randomized sequence against an independent model ----------------------


def check_rules(book, model, path):
    """R1, R2 and R3, recomputed from scratch against the file on disk."""
    lines = file_lines(path)
    assert book.ledger_lines() == lines

    for tenant, quota in model["quotas"].items():
        held = sum(
            amount for (rid, owner, amount) in model["live"] if owner == tenant
        )
        # R1 -- conservation.
        assert book.available(tenant) + held + book.committed(tenant) == quota
        assert book.committed(tenant) == model["committed"][tenant]

        # R2 -- the durable ledger agrees with memory.
        running = 0
        for line in lines:
            kind, owner, *rest = line.split()
            if kind == "COMMIT" and owner == tenant:
                running += int(rest[0])
                assert int(rest[1]) == running
        assert running == book.committed(tenant)

        # R3 -- a close is final and singular.
        closes = [
            line for line in lines if line.startswith(f"CLOSE {tenant} ")
        ]
        assert book.is_closed(tenant) == (tenant in model["closed"])
        if book.is_closed(tenant):
            assert closes == [f"CLOSE {tenant} {book.committed(tenant)}"]
            assert held == 0
        else:
            assert closes == []

    assert book.outstanding_ids() == [rid for (rid, _, _) in model["live"]]


def test_rules_hold_through_a_long_random_sequence(path):
    """A model-based sweep: every command, accepted or rejected, then recheck."""
    quotas = {"acme": 10, "globex": 4, "initech": 7}
    book = QuotaLedger(dict(quotas), path)
    model = {
        "quotas": quotas,
        "committed": {tenant: 0 for tenant in quotas},
        "closed": set(),
        "live": [],  # (reservation_id, tenant, amount), in allocation order
    }

    rng = random.Random(20260804)
    tenants = list(quotas) + ["nobody"]

    for _ in range(400):
        choice = rng.random()
        if choice < 0.45:
            tenant = rng.choice(tenants)
            amount = rng.randint(-2, 12)
            result = book.reserve(tenant, amount)
            if result.status == "accepted":
                assert tenant in quotas and tenant not in model["closed"] and amount >= 1
                model["live"].append((result.reservation_id, tenant, amount))
        elif choice < 0.70:
            rid = _some_id(rng, model)
            result = book.commit(rid)
            if result.status == "accepted":
                entry = _take(model["live"], rid)
                model["committed"][entry[1]] += entry[2]
        elif choice < 0.90:
            rid = _some_id(rng, model)
            result = book.release(rid)
            if result.status == "accepted":
                _take(model["live"], rid)
        else:
            tenant = rng.choice(tenants)
            result = book.close_tenant(tenant)
            if result.status == "accepted":
                model["closed"].add(tenant)

        assert result.status in {"accepted", "rejected"}
        check_rules(book, model, path)

    # The sweep should have exercised both outcomes of every command, not just
    # rejections; a sequence that only ever rejected would prove nothing.
    assert any(model["committed"].values())
    assert model["closed"]
    assert file_lines(path)


def _some_id(rng, model):
    """A live id most of the time, a plausible dead or invented one otherwise."""
    if model["live"] and rng.random() < 0.75:
        return rng.choice(model["live"])[0]
    return f"r{rng.randint(1, 40)}"


def _take(live, rid):
    for index, entry in enumerate(live):
        if entry[0] == rid:
            return live.pop(index)
    raise AssertionError(f"model has no live reservation {rid}")
