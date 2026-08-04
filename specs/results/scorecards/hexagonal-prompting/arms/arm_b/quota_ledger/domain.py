"""The rules of the quota ledger.

This module is the domain. It holds no path, no file handle, no clock, no
environment and no global, and it imports nothing that touches any of them --
in particular it does not import the modules that implement its one port. What
it does is a function of what it was constructed with and what it is told.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


class CommitJournal(Protocol):
    """Driven port: the durable, append-only record of what was committed.

    Declared here, in the domain's vocabulary, and named for the need -- a
    record that outlives the run and can be read back in the order it was
    written -- rather than for whatever satisfies it. The domain renders the
    line; the port's whole job is durability and order.
    """

    def append(self, line: str) -> None:
        """Add one line to the end of the record. Never rewrites or reorders."""

    def lines(self) -> list[str]:
        """The record's lines, in the order written, no blanks."""


@dataclass(frozen=True)
class Result:
    """What every command returns."""

    status: str
    reason: str | None = None
    reservation_id: str | None = None


def _accepted(reservation_id: str | None = None) -> Result:
    return Result(status="accepted", reservation_id=reservation_id)


def _rejected(reason: str) -> Result:
    return Result(status="rejected", reason=reason)


@dataclass(frozen=True)
class _Reservation:
    """A live hold. `number` is what "ascending" means for ids."""

    number: int
    tenant: str
    amount: int


class ReservationBook:
    """Reservations held against a per-tenant quota, committed to a journal.

    Constructed with the quotas and with *some* CommitJournal. Which one is
    somebody else's decision; see the package's __init__.
    """

    def __init__(self, quotas: Mapping[str, int], journal: CommitJournal) -> None:
        self._quota = dict(quotas)
        self._journal = journal
        self._committed = {tenant: 0 for tenant in self._quota}
        self._closed: set[str] = set()
        self._outstanding: dict[str, _Reservation] = {}
        self._issued = 0

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        """Quota not currently held or committed.

        Derived, not stored: R1 is then arithmetic rather than an invariant
        four commands have to remember to maintain.
        """
        return self._quota[tenant] - self._committed[tenant] - self._held(tenant)

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return tenant in self._closed

    def outstanding_ids(self) -> list[str]:
        return [
            reservation_id
            for reservation_id, _ in sorted(
                self._outstanding.items(), key=lambda item: item[1].number
            )
        ]

    def ledger_lines(self) -> list[str]:
        return self._journal.lines()

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quota:
            return _rejected("unknown_tenant")
        if tenant in self._closed:
            return _rejected("tenant_closed")
        if amount < 1:
            return _rejected("amount_not_positive")
        if amount > self.available(tenant):
            return _rejected("quota_exceeded")

        self._issued += 1
        reservation_id = f"r{self._issued}"
        self._outstanding[reservation_id] = _Reservation(
            number=self._issued, tenant=tenant, amount=amount
        )
        return _accepted(reservation_id)

    def commit(self, reservation_id: str) -> Result:
        held = self._outstanding.pop(reservation_id, None)
        if held is None:
            return _rejected("unknown_reservation")

        total = self._committed[held.tenant] + held.amount
        self._committed[held.tenant] = total
        self._journal.append(f"COMMIT {held.tenant} {held.amount} {total}")
        return _accepted(reservation_id)

    def release(self, reservation_id: str) -> Result:
        if self._outstanding.pop(reservation_id, None) is None:
            return _rejected("unknown_reservation")
        # The amount comes back to `available` by ceasing to be held; there is
        # no second number to put it back into.
        return _accepted(reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quota:
            return _rejected("unknown_tenant")
        if tenant in self._closed:
            return _rejected("tenant_closed")
        if self._held(tenant):
            return _rejected("outstanding_reservations")

        self._closed.add(tenant)
        self._journal.append(f"CLOSE {tenant} {self._committed[tenant]}")
        return _accepted()

    # -- internals ---------------------------------------------------------

    def _held(self, tenant: str) -> int:
        return sum(
            reservation.amount
            for reservation in self._outstanding.values()
            if reservation.tenant == tenant
        )
