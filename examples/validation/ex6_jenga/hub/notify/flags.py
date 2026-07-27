"""`dirty` and `lastCommand`. Reaches orders and billing directly."""

from __future__ import annotations


class DirtyFlags:
    def __init__(self) -> None:
        self.dirty = False
        self.last_command = "none"

    def mark(self, dirty: bool, command: str) -> None:
        self.dirty = dirty
        self.last_command = command

    def poll(self, lifecycle: object, audit: object) -> str:
        """Coordination by polling: re-read everybody, re-stamp the flags."""
        from hub.billing.audit import AuditTrail
        from hub.orders.lifecycle import Lifecycle

        if isinstance(lifecycle, Lifecycle) and isinstance(audit, AuditTrail):
            self.dirty = False
            self.last_command = "poll"
        return self.last_command
