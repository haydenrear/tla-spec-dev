"""Four point-local providers sharing one immutable bundle and journal."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import random
from typing import Any

from app import (
    PermanentAddressError,
    PermanentPolicyError,
    RetryableThrottleError,
    RetryableTransportError,
)
from spec_double_compiler.effects import derive_effect_seed


class DetectorFailure(AssertionError):
    def __init__(self, detector: str, message: str) -> None:
        super().__init__(f"DETECTOR[{detector}] {message}")
        self.detector = detector


@dataclass(frozen=True)
class Job:
    job_id: str
    recipient: str
    body: str
    idempotency_key: str
    due_at: int


@dataclass(frozen=True)
class Entry:
    sent: bool
    receipt: str | None


@dataclass(frozen=True)
class Bundle:
    scenario: str
    concretization_seed: int
    now: int
    job: Job
    receipt: str
    exception_kind: str
    exception_variant: int
    due_offset: int

    @classmethod
    def from_context(cls, context: Any) -> "Bundle":
        scenario = str(dict(context.case.before)["scenario"])
        seed = derive_effect_seed(
            context.root_seed,
            str(context.case.name),
            context.iteration,
            "__reminder_bundle__",
        )
        rng = random.Random(seed)
        fragments = ["plain", "space value", "café", "λ-reminder", "emoji-🚀"]
        fragment = fragments[rng.randrange(len(fragments))]
        now = 1_700_000_000 + rng.randrange(10_000)
        due_offset = [1, 30, 3600][rng.randrange(3)] if scenario == "not_due" else 0
        due_at = now + due_offset
        job_id = f"job-{fragment}-{rng.randrange(10_000):04d}"
        return cls(
            scenario=scenario,
            concretization_seed=seed,
            now=now,
            job=Job(
                job_id=job_id,
                recipient=f"{fragment.replace(' ', '.')}@example.test",
                body=f"Reminder: {fragment}",
                idempotency_key=f"idem-{rng.randrange(1_000_000):06d}",
                due_at=due_at,
            ),
            receipt=f"receipt-{rng.randrange(1_000_000):06d}",
            exception_kind="retryable" if scenario == "retryable" else "permanent" if scenario == "permanent" else "none",
            exception_variant=rng.randrange(2),
            due_offset=due_offset,
        )


class PointState:
    def __init__(self, context: Any) -> None:
        self.case_name = str(context.case.name)
        self.action = str(context.action)
        self.iteration = int(context.iteration)
        self.root_seed = int(context.root_seed)
        self.bundle = Bundle.from_context(context)
        before = dict(context.case.before)
        self.queue_state = str(before["queueState"])
        self.outbox_state = str(before["outboxState"])
        self.receipt = self.bundle.receipt if before["receiptState"] == "stored" else None
        self.notification_count = int(before["notificationCount"])
        self.journal: list[str] = []
        self.clock_reads = 0
        self.bindings = 0
        self.result = str(before["result"])

    def event(self, value: str) -> None:
        self.journal.append(value)

    def assert_semantic_order(self) -> None:
        def position(event: str) -> int:
            try:
                return self.journal.index(event)
            except ValueError:
                return -1

        if self.action in {"ProcessAccepted", "ProcessRetryable", "ProcessPermanent"}:
            stage, send = position("outbox.stage"), position("notifier.send")
            if stage < 0 or send < 0 or stage > send:
                raise DetectorFailure("shared_journal", f"stage must precede send: {self.journal!r}")
        if self.action in {"ProcessAccepted", "ProcessPendingRetry"}:
            send, mark, ack = (
                position("notifier.send"),
                position("outbox.mark_sent"),
                position("queue.ack"),
            )
            if min(send, mark, ack) < 0 or not send < mark < ack:
                raise DetectorFailure("shared_journal", f"send < mark < ack required: {self.journal!r}")

    def snapshot(self, result: str) -> dict[str, Any]:
        receipt_state = "none"
        if self.outbox_state == "sent":
            receipt_state = "stored" if self.receipt == self.bundle.receipt else "invalid"
        return {
            "scenario": self.bundle.scenario,
            "queueState": self.queue_state,
            "outboxState": self.outbox_state,
            "notificationCount": self.notification_count,
            "receiptState": receipt_state,
            "result": result,
        }

    def trace_record(
        self,
        mutant: str | None,
        error: BaseException | None,
        duration_ms: float,
    ) -> dict[str, Any]:
        payload = {
            "case": self.case_name,
            "action": self.action,
            "iteration": self.iteration,
            "root_seed": self.root_seed,
            "mutant": mutant,
            "bundle": asdict(self.bundle),
            "journal": list(self.journal),
            "snapshot": self.snapshot(self.result),
            "error": None if error is None else f"{type(error).__name__}: {error}",
        }
        payload["digest"] = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        payload["duration_ms"] = round(duration_ms, 6)
        return payload


_POINTS: dict[tuple[str, int, int, str], PointState] = {}


def _point_key(context: Any) -> tuple[str, int, int, str]:
    return (
        str(context.case.name),
        int(context.iteration),
        int(context.root_seed),
        str(Path(context.work_dir).resolve()),
    )


class _Scope:
    def __init__(self, context: Any, binding_type: type[Any]) -> None:
        self.context = context
        self.binding_type = binding_type
        self.key = _point_key(context)
        self.state: PointState | None = None

    def __enter__(self) -> Any:
        state = _POINTS.get(self.key)
        if state is None:
            state = PointState(self.context)
            _POINTS[self.key] = state
        state.bindings += 1
        self.state = state
        return self.binding_type(state)

    def __exit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> bool:
        assert self.state is not None
        self.state.bindings -= 1
        if self.state.bindings == 0:
            del _POINTS[self.key]
            cleanup_path = os.environ.get("REMINDER_CLEANUP_LOG")
            if cleanup_path:
                record = {
                    "case": self.state.case_name,
                    "iteration": self.state.iteration,
                    "registry_empty": not _POINTS,
                }
                with Path(cleanup_path).open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
        return False


class _Provider:
    def __init__(self, binding_type: type[Any]) -> None:
        self.binding_type = binding_type

    def bind(self, context: Any) -> _Scope:
        return _Scope(context, self.binding_type)


class ClockBinding:
    def __init__(self, state: PointState) -> None:
        self.state = state

    def now(self, _command: Any) -> int:
        self.state.clock_reads += 1
        self.state.event("clock.now")
        if self.state.clock_reads > 1:
            raise DetectorFailure("provider_local_assertion", "clock read more than once")
        return self.state.bundle.now


class QueueBinding:
    def __init__(self, state: PointState) -> None:
        self.state = state

    def claim(self, _command: Any) -> Job | None:
        self.state.event("queue.claim")
        if self.state.queue_state == "empty":
            return None
        self.state.queue_state = "claimed"
        return self.state.bundle.job

    def _check(self, command: Any) -> None:
        if command.job_id != self.state.bundle.job.job_id:
            raise DetectorFailure("provider_local_assertion", "queue job id mismatch")

    def acknowledge(self, command: Any) -> None:
        self._check(command)
        self.state.event("queue.ack")
        self.state.queue_state = "acked"

    def release(self, command: Any) -> None:
        self._check(command)
        self.state.event("queue.release")
        self.state.queue_state = "ready"

    def dead_letter(self, command: Any) -> None:
        self._check(command)
        self.state.event("queue.dead_letter")
        self.state.queue_state = "dead"


class OutboxBinding:
    def __init__(self, state: PointState) -> None:
        self.state = state

    def lookup(self, command: Any) -> Entry | None:
        if command.job_id != self.state.bundle.job.job_id:
            raise DetectorFailure("provider_local_assertion", "outbox lookup id mismatch")
        self.state.event("outbox.lookup")
        if self.state.outbox_state == "none":
            return None
        return Entry(sent=self.state.outbox_state == "sent", receipt=self.state.receipt)

    def stage(self, command: Any) -> None:
        expected = self.state.bundle.job
        actual = (command.job_id, command.recipient, command.body, command.idempotency_key)
        wanted = (expected.job_id, expected.recipient, expected.body, expected.idempotency_key)
        if actual != wanted:
            raise DetectorFailure("provider_local_assertion", f"staged message mismatch: {actual!r}")
        self.state.event("outbox.stage")
        self.state.outbox_state = "pending"

    def mark_sent(self, command: Any) -> None:
        if command.job_id != self.state.bundle.job.job_id:
            raise DetectorFailure("provider_local_assertion", "mark-sent job id mismatch")
        self.state.event("outbox.mark_sent")
        self.state.outbox_state = "sent"
        self.state.receipt = command.receipt


class NotifierBinding:
    def __init__(self, state: PointState) -> None:
        self.state = state

    def send(self, command: Any) -> str:
        expected = self.state.bundle.job
        if self.state.bundle.scenario == "duplicate":
            raise DetectorFailure("provider_local_assertion", "duplicate notification send")
        actual = (command.recipient, command.body, command.idempotency_key)
        wanted = (expected.recipient, expected.body, expected.idempotency_key)
        if actual != wanted:
            raise DetectorFailure("provider_local_assertion", f"notification payload mismatch: {actual!r}")
        self.state.event("notifier.send")
        self.state.notification_count += 1
        if self.state.bundle.exception_kind == "retryable":
            error_type = (
                RetryableTransportError
                if self.state.bundle.exception_variant == 0
                else RetryableThrottleError
            )
            raise error_type("provider-selected retryable failure")
        if self.state.bundle.exception_kind == "permanent":
            error_type = (
                PermanentAddressError
                if self.state.bundle.exception_variant == 0
                else PermanentPolicyError
            )
            raise error_type("provider-selected permanent failure")
        return self.state.bundle.receipt


clock_provider = _Provider(ClockBinding)
queue_provider = _Provider(QueueBinding)
outbox_provider = _Provider(OutboxBinding)
notifier_provider = _Provider(NotifierBinding)


def active_point_count() -> int:
    return len(_POINTS)
