"""How the shared oracle reaches artifact_E's and artifact_F's internals.

Domain + `Journal` port + two adapters. `available` is DERIVED from the live
holds; the durable side is reached through the journal the composition point
wired, so the line observer wraps the ADAPTER rather than a method on the
domain -- the only one of the three bindings for which that is true.
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
_domain = importlib.import_module("quota_ledger.domain")

ARM = "artifact_E/F"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl.QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    for name, account in book._accounts.items():
        account.committed = committed.get(name, 0)
        account.closed = name in closed
    book._holds = {}
    for rid, tenant_name, amount in reservations:
        book._holds[rid] = _domain._Hold(tenant_name, amount)
    book._issued = next_ordinal - 1


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._holds.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    journal = book._journal
    original = journal.append

    def append(line: str) -> None:
        observer(line)
        original(line)

    journal.append = append
