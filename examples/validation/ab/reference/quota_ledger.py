"""Reference implementation of the quota-ledger feature. See ../FEATURE.md.

THIS IS NOT AN ARM. It is never dispatched to an agent, never judged, never
scored, and its numbers are never placed in a table beside arm A's or arm B's.

It exists for exactly one reason: the seeded catalogue
(`../seeded_faults.toml`) uses literal `find`/`replace` text substitution, and
literal substitution needs a tree whose bytes are fixed. This file is that
tree. Because it is fixed, `check_catalogue.py` can assert that every `find`
pattern occurs EXACTLY ONCE, that applying and reverting a mutant is
byte-identical, and that every mutant still parses -- today, at HP-01, rather
than at HP-06 when the measurement is already running.

Its STYLE is deliberately irrelevant. A reader may reasonably note that a
single module with no ports looks like what arm A would produce; that
observation cannot matter, because nothing here is judged. What matters is its
BEHAVIOR, and its behavior is the feature specification, which is the same
specification both arms receive.

`available` is stored rather than derived. That is a deliberate choice with a
measurement consequence: a derived `available` cannot disagree with
`outstanding` and `committed`, which would silently delete the entire
cross-aspect fault surface M08 is seeded into. A fixture that cannot express a
fault class produces a zero that says nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

#: The complete rejection vocabulary. A guard that refuses for a reason outside
#: this set is as much a defect as a guard that does not refuse at all.
REJECTION_REASONS = (
    "unknown_tenant",
    "tenant_closed",
    "amount_not_positive",
    "quota_exceeded",
    "unknown_reservation",
    "outstanding_reservations",
)


@dataclass(frozen=True)
class Result:
    """Every command returns one of these. `status` is the output oracle."""

    status: str
    reason: str | None = None
    reservation_id: str | None = None

    @staticmethod
    def accepted(reservation_id: str | None = None) -> "Result":
        return Result(status="accepted", reservation_id=reservation_id)

    @staticmethod
    def rejected(reason: str) -> "Result":
        return Result(status="rejected", reason=reason)


@dataclass(frozen=True)
class Reservation:
    id: str
    tenant: str
    amount: int


class QuotaLedger:
    """Reservations held against a per-tenant quota, committed to a durable ledger.

    Two aspects, named here because the eval slices on them:

      RESERVATIONS  _available, _outstanding, _closed
      LEDGER        _committed, and the ledger file

    `commit` and `close_tenant` are the cross-aspect actions: their guards read
    the RESERVATIONS aspect and their effects write the LEDGER aspect.
    """

    def __init__(self, quotas: dict[str, int], ledger_path: Path | str) -> None:
        self._quota = dict(quotas)
        self._available = dict(quotas)
        self._committed = {tenant: 0 for tenant in quotas}
        self._closed: set[str] = set()
        self._outstanding: dict[str, Reservation] = {}
        self._next_id = 1
        self._ledger_path = Path(ledger_path)
        self._ledger_path.write_text("", encoding="utf-8")

    # -- queries -----------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._available[tenant]

    def committed(self, tenant: str) -> int:
        return self._committed[tenant]

    def is_closed(self, tenant: str) -> bool:
        return tenant in self._closed

    def outstanding_ids(self) -> list[str]:
        return sorted(self._outstanding)

    def ledger_lines(self) -> list[str]:
        text = self._ledger_path.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if line]

    # -- commands ----------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        if tenant not in self._quota:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if amount < 1:
            return Result.rejected("amount_not_positive")
        if amount > self._available[tenant]:
            return Result.rejected("quota_exceeded")
        reservation_id = f"r{self._next_id}"
        self._next_id += 1
        self._available[tenant] -= amount
        self._outstanding[reservation_id] = Reservation(reservation_id, tenant, amount)
        return Result.accepted(reservation_id)

    def commit(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return Result.rejected("unknown_reservation")
        del self._outstanding[reservation_id]
        self._committed[reservation.tenant] += reservation.amount
        self._append_line(
            f"COMMIT {reservation.tenant} {reservation.amount} "
            f"{self._committed[reservation.tenant]}"
        )
        return Result.accepted(reservation_id)

    def release(self, reservation_id: str) -> Result:
        reservation = self._outstanding.get(reservation_id)
        if reservation is None:
            return Result.rejected("unknown_reservation")
        del self._outstanding[reservation_id]
        self._available[reservation.tenant] += reservation.amount
        return Result.accepted(reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        if tenant not in self._quota:
            return Result.rejected("unknown_tenant")
        if tenant in self._closed:
            return Result.rejected("tenant_closed")
        if any(held.tenant == tenant for held in self._outstanding.values()):
            return Result.rejected("outstanding_reservations")
        self._closed.add(tenant)
        self._append_line(f"CLOSE {tenant} {self._committed[tenant]}")
        return Result.accepted()

    # -- the durable side --------------------------------------------------

    def _append_line(self, line: str) -> None:
        with self._ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
