"""Generated-case adapter for the real reminder worker application."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any

from app import ReminderWorker
from spec_double_compiler.runtime import CaseRunResult


class ReminderAdapter:
    def setup(self, context: Any) -> None:
        self.started_at = time.perf_counter()
        self.clock = context.effects["ClockPort"]
        self.queue = context.effects["QueuePort"]
        self.outbox = context.effects["OutboxPort"]
        self.notifier = context.effects["NotifierPort"]
        states = {id(binding.state): binding.state for binding in context.effects.values()}
        if len(states) != 1:
            raise AssertionError("DETECTOR[shared_journal] providers did not share one point state")
        self.state = next(iter(states.values()))
        self.error: BaseException | None = None

    def run(self, _case: Any, work_dir: Path | None = None) -> CaseRunResult:
        mutant = os.environ.get("REMINDER_MUTANT") or None
        worker = ReminderWorker(self.clock, self.queue, self.outbox, self.notifier)
        try:
            output = worker.run_once(mutant)
            self.state.result = output["status"]
            self.state.assert_semantic_order()
            return CaseRunResult(
                output=output,
                after=self.state.snapshot(output["status"]),
            )
        except BaseException as exc:
            self.error = exc
            raise

    def teardown(self, _context: Any) -> None:
        trace_path = os.environ.get("REMINDER_TRACE_LOG")
        if not trace_path:
            return
        record = self.state.trace_record(
            os.environ.get("REMINDER_MUTANT") or None,
            self.error,
            (time.perf_counter() - self.started_at) * 1000,
        )
        with Path(trace_path).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
