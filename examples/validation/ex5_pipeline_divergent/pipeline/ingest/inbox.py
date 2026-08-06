"""Model variables `inbox` and `accepted`.

Component: ingest. Writes only ingest state.

SEEDED DIVERGENCE D2 lives in this file: the status-line helper reaches into
the ledger component directly, and there is no ingest <-> ledger port.
"""

from __future__ import annotations

from pipeline.ledger.journal import format_entry


class Inbox:
    """Holds unaccepted items and the set of accepted ones."""

    def __init__(self, items: list[str]) -> None:
        self._inbox: set[str] = set(items)
        self._accepted: set[str] = set()

    @property
    def pending(self) -> frozenset[str]:
        return frozenset(self._inbox)

    @property
    def accepted(self) -> frozenset[str]:
        return frozenset(self._accepted)

    def accept(self, item: str) -> bool:
        """`Accept(i)`: move an item from inbox to accepted."""
        if item not in self._inbox:
            return False
        self._inbox.discard(item)
        self._accepted.add(item)
        return True

    def status_line(self) -> str:
        """Reporting only. Renders accepted items in the ledger's own format."""
        return " ".join(format_entry(item) for item in sorted(self._accepted))
