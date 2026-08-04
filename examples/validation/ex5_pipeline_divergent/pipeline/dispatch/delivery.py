"""Model variable `delivered`, and the dispatch side of port P1.

Component: dispatch. Reaches ingest through `WorkQueue.take` only -- that is
port P1 (`Deliver`). It must not reach ledger: `Record` is dispatch <-> ledger
(port P2) and is driven from the ledger side.
"""

from __future__ import annotations

from pipeline.ingest.queue import WorkQueue


class Dispatcher:
    """`delivered`: items handed off from the queue."""

    def __init__(self, queue: WorkQueue) -> None:
        self._queue = queue
        self._delivered: set[str] = set()

    @property
    def delivered(self) -> frozenset[str]:
        return frozenset(self._delivered)

    def deliver(self, item: str, failed: frozenset[str]) -> bool:
        """`Deliver(i)`: take a queued, not-failed item and mark it delivered."""
        if item in failed:
            return False
        if not self._queue.take(item):
            return False
        self._delivered.add(item)
        return True

    def release(self, item: str) -> bool:
        """The dispatch-internal half of `Fail(i)`."""
        if item not in self._delivered:
            return False
        self._delivered.discard(item)
        return True
