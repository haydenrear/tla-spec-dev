"""A quota ledger: per-tenant reservations committed to an append-only file.

See examples/validation/ab/FEATURE.md for the requirement this implements.

Public surface:

    QuotaLedger(quotas, ledger_path)

    Queries: available(tenant), committed(tenant), is_closed(tenant),
             outstanding_ids(), ledger_lines()
    Commands: reserve(tenant, amount), commit(reservation_id),
              release(reservation_id), close_tenant(tenant)

Every command returns a Result. Rejections are total: they name a reason from
the declared vocabulary and leave both memory and the ledger file untouched.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Union

__all__ = ["QuotaLedger", "Result", "Reason", "REASONS"]


# -- the rejection vocabulary ---------------------------------------------
#
# The six reasons in FEATURE.md and no others. Kept as a module constant so
# that the reasons a caller may see and the reasons this code can produce are
# the same list in one place.


class Reason:
    UNKNOWN_TENANT = "unknown_tenant"
    TENANT_CLOSED = "tenant_closed"
    AMOUNT_NOT_POSITIVE = "amount_not_positive"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN_RESERVATION = "unknown_reservation"
    OUTSTANDING_RESERVATIONS = "outstanding_reservations"


REASONS = frozenset(
    {
        Reason.UNKNOWN_TENANT,
        Reason.TENANT_CLOSED,
        Reason.AMOUNT_NOT_POSITIVE,
        Reason.QUOTA_EXCEEDED,
        Reason.UNKNOWN_RESERVATION,
        Reason.OUTSTANDING_RESERVATIONS,
    }
)


@dataclass(frozen=True)
class Result:
    """What every command returns.

    ``status`` is "accepted" or "rejected". A rejected result carries a
    ``reason``; an accepted one carries a ``reservation_id`` when the command
    has one (only ``reserve`` does).
    """

    status: str
    reason: Optional[str] = None
    reservation_id: Optional[str] = None

    @classmethod
    def accepted(cls, reservation_id: Optional[str] = None) -> "Result":
        return cls(status="accepted", reservation_id=reservation_id)

    @classmethod
    def rejected(cls, reason: str) -> "Result":
        assert reason in REASONS, f"undeclared rejection reason: {reason!r}"
        return cls(status="rejected", reason=reason)


@dataclass
class _Tenant:
    """A tenant's whole in-memory position.

    ``available`` is decremented at reserve and is deliberately NOT restored at
    commit: the amount leaves availability when it is held and only comes back
    on release.
    """

    quota: int
    available: int
    committed: int = 0
    closed: bool = False
    outstanding: int = 0  # count of live reservations, for the close guard


@dataclass(frozen=True)
class _Reservation:
    tenant: str
    amount: int


class QuotaLedger:
    def __init__(self, quotas: Mapping[str, int], ledger_path: Union[str, Path]) -> None:
        self._tenants: Dict[str, _Tenant] = {
            name: _Tenant(quota=quota, available=quota) for name, quota in quotas.items()
        }
        self._reservations: Dict[str, _Reservation] = {}
        self._next_id = 1
        self._path = Path(ledger_path)
        # The ledger file starts empty. Creating it here means ledger_lines()
        # has something to read before the first accepted write.
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("", encoding="utf-8")

    # -- queries ----------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._tenant(tenant).available

    def committed(self, tenant: str) -> int:
        return self._tenant(tenant).committed

    def is_closed(self, tenant: str) -> bool:
        return self._tenant(tenant).closed

    def outstanding_ids(self) -> List[str]:
        """Live reservation ids, ascending.

        Sorted by the numeric part rather than by string, so r2 sorts before
        r10 once more than nine reservations have been made.
        """
        return sorted(self._reservations, key=lambda rid: int(rid[1:]))

    def ledger_lines(self) -> List[str]:
        """The durable ledger's lines, read back off disk, blanks dropped.

        Read from the file rather than from a memory copy on purpose: R2 says
        the durable side agrees with memory, and a query answered from memory
        could not tell you when it does not.
        """
        text = self._path.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if line.strip()]

    # -- commands ---------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        # Checks run in the order FEATURE.md lists them, so a command that
        # fails two of them reports the first.
        record = self._tenants.get(tenant)
        if record is None:
            return Result.rejected(Reason.UNKNOWN_TENANT)
        if record.closed:
            return Result.rejected(Reason.TENANT_CLOSED)
        if amount < 1:
            return Result.rejected(Reason.AMOUNT_NOT_POSITIVE)
        if amount > record.available:
            return Result.rejected(Reason.QUOTA_EXCEEDED)

        reservation_id = f"r{self._next_id}"
        # Ids run in order of ACCEPTANCE and are never reused: the counter
        # moves here and nowhere else, so a rejected reserve consumes no id.
        self._next_id += 1
        self._reservations[reservation_id] = _Reservation(tenant=tenant, amount=amount)
        record.available -= amount
        record.outstanding += 1
        return Result.accepted(reservation_id=reservation_id)

    def commit(self, reservation_id: str) -> Result:
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            return Result.rejected(Reason.UNKNOWN_RESERVATION)

        record = self._tenants[reservation.tenant]
        del self._reservations[reservation_id]
        record.outstanding -= 1
        record.committed += reservation.amount
        # available is NOT restored: the amount was deducted at reserve.
        self._append(f"COMMIT {reservation.tenant} {reservation.amount} {record.committed}")
        return Result.accepted()

    def release(self, reservation_id: str) -> Result:
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            return Result.rejected(Reason.UNKNOWN_RESERVATION)

        record = self._tenants[reservation.tenant]
        del self._reservations[reservation_id]
        record.outstanding -= 1
        record.available += reservation.amount
        # Nothing durable: a release is not a ledger event.
        return Result.accepted()

    def close_tenant(self, tenant: str) -> Result:
        record = self._tenants.get(tenant)
        if record is None:
            return Result.rejected(Reason.UNKNOWN_TENANT)
        if record.closed:
            return Result.rejected(Reason.TENANT_CLOSED)
        if record.outstanding > 0:
            return Result.rejected(Reason.OUTSTANDING_RESERVATIONS)

        record.closed = True
        self._append(f"CLOSE {tenant} {record.committed}")
        return Result.accepted()

    # -- internals --------------------------------------------------------

    def _tenant(self, tenant: str) -> _Tenant:
        try:
            return self._tenants[tenant]
        except KeyError:
            raise KeyError(f"unknown tenant: {tenant!r}") from None

    def _append(self, line: str) -> None:
        """Append exactly one line. The only way anything reaches the file.

        Append mode plus a flush and fsync: nothing already written can be
        rewritten, reordered, or removed by this call (R5), and the line is on
        disk before the accepting command returns.
        """
        with open(self._path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
