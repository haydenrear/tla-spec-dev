"""Spec-unit adapters for the EV-01 decomposable fixture.

One adapter per model action. Each MATERIALIZEs `case.before` into the real
production objects, EXECUTEs the action, and PROJECTs the real objects back
into the six model variables. The generated-case runner does the COMPARE.

KNOWN INSTRUMENT LIMITATION -- read this before scoring anything with it.
`scripts/infer_action_params.py` (MF-029) recovers **0 of 5** parameters on
this model: every action is `\\E i \\in Items` guarded by set membership, and
the inference wants a parameter that indexes a function or is written into the
after-state. Every case therefore carries `params={'i': UNCHECKED}`, and the
adapter has to decide which item to act on.

It decides by diffing `case.before` against `case.after`. That is ORACLE
LEAKAGE and it is stated here rather than hidden: the corpus cannot catch a
fault whose only symptom is *acting on the wrong item*, because the adapter is
told which item by the oracle. It can still catch a wrong value, a wrong field,
a wrong count, a wrong status, and a state change that should not have
happened. The seeded-fault table in the fixture README marks the classes this
limitation neutralizes.

Filed as EV-01-DF-01.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _path in (_PROJECT_ROOT, _PROJECT_ROOT / "generated"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from spec_double_compiler.runtime import CaseRunResult  # noqa: E402

from pipeline.dispatch.delivery import Dispatcher  # noqa: E402
from pipeline.dispatch.failures import FailureLog  # noqa: E402
from pipeline.ingest.inbox import Inbox  # noqa: E402
from pipeline.ingest.queue import WorkQueue  # noqa: E402
from pipeline.ledger.journal import Journal  # noqa: E402

VARIABLES = ("inbox", "accepted", "queue", "delivered", "failed", "ledger")


class _Harness:
    """The composition root the adapters drive.

    It is a copy of `tests/driver.py`, deliberately duplicated rather than
    imported: `tests/` is outside the scanned code root, and an adapter that
    imported it would still not be in the code root, so the reflexion answer
    key is unaffected either way. Duplication keeps `specs/` free of a
    dependency on `tests/`.
    """

    def __init__(self, before: dict[str, Any], store: object | None = None) -> None:
        self.inbox = Inbox(sorted(before["inbox"]))
        self.queue = WorkQueue(self.inbox)
        self.dispatcher = Dispatcher(self.queue)
        self.failures = FailureLog(self.dispatcher)
        self.journal = Journal(self.dispatcher, store)
        # MATERIALIZE the rest of the before-state through the real objects'
        # own private stores; there is no public "load a snapshot" surface and
        # inventing one would be changing the program to suit the test.
        self.inbox._accepted = set(before["accepted"])
        self.queue._queue = sorted(before["queue"])
        self.dispatcher._delivered = set(before["delivered"])
        self.failures._failed = set(before["failed"])
        self.journal._entries = sorted(before["ledger"])

    def project(self) -> dict[str, Any]:
        return {
            "inbox": frozenset(self.inbox.pending),
            "accepted": frozenset(self.inbox.accepted),
            "queue": frozenset(self.queue.items),
            "delivered": frozenset(self.dispatcher.delivered),
            "failed": frozenset(self.failures.failed),
            "ledger": frozenset(self.journal.entries),
        }


def _argument(case: Any, gained: str, lost: str | None = None) -> str | None:
    """The item this transition acted on. See ORACLE LEAKAGE above."""
    added = set(case.after[gained]) - set(case.before[gained])
    if len(added) == 1:
        return next(iter(added))
    if lost is not None:
        removed = set(case.before[lost]) - set(case.after[lost])
        if len(removed) == 1:
            return next(iter(removed))
    return None


class _PipelineAdapter:
    action: str = ""
    _store: object | None = None

    def setup(self, context: Any) -> None:
        """Bind the LedgerStorePort effect when the action declares one."""
        effects = getattr(context, "effects", None) or {}
        self._store = effects.get("LedgerStorePort")

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        harness = _Harness(case.before, self._store)
        item = self.select(case)
        applied = False if item is None else self.apply(harness, item)
        after = harness.project()
        return CaseRunResult(
            output={
                "action": self.action,
                "status": "applied" if applied else "rejected",
                "ledger_size": len(after["ledger"]),
                "queue_size": len(after["queue"]),
                "delivered_size": len(after["delivered"]),
            },
            after={name: sorted(value) for name, value in after.items()},
        )

    def select(self, case: Any) -> str | None:
        raise NotImplementedError

    def apply(self, harness: _Harness, item: str) -> bool:
        raise NotImplementedError


class AcceptAdapter(_PipelineAdapter):
    action = "Accept"

    def select(self, case: Any) -> str | None:
        return _argument(case, "accepted", "inbox")

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.inbox.accept(item)


class EnqueueAdapter(_PipelineAdapter):
    action = "Enqueue"

    def select(self, case: Any) -> str | None:
        return _argument(case, "queue")

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.queue.enqueue(item)


class DeliverAdapter(_PipelineAdapter):
    action = "Deliver"

    def select(self, case: Any) -> str | None:
        return _argument(case, "delivered", "queue")

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.dispatcher.deliver(item, harness.failures.failed)


class FailAdapter(_PipelineAdapter):
    action = "Fail"

    def select(self, case: Any) -> str | None:
        return _argument(case, "failed", "delivered")

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.failures.fail(item)


class RecordAdapter(_PipelineAdapter):
    action = "Record"

    def select(self, case: Any) -> str | None:
        return _argument(case, "ledger")

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.journal.record(item)
