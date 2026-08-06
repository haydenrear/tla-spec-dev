"""Composition root for the divergent twin.

Identical observable behavior to `ex4_pipeline_coherent/tests/driver.py`. The
twin differs ONLY in dependency structure: the seeded divergences are reporting
helpers, and the seeded absence is a parameter passed instead of an import. A
behavioral test suite cannot tell the two fixtures apart, which is the point --
whatever EV-02 measures here is measuring structure, not behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "generated"))

from pipeline.dispatch.delivery import Dispatcher  # noqa: E402
from pipeline.dispatch.failures import FailureLog  # noqa: E402
from pipeline.ingest.inbox import Inbox  # noqa: E402
from pipeline.ingest.queue import WorkQueue  # noqa: E402
from pipeline.ledger.journal import Journal  # noqa: E402


class Pipeline:
    """The five model actions, wired."""

    def __init__(self, items: list[str]) -> None:
        self.inbox = Inbox(items)
        self.queue = WorkQueue(self.inbox)
        self.dispatcher = Dispatcher(self.queue)
        self.failures = FailureLog(self.dispatcher)
        self.journal = Journal()

    def accept(self, item: str) -> bool:
        return self.inbox.accept(item)

    def enqueue(self, item: str) -> bool:
        return self.queue.enqueue(item)

    def deliver(self, item: str) -> bool:
        return self.dispatcher.deliver(item, self.failures.failed)

    def fail(self, item: str) -> bool:
        return self.failures.fail(item)

    def record(self, item: str) -> bool:
        return self.journal.record(item, self.dispatcher.delivered)

    def state(self) -> dict[str, object]:
        return {
            "inbox": sorted(self.inbox.pending),
            "accepted": sorted(self.inbox.accepted),
            "queue": list(self.queue.items),
            "delivered": sorted(self.dispatcher.delivered),
            "failed": sorted(self.failures.failed),
            "ledger": list(self.journal.entries),
        }
