"""A small worker designed around four explicit effect ports."""

from __future__ import annotations

from reminder_contract.ports import ClockPort, NotifierPort, OutboxPort, QueuePort
from reminder_contract.types import (
    ClaimJob,
    LookupOutbox,
    MarkSent,
    QueueMutation,
    ReadClock,
    SendMessage,
    StageMessage,
)


class RetryableNotificationError(RuntimeError):
    pass


class PermanentNotificationError(RuntimeError):
    pass


class RetryableTransportError(RetryableNotificationError):
    pass


class RetryableThrottleError(RetryableNotificationError):
    pass


class PermanentAddressError(PermanentNotificationError):
    pass


class PermanentPolicyError(PermanentNotificationError):
    pass


class ReminderWorker:
    def __init__(
        self,
        clock: ClockPort,
        queue: QueuePort,
        outbox: OutboxPort,
        notifier: NotifierPort,
    ) -> None:
        self.clock = clock
        self.queue = queue
        self.outbox = outbox
        self.notifier = notifier

    def run_once(self, mutant: str | None = None) -> dict[str, str]:
        job = self.queue.claim(ClaimJob())
        if job is None:
            return {"status": "empty"}

        now = self.clock.now(ReadClock())
        if mutant == "RW-07":
            self.clock.now(ReadClock())
        not_due = now < job.due_at or (mutant == "RW-06" and now <= job.due_at)
        if not_due:
            self.queue.release(QueueMutation(job_id=job.job_id))
            return {"status": "not_due"}

        entry = self.outbox.lookup(LookupOutbox(job_id=job.job_id))
        if entry is not None and entry.sent:
            if mutant == "RW-05":
                self.notifier.send(
                    SendMessage(
                        recipient=job.recipient,
                        body=job.body,
                        idempotency_key=job.idempotency_key,
                    )
                )
            self.queue.acknowledge(QueueMutation(job_id=job.job_id))
            return {"status": "duplicate"}

        stage = StageMessage(
            job_id=job.job_id,
            recipient=job.recipient,
            body=job.body,
            idempotency_key=job.idempotency_key,
        )
        send = SendMessage(
            recipient=(job.recipient + "-wrong") if mutant == "RW-08" else job.recipient,
            body=(job.body + "!") if mutant == "RW-09" else job.body,
            idempotency_key=job.job_id if mutant == "RW-10" else job.idempotency_key,
        )

        staged_now = entry is None
        if staged_now and mutant != "RW-01":
            self.outbox.stage(stage)

        if mutant == "RW-02":
            self.outbox.mark_sent(MarkSent(job_id=job.job_id, receipt="premature"))
            self.queue.acknowledge(QueueMutation(job_id=job.job_id))

        try:
            receipt = self.notifier.send(send)
            if staged_now and mutant == "RW-01":
                self.outbox.stage(stage)
        except RetryableNotificationError:
            if mutant == "RW-03":
                self.queue.acknowledge(QueueMutation(job_id=job.job_id))
            elif mutant != "RW-04":
                self.queue.release(QueueMutation(job_id=job.job_id))
            return {"status": "retryable"}
        except PermanentNotificationError:
            if mutant == "RW-12":
                self.queue.release(QueueMutation(job_id=job.job_id))
                return {"status": "retryable"}
            self.queue.dead_letter(QueueMutation(job_id=job.job_id))
            return {"status": "permanent"}

        if mutant != "RW-02":
            stored_receipt = job.job_id if mutant == "RW-11" else receipt
            self.outbox.mark_sent(MarkSent(job_id=job.job_id, receipt=stored_receipt))
            self.queue.acknowledge(QueueMutation(job_id=job.job_id))
        return {"status": "accepted"}
