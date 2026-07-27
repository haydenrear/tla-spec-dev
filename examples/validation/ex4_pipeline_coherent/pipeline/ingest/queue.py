"""Model variable `queue`, and the ingest side of the ingest <-> dispatch port.

Component: ingest. Writes only ingest state. It reaches `inbox` (an internal
edge) and is reached BY dispatch across port P1; it must not reach dispatch or
ledger itself.
"""

from __future__ import annotations

from pipeline.ingest.inbox import Inbox


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
        """The ingest half of the `Deliver(i)` handoff: release a queued item.

        Called by dispatch across port P1. `Deliver` writes on both sides of the
        boundary in one step in the model, and the code mirrors that: this
        method commits the ingest-side write, and dispatch commits its own in
        the same call. There is no explicit commit point -- that is the modelled
        atomicity-fidelity finding, in the code, on purpose.
        """
        if item not in self._queue:
            return False
        self._queue.remove(item)
        return True
