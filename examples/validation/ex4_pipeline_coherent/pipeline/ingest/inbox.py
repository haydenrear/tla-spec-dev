"""Model variables `inbox` and `accepted`.

Component: ingest. Writes only ingest state.
"""

from __future__ import annotations


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
