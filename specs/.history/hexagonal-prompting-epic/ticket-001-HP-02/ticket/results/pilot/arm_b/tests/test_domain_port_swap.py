"""The domain (`QuotaBook`) never imports the module that implements its
`DurableLedger` port. This file is the proof: identical command scenarios,
each run once against `QuotaBook` wired to the real file-backed adapter and
once wired to the in-memory fake, asserting the externally observable result
-- every query, not just the ledger -- comes out identical either way.

If a scenario could only be written meaningfully for one of the two, the port
would be leaking. None of these can.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quota_ledger.adapters.file_adapter import FileLedgerAdapter
from quota_ledger.adapters.memory_adapter import InMemoryLedgerAdapter
from quota_ledger.domain import QuotaBook

QUOTAS = {"acme": 10, "globex": 4}


def observe(book: QuotaBook):
    return (
        {tenant: book.available(tenant) for tenant in QUOTAS},
        {tenant: book.committed(tenant) for tenant in QUOTAS},
        {tenant: book.is_closed(tenant) for tenant in QUOTAS},
        book.outstanding_ids(),
        book.ledger_lines(),
    )


def scenario_mixed_sequence_ending_in_a_close(book: QuotaBook):
    first = book.reserve("acme", 4).reservation_id
    second = book.reserve("acme", 3).reservation_id
    third = book.reserve("globex", 2).reservation_id
    book.commit(first)
    book.release(second)
    book.commit(third)
    book.close_tenant("globex")
    return observe(book)


def scenario_rejections_leave_no_trace(book: QuotaBook):
    book.reserve("nobody", 1)
    book.reserve("acme", 0)
    book.reserve("acme", 999)
    book.commit("r99")
    book.release("r99")
    book.close_tenant("nobody")
    rid = book.reserve("acme", 2).reservation_id
    book.close_tenant("acme")  # outstanding_reservations
    book.release(rid)
    return observe(book)


SCENARIOS = [
    scenario_mixed_sequence_ending_in_a_close,
    scenario_rejections_leave_no_trace,
]


def test_fake_and_real_agree_on_every_scenario(tmp_path):
    for index, scenario in enumerate(SCENARIOS):
        fake_book = QuotaBook(dict(QUOTAS), InMemoryLedgerAdapter())
        real_book = QuotaBook(
            dict(QUOTAS), FileLedgerAdapter(tmp_path / f"scenario_{index}.txt")
        )
        assert scenario(fake_book) == scenario(real_book)
