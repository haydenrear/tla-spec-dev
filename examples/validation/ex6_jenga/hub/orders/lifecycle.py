"""`status`. Reaches billing and notify directly, because everything does."""

from __future__ import annotations

from hub.billing.audit import AuditTrail
from hub.notify.flags import DirtyFlags


class Lifecycle:
    def __init__(self, audit: AuditTrail, flags: DirtyFlags) -> None:
        self.status: dict[str, str] = {}
        self._audit = audit
        self._flags = flags

    def place(self, order_id: str) -> None:
        self.status[order_id] = "new"
        self._audit.append("place")
        self._flags.mark(True, "place")

    def bill(self, order_id: str) -> None:
        self.status[order_id] = "billed"
        self._audit.append("bill")
        self._flags.mark(True, "bill")

    def close(self, order_id: str) -> None:
        self.status[order_id] = "closed"
        self._audit.append("close")
        self._flags.mark(False, "close")
