"""Model variable `ledger`.

Component: ledger. Reaches dispatch through port P2 (`Record`) and NOTHING
else. There is no port between ingest and ledger; an edge from this file to
`pipeline.ingest.*`, or from `pipeline.ingest.*` to this file, is the
divergence the twin fixture seeds.
"""

from __future__ import annotations

from pipeline_contract.types import PersistLedger

from pipeline.dispatch.delivery import Dispatcher


class Journal:
    """`ledger`: an append-only record of what dispatch delivered.

    `store` is the `LedgerStorePort` effect: the durable side of the ledger.
    It is optional so the in-memory driver and the behavioral tests need no
    boundary; when a store is bound, `record` persists through it. This is the
    ONLY observable boundary in the fixture, and it is what makes the
    corpus-alone arm and the corpus-plus-content-provider arm different runs
    rather than the same run twice.
    """

    def __init__(self, dispatcher: Dispatcher, store: object | None = None) -> None:
        self._dispatcher = dispatcher
        self._entries: list[str] = []
        self._store = store

    @property
    def entries(self) -> tuple[str, ...]:
        return tuple(self._entries)

    def record(self, item: str) -> bool:
        """`Record(i)`: a delivered item, not already recorded, is appended."""
        if item not in self._dispatcher.delivered:
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
