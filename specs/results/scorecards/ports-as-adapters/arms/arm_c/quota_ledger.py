"""QuotaLedger: reservations against a per-tenant quota, committed to a
durable, append-only ledger file.

Implements the feature in examples/validation/ab/FEATURE.md. See NOTES.md in
this directory for what was decided and what was left unsure.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Result:
    """Every command returns one of these. `reason` is set only when
    status == "rejected"; `reservation_id` is set on the commands that have
    one to report (see NOTES.md on the commit/release/close cases)."""

    status: str
    reason: Optional[str] = None
    reservation_id: Optional[str] = None


class QuotaLedger:
    def __init__(self, quotas: Dict[str, int], ledger_path) -> None:
        # Each dict is keyed by tenant name; a name absent from `quotas` is an
        # unknown tenant for the lifetime of this ledger (no tenant is added
        # later — the feature gives no command that would create one).
        self._quota: Dict[str, int] = dict(quotas)
        self._available: Dict[str, int] = dict(quotas)
        self._committed: Dict[str, int] = {t: 0 for t in quotas}
        self._closed: Dict[str, bool] = {t: False for t in quotas}
        # reservation id -> (tenant, amount), only while outstanding.
        self._outstanding: Dict[str, Tuple[str, int]] = {}
        self._next_id: int = 1

        self._ledger_path = Path(ledger_path)
        # "The ledger file starts empty." Truncate/create it now so
        # ledger_lines() has a real file to read from the first call.
        self._ledger_path.write_text("")

    # -- queries -------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._available[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return self._closed[tenant]

    def outstanding_ids(self) -> List[str]:
        # Ascending. Ids are "r1", "r2", ... — a plain string sort would put
        # "r10" before "r2", so sort on the numeric suffix instead.
        return sorted(self._outstanding.keys(), key=lambda rid: int(rid[1:]))

    def ledger_lines(self) -> List[str]:
        # Read the file itself rather than trust an in-memory mirror: the
        # feature calls this the "durable" ledger, and a query that only
        # reflects memory would not actually be evidence the write happened.
        text = self._ledger_path.read_text()
        return [line for line in text.splitlines() if line != ""]

    # -- commands --------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quota:
            return Result(status="rejected", reason="unknown_tenant")
        if self._closed[tenant]:
            return Result(status="rejected", reason="tenant_closed")
        if amount < 1:
            return Result(status="rejected", reason="amount_not_positive")
        if amount > self._available[tenant]:
            return Result(status="rejected", reason="quota_exceeded")

        rid = f"r{self._next_id}"
        self._next_id += 1
        self._available[tenant] -= amount
        self._outstanding[rid] = (tenant, amount)
        return Result(status="accepted", reservation_id=rid)

    def commit(self, reservation_id: str) -> Result:
        if reservation_id not in self._outstanding:
            return Result(status="rejected", reason="unknown_reservation")

        tenant, amount = self._outstanding.pop(reservation_id)
        self._committed[tenant] += amount
        # available(tenant) is deliberately left untouched: the amount was
        # already deducted at reserve() and committing does not return it.
        self._append_line(f"COMMIT {tenant} {amount} {self._committed[tenant]}")
        return Result(status="accepted", reservation_id=reservation_id)

    def release(self, reservation_id: str) -> Result:
        if reservation_id not in self._outstanding:
            return Result(status="rejected", reason="unknown_reservation")

        tenant, amount = self._outstanding.pop(reservation_id)
        self._available[tenant] += amount
        # "Writes nothing to the ledger" — no _append_line call here.
        return Result(status="accepted", reservation_id=reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quota:
            return Result(status="rejected", reason="unknown_tenant")
        if self._closed[tenant]:
            return Result(status="rejected", reason="tenant_closed")
        if any(held_tenant == tenant for held_tenant, _ in self._outstanding.values()):
            return Result(status="rejected", reason="outstanding_reservations")

        self._closed[tenant] = True
        self._append_line(f"CLOSE {tenant} {self._committed[tenant]}")
        return Result(status="accepted")

    # -- internal --------------------------------------------------------

    def _append_line(self, line: str) -> None:
        with open(self._ledger_path, "a") as f:
            f.write(line + "\n")
