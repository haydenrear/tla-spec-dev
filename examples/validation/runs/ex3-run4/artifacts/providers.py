"""Agent-authored effect provider for AuditJournalPort.

The audit journal is OrderHub's one observable effect. The provider owns the
concrete journal representation; the generated case carries the modeled
outcome (the auditLog counter) as the oracle. Content assertions:

- ordering: entries must arrive with consecutive ``seq`` values continuing
  the modeled before-state count, and the operation name must match the
  case's action;
- count: at scope exit the journal must hold exactly ``after.auditLog``
  entries -- the modeled before count plus one per modeled increment.

Fuzz dimensions (deterministic from ``context.derived_seed``): the storage
encoding of entries (tuple / dict / formatted line) and the synthetic
operation names of the ``before.auditLog`` historical entries the provider
materializes. Representation varies; semantics may not.
"""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
from random import Random
from typing import Any

from order_hub_contract.types import RecordAuditEntry, RecordAuditResult

_ACTION_TO_OPERATION = {
    "PlaceOrder": "place_order",
    "ShipOrder": "ship_order",
    "RetrySweep": "retry_sweep",
    "AuditSweep": "audit_sweep",
}

_OPERATIONS = tuple(_ACTION_TO_OPERATION.values())

_ENCODINGS = ("tuple", "dict", "line")


class AuditJournalBinding:
    """In-memory audit journal implementing the generated AuditJournalPort."""

    def __init__(self, context: Any) -> None:
        self._context = context
        self._rng = Random(context.derived_seed)
        self._encoding = self._rng.choice(_ENCODINGS)
        self._entries: list[Any] = []
        # Materialize the modeled before-state: the journal already holds
        # before.auditLog historical entries with seq 1..N.
        before_count = int(context.case.before["auditLog"])
        for seq in range(1, before_count + 1):
            self._store(self._rng.choice(_OPERATIONS), seq)
        self._expected_operation = _ACTION_TO_OPERATION[str(context.case.input.action)]

    def _store(self, operation: str, seq: int) -> None:
        if self._encoding == "tuple":
            self._entries.append((seq, operation))
        elif self._encoding == "dict":
            self._entries.append({"seq": seq, "operation": operation})
        else:
            self._entries.append(f"{seq:04d} {operation}")

    def _decode(self, entry: Any) -> tuple[int, str]:
        if self._encoding == "tuple":
            return int(entry[0]), str(entry[1])
        if self._encoding == "dict":
            return int(entry["seq"]), str(entry["operation"])
        seq_text, operation = str(entry).split(" ", 1)
        return int(seq_text), operation

    def record(self, command: RecordAuditEntry) -> RecordAuditResult:
        expected_seq = len(self._entries) + 1
        if command.seq != expected_seq:
            raise AssertionError(
                f"audit ordering violated: entry arrived with seq={command.seq}, "
                f"journal expected consecutive seq={expected_seq}"
            )
        if command.operation != self._expected_operation:
            raise AssertionError(
                f"audit content violated: operation={command.operation!r} but the "
                f"modeled action {self._context.case.input.action} audits as "
                f"{self._expected_operation!r}"
            )
        self._store(command.operation, command.seq)
        return RecordAuditResult(recorded=True)

    def assert_complete(self) -> None:
        expected_total = int(self._context.case.after["auditLog"])
        actual_total = len(self._entries)
        if actual_total != expected_total:
            raise AssertionError(
                f"audit count violated: journal holds {actual_total} entries but the "
                f"modeled auditLog is {expected_total} "
                f"(before={self._context.case.before['auditLog']})"
            )
        decoded = [self._decode(entry) for entry in self._entries]
        seqs = [seq for seq, _ in decoded]
        if seqs != list(range(1, expected_total + 1)):
            raise AssertionError(f"audit ordering violated in stored journal: seqs={seqs}")


class AuditJournalProvider:
    @contextmanager
    def bind(self, context: Any) -> Iterator[Any]:
        binding = AuditJournalBinding(context)
        yield binding
        # Runs only when the application phase succeeded; a propagating
        # application failure is never masked by provider assertions.
        binding.assert_complete()


audit_journal_provider = AuditJournalProvider()
