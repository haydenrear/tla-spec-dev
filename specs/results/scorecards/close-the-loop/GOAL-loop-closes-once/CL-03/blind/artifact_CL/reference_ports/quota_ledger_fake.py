"""Composition point -- the FAKE wiring. `QUOTA_LEDGER_IMPL=quota_ledger_fake`.

Same domain, same constructor signature, other side of the port. `ledger_path`
is accepted and unused: the fake's durability is the object's lifetime, which
is exactly what makes it a fake and not a second real adapter.

THIS FILE IS AN INSTRUMENT, NOT A CONVENIENCE. It is the difference between a
fault in `journal_memory.py` being observable and being invisible, and the
predecessor measured that difference as the whole of `BA-B14`: an adapter with
no composition point pointing at it is verified by nothing. It is four lines
because the remedy for that blind region is four lines, which is itself the
finding -- the region was not expensive to reach, it was simply never reached.

What it does NOT do, deliberately:

  * it does not assert that the two wirings agree. A test that only compares
    two wirings of one domain passes when the domain is wrong, because both
    wirings are wrong together. The shared suite asserts EXPECTED VALUES, and
    running the identical expected-value suite through both wirings is what
    makes a fault in either adapter die.
  * it does not gate, refuse, or report a verdict. It is a module the suite can
    be pointed at.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from domain import LedgerJournal, REJECTION_REASONS, Reservation, ReservationBook, Result
from journal_memory import InMemoryJournal


class QuotaLedger(ReservationBook):
    """A ReservationBook wired to the fake, matching FEATURE.md's constructor."""

    def __init__(self, quotas: Mapping[str, int], ledger_path: str | Path) -> None:
        super().__init__(quotas, InMemoryJournal())


__all__ = [
    "InMemoryJournal",
    "LedgerJournal",
    "QuotaLedger",
    "REJECTION_REASONS",
    "Reservation",
    "ReservationBook",
    "Result",
]
