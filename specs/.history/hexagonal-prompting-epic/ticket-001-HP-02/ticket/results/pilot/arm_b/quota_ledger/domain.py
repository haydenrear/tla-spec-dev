"""The domain: reservations held against per-tenant quota, committed to a
durable ledger.

Holds no file handle, no path, no clock, no environment, no network, no
global. What it does is a function of what it was given (the quotas) and what
it was told (the `DurableLedger` port, and the sequence of commands called on
it). It does not import anything that implements that port.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .ports import DurableLedger

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
    """What every command returns. `reason` is set only when rejected;
    `reservation_id` is set only by an accepted `reserve`."""

    status: str
    reason: Optional[str] = None
    reservation_id: Optional[str] = None

    @classmethod
    def accepted(cls, reservation_id: Optional[str] = None) -> "Result":
        return cls(status="accepted", reservation_id=reservation_id)

    @classmethod
    def rejected(cls, reason: str) -> "Result":
        assert reason in REJECTION_REASONS, f"undeclared rejection reason: {reason!r}"
        return cls(status="rejected", reason=reason)


class QuotaBook:
    """The domain object. Depends only on the `DurableLedger` port -- never on
    a path, and never on the module that implements it.

    Deliberately not storing `available` as its own field: it is fully
    determined by quota, held, and committed, and a value that is only ever
    read back out of the other three is representation, not state. Storing it
    separately would be one more thing every command has to keep in step for
    no behavior anything reads.
    """

    def __init__(self, quotas: Dict[str, int], durable_ledger: DurableLedger):
        self._quotas: Dict[str, int] = dict(quotas)
        self._durable: DurableLedger = durable_ledger
        self._held: Dict[str, int] = {tenant: 0 for tenant in self._quotas}
        self._committed: Dict[str, int] = {tenant: 0 for tenant in self._quotas}
        self._closed: Set[str] = set()
        # id -> (tenant, amount), insertion-ordered, which is also ascending
        # numeric order since ids are assigned strictly increasing and never
        # reinserted.
        self._reservations: Dict[str, Tuple[str, int]] = {}
        self._next_id: int = 1

    # -- queries -------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._quotas[tenant] - self._held[tenant] - self._committed[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return tenant in self._closed

    def outstanding_ids(self) -> List[str]:
        return list(self._reservations.keys())

    def ledger_lines(self) -> List[str]:
        return list(self._durable.lines())

    # -- commands --------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quotas:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if amount < 1:
            return Result.rejected("amount_not_positive")
        if amount > self.available(tenant):
            return Result.rejected("quota_exceeded")

        reservation_id = f"r{self._next_id}"
        self._next_id += 1
        self._held[tenant] += amount
        self._reservations[reservation_id] = (tenant, amount)
        return Result.accepted(reservation_id=reservation_id)

    def commit(self, reservation_id: str) -> Result:
        if reservation_id not in self._reservations:
            return Result.rejected("unknown_reservation")

        tenant, amount = self._reservations.pop(reservation_id)
        self._held[tenant] -= amount
        self._committed[tenant] += amount
        self._durable.append_line(f"COMMIT {tenant} {amount} {self._committed[tenant]}")
        return Result.accepted()

    def release(self, reservation_id: str) -> Result:
        if reservation_id not in self._reservations:
            return Result.rejected("unknown_reservation")

        tenant, amount = self._reservations.pop(reservation_id)
        self._held[tenant] -= amount
        return Result.accepted()

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quotas:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if any(held_tenant == tenant for held_tenant, _ in self._reservations.values()):
            return Result.rejected("outstanding_reservations")

        self._closed.add(tenant)
        self._durable.append_line(f"CLOSE {tenant} {self._committed[tenant]}")
        return Result.accepted()
