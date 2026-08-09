"""How the shared oracle reaches artifact_N's and artifact_D's internals.

One flat module. `available` is DERIVED: artifact_N keeps a per-tenant `_held`
running total, artifact_D walks `_outstanding`. The binding handles both by
writing `_held` only when it exists.
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

ARM = "artifact_N/D"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl.QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    for name in book._quota:
        book._committed[name] = committed.get(name, 0)
        book._closed[name] = name in closed
    book._outstanding = {}
    if hasattr(book, "_held"):
        book._held = {name: 0 for name in book._quota}
    for rid, tenant_name, amount in reservations:
        book._outstanding[rid] = _impl.Reservation(tenant_name, amount)
        if hasattr(book, "_held"):
            book._held[tenant_name] += amount
    book._next_id = next_ordinal


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    original = book._append

    def append(line: str) -> None:
        observer(line)
        original(line)

    book._append = append
