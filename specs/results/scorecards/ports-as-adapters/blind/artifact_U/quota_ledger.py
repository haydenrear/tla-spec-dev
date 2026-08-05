"""A quota ledger: reservations held against per-tenant quota, committed to a
durable append-only ledger file.

See FEATURE.md for the requirement. Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

__all__ = ["QuotaLedger", "Result"]


# -- rejection reasons ------------------------------------------------------
#
# The whole declared vocabulary, in one place. A command may only reject with
# one of these (R4).

UNKNOWN_TENANT = "unknown_tenant"
TENANT_CLOSED = "tenant_closed"
AMOUNT_NOT_POSITIVE = "amount_not_positive"
QUOTA_EXCEEDED = "quota_exceeded"
UNKNOWN_RESERVATION = "unknown_reservation"
OUTSTANDING_RESERVATIONS = "outstanding_reservations"

REJECTION_REASONS = frozenset(
    {
        UNKNOWN_TENANT,
        TENANT_CLOSED,
        AMOUNT_NOT_POSITIVE,
        QUOTA_EXCEEDED,
        UNKNOWN_RESERVATION,
        OUTSTANDING_RESERVATIONS,
    }
)


@dataclass(frozen=True)
class Result:
    """What every command returns.

    An accepted result carries a ``reservation_id`` where the command has one;
    a rejected result carries a ``reason``. The other field is None.
    """

    status: str
    reason: str | None = None
    reservation_id: str | None = None

    @staticmethod
    def accepted(reservation_id: str | None = None) -> "Result":
        return Result(status="accepted", reservation_id=reservation_id)

    @staticmethod
    def rejected(reason: str) -> "Result":
        assert reason in REJECTION_REASONS, f"undeclared rejection reason: {reason}"
        return Result(status="rejected", reason=reason)


@dataclass
class _Reservation:
    """A live hold. ``seq`` is the allocation order, which is also id order."""

    reservation_id: str
    tenant: str
    amount: int
    seq: int


class _LedgerFile:
    """The durable side: an append-only text file, one record per line.

    Reads come back from the file rather than from a mirror kept in memory, so
    that what a reader observes really is what was written (R2, R5).
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        # "The ledger file starts empty."
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("", encoding="utf-8")

    def append(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()

    def lines(self) -> list[str]:
        text = self._path.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if line.strip()]


class QuotaLedger:
    """Reservations against a per-tenant quota, committed to a durable ledger.

    Invariant, for every tenant (R1):

        available + sum(outstanding amounts) + committed == quota
    """

    def __init__(self, quotas: Mapping[str, int], ledger_path: Path | str) -> None:
        self._quotas: dict[str, int] = dict(quotas)
        self._available: dict[str, int] = dict(quotas)
        self._committed: dict[str, int] = {tenant: 0 for tenant in self._quotas}
        self._closed: set[str] = set()
        self._reservations: dict[str, _Reservation] = {}
        self._next_seq = 1
        self._ledger = _LedgerFile(ledger_path)

    # -- queries ------------------------------------------------------------

    def available(self, tenant: str) -> int:
        """The quota not currently held by a live reservation or committed."""
        return self._available[tenant]

    def committed(self, tenant: str) -> int:
        """The total committed so far."""
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return tenant in self._closed

    def outstanding_ids(self) -> list[str]:
        """The ids of all live reservations, ascending."""
        return [
            reservation.reservation_id
            for reservation in sorted(self._reservations.values(), key=lambda r: r.seq)
        ]

    def ledger_lines(self) -> list[str]:
        """The durable ledger's lines, in the order written, no blanks."""
        return self._ledger.lines()

    # -- commands -----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        """Hold ``amount`` of ``tenant``'s quota under a fresh reservation id."""
        if tenant not in self._quotas:
            return Result.rejected(UNKNOWN_TENANT)
        if self.is_closed(tenant):
            return Result.rejected(TENANT_CLOSED)
        if amount < 1:
            return Result.rejected(AMOUNT_NOT_POSITIVE)
        if amount > self._available[tenant]:
            return Result.rejected(QUOTA_EXCEEDED)

        reservation = self._allocate(tenant, amount)
        self._available[tenant] -= amount
        self._reservations[reservation.reservation_id] = reservation
        return Result.accepted(reservation.reservation_id)

    def commit(self, reservation_id: str) -> Result:
        """Turn a live hold into committed quota and record it durably.

        ``available`` is not changed: the amount was deducted at ``reserve``
        and committing it does not give it back.
        """
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            return Result.rejected(UNKNOWN_RESERVATION)

        # The durable write happens before the in-memory change, so that a
        # write that fails leaves the two sides agreeing (R2) rather than
        # leaving memory ahead of the ledger.
        total_after = self._committed[reservation.tenant] + reservation.amount
        self._ledger.append(f"COMMIT {reservation.tenant} {reservation.amount} {total_after}")

        self._committed[reservation.tenant] = total_after
        del self._reservations[reservation_id]
        return Result.accepted(reservation_id)

    def release(self, reservation_id: str) -> Result:
        """Drop a live hold and return its amount to available. Writes nothing."""
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            return Result.rejected(UNKNOWN_RESERVATION)

        self._available[reservation.tenant] += reservation.amount
        del self._reservations[reservation_id]
        return Result.accepted(reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        """Close a tenant for good and record the final total durably."""
        if tenant not in self._quotas:
            return Result.rejected(UNKNOWN_TENANT)
        if self.is_closed(tenant):
            return Result.rejected(TENANT_CLOSED)
        if self._has_outstanding(tenant):
            return Result.rejected(OUTSTANDING_RESERVATIONS)

        self._ledger.append(f"CLOSE {tenant} {self._committed[tenant]}")
        self._closed.add(tenant)
        return Result.accepted()

    # -- internals ----------------------------------------------------------

    def _allocate(self, tenant: str, amount: int) -> _Reservation:
        """Allocate the next id. Ids run r1, r2, r3, ... and are never reused."""
        seq = self._next_seq
        self._next_seq += 1
        return _Reservation(
            reservation_id=f"r{seq}", tenant=tenant, amount=amount, seq=seq
        )

    def _has_outstanding(self, tenant: str) -> bool:
        return any(
            reservation.tenant == tenant for reservation in self._reservations.values()
        )
