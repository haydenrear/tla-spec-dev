"""The rules of the quota ledger, with the durable side behind a port.

THIS IS NOT AN ARM. Neither is `../reference/`. See `README.md` in this
directory for why a second reference tree exists at all; the short form is that
`../reference/quota_ledger.py` has no adapter, and a catalogue cannot seed a
fault INSIDE an adapter implementation in a tree that contains none.

The behavior here is the behavior of `../reference/quota_ledger.py`, statement
for statement, and the shared suite
(`examples/validation/ab/tests/test_behavior.py`) is the thing that says so.
Nothing about the feature changed; the ledger file moved behind an interface
the domain declares.

This module is the domain. It holds no path, no file handle, no clock, no
environment and no global, and **it does not import the modules that implement
its port**. `journal_file` and `journal_memory` are imported by the composition
points (`quota_ledger.py`, `quota_ledger_fake.py`) and by nothing else here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

#: The complete rejection vocabulary, unchanged from the flat reference. A
#: guard that refuses for a reason outside this set is as much a defect as a
#: guard that does not refuse at all.
REJECTION_REASONS = (
    "unknown_tenant",
    "tenant_closed",
    "amount_not_positive",
    "quota_exceeded",
    "unknown_reservation",
    "outstanding_reservations",
)


class LedgerJournal(Protocol):
    """Driven port: the durable, append-only record of what was committed.

    Declared here, in the domain's vocabulary, and named for the need -- a
    record that outlives the run and reads back in the order it was written --
    rather than for whatever satisfies it. The domain renders the line; the
    port's whole job is durability and order.

    This is the boundary the catalogue calls `LedgerAppendPort`. Two
    implementations satisfy it, `journal_file.FileJournal` and
    `journal_memory.InMemoryJournal`, and the point of having both is that the
    SAME cases run against both: a fault in either one has somewhere to be
    seen. Before this tree existed there was exactly one implementation and a
    fault inside it was indistinguishable from a fault in the domain.
    """

    def append(self, line: str) -> None:
        """Add one line to the end of the record. Never rewrites or reorders."""

    def lines(self) -> list[str]:
        """The record's lines, in the order written, no blanks."""


@dataclass(frozen=True)
class Result:
    """Every command returns one of these. `status` is the output oracle."""

    status: str
    reason: str | None = None
    reservation_id: str | None = None

    @staticmethod
    def accepted(reservation_id: str | None = None) -> "Result":
        return Result(status="accepted", reservation_id=reservation_id)

    @staticmethod
    def rejected(reason: str) -> "Result":
        return Result(status="rejected", reason=reason)


@dataclass(frozen=True)
class Reservation:
    id: str
    tenant: str
    amount: int


class ReservationBook:
    """Reservations held against a per-tenant quota, committed to a journal.

    Two aspects, the same two the flat reference names, because the eval slices
    on them:

      RESERVATIONS  _available, _outstanding, _closed
      LEDGER        _committed, and whatever is behind the port

    `commit` and `close_tenant` are the cross-aspect actions: their guards read
    the RESERVATIONS aspect and their effects write the LEDGER aspect.

    Constructed with the quotas and with *some* LedgerJournal. Which one is not
    this module's business and is not knowable from this file.
    """

    def __init__(self, quotas: Mapping[str, int], journal: LedgerJournal) -> None:
        self._quota = dict(quotas)
        self._available = dict(quotas)
        self._committed = {tenant: 0 for tenant in quotas}
        self._closed: set[str] = set()
        self._outstanding: dict[str, Reservation] = {}
        self._next_id = 1
        self._journal = journal

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._available[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return tenant in self._closed

    def outstanding_ids(self) -> list[str]:
        return sorted(self._outstanding)

    def ledger_lines(self) -> list[str]:
        return self._journal.lines()

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quota:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if amount < 1:
            return Result.rejected("amount_not_positive")
        if amount > self._available[tenant]:
            return Result.rejected("quota_exceeded")
        reservation_id = f"r{self._next_id}"
        self._next_id += 1
        self._available[tenant] -= amount
        self._outstanding[reservation_id] = Reservation(reservation_id, tenant, amount)
        return Result.accepted(reservation_id)

    def commit(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return Result.rejected("unknown_reservation")
        del self._outstanding[reservation_id]
        self._committed[reservation.tenant] += reservation.amount
        self._journal.append(
            f"COMMIT {reservation.tenant} {reservation.amount} "
            f"{self._committed[reservation.tenant]}"
        )
        return Result.accepted(reservation_id)

    def release(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return Result.rejected("unknown_reservation")
        del self._outstanding[reservation_id]
        self._available[reservation.tenant] += reservation.amount
        return Result.accepted(reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quota:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if any(held.tenant == tenant for held in self._outstanding.values()):
            return Result.rejected("outstanding_reservations")
        self._closed.add(tenant)
        self._journal.append(f"CLOSE {tenant} {self._committed[tenant]}")
        return Result.accepted()
