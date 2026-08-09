"""Driven adapter: the `Journal` port kept in memory.

A working implementation of the same interface, not a mock: it records no calls
and makes no assertions. It is what `tests/test_journal_parity.py` runs the
identical case list against, and it is the concrete alternative behind the swap
sentence in NOTES.md.
"""

from __future__ import annotations


class MemoryJournal:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def append(self, line: str) -> None:
        self._lines.append(line)

    def lines(self) -> list[str]:
        return list(self._lines)
