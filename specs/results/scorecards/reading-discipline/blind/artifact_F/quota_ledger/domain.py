"""The rules of the quota ledger.

This module is the domain. It holds no path, no file handle, no clock, no
environment, no global, and it imports nothing from the modules that implement
its port. Everything outside the rules is reached through `Journal`, declared
here in the domain's own vocabulary; the concrete journal is built at the
composition point (see ``__init__.py``) and handed in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


class Journal(Protocol):
    """Driven port: the durable, append-only record the ledger commits to.

    Named for the need -- somewhere lines go, stay, and keep their order --
    rather than for the storage that happens to satisfy it.
    """

    def append(self, line: str) -> None:
        """Add one line to the end. Never rewrites, reorders, or removes."""

    def lines(self) -> list[str]:
        """Every line appended, in the order appended, none of them blank."""


@dataclass(frozen=True)
class Result:
    """What a command reports back.

    `status` is derived rather than stored: an accepted result is exactly one
    with no reason, so a stored status could only ever contradict the reason.
    """

    reason: str | None = None
    reservation_id: str | None = None

    @property
    def status(self) -> str:
        return "rejected" if self.reason is not None else "accepted"

    @classmethod
    def accept(cls, reservation_id: str | None = None) -> "Result":
        return cls(reservation_id=reservation_id)

    @classmethod
    def reject(cls, reason: str) -> "Result":
        return cls(reason=reason)


@dataclass
class _Account:
    """A tenant's standing: its fixed quota, what it has committed, whether it
    is closed. `committed` has exactly one writer, `Ledger.commit`; `closed`
    has exactly one writer, `Ledger.close_tenant`."""

    quota: int
    committed: int = 0
    closed: bool = False


@dataclass(frozen=True)
class _Hold:
    """A live reservation. It carries no id of its own -- the id is the key it
    is stored under, and a copy inside the value would be state nothing reads.
    """

    tenant: str
    amount: int


def _issue_order(reservation_id: str) -> int:
    """Ids are ``r<n>``; ascending means by n, so r2 precedes r10."""
    return int(reservation_id[1:])


class Ledger:
    """Reservations held against per-tenant quota, committed to a `Journal`."""

    def __init__(self, quotas: Mapping[str, int], journal: Journal) -> None:
        self._accounts = {name: _Account(quota) for name, quota in quotas.items()}
        self._journal = journal
        self._holds: dict[str, _Hold] = {}
        self._issued = 0

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        """Quota not currently held or committed.

        Derived, not stored. R1 (available + held + committed == quota) is then
        arithmetic rather than an invariant three commands have to remember to
        maintain, and `release` gets to be a single removal.
        """
        account = self._accounts[tenant]
        return account.quota - account.committed - sum(h.amount for h in self._held_by(tenant))

    def committed(self, tenant: str) -> int:
        return self._accounts[tenant].committed

    def is_closed(self, tenant: str) -> bool:
        return self._accounts[tenant].closed

    def outstanding_ids(self) -> list[str]:
        return sorted(self._holds, key=_issue_order)

    def ledger_lines(self) -> list[str]:
        return self._journal.lines()

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        account = self._accounts.get(tenant)
        if account is None:
            return Result.reject("unknown_tenant")
        if account.closed:
            return Result.reject("tenant_closed")
        if amount < 1:
            return Result.reject("amount_not_positive")
        if amount > self.available(tenant):
            return Result.reject("quota_exceeded")
        self._issued += 1
        reservation_id = f"r{self._issued}"
        self._holds[reservation_id] = _Hold(tenant, amount)
        return Result.accept(reservation_id)

    def commit(self, reservation_id: str) -> Result:
        hold = self._holds.pop(reservation_id, None)
        if hold is None:
            return Result.reject("unknown_reservation")
        account = self._accounts[hold.tenant]
        account.committed += hold.amount
        self._journal.append(f"COMMIT {hold.tenant} {hold.amount} {account.committed}")
        return Result.accept()

    def release(self, reservation_id: str) -> Result:
        if self._holds.pop(reservation_id, None) is None:
            return Result.reject("unknown_reservation")
        return Result.accept()

    def close_tenant(self, tenant: str) -> Result:
        account = self._accounts.get(tenant)
        if account is None:
            return Result.reject("unknown_tenant")
        if account.closed:
            return Result.reject("tenant_closed")
        if self._held_by(tenant):
            return Result.reject("outstanding_reservations")
        account.closed = True
        self._journal.append(f"CLOSE {tenant} {account.committed}")
        return Result.accept()

    # -- internals ---------------------------------------------------------

    def _held_by(self, tenant: str) -> list[_Hold]:
        return [hold for hold in self._holds.values() if hold.tenant == tenant]
