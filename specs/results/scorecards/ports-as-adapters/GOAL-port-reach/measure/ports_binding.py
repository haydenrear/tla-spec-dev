"""How the oracle reaches the PORTED reference's internals.

Same shape and the same disclosure as `examples/validation/ab/eval/reference_binding.py`:
installing a model before-state into a program means reaching past its public
API, so whoever writes a binding has read the code.

It differs from its flat ancestor in exactly one place, and the difference is
the ticket:

    reference/quota_ledger.py       writes through `self._append_line(line)`
    reference_ports/domain.py       writes through `self._journal.append(line)`

The flat binding's `install_line_observer` shadows a bound METHOD on the book.
There is no such method here -- the durable write left the domain when the port
was introduced -- so the seam is the PORT OBJECT, and wrapping it is the only
place a durable write can be observed from. That is the same fact PA-04 is
about, met from the other side: once a port exists, everything that wants to
watch the write has to go through the port, including the oracle.

What the ported reference looks like, stated so the reach is auditable:

    ReservationBook._quota[t]        the tenant's quota
    ReservationBook._available[t]    stored, not derived
    ReservationBook._committed[t]
    ReservationBook._closed          a set of tenant names
    ReservationBook._outstanding[rid] -> Reservation(id, tenant, amount)
    ReservationBook._next_id         the next id ordinal
    ReservationBook._journal         the LedgerJournal port itself

`make()` composes over whichever composition point `use()` selected. Both
composition points construct the SAME `ReservationBook` over a different
`LedgerJournal`, so everything below `make` is wiring-independent -- which is
why one binding module serves both wirings and the numbers are comparable.
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

#: The composition point `make()` currently builds over. `quota_ledger` wires
#: the REAL adapter (a file on disk); `quota_ledger_fake` wires the FAKE (the
#: record in memory). Selected by the RUNNER from the mapping's `[ports.*]`
#: table, never by an environment variable -- the whole acceptance criterion is
#: that the wiring is readable from the mapping.
_IMPL = "quota_ledger"

ARM = "reference_ports"


def use(impl_module: str) -> None:
    global _IMPL
    _IMPL = impl_module


def active() -> str:
    return _IMPL


def _module() -> Any:
    return importlib.import_module(_IMPL)


def make(quotas: dict[str, int], path: Path) -> Any:
    return _module().QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    """Put the model's before-state into the book.

    Carried over verbatim in effect from the flat binding, including the reason
    `available` is RECONSTRUCTED rather than copied: the model's `Commit` leaves
    `available` unchanged, so a committed amount stays deducted forever and
    `available = Quota - committed - held`. Installing `Quota - held` alone
    turned the negative corpus's control red on 67 of 94 executed cases on
    unmutated code, which is what a control is for.
    """
    for name in book._quota:
        book._committed[name] = committed.get(name, 0)
        book._available[name] = book._quota[name] - book._committed[name]
    book._closed = set(closed)
    book._outstanding = {}
    for rid, tenant_name, amount in reservations:
        book._outstanding[rid] = _module().Reservation(rid, tenant_name, amount)
        book._available[tenant_name] -= amount
    book._next_id = next_ordinal


def seed_journal(book: Any, lines: list[str]) -> None:
    """Put the model's before-state LEDGER into the book, THROUGH THE PORT.

    The flat binding did not need this: its before-ledger was installed by
    writing the file the flat reference reads back. That is not available here
    and MUST NOT be faked back into existence, because it is exactly the thing
    under measurement -- a fake journal ignores the path, so a before-state
    installed by writing a file arrives at the real wiring and vanishes at the
    fake one, and every case with a non-empty before-ledger would go red on
    unmutated code for a reason that has nothing to do with any mutant.

    Appending through the port is both correct and the honest shape: the port is
    how this program records a committed line, so it is how a recorded line is
    installed.
    """
    for line in lines:
        book._journal.append(line)


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    """Route the durable append through `observer` AS WELL AS to the port.

    An ADDITIONAL oracle, never a replacement: the port still receives the line
    and `ledger_lines()` still reads it back, so the state projection loses
    nothing it had. The seam is an instance attribute on the PORT OBJECT rather
    than on the book, because the ported domain has no durable write of its own
    to shadow; it disappears with the instance either way.
    """
    journal = book._journal
    original = journal.append

    def append(line: str) -> None:
        observer(line)
        original(line)

    journal.append = append
