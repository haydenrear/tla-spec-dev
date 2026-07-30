"""Spec-unit adapters for the EV-01 decomposable fixture.

One adapter per model action. Each MATERIALIZEs `case.before` into the real
production objects, EXECUTEs the action, and PROJECTs the real objects back
into the six model variables. The generated-case runner does the COMPARE.

THE ADAPTER TAKES ITS ARGUMENT FROM THE CASE (RP-02, closing EV-01-DF-01).
It used to take it from `case.after` -- it diffed the before-state against the
after-state to work out which item to act on, because `infer_action_params.py`
recovered **0 of 5** parameters on this model and every case arrived carrying
`params={'i': UNCHECKED}`. That was ORACLE LEAKAGE: the answer key was handing
the adapter its input at execution time, in a place no audit looked.

RP-02 added the `set-membership` mechanism to the generator -- for an action
whose body is `v' = v \\cup {i}` or `v' = v \\ {i}`, the argument is the element
that entered or left the set, cross-checked across every such conjunct. All
five parameters now recover, and the corpus carries the argument as data. So
this adapter reads `case.input.params['i']` and never looks at `case.after`.

WHAT THAT DOES AND DOES NOT BUY, so a silence is not read as a result. The
argument is now fixed in the artifact, audited, and identical on every replay,
and `case.after` is untouched by the execution path. It does NOT make the
argument independent of the after-state -- an existentially quantified `i` is
genuinely underdetermined by the before-state alone, and the generator
recovered it from the state PAIR. What is no longer independently checkable is
exactly "which element moved in the source sets", and the generated audit says
so per action under `Observations the recovery consumed`.

An UNCHECKED argument is a hard failure here, not a shrug: a case that cannot
say what to call the action with must not be silently executed as a no-op.
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


def _argument(case: Any) -> str:
    """The item this transition acts on, as the CASE ITSELF declares it.

    Reads `case.input.params`, which the generator recovered from the model's
    own `\\cup` / `\\` conjuncts. `case.after` is not consulted, and neither is
    `case.before`.

    A parameter the generator could not recover arrives as the `UNCHECKED`
    sentinel, which is not a `str`. That is a HARD FAILURE and not a fallback:
    an adapter that quietly degraded to a no-op would report a green case for a
    transition it never executed, which is the vacuous pass this whole fixture
    exists to make impossible.
    """
    params = getattr(getattr(case, "input", None), "params", None) or {}
    item = params.get("i")
    if not isinstance(item, str):
        raise AssertionError(
            f"{getattr(case, 'name', '<case>')}: no usable argument for `i` "
            f"(got {item!r}). The case does not state which item to act on; see "
            f"param_recovery_audit.md in the generated package for why."
        )
    return item


class _PipelineAdapter:
    action: str = ""
    _store: object | None = None

    def setup(self, context: Any) -> None:
        """Bind the LedgerStorePort effect when the action declares one."""
        effects = getattr(context, "effects", None) or {}
        self._store = effects.get("LedgerStorePort")

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        harness = _Harness(case.before, self._store)
        item = _argument(case)
        applied = self.apply(harness, item)
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

    def apply(self, harness: _Harness, item: str) -> bool:
        raise NotImplementedError


class AcceptAdapter(_PipelineAdapter):
    action = "Accept"

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.inbox.accept(item)


class EnqueueAdapter(_PipelineAdapter):
    action = "Enqueue"

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.queue.enqueue(item)


class DeliverAdapter(_PipelineAdapter):
    action = "Deliver"

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.dispatcher.deliver(item, harness.failures.failed)


class FailAdapter(_PipelineAdapter):
    action = "Fail"

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.failures.fail(item)


class RecordAdapter(_PipelineAdapter):
    action = "Record"

    def apply(self, harness: _Harness, item: str) -> bool:
        return harness.journal.record(item)
