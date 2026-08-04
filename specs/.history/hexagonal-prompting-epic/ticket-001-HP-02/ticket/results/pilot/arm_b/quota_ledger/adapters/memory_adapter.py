"""The fake `DurableLedger`: a working in-memory implementation, not a mock
that records calls. Used to exercise the domain in tests without touching a
filesystem.

Swap sentence: replace `FileLedgerAdapter` with `InMemoryLedgerAdapter` (or
vice versa) and no file under `quota_ledger/domain.py` changes.
"""

from __future__ import annotations

from typing import List


class InMemoryLedgerAdapter:
    def __init__(self) -> None:
        self._lines: List[str] = []

    def append_line(self, line: str) -> None:
        self._lines.append(line)

    def lines(self) -> List[str]:
        return list(self._lines)
