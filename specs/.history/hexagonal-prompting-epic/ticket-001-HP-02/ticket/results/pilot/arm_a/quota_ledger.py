"""A quota ledger: per-tenant quota, held reservations, and a durable,
append-only commit/close ledger.

See FEATURE.md (examples/validation/ab/FEATURE.md) for the full spec this
implements.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Result:
    status: str  # "accepted" or "rejected"
    reason: Optional[str] = None
    reservation_id: Optional[str] = None


def _accepted(reservation_id: Optional[str] = None) -> Result:
    return Result(status="accepted", reservation_id=reservation_id)


def _rejected(reason: str) -> Result:
    return Result(status="rejected", reason=reason)


class QuotaLedger:
    """Manages reservations against a per-tenant quota and commits them to a
    durable, append-only ledger file.
    """

    def __init__(self, quotas: dict, ledger_path):
        self._quotas = dict(quotas)
        self._available = dict(quotas)
        self._committed = {tenant: 0 for tenant in quotas}
        self._closed = {tenant: False for tenant in quotas}

        # reservation_id -> (tenant, amount), for live reservations only.
        self._outstanding: dict = {}
        self._next_serial = 1

        self._ledger_path = Path(ledger_path)
        self._lines: list = []
        # The ledger file starts empty, regardless of whatever (if anything)
        # was already at this path.
        self._ledger_path.write_text("")

    # -- queries -------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._available[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return self._closed[tenant]

    def outstanding_ids(self) -> list:
        return sorted(self._outstanding, key=lambda rid: int(rid[1:]))

    def ledger_lines(self) -> list:
        return list(self._lines)

    # -- commands --------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quotas:
            return _rejected("unknown_tenant")
        if self._closed[tenant]:
            return _rejected("tenant_closed")
        if amount < 1:
            return _rejected("amount_not_positive")
        if amount > self._available[tenant]:
            return _rejected("quota_exceeded")

        reservation_id = f"r{self._next_serial}"
        self._next_serial += 1
        self._available[tenant] -= amount
        self._outstanding[reservation_id] = (tenant, amount)
        return _accepted(reservation_id=reservation_id)

    def commit(self, reservation_id: str) -> Result:
        if reservation_id not in self._outstanding:
            return _rejected("unknown_reservation")

        tenant, amount = self._outstanding.pop(reservation_id)
        self._committed[tenant] += amount
        self._append_line(f"COMMIT {tenant} {amount} {self._committed[tenant]}")
        return _accepted()

    def release(self, reservation_id: str) -> Result:
        if reservation_id not in self._outstanding:
            return _rejected("unknown_reservation")

        tenant, amount = self._outstanding.pop(reservation_id)
        self._available[tenant] += amount
        return _accepted()

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quotas:
            return _rejected("unknown_tenant")
        if self._closed[tenant]:
            return _rejected("tenant_closed")
        if any(t == tenant for t, _ in self._outstanding.values()):
            return _rejected("outstanding_reservations")

        self._closed[tenant] = True
        self._append_line(f"CLOSE {tenant} {self._committed[tenant]}")
        return _accepted()

    # -- internals ---------------------------------------------------------

    def _append_line(self, line: str) -> None:
        with self._ledger_path.open("a") as fh:
            fh.write(line + "\n")
        self._lines.append(line)
