"""How the stable-controls oracle reaches the FIXTURE REFERENCE's internals.

Same shape as HP-06's `arm_a_binding.py` / `arm_b_binding.py` and written from
the same disclosure: installing a model before-state into a program requires
reaching past its public API, so whoever writes a binding has read the code.

The reference is not an arm. It is never judged and never scored. It is used
here because the SEALED catalogue (`../seeded_faults.toml`) anchors its literal
find/replace on this exact tree, so the controls can be checked against the
mutants as they were declared rather than against a re-anchoring.

What the reference looks like, stated so the reach is auditable:

    QuotaLedger._available[t]        stored, not derived
    QuotaLedger._committed[t]
    QuotaLedger._closed              a set of tenant names
    QuotaLedger._outstanding[rid] -> Reservation(id, tenant, amount)
    QuotaLedger._next_id             the next id ordinal
    QuotaLedger._append_line(line)   the durable write, called through `self`
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

ARM = "reference"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl.QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    """Put the model's before-state into the book.

    `reservations` is [(reservation_id, tenant, amount)] in ascending id order.

    `available` is STORED here rather than derived, so it must be RECONSTRUCTED
    from the model's own arithmetic instead of copied: the model's `Commit`
    leaves `available` UNCHANGED, so a committed amount stays deducted forever
    and `available = Quota - committed - held`. Installing `Quota - held` alone
    turned the negative corpus's control red on 67 of 94 executed cases on
    unmutated code -- which is what a control is for.
    """
    for name in book._quota:
        book._committed[name] = committed.get(name, 0)
        book._available[name] = book._quota[name] - book._committed[name]
    book._closed = set(closed)
    book._outstanding = {}
    for rid, tenant_name, amount in reservations:
        book._outstanding[rid] = _impl.Reservation(rid, tenant_name, amount)
        book._available[tenant_name] -= amount
    book._next_id = next_ordinal


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    """Route the durable append through `observer` AS WELL AS to the file.

    An ADDITIONAL oracle, never a replacement: the file still receives the line
    and `ledger_lines()` still reads it back, so the state projection loses
    nothing it had. The reference writes through `self._append_line`, so the
    seam is an instance attribute shadowing the bound method; it disappears with
    the instance.
    """
    original = book._append_line

    def append_line(line: str) -> None:
        observer(line)
        original(line)

    book._append_line = append_line
