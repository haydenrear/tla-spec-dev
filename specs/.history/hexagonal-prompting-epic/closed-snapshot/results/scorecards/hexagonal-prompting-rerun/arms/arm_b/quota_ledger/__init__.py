"""The composition point.

This is the only module allowed to know both the rules and the machinery that
satisfies them. It imports the domain and it imports a concrete Journal; the
domain imports neither this module nor any adapter.

`QuotaLedger` is the entry point the feature names, and it is a factory rather
than a class: the feature requires it to be constructed from a mapping and a
*path*, and a path is a filesystem word that the rules must not learn. So the
factory takes the path, builds the adapter that understands paths, and hands
the rules a Journal.

The swap, in one sentence: replace `FileJournal(ledger_path)` on the line
below with `InMemoryJournal()` and no domain file changes.
"""

from __future__ import annotations

import os
from typing import Mapping

from .domain import Journal, Ledger, Reservation, Result
from .file_journal import FileJournal
from .memory_journal import InMemoryJournal

__all__ = [
    "QuotaLedger",
    "Ledger",
    "Journal",
    "Result",
    "Reservation",
    "FileJournal",
    "InMemoryJournal",
]


def QuotaLedger(quotas: Mapping[str, int], ledger_path: str | os.PathLike[str]) -> Ledger:
    """A ledger whose durable side is a file at `ledger_path`."""
    return Ledger(quotas, FileJournal(ledger_path))
