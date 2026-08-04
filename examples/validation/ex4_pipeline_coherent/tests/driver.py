"""Composition root for the coherent pipeline.

It lives OUTSIDE the scanned code root on purpose, and that is a fixture fact
worth stating rather than hiding: a composition root wires every component, so
placing it inside `pipeline/` would give whatever component held it an edge to
all three -- including the unported ingest <-> ledger pair -- and the coherent
fixture would report a divergence for a file whose whole job is wiring. Real
projects hit this. The reflexion check has no concept of a composition root, so
the fixture answers it the only way the shipped tool allows: keep the wiring
out of `--code`. EV-02 should treat "where does the composition root go" as a
question the check cannot answer, not as a defect of this fixture.
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
        self.journal = Journal(self.dispatcher)

    def accept(self, item: str) -> bool:
        return self.inbox.accept(item)

    def enqueue(self, item: str) -> bool:
        return self.queue.enqueue(item)

    def deliver(self, item: str) -> bool:
        return self.dispatcher.deliver(item, self.failures.failed)

    def fail(self, item: str) -> bool:
        return self.failures.fail(item)

    def record(self, item: str) -> bool:
        return self.journal.record(item)

    def state(self) -> dict[str, object]:
        return {
            "inbox": sorted(self.inbox.pending),
            "accepted": sorted(self.inbox.accepted),
            "queue": list(self.queue.items),
            "delivered": sorted(self.dispatcher.delivered),
            "failed": sorted(self.failures.failed),
            "ledger": list(self.journal.entries),
        }
