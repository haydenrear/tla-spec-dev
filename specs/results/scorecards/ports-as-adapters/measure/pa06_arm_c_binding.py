"""How the stable-controls oracle reaches PA-06 arm C's internals.

Same shape and the same disclosure as `examples/validation/ab/eval/
reference_binding.py` and EVAL-RERUN's two arm bindings: installing a model
before-state into a program requires reaching past its public API, so whoever
writes a binding has read the code. **The binding is not blind and never
claimed to be; the JUDGES are.** This file was written after arm C's tree
existed, by the measuring agent, and is not shown to any judge.

What arm C looks like, stated so the reach is auditable:

    QuotaLedger._quota[t]             the quota
    QuotaLedger._available[t]         STORED, not derived
    QuotaLedger._committed[t]
    QuotaLedger._closed[t] -> bool    A DICT OF FLAGS, not a set of names
    QuotaLedger._outstanding[rid] -> (tenant, amount)   a PLAIN TUPLE
    QuotaLedger._next_id              the next id ordinal
    QuotaLedger._append_line(line)    the durable write, called through `self`

Two differences from `reference_binding.py`, both forced by arm C's own shape
and both recorded rather than smoothed over:

1. `_closed` is a `dict[str, bool]` here and a `set[str]` on the reference and
   on arm A. Assigning a set would leave `is_closed()` raising `KeyError`, so
   the flags are rewritten in place.
2. `_outstanding` holds `(tenant, amount)` tuples rather than a `Reservation`
   object, so there is no class to construct.

CACHE DISCLOSURE, and it is why this file looks the tree up on every call. The
driver's `_purge_modules` drops `quota_ledger*` plus a list of module names, and
since EVAL-RERUN-DF-01 it also drops every module holding a tree handle. A
module-level `_impl = import_module("quota_ledger")` was what produced
EVAL-RERUN-DF-01 -- every mutant executed against the PRISTINE tree and reported
SURVIVED with green controls. Looking the tree up per call makes that class of
bug unreachable here rather than dependent on a list being right.
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


def _impl():
    return importlib.import_module("quota_ledger")


ARM = "C"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl().QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    """Put the model's before-state into the book.

    `available` is STORED on this arm, so it is RECONSTRUCTED from the model's
    own arithmetic rather than copied: the model's `Commit` leaves `available`
    unchanged, so a committed amount stays deducted and
    `available = quota - committed - held`.
    """
    for name in book._quota:
        book._committed[name] = committed.get(name, 0)
        book._available[name] = book._quota[name] - book._committed[name]
        book._closed[name] = name in closed
    book._outstanding = {}
    for rid, tenant_name, amount in reservations:
        book._outstanding[rid] = (tenant_name, amount)
        book._available[tenant_name] -= amount
    book._next_id = next_ordinal


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held[0], held[1])


def install_line_observer(book: Any, observer: Any) -> None:
    """Route the durable append through `observer` AS WELL AS to the file.

    An ADDITIONAL oracle, never a replacement: the file still receives the line
    and `ledger_lines()` still reads it back, so the state projection loses
    nothing it had. Arm C writes through `self._append_line`, so the seam is an
    instance attribute shadowing the bound method; it disappears with the
    instance.
    """
    original = book._append_line

    def append_line(line: str) -> None:
        observer(line)
        original(line)

    book._append_line = append_line
