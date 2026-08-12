"""A Journal kept in a list. The fake driven adapter.

Not a mock: it is a working implementation of the same port, obeying the same
contract, and the same behavioral cases run against it and against
`FileJournal` unchanged (see tests/test_ledger.py). It exists so the rules can
be exercised with nothing durable behind them, and so that "the port is a
port" is a fact demonstrated by a second implementation rather than an
assertion in a comment.
"""

from __future__ import annotations


class InMemoryJournal:
    def __init__(self) -> None:
        self._records: list[str] = []

    def append(self, record: str) -> None:
        self._records.append(record)

    def records(self) -> list[str]:
        return list(self._records)
