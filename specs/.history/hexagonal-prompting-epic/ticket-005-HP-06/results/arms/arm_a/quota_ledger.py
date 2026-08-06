"""A quota ledger: per-tenant reservations, committed to an append-only file.

See ``examples/validation/ab/FEATURE.md`` for the requirement this implements.

The public surface is :class:`QuotaLedger`. Every command returns a
:class:`Result` whose ``status`` is ``"accepted"`` or ``"rejected"``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

__all__ = ["QuotaLedger", "Result", "ACCEPTED", "REJECTED", "REASONS"]


ACCEPTED = "accepted"
REJECTED = "rejected"

#: The complete rejection vocabulary. Nothing outside this set is ever
#: returned as a ``reason`` (FEATURE.md R4).
REASONS = frozenset(
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
    """The outcome of a command.

    ``reason`` is set only on a rejection; ``reservation_id`` only on an
    acceptance of a command that has one (``reserve``).
    """

    status: str
    reason: Optional[str] = None
    reservation_id: Optional[str] = None

    @property
    def accepted(self) -> bool:
        return self.status == ACCEPTED

    @property
    def rejected(self) -> bool:
        return self.status == REJECTED


def _accept(reservation_id: Optional[str] = None) -> Result:
    return Result(status=ACCEPTED, reservation_id=reservation_id)


def _reject(reason: str) -> Result:
    assert reason in REASONS, f"undeclared rejection reason: {reason!r}"
    return Result(status=REJECTED, reason=reason)


@dataclass
class _Reservation:
    """A live hold against a tenant's quota."""

    reservation_id: str
    tenant: str
    amount: int
    sequence: int


@dataclass
class _Tenant:
    """One tenant's in-memory position."""

    name: str
    quota: int
    held: int = 0
    committed: int = 0
    closed: bool = False

    @property
    def available(self) -> int:
        # R1 restated as a derivation rather than a fourth mutable counter:
        # available + held + committed == quota holds by construction.
        return self.quota - self.held - self.committed


class _LedgerFile:
    """The durable side: an append-only text file, one record per line.

    Nothing here rewrites, reorders, or removes a line (R5); the only write
    operation is an append, and reads always come back from disk.
    """

    def __init__(self, path: os.PathLike | str) -> None:
        self._path = Path(path)
        parent = self._path.parent
        if str(parent) and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        # "The ledger file starts empty."
        self._path.write_text("", encoding="utf-8")

    @property
    def path(self) -> Path:
        return self._path

    def append(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def lines(self) -> List[str]:
        text = self._path.read_text(encoding="utf-8")
        return [line for line in text.split("\n") if line.strip()]


class QuotaLedger:
    """Reservations held against per-tenant quotas, committed durably.

    :param quotas: mapping of tenant name to integer quota.
    :param ledger_path: path to the durable ledger file; created empty.
    """

    def __init__(self, quotas: Dict[str, int], ledger_path: os.PathLike | str) -> None:
        self._tenants: Dict[str, _Tenant] = {
            name: _Tenant(name=name, quota=quota) for name, quota in dict(quotas).items()
        }
        self._outstanding: Dict[str, _Reservation] = {}
        self._next_sequence = 1
        self._ledger = _LedgerFile(ledger_path)

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        """The quota not currently held by a live reservation or committed."""
        return self._tenant(tenant).available

    def committed(self, tenant: str) -> int:
        """The total committed so far for this tenant."""
        return self._tenant(tenant).committed

    def is_closed(self, tenant: str) -> bool:
        """Whether this tenant is closed."""
        return self._tenant(tenant).closed

    def outstanding_ids(self) -> List[str]:
        """The ids of all live reservations, ascending by allocation order."""
        return [
            reservation.reservation_id
            for reservation in sorted(
                self._outstanding.values(), key=lambda held: held.sequence
            )
        ]

    def ledger_lines(self) -> List[str]:
        """The durable ledger's lines, in the order written, no blanks."""
        return self._ledger.lines()

    @property
    def ledger_path(self) -> Path:
        """Where the durable ledger lives."""
        return self._ledger.path

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        """Hold ``amount`` of ``tenant``'s quota under a fresh reservation id.

        Checks run in the order given by FEATURE.md, so the reported reason
        for a request that fails several checks is the first one it fails.
        """
        found = self._tenants.get(tenant)
        if found is None:
            return _reject("unknown_tenant")
        if found.closed:
            return _reject("tenant_closed")
        if amount < 1:
            return _reject("amount_not_positive")
        if amount > found.available:
            return _reject("quota_exceeded")

        sequence = self._next_sequence
        self._next_sequence += 1
        reservation_id = f"r{sequence}"
        self._outstanding[reservation_id] = _Reservation(
            reservation_id=reservation_id,
            tenant=tenant,
            amount=amount,
            sequence=sequence,
        )
        found.held += amount
        return _accept(reservation_id=reservation_id)

    def commit(self, reservation_id: str) -> Result:
        """Turn a live reservation into a committed amount, durably recorded.

        ``available`` does not move: the amount left it at ``reserve`` time
        and committing does not give it back.
        """
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return _reject("unknown_reservation")

        tenant = self._tenants[reservation.tenant]
        total_after = tenant.committed + reservation.amount

        # Durable write first: if it fails, memory is untouched and R2 still
        # holds. Memory then follows the line that was actually written.
        self._ledger.append(f"COMMIT {tenant.name} {reservation.amount} {total_after}")

        del self._outstanding[reservation_id]
        tenant.held -= reservation.amount
        tenant.committed = total_after
        return _accept()

    def release(self, reservation_id: str) -> Result:
        """Drop a live reservation, returning its amount to ``available``.

        Writes nothing to the ledger: a release is not a durable event.
        """
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return _reject("unknown_reservation")

        del self._outstanding[reservation_id]
        self._tenants[reservation.tenant].held -= reservation.amount
        return _accept()

    def close_tenant(self, tenant: str) -> Result:
        """Close a tenant for good, recording its final committed total."""
        found = self._tenants.get(tenant)
        if found is None:
            return _reject("unknown_tenant")
        if found.closed:
            return _reject("tenant_closed")
        if any(held.tenant == tenant for held in self._outstanding.values()):
            return _reject("outstanding_reservations")

        self._ledger.append(f"CLOSE {found.name} {found.committed}")
        found.closed = True
        return _accept()

    # -- internals ---------------------------------------------------------

    def _tenant(self, tenant: str) -> _Tenant:
        try:
            return self._tenants[tenant]
        except KeyError:
            raise KeyError(f"unknown tenant: {tenant!r}") from None
