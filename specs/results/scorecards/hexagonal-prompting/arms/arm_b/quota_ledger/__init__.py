"""Composition point.

The one place allowed to know both halves: it picks the adapter that satisfies
the domain's CommitJournal port and hands it in. Everything it knows, it knows
here -- `domain.py` imports neither adapter module.

Swap sentence: replace FileJournal with InMemoryJournal on the line below and
no domain file changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .domain import CommitJournal, ReservationBook, Result
from .journal_file import FileJournal
from .journal_memory import InMemoryJournal


class QuotaLedger(ReservationBook):
    """A ReservationBook wired to a file.

    Wiring by construction rather than by delegation: a wrapper would have to
    restate all nine domain methods to forward them, and a restated surface is
    a second place for the behavior to drift.
    """

    def __init__(self, quotas: Mapping[str, int], ledger_path: str | Path) -> None:
        super().__init__(quotas, FileJournal(ledger_path))


__all__ = [
    "CommitJournal",
    "FileJournal",
    "InMemoryJournal",
    "QuotaLedger",
    "ReservationBook",
    "Result",
]
