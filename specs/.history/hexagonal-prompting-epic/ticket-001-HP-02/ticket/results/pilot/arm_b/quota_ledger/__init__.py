"""Composition root and public entry point.

The feature spec fixes `QuotaLedger`'s constructor signature: a mapping of
tenant to quota, and a path for the ledger file. That signature is a real
outside dependency (the filesystem) baked into the public API, so this module
-- and only this module -- is allowed to know about both the domain
(`QuotaBook`) and the concrete adapter that satisfies its durable-ledger port
(`FileLedgerAdapter`). It wires them together once, in the constructor, and
delegates every command and every query straight through.

Swap sentence: to run the same domain behavior against a different kind of
durable storage, write a new adapter for `quota_ledger.ports.DurableLedger`
and change the one line below that constructs `FileLedgerAdapter` -- no file
under `quota_ledger/domain.py` changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

from .adapters.file_adapter import FileLedgerAdapter
from .domain import QuotaBook, Result

__all__ = ["QuotaLedger", "Result"]


class QuotaLedger:
    def __init__(self, quotas: Dict[str, int], ledger_path: Union[str, Path]):
        self._book = QuotaBook(quotas, FileLedgerAdapter(ledger_path))

    # -- queries -------------------------------------------------------

    def available(self, tenant: str) -> int:
        return self._book.available(tenant)

    def committed(self, tenant: str) -> int:
        return self._book.committed(tenant)

    def is_closed(self, tenant: str) -> bool:
        return self._book.is_closed(tenant)

    def outstanding_ids(self) -> List[str]:
        return self._book.outstanding_ids()

    def ledger_lines(self) -> List[str]:
        return self._book.ledger_lines()

    # -- commands --------------------------------------------------------

    def reserve(self, tenant: str, amount: int) -> Result:
        return self._book.reserve(tenant, amount)

    def commit(self, reservation_id: str) -> Result:
        return self._book.commit(reservation_id)

    def release(self, reservation_id: str) -> Result:
        return self._book.release(reservation_id)

    def close_tenant(self, tenant: str) -> Result:
        return self._book.close_tenant(tenant)
