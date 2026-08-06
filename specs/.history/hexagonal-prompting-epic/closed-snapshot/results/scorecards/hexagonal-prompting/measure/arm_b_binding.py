"""How the shared oracle reaches ARM B's internals.

The arm-A binding's docstring carries the shared caveat (a binding is not blind);
it applies here identically.

What the arm looks like:

    QuotaLedger(ReservationBook)._quota[name]        the quota
    ReservationBook._committed[name]                 committed totals
    ReservationBook._closed                          a set of names
    ReservationBook._outstanding[rid] -> _Reservation(number, tenant, amount)
    ReservationBook._issued                          the last id ordinal
    ReservationBook._journal                         the CommitJournal port,
                                                     with .append(line)/.lines()

`available` is DERIVED here too (`quota - committed - sum(live holds)`), and
this arm has NO separate `held` counter at all: the held total is computed from
`_outstanding` on every read. That difference is why two of the ten mutants
cannot be re-anchored onto this arm -- see catalogue_arm_b.toml.
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

ARM = "B"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl.QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    book._committed = {name: committed.get(name, 0) for name in book._quota}
    book._closed = set(closed)
    book._outstanding = {}
    for ordinal, (rid, tenant_name, amount) in enumerate(reservations, start=1):
        book._outstanding[rid] = _domain._Reservation(
            number=ordinal, tenant=tenant_name, amount=amount,
        )
    book._issued = next_ordinal - 1


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    """Route the durable append through `observer` AS WELL AS to the journal."""
    journal = book._journal
    original = journal.append

    def append(line: str) -> None:
        observer(line)
        original(line)

    journal.append = append
