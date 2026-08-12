"""Composition point -- the REAL wiring. `QUOTA_LEDGER_IMPL=quota_ledger`.

The one place allowed to know both halves: it picks the adapter that satisfies
the domain's `LedgerJournal` port and hands it in. `domain.py` imports neither
adapter module.

Swap sentence: replace `FileJournal` with `InMemoryJournal` on the line below
and no domain file changes. `quota_ledger_fake.py` is that sentence, executed,
so the claim is not a claim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from domain import LedgerJournal, REJECTION_REASONS, Reservation, ReservationBook, Result
from journal_file import FileJournal


class QuotaLedger(ReservationBook):
    """A ReservationBook wired to a file, matching FEATURE.md's constructor."""

    def __init__(self, quotas: Mapping[str, int], ledger_path: str | Path) -> None:
        super().__init__(quotas, FileJournal(ledger_path))


__all__ = [
    "FileJournal",
    "LedgerJournal",
    "QuotaLedger",
    "REJECTION_REASONS",
    "Reservation",
    "ReservationBook",
    "Result",
]
