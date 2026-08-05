"""A CommitJournal that keeps the record in memory.

The fake for the one driven port: a working implementation of the same
interface, not a recorder of calls. Anything the domain can be asked through a
FileJournal it can be asked through this one, which is what
tests/test_journal_parity.py checks.
"""

from __future__ import annotations


class InMemoryJournal:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def append(self, line: str) -> None:
        self._lines.append(line)

    def lines(self) -> list[str]:
        return list(self._lines)
