"""My own tests, alongside (not instead of) the shared behavioral suite.

These deliberately go where the shared suite does not: check ORDER between
rejection reasons when two would fire, read the ledger file back off disk
instead of trusting the query, push id allocation past r9 where string sorting
would break, and grind the four rules through a long deterministic random
sequence.

    uv run --with pytest python -m pytest subjects/artifact_Z/test_quota_ledger.py -q
"""

from __future__ import annotations

import random
from collections import Counter

import pytest

from quota_ledger import REASONS, QuotaLedger

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture()
def ledger(tmp_path):
    return QuotaLedger(dict(QUOTAS), tmp_path / "ledger.txt")


# -- the file itself -------------------------------------------------------


def test_the_ledger_file_starts_empty(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    assert path.exists()
    assert path.read_text() == ""
    assert book.ledger_lines() == []


def test_ledger_lines_matches_what_is_actually_on_disk(tmp_path):
    """ledger_lines() is a claim about the file, so check the file."""
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    book.close_tenant("globex")
    assert path.read_text() == "COMMIT acme 3 3\nCLOSE globex 0\n"
    assert book.ledger_lines() == ["COMMIT acme 3 3", "CLOSE globex 0"]


def test_a_string_path_works_as_well_as_a_path_object(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), str(path))
    book.close_tenant("acme")
    assert book.ledger_lines() == ["CLOSE acme 0"]


def test_release_never_touches_the_file(tmp_path):
    path = tmp_path / "ledger.txt"
    book = QuotaLedger(dict(QUOTAS), path)
    for _ in range(5):
        book.release(book.reserve("acme", 2).reservation_id)
    assert path.read_text() == ""


# -- reason ORDER when more than one check would fire ----------------------


def test_unknown_tenant_beats_a_bad_amount(ledger):
    assert ledger.reserve("nobody", 0).reason == "unknown_tenant"
    assert ledger.reserve("nobody", -5).reason == "unknown_tenant"


def test_closed_beats_a_bad_amount_and_beats_quota(ledger):
    ledger.close_tenant("globex")
    assert ledger.reserve("globex", 0).reason == "tenant_closed"
    assert ledger.reserve("globex", 99).reason == "tenant_closed"


def test_a_bad_amount_beats_quota_exceeded(ledger):
    """-1 exceeds nothing; it must report the amount, not the quota."""
    assert ledger.reserve("globex", -1).reason == "amount_not_positive"


def test_close_reports_closed_before_outstanding(ledger):
    ledger.close_tenant("acme")
    # A closed tenant cannot acquire reservations, so the only way to check
    # the order is that closed still wins on a tenant that has none.
    assert ledger.close_tenant("acme").reason == "tenant_closed"


def test_every_declared_reason_is_reachable_and_no_other_is(ledger):
    ledger.reserve("acme", 1)  # so acme has something outstanding
    ledger.close_tenant("globex")  # so globex is closed
    seen = {
        ledger.reserve("nobody", 1).reason,
        ledger.reserve("globex", 1).reason,
        ledger.reserve("acme", 0).reason,
        ledger.reserve("acme", 99).reason,
        ledger.commit("nope").reason,
        ledger.release("nope").reason,
        ledger.close_tenant("nobody").reason,
        ledger.close_tenant("acme").reason,
    }
    assert seen == set(REASONS)


# -- id allocation ---------------------------------------------------------


def test_a_rejected_reserve_consumes_no_id(ledger):
    assert ledger.reserve("acme", 1).reservation_id == "r1"
    assert ledger.reserve("nobody", 1).reservation_id is None
    assert ledger.reserve("acme", 0).reservation_id is None
    assert ledger.reserve("acme", 500).reservation_id is None
    assert ledger.reserve("acme", 1).reservation_id == "r2"


def test_ids_are_not_reused_after_commit_or_release(ledger):
    first = ledger.reserve("acme", 1).reservation_id
    ledger.commit(first)
    second = ledger.reserve("acme", 1).reservation_id
    ledger.release(second)
    third = ledger.reserve("acme", 1).reservation_id
    assert [first, second, third] == ["r1", "r2", "r3"]


def test_outstanding_ids_are_ascending_past_nine(ledger):
    """r10 must sort after r9, which plain string sorting gets wrong."""
    for _ in range(12):
        ledger.reserve("acme", 0)  # rejected, so it must not appear
    ids = [ledger.reserve("acme", 1).reservation_id for _ in range(10)]
    assert ids == [f"r{n}" for n in range(1, 11)]
    assert ledger.outstanding_ids() == ids


def test_outstanding_ids_stay_ascending_after_removals(ledger):
    ids = [ledger.reserve("acme", 1).reservation_id for _ in range(5)]
    ledger.commit(ids[1])
    ledger.release(ids[3])
    assert ledger.outstanding_ids() == ["r1", "r3", "r5"]


# -- resolution is once and once only --------------------------------------


def test_release_after_commit_rejects(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.commit(rid)
    assert ledger.release(rid).reason == "unknown_reservation"
    assert ledger.available("acme") == 7
    assert ledger.ledger_lines() == ["COMMIT acme 3 3"]


def test_commit_after_release_rejects(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    ledger.release(rid)
    assert ledger.commit(rid).reason == "unknown_reservation"
    assert ledger.committed("acme") == 0
    assert ledger.ledger_lines() == []


def test_release_twice_rejects_the_second(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    assert ledger.release(rid).status == "accepted"
    assert ledger.release(rid).reason == "unknown_reservation"
    assert ledger.available("acme") == 10, "the amount comes back once, not twice"


# -- close -----------------------------------------------------------------


def test_close_is_singular_in_the_file_even_under_repeated_attempts(ledger):
    ledger.commit(ledger.reserve("acme", 2).reservation_id)
    ledger.close_tenant("acme")
    for _ in range(3):
        assert ledger.close_tenant("acme").reason == "tenant_closed"
    assert ledger.ledger_lines().count("CLOSE acme 2") == 1
    assert sum(line.startswith("CLOSE") for line in ledger.ledger_lines()) == 1


def test_closing_one_tenant_leaves_the_other_alone(ledger):
    ledger.close_tenant("acme")
    assert ledger.is_closed("acme")
    assert not ledger.is_closed("globex")
    assert ledger.reserve("globex", 4).status == "accepted"


def test_close_total_counts_commits_and_ignores_releases(ledger):
    ledger.commit(ledger.reserve("acme", 2).reservation_id)
    ledger.release(ledger.reserve("acme", 5).reservation_id)
    ledger.commit(ledger.reserve("acme", 1).reservation_id)
    assert ledger.close_tenant("acme").status == "accepted"
    assert ledger.ledger_lines()[-1] == "CLOSE acme 3"


def test_a_released_reservation_unblocks_close_but_a_committed_one_also_does(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    assert ledger.close_tenant("acme").reason == "outstanding_reservations"
    ledger.commit(rid)
    assert ledger.close_tenant("acme").status == "accepted"


# -- the rules under a long mixed sequence ---------------------------------


def test_the_four_rules_survive_a_long_random_sequence():
    """A deterministic driver: shadow the state, then compare on every step."""
    import tempfile

    rng = random.Random(20260809)
    # Mixed quotas on purpose. A commit consumes availability for good, so two
    # roomy tenants keep the run alive for 600 steps and keep live
    # reservations around for the close phase; the tiny one drains at once and
    # is what produces quota_exceeded.
    quotas = {"acme": 4000, "globex": 6, "initech": 3000}

    with tempfile.TemporaryDirectory() as directory:
        book = QuotaLedger(dict(quotas), f"{directory}/ledger.txt")

        held = {}  # id -> (tenant, amount)
        available = dict(quotas)
        committed = {tenant: 0 for tenant in quotas}
        closed = {tenant: False for tenant in quotas}
        expected_lines = []
        outcomes = Counter()
        reasons = Counter()

        # Closing is withheld until late on purpose: a closed tenant accepts
        # nothing, so closing early would end the run in a few dozen steps and
        # the long sequence would not be long.
        for step in range(600):
            pool = ["reserve", "reserve", "reserve", "commit", "release"]
            if step >= 400:
                pool += ["close", "close"]
            action = rng.choice(pool)
            before = list(book.ledger_lines())

            if action == "reserve":
                tenant = rng.choice(list(quotas) + ["nobody"])
                amount = rng.randint(-2, 8)
                result = book.reserve(tenant, amount)
                accepted = (
                    tenant in quotas
                    and not closed[tenant]
                    and amount >= 1
                    and amount <= available[tenant]
                )
                assert (result.status == "accepted") == accepted
                if accepted:
                    held[result.reservation_id] = (tenant, amount)
                    available[tenant] -= amount

            elif action in ("commit", "release"):
                rid = rng.choice(list(held) + ["r999"]) if held else "r999"
                result = getattr(book, action)(rid)
                assert (result.status == "accepted") == (rid in held)
                if rid in held:
                    tenant, amount = held.pop(rid)
                    if action == "commit":
                        committed[tenant] += amount
                        expected_lines.append(f"COMMIT {tenant} {amount} {committed[tenant]}")
                    else:
                        available[tenant] += amount

            else:
                tenant = rng.choice(list(quotas) + ["nobody"])
                live = any(owner == tenant for owner, _ in held.values())
                result = book.close_tenant(tenant)
                accepted = tenant in quotas and not closed[tenant] and not live
                assert (result.status == "accepted") == accepted
                if accepted:
                    closed[tenant] = True
                    expected_lines.append(f"CLOSE {tenant} {committed[tenant]}")

            outcomes[(action, result.status)] += 1
            if result.status == "rejected":
                assert result.reason in REASONS
                reasons[result.reason] += 1
                assert book.ledger_lines() == before, "R4: a rejection writes nothing"

            # R5: append-only and in command order.
            assert book.ledger_lines() == expected_lines

            for tenant in quotas:
                outstanding = sum(a for t, a in held.values() if t == tenant)
                # R1: conservation.
                assert book.available(tenant) + outstanding + book.committed(tenant) == quotas[tenant]
                assert book.available(tenant) == available[tenant]
                assert book.committed(tenant) == committed[tenant]
                assert book.is_closed(tenant) == closed[tenant]
                # R3: a closed tenant holds nothing live.
                if closed[tenant]:
                    assert outstanding == 0

            assert book.outstanding_ids() == sorted(held, key=lambda r: int(r[1:]))

        # R2: the durable side agrees with memory, per tenant.
        lines = book.ledger_lines()
        for tenant in quotas:
            running = 0
            for line in lines:
                fields = line.split()
                if fields[0] == "COMMIT" and fields[1] == tenant:
                    running += int(fields[2])
                    assert int(fields[3]) == running
            assert running == book.committed(tenant)
            # R3: at most one CLOSE, carrying the final total.
            closes = [l for l in lines if l.startswith(f"CLOSE {tenant} ")]
            assert len(closes) == (1 if book.is_closed(tenant) else 0)
            for line in closes:
                assert int(line.split()[2]) == book.committed(tenant)

        # The run is only evidence if it actually reached the states it claims
        # to have checked: both outcomes of every command, and all six reasons.
        for action in ("reserve", "commit", "release", "close"):
            assert outcomes[(action, "accepted")] > 0, f"{action} never succeeded"
            assert outcomes[(action, "rejected")] > 0, f"{action} was never rejected"
        assert set(reasons) == set(REASONS), f"reasons not exercised: {set(REASONS) - set(reasons)}"
        assert len(expected_lines) > 40, "the sequence has to actually exercise the file"
