"""Quota ledger: reservations held against a per-tenant quota, committed to a
durable append-only ledger file.

See examples/validation/ab/FEATURE.md. Names here follow the feature file's
vocabulary exactly (`available`, `committed`, `outstanding`, `reason`) because a
synonym is where a misunderstanding hides.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

# The six reasons named by the feature. R4 says a rejection reason is always one
# of these, so they are written down once rather than spelled at each call site.
UNKNOWN_TENANT = "unknown_tenant"
TENANT_CLOSED = "tenant_closed"
AMOUNT_NOT_POSITIVE = "amount_not_positive"
QUOTA_EXCEEDED = "quota_exceeded"
UNKNOWN_RESERVATION = "unknown_reservation"
OUTSTANDING_RESERVATIONS = "outstanding_reservations"


@dataclass(frozen=True)
class Result:
    """What every command returns.

    Frozen because a caller holding a result must not be able to edit the
    record of what happened.
    """

    status: str
    reason: str | None = None
    reservation_id: str | None = None


@dataclass(frozen=True)
class Reservation:
    tenant: str
    amount: int


def _accepted(reservation_id: str | None = None) -> Result:
    return Result(status="accepted", reservation_id=reservation_id)


def _rejected(reason: str) -> Result:
    return Result(status="rejected", reason=reason)


class QuotaLedger:
    def __init__(self, quotas: Mapping[str, int], ledger_path) -> None:
        self._quota = dict(quotas)
        self._committed = {tenant: 0 for tenant in self._quota}
        self._closed = {tenant: False for tenant in self._quota}
        # Insertion order is allocation order; `outstanding_ids` sorts anyway so
        # that r10 does not sort before r2.
        self._outstanding: dict[str, Reservation] = {}
        self._next_id = 1

        self._ledger_path = Path(ledger_path)
        # "The ledger file starts empty" — truncate rather than append to
        # whatever was there, so a reused path cannot make R2 false at line one.
        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._ledger_path.write_text("", encoding="utf-8")

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        # The held amount is read off the outstanding table, not kept as a second
        # running total: `outstanding` already says which reservations are live
        # and for how much, so a stored copy would be a second thing that has to
        # be right for R1 to hold.
        held = sum(r.amount for r in self._outstanding.values() if r.tenant == tenant)
        return self._quota[tenant] - held - self._committed[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return self._closed[tenant]

    def outstanding_ids(self) -> list[str]:
        # Ascending by allocation number, not by string: "r10" < "r2" as text.
        return sorted(self._outstanding, key=lambda rid: int(rid[1:]))

    def ledger_lines(self) -> list[str]:
        # Read the file rather than an in-memory mirror: R2 is a claim about the
        # durable side, and a mirror would make it true by construction.
        text = self._ledger_path.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if line]

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        # Order is fixed by the feature: an unknown tenant is reported as
        # unknown even when the amount is also bad.
        if tenant not in self._quota:
            return _rejected(UNKNOWN_TENANT)
        if self._closed[tenant]:
            return _rejected(TENANT_CLOSED)
        if amount < 1:
            return _rejected(AMOUNT_NOT_POSITIVE)
        if amount > self.available(tenant):
            return _rejected(QUOTA_EXCEEDED)

        reservation_id = f"r{self._next_id}"
        # Bumped on acceptance only, and never decremented: ids are never reused
        # even after the reservation leaves `outstanding`.
        self._next_id += 1
        self._outstanding[reservation_id] = Reservation(tenant, amount)
        return _accepted(reservation_id)

    def commit(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return _rejected(UNKNOWN_RESERVATION)

        del self._outstanding[reservation_id]
        # The hold becomes committed; `available` is unchanged because dropping
        # the reservation and adding to `committed` cancel in its arithmetic.
        self._committed[reservation.tenant] += reservation.amount
        self._append(
            f"COMMIT {reservation.tenant} {reservation.amount} "
            f"{self._committed[reservation.tenant]}"
        )
        return _accepted(reservation_id)

    def release(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return _rejected(UNKNOWN_RESERVATION)

        del self._outstanding[reservation_id]
        # No ledger write: a release is not a durable event.
        return _accepted(reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quota:
            return _rejected(UNKNOWN_TENANT)
        if self._closed[tenant]:
            return _rejected(TENANT_CLOSED)
        if any(r.tenant == tenant for r in self._outstanding.values()):
            # R3: a closed tenant has no outstanding reservations, so the check
            # has to happen before the write, not after.
            return _rejected(OUTSTANDING_RESERVATIONS)

        self._closed[tenant] = True
        self._append(f"CLOSE {tenant} {self._committed[tenant]}")
        return _accepted()

    # -- durable side ------------------------------------------------------

    def _append(self, line: str) -> None:
        # Append mode only, one line per accepting command: R5 forbids rewriting
        # or reordering, so there is no seek and no rewrite path in this class.
        with self._ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
