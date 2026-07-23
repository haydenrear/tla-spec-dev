#!/usr/bin/env python3
"""Small process boundary backed by file-persisted queue and outbox state."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from app import PermanentAddressError, ReminderWorker, RetryableTransportError


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


class JsonState:
    def __init__(self, root: Path, scenario: str) -> None:
        self.path = root / "state.json"
        root.mkdir(parents=True, exist_ok=True)
        queue = "empty" if scenario == "empty" else "ready"
        outbox = "sent" if scenario == "duplicate" else "pending" if scenario == "pending" else "none"
        receipt = "receipt-cli" if scenario == "duplicate" else None
        self.value: dict[str, Any] = {
            "scenario": scenario,
            "queue": queue,
            "outbox": outbox,
            "receipt": receipt,
            "notifications": 0,
            "journal": [],
        }
        self.flush()

    def event(self, name: str) -> None:
        self.value["journal"].append(name)
        self.flush()

    def flush(self) -> None:
        self.path.write_text(
            json.dumps(self.value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class CliClock:
    def __init__(self, state: JsonState) -> None:
        self.state = state

    def now(self, _command: Any) -> int:
        self.state.event("clock.now")
        return 100


class FileQueue:
    def __init__(self, state: JsonState, job: Job) -> None:
        self.state = state
        self.job = job

    def claim(self, _command: Any) -> Job | None:
        self.state.event("queue.claim")
        if self.state.value["queue"] == "empty":
            return None
        self.state.value["queue"] = "claimed"
        self.state.flush()
        return self.job

    def _mutate(self, command: Any, event: str, value: str) -> None:
        if command.job_id != self.job.job_id:
            raise AssertionError("queue command used the wrong job id")
        self.state.event(event)
        self.state.value["queue"] = value
        self.state.flush()

    def acknowledge(self, command: Any) -> None:
        self._mutate(command, "queue.ack", "acked")

    def release(self, command: Any) -> None:
        self._mutate(command, "queue.release", "ready")

    def dead_letter(self, command: Any) -> None:
        self._mutate(command, "queue.dead_letter", "dead")


class FileOutbox:
    def __init__(self, state: JsonState, job: Job) -> None:
        self.state = state
        self.job = job

    def lookup(self, command: Any) -> Entry | None:
        if command.job_id != self.job.job_id:
            raise AssertionError("outbox lookup used the wrong job id")
        self.state.event("outbox.lookup")
        if self.state.value["outbox"] == "none":
            return None
        return Entry(
            sent=self.state.value["outbox"] == "sent",
            receipt=self.state.value["receipt"],
        )

    def stage(self, command: Any) -> None:
        expected = asdict(self.job)
        for field in ("job_id", "recipient", "body", "idempotency_key"):
            if getattr(command, field) != expected[field]:
                raise AssertionError(f"staged {field} differs from claimed job")
        self.state.event("outbox.stage")
        self.state.value["outbox"] = "pending"
        self.state.flush()

    def mark_sent(self, command: Any) -> None:
        if command.job_id != self.job.job_id:
            raise AssertionError("mark-sent used the wrong job id")
        self.state.event("outbox.mark_sent")
        self.state.value["outbox"] = "sent"
        self.state.value["receipt"] = command.receipt
        self.state.flush()


class CliNotifier:
    def __init__(self, state: JsonState, job: Job) -> None:
        self.state = state
        self.job = job

    def send(self, command: Any) -> str:
        actual = (command.recipient, command.body, command.idempotency_key)
        expected = (self.job.recipient, self.job.body, self.job.idempotency_key)
        if actual != expected:
            raise AssertionError("notification command differs from claimed job")
        self.state.event("notifier.send")
        self.state.value["notifications"] += 1
        self.state.flush()
        if self.state.value["scenario"] == "retryable":
            raise RetryableTransportError("CLI retryable outcome")
        if self.state.value["scenario"] == "permanent":
            raise PermanentAddressError("CLI permanent outcome")
        return "receipt-cli"


def projected_state(state: JsonState, status: str) -> dict[str, Any]:
    receipt_state = "none"
    if state.value["outbox"] == "sent":
        receipt_state = "stored" if state.value["receipt"] == "receipt-cli" else "invalid"
    return {
        "scenario": state.value["scenario"],
        "queueState": state.value["queue"],
        "outboxState": state.value["outbox"],
        "notificationCount": state.value["notifications"],
        "receiptState": receipt_state,
        "result": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    state = JsonState(args.root, args.scenario)
    job = Job(
        job_id="job-cli-café",
        recipient="cli@example.test",
        body="Reminder from CLI 🚀",
        idempotency_key="idem-cli",
        due_at=101 if args.scenario == "not_due" else 100,
    )
    worker = ReminderWorker(
        CliClock(state),
        FileQueue(state, job),
        FileOutbox(state, job),
        CliNotifier(state, job),
    )
    output = worker.run_once()
    args.result.write_text(
        json.dumps(
            {
                "output": output,
                "after": projected_state(state, output["status"]),
                "journal": state.value["journal"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
