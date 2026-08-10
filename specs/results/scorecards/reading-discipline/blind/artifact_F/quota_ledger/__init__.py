"""Composition point.

The one place allowed to know both the rules and the technology that satisfies
their port. `QuotaLedger` is the domain `Ledger` wired to a file: it adds the
wiring and nothing else, which is why it extends the domain class instead of
forwarding nine methods to it. Anyone who wants a different durable side builds
`Ledger(quotas, some_other_journal)` directly and never touches this class.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .domain import Journal, Ledger, Result
from .file_journal import FileJournal
from .memory_journal import MemoryJournal

__all__ = ["QuotaLedger", "Ledger", "Journal", "Result", "FileJournal", "MemoryJournal"]


class QuotaLedger(Ledger):
    def __init__(self, quotas: Mapping[str, int], ledger_path: Path | str) -> None:
        super().__init__(quotas, FileJournal(ledger_path))
