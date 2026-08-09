"""How the shared oracle reaches artifact_Z's (and artifact_M's) internals.

Both are one flat module with `available` STORED on a per-tenant record.
artifact_M deleted the `quota` field, so the quota is captured at `make` time
by this binding rather than read off the record.

A binding is not blind: writing one means reading the tree. That disclosure is
inherited verbatim from eval/reference_binding.py.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any

_IMPL_DIR = os.environ.get("QUOTA_LEDGER_DIR")
if _IMPL_DIR and _IMPL_DIR not in sys.path:
    sys.path.insert(0, _IMPL_DIR)
_impl = importlib.import_module("quota_ledger")

ARM = "artifact_Z/M"


def make(quotas: dict[str, int], path: Path) -> Any:
    book = _impl.QuotaLedger(dict(quotas), path)
    book._probe_quota = dict(quotas)
    return book


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    quota = book._probe_quota
    for name, record in book._tenants.items():
        record.committed = committed.get(name, 0)
        record.available = quota[name] - record.committed
        record.closed = name in closed
        if hasattr(record, "outstanding"):
            record.outstanding = 0
    book._reservations = {}
    for rid, tenant_name, amount in reservations:
        book._reservations[rid] = _impl._Reservation(tenant=tenant_name, amount=amount)
        book._tenants[tenant_name].available -= amount
        if hasattr(book._tenants[tenant_name], "outstanding"):
            book._tenants[tenant_name].outstanding += 1
    book._next_id = next_ordinal


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._reservations.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    original = book._append

    def append(line: str) -> None:
        observer(line)
        original(line)

    book._append = append
