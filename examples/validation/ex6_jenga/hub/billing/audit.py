"""`auditLog`. Reaches orders and notify directly."""

from __future__ import annotations

from hub.notify.flags import DirtyFlags


class AuditTrail:
    def __init__(self, flags: DirtyFlags | None = None) -> None:
        self.entries: list[str] = []
        self._flags = flags

    def append(self, what: str) -> None:
        if len(self.entries) < 6:
            self.entries.append(what)
        if self._flags is not None:
            self._flags.mark(True, what)

    def replay_status(self) -> dict[str, str]:
        from hub.orders.lifecycle import Lifecycle

        return dict(Lifecycle.__dict__.get("status", {}) or {})
