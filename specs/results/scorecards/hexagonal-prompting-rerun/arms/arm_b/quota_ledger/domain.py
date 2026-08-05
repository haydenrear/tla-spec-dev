"""The rules of the quota ledger.

This module is the domain. It holds no file handle, no path, no clock, no
environment, no network, no global, and it imports nothing that touches any of
them -- only the standard library's typing and dataclass helpers.

The one thing outside itself that the rules need is a durable, append-only
record of what has been committed and closed. That need is declared here, as
the `Journal` port, in the domain's own vocabulary. The domain never builds a
Journal; one is handed to it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


# -- the driven port -------------------------------------------------------


class Journal(Protocol):
    """A durable, append-only sequence of records.

    The rules need exactly two things from the outside world: to add one
    record to the end of a permanent sequence, and to read the sequence back
    in the order it was written. Anything that can do those two things is a
    Journal -- a file, a list, a table.

    Contract, binding on every implementation:

    * `append` puts one record at the end. It never rewrites, reorders or
      removes an existing record.
    * `records` returns every record appended so far, in append order, and
      nothing else -- no blanks, no framing, no partial records.
    * a Journal that has had nothing appended returns no records.
    * the list `records` returns belongs to the caller; mutating it does not
      disturb the journal.
    """

    def append(self, record: str) -> None: ...

    def records(self) -> list[str]: ...


# -- the domain's answers --------------------------------------------------

REJECTION_REASONS = frozenset(
    {
        "unknown_tenant",
        "tenant_closed",
        "amount_not_positive",
        "quota_exceeded",
        "unknown_reservation",
        "outstanding_reservations",
    }
)


@dataclass(frozen=True)
class Result:
    """What every command returns."""

    status: str
    reason: str | None = None
    reservation_id: str | None = None

    @staticmethod
    def accepted(reservation_id: str | None = None) -> "Result":
        return Result(status="accepted", reservation_id=reservation_id)

    @staticmethod
    def rejected(reason: str) -> "Result":
        assert reason in REJECTION_REASONS, reason
        return Result(status="rejected", reason=reason)


@dataclass(frozen=True)
class Reservation:
    tenant: str
    amount: int


# -- the rules -------------------------------------------------------------


class Ledger:
    """Reservations held against a per-tenant quota, committed to a Journal.

    Only three pieces of state are written, and each has one writer's worth of
    meaning:

    * `_outstanding` -- the live reservations. Written by reserve (add) and by
      commit and release (remove).
    * `_committed` -- the per-tenant committed total. Written by commit alone.
    * `_closed` -- the closed tenants. Written by close_tenant alone.

    `available` is deliberately *not* stored. It is quota minus what is held
    minus what is committed, computed on demand, so R1 (conservation) is true
    by construction rather than by three operations remembering to maintain it.
    That is also why commit does not change `available`: commit moves an amount
    out of `_outstanding` and into `_committed`, and the subtraction does not
    notice.
    """

    def __init__(self, quotas: Mapping[str, int], journal: Journal) -> None:
        self._quota: dict[str, int] = dict(quotas)
        self._committed: dict[str, int] = {tenant: 0 for tenant in self._quota}
        self._closed: set[str] = set()
        # Insertion-ordered, and ids are allocated ascending and never reused,
        # so iterating this dict yields the outstanding ids in ascending order.
        self._outstanding: dict[str, Reservation] = {}
        self._issued = 0
        self._journal = journal

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        """The quota not currently held or committed."""
        return self._quota[tenant] - self._held(tenant) - self._committed[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return tenant in self._closed

    def outstanding_ids(self) -> list[str]:
        return list(self._outstanding)

    def ledger_lines(self) -> list[str]:
        return self._journal.records()

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quota:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if amount < 1:
            return Result.rejected("amount_not_positive")
        if amount > self.available(tenant):
            return Result.rejected("quota_exceeded")

        self._issued += 1
        reservation_id = f"r{self._issued}"
        self._outstanding[reservation_id] = Reservation(tenant, amount)
        return Result.accepted(reservation_id=reservation_id)

    def commit(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return Result.rejected("unknown_reservation")

        del self._outstanding[reservation_id]
        total = self._committed[reservation.tenant] + reservation.amount
        self._committed[reservation.tenant] = total
        self._journal.append(f"COMMIT {reservation.tenant} {reservation.amount} {total}")
        return Result.accepted()

    def release(self, reservation_id: str) -> Result:
        if reservation_id not in self._outstanding:
            return Result.rejected("unknown_reservation")

        # Dropping the reservation returns the amount to `available`, because
        # `available` is derived from what is still held. Nothing durable
        # happens: a release leaves no trace in the journal.
        del self._outstanding[reservation_id]
        return Result.accepted()

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quota:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if self._holdings(tenant):
            return Result.rejected("outstanding_reservations")

        self._closed.add(tenant)
        self._journal.append(f"CLOSE {tenant} {self._committed[tenant]}")
        return Result.accepted()

    # -- internals ---------------------------------------------------------

    def _holdings(self, tenant: str) -> list[Reservation]:
        """The one place that knows which reservations belong to a tenant."""
        return [held for held in self._outstanding.values() if held.tenant == tenant]

    def _held(self, tenant: str) -> int:
        return sum(held.amount for held in self._holdings(tenant))
