"""Model variable `queue`, and the ingest side of the ingest <-> dispatch port.

Component: ingest.

SEEDED DIVERGENCE D1 lives in this file: the backlog report reaches into the
ledger component directly, and there is no ingest <-> ledger port.
"""

from __future__ import annotations

from pipeline.ingest.inbox import Inbox
from pipeline.ledger.journal import Journal


class WorkQueue:
    """`queue`: items handed to dispatch, in insertion order."""

    def __init__(self, inbox: Inbox) -> None:
        self._inbox = inbox
        self._queue: list[str] = []

    @property
    def items(self) -> tuple[str, ...]:
        return tuple(self._queue)

    def enqueue(self, item: str) -> bool:
        """`Enqueue(i)`: an accepted item, not already queued, joins the queue."""
        if item not in self._inbox.accepted:
            return False
        if item in self._queue:
            return False
        self._queue.append(item)
        return True

    def take(self, item: str) -> bool:
        """The ingest half of the `Deliver(i)` handoff: release a queued item."""
        if item not in self._queue:
            return False
        self._queue.remove(item)
        return True

    def backlog_report(self, journal: Journal) -> str:
        """Reporting only. Reads the ledger's entries to size the backlog."""
        return f"queued={len(self._queue)} recorded={len(journal.entries)}"
