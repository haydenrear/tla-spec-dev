"""Model variable `ledger`.

Component: ledger.

SEEDED DIVERGENCE D3 lives in this file: `backlog_hint` reaches into the ingest
component, and there is no ingest <-> ledger port. The import is function-local
because the top-level direction is already taken by D1/D2 -- exactly the
cycle-breaking move a real codebase makes, and a check that only reads
module-level imports would miss it.

SEEDED ABSENCE A1 also lives here: `Record(i)` reads `delivered`, so the model
declares port P2 (dispatch <-> ledger). This file no longer imports
`pipeline.dispatch.delivery` -- the delivered set arrives as an argument from
the composition root -- so no code edge realizes P2.
"""

from __future__ import annotations

from pipeline_contract.types import PersistLedger


def format_entry(item: str) -> str:
    """The ledger's rendering of one item. Used by ingest in D2."""
    return f"[{item}]"


class Journal:
    """`ledger`: an append-only record of what dispatch delivered."""

    def __init__(self, store: object | None = None) -> None:
        self._entries: list[str] = []
        self._store = store

    @property
    def entries(self) -> tuple[str, ...]:
        return tuple(self._entries)

    def record(self, item: str, delivered: frozenset[str]) -> bool:
        """`Record(i)`: a delivered item, not already recorded, is appended."""
        if item not in delivered:
            return False
        if item in self._entries:
            return False
        self._entries.append(item)
        self._persist()
        return True

    def _persist(self) -> None:
        if self._store is None:
            return
        self._store.persist(PersistLedger(entries=",".join(self._entries)))

    def backlog_hint(self, inbox: object) -> int:
        """Reporting only. Counts what ingest has accepted but not recorded."""
        from pipeline.ingest.inbox import Inbox

        if not isinstance(inbox, Inbox):
            return 0
        return len(inbox.accepted - set(self._entries))
