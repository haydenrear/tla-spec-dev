"""My own tests. The shared suite in examples/validation/ab/tests is the floor.

Two things this file does that the shared suite cannot:

1. Every behavioral case runs TWICE -- once with the rules wired to
   `FileJournal` and once wired to `InMemoryJournal` -- from one case list.
   Every case asserts an expected value, never merely that the two wirings
   agree: two wirings of the same domain agree with each other even when the
   domain is wrong.
2. It checks the port contract itself against both implementations, and checks
   that the domain module really does not import its adapters.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from quota_ledger import FileJournal, InMemoryJournal, Ledger

QUOTAS = {"acme": 10, "globex": 4}


@pytest.fixture(params=["file", "memory"])
def journal(request, tmp_path):
    """The same case, wired to the real adapter and to the fake."""
    if request.param == "file":
        return FileJournal(tmp_path / "ledger.txt")
    return InMemoryJournal()


@pytest.fixture()
def ledger(journal):
    return Ledger(dict(QUOTAS), journal)


# -- the port contract, against both implementations -----------------------


def test_a_fresh_journal_has_no_records(journal):
    assert journal.records() == []


def test_records_come_back_in_append_order(journal):
    journal.append("first")
    journal.append("second")
    journal.append("third")
    assert journal.records() == ["first", "second", "third"]


def test_appending_never_disturbs_what_is_already_there(journal):
    journal.append("first")
    before = journal.records()
    journal.append("second")
    assert journal.records()[: len(before)] == before
    assert journal.records() == ["first", "second"]


def test_duplicate_records_are_kept_as_two(journal):
    journal.append("COMMIT acme 1 1")
    journal.append("COMMIT acme 1 1")
    assert journal.records() == ["COMMIT acme 1 1", "COMMIT acme 1 1"]


def test_the_returned_list_belongs_to_the_caller(journal):
    journal.append("first")
    stolen = journal.records()
    stolen.append("forged")
    assert journal.records() == ["first"]


# -- the rules, through the port, on both wirings ---------------------------


def test_reserve_holds_the_amount_without_writing_anything(ledger):
    result = ledger.reserve("acme", 3)
    assert (result.status, result.reservation_id) == ("accepted", "r1")
    assert ledger.available("acme") == 7
    assert ledger.committed("acme") == 0
    assert ledger.outstanding_ids() == ["r1"]
    assert ledger.ledger_lines() == []


def test_ids_ascend_across_tenants_and_are_never_reused(ledger):
    first = ledger.reserve("acme", 1).reservation_id
    second = ledger.reserve("globex", 1).reservation_id
    ledger.release(first)
    third = ledger.reserve("acme", 1).reservation_id
    assert [first, second, third] == ["r1", "r2", "r3"]
    assert ledger.outstanding_ids() == ["r2", "r3"]


def test_a_rejected_reserve_does_not_burn_an_id(ledger):
    assert ledger.reserve("acme", 99).status == "rejected"
    assert ledger.reserve("acme", 1).reservation_id == "r1"


def test_outstanding_ids_stay_ascending_past_ten(ledger):
    """Ascending, not lexicographic: 'r10' must not sort before 'r2'."""
    for _ in range(10):
        ledger.reserve("acme", 1)
        ledger.reserve("globex", 0)  # rejected; must not shift the sequence
    assert ledger.outstanding_ids() == [f"r{n}" for n in range(1, 11)]


def test_commit_writes_one_line_and_keeps_the_amount_deducted(ledger):
    rid = ledger.reserve("acme", 3).reservation_id
    assert ledger.commit(rid).status == "accepted"
    assert ledger.committed("acme") == 3
    assert ledger.available("acme") == 7
    assert ledger.outstanding_ids() == []
    assert ledger.ledger_lines() == ["COMMIT acme 3 3"]


def test_running_totals_are_per_tenant_and_interleave(ledger):
    acme_first = ledger.reserve("acme", 4).reservation_id
    globex_first = ledger.reserve("globex", 1).reservation_id
    acme_second = ledger.reserve("acme", 2).reservation_id
    globex_second = ledger.reserve("globex", 3).reservation_id
    for rid in (globex_first, acme_first, acme_second, globex_second):
        assert ledger.commit(rid).status == "accepted"
    assert ledger.ledger_lines() == [
        "COMMIT globex 1 1",
        "COMMIT acme 4 4",
        "COMMIT acme 2 6",
        "COMMIT globex 3 4",
    ]
    assert (ledger.committed("acme"), ledger.committed("globex")) == (6, 4)
    assert (ledger.available("acme"), ledger.available("globex")) == (4, 0)


def test_release_writes_nothing_and_gives_the_amount_back(ledger):
    rid = ledger.reserve("globex", 4).reservation_id
    assert ledger.release(rid).status == "accepted"
    assert ledger.available("globex") == 4
    assert ledger.committed("globex") == 0
    assert ledger.ledger_lines() == []


def test_close_writes_exactly_one_line_with_the_final_total(ledger):
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    ledger.commit(ledger.reserve("acme", 2).reservation_id)
    assert ledger.close_tenant("acme").status == "accepted"
    assert ledger.is_closed("acme") is True
    assert ledger.is_closed("globex") is False
    assert ledger.ledger_lines() == [
        "COMMIT acme 3 3",
        "COMMIT acme 2 5",
        "CLOSE acme 5",
    ]


def test_a_closed_tenant_takes_no_more_reservations(ledger):
    ledger.close_tenant("globex")
    assert ledger.reserve("globex", 1).reason == "tenant_closed"
    assert ledger.ledger_lines() == ["CLOSE globex 0"]


@pytest.mark.parametrize(
    "command,reason",
    [
        (lambda book: book.reserve("nobody", 1), "unknown_tenant"),
        (lambda book: book.reserve("acme", 0), "amount_not_positive"),
        (lambda book: book.reserve("acme", -5), "amount_not_positive"),
        (lambda book: book.reserve("acme", 8), "quota_exceeded"),
        (lambda book: book.commit("r404"), "unknown_reservation"),
        (lambda book: book.commit("r1"), "unknown_reservation"),
        (lambda book: book.release("r404"), "unknown_reservation"),
        (lambda book: book.close_tenant("nobody"), "unknown_tenant"),
        (lambda book: book.close_tenant("acme"), "outstanding_reservations"),
    ],
)
def test_a_rejection_names_its_reason_and_changes_nothing(ledger, command, reason):
    """R4, including the durable side: a rejection writes no line either."""
    ledger.commit(ledger.reserve("acme", 5).reservation_id)  # r1, spent
    ledger.reserve("acme", 3)  # r2, live, so acme cannot close

    before = (
        {tenant: ledger.available(tenant) for tenant in QUOTAS},
        {tenant: ledger.committed(tenant) for tenant in QUOTAS},
        {tenant: ledger.is_closed(tenant) for tenant in QUOTAS},
        ledger.outstanding_ids(),
        ledger.ledger_lines(),
    )
    result = command(ledger)
    assert result.status == "rejected"
    assert result.reason == reason
    assert result.reservation_id is None
    after = (
        {tenant: ledger.available(tenant) for tenant in QUOTAS},
        {tenant: ledger.committed(tenant) for tenant in QUOTAS},
        {tenant: ledger.is_closed(tenant) for tenant in QUOTAS},
        ledger.outstanding_ids(),
        ledger.ledger_lines(),
    )
    assert after == before
    assert before[4] == ["COMMIT acme 5 5"]


def test_ordering_and_exact_content_of_a_long_mixed_run(ledger):
    """R1, R2, R3 and R5 read off one concrete expected transcript."""
    a1 = ledger.reserve("acme", 4).reservation_id
    g1 = ledger.reserve("globex", 4).reservation_id
    a2 = ledger.reserve("acme", 3).reservation_id
    ledger.release(g1)
    ledger.commit(a1)
    g2 = ledger.reserve("globex", 2).reservation_id
    ledger.commit(g2)
    ledger.release(a2)
    assert ledger.close_tenant("acme").status == "accepted"
    assert ledger.close_tenant("globex").status == "accepted"

    assert ledger.ledger_lines() == [
        "COMMIT acme 4 4",
        "COMMIT globex 2 2",
        "CLOSE acme 4",
        "CLOSE globex 2",
    ]
    assert ledger.outstanding_ids() == []
    assert (ledger.available("acme"), ledger.committed("acme")) == (6, 4)
    assert (ledger.available("globex"), ledger.committed("globex")) == (2, 2)
    for tenant, quota in QUOTAS.items():
        assert ledger.available(tenant) + ledger.committed(tenant) == quota


def test_the_quota_can_be_exhausted_and_recovered(ledger):
    first = ledger.reserve("globex", 4).reservation_id
    assert ledger.available("globex") == 0
    assert ledger.reserve("globex", 1).reason == "quota_exceeded"
    ledger.release(first)
    assert ledger.available("globex") == 4
    assert ledger.reserve("globex", 4).status == "accepted"
    assert ledger.ledger_lines() == []


# -- the file adapter's own business ---------------------------------------


def test_the_file_starts_empty_and_grows_by_one_line_per_record(tmp_path):
    path = tmp_path / "ledger.txt"
    journal = FileJournal(path)
    assert path.read_text() == ""
    journal.append("COMMIT acme 1 1")
    journal.append("CLOSE acme 1")
    assert path.read_text() == "COMMIT acme 1 1\nCLOSE acme 1\n"
    assert journal.records() == ["COMMIT acme 1 1", "CLOSE acme 1"]


def test_a_second_journal_at_the_same_path_starts_empty(tmp_path):
    path = tmp_path / "ledger.txt"
    FileJournal(path).append("COMMIT acme 1 1")
    assert FileJournal(path).records() == []


# -- the boundary itself ----------------------------------------------------


def test_the_domain_module_imports_no_adapter_and_nothing_that_does_io():
    """'Does not import' is the claim, so read the imports."""
    source = Path(__file__).resolve().parent.parent / "quota_ledger" / "domain.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert imported == {"__future__", "dataclasses", "typing"}
