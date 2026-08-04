"""How the shared oracle reaches ARM A's internals.

HP-06 measurement instrument. There is one of these per arm and they are the
ONLY arm-specific code in the kill-table instrument: `arm_adapter.py` holds
every projection, every comparison and every skip rule, and it is byte-identical
across the two arms by construction because there is only one copy of it.

A BINDING IS NOT BLIND, AND THAT IS A CONFOUND THIS ROUND CANNOT REMOVE.
Installing a model before-state into a program requires reaching past its public
API -- the feature's surface has no "become this state" command -- so whoever
writes a binding has read the arm. The judges are blind; the instrument's author
is not. Recorded here rather than in a footnote.

What the arm looks like, stated so the reach is auditable:

    QuotaLedger._tenants[name] -> _Tenant(quota, held, committed, closed)
    QuotaLedger._outstanding[rid] -> _Reservation(reservation_id, tenant,
                                                  amount, sequence)
    QuotaLedger._next_sequence     the next id ordinal
    QuotaLedger._ledger            a _LedgerFile with .append(line)/.lines()

`available` is DERIVED (`quota - held - committed`), so it is installed by
setting `held`, never by assignment.
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

ARM = "A"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl.QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    """Put the model's before-state into the book.

    `reservations` is [(reservation_id, tenant, amount)] in ascending id order.
    """
    for name, tenant in book._tenants.items():
        tenant.committed = committed.get(name, 0)
        tenant.closed = name in closed
        tenant.held = 0
    book._outstanding = {}
    for ordinal, (rid, tenant_name, amount) in enumerate(reservations, start=1):
        book._outstanding[rid] = _impl._Reservation(
            reservation_id=rid, tenant=tenant_name, amount=amount, sequence=ordinal,
        )
        book._tenants[tenant_name].held += amount
    book._next_sequence = next_ordinal


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    """Route the durable append through `observer` AS WELL AS to the file.

    An ADDITIONAL oracle, never a replacement: the file still receives the line
    and `ledger_lines()` still reads it back, so the state projection loses
    nothing it had.
    """
    ledger = book._ledger
    original = ledger.append

    def append(line: str) -> None:
        observer(line)
        original(line)

    ledger.append = append
