"""The FAKE adapter for `domain.LedgerJournal`: the record kept in memory.

A working implementation of the same interface, not a recorder of calls.
Anything the domain can be asked through a `FileJournal` it can be asked
through this one.

WHY THIS FILE IS THE POINT OF THE PA CATALOGUE
----------------------------------------------
The predecessor measured, and nobody predicted, that a fault in exactly this
kind of file **survives every instrument including the hand-written suite**
(`BA-B14`, recorded in
`specs/results/scorecards/hexagonal-prompting/FINDINGS.md`). Its sentence: *the
port removes places for some faults to live and creates a region no shared
oracle reaches -- the fake that earned arm B its D3 = 4 is verified by nothing
outside arm B's own tests.*

The reason is mechanical, not mysterious. The shared suite constructs
`QuotaLedger(quotas, path)`. That constructor is a composition point, and the
composition point it names picks the FILE adapter. So the fake is on nobody's
execution path and a fault inside it cannot be observed by a test that never
runs it.

`quota_ledger_fake.py` is the whole remedy and it is four lines long: a second
composition point that satisfies the same constructor signature with this
adapter instead. The identical suite then runs through the identical domain
against the other side of the port. Nothing else changes -- not the suite, not
the feature, not the domain, not the model.
"""

from __future__ import annotations


class InMemoryJournal:
    """Durable for the lifetime of the object; append-only; ordered."""

    def __init__(self) -> None:
        self._lines: list[str] = []

    def append(self, line: str) -> None:
        self._lines.append(line)

    def lines(self) -> list[str]:
        return [entry for entry in self._lines if entry]
