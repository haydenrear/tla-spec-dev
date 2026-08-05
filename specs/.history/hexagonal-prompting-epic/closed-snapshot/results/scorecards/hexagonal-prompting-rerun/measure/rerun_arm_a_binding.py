"""How the stable-controls oracle reaches EVAL-RERUN arm A's internals.

Same shape and the same disclosure as `examples/validation/ab/eval/
reference_binding.py`: installing a model before-state into a program requires
reaching past its public API, so whoever writes a binding has read the code. The
binding is not blind and never claimed to be; the JUDGES are.

What this arm looks like, stated so the reach is auditable:

    QuotaLedger._quotas[t]            the quota
    QuotaLedger._available[t]         STORED, not derived
    QuotaLedger._committed[t]
    QuotaLedger._closed               a set of tenant names
    QuotaLedger._reservations[rid] -> _Reservation(reservation_id, tenant,
                                                   amount, seq)
    QuotaLedger._next_seq             the next id ordinal
    QuotaLedger._ledger               a `_LedgerFile` with .append(line)


CACHE DISCLOSURE, and it is the reason this file differs from
`reference_binding.py` in one place. The driver's `_purge_modules` drops
`quota_ledger*` and a FIXED LIST of binding module names ("oracle",
"reference_binding", "arm_a_binding", "arm_b_binding") between mutants. This
binding's name is not on that list and the list is in a file this measurement
may not edit, so a module-level `_impl = import_module("quota_ledger")` would be
captured ONCE, against the PRISTINE tree, and every mutant would then be
executed against unmutated code and reported as SURVIVED.

That is not hypothetical: it is what the first EVAL-RERUN arm-A run produced --
11 of 11 mutants surviving all six generated instruments with green controls and
the suite killing 10 of 11. Filed as EVAL-RERUN-DF-01. It was caught because
the SUITE column disagreed with every corpus column, which is the disagreement
`references/eval_scorecard.md` rule 7 puts the mechanical block there to expose.

So the tree is looked up on every call instead of held. `sys.path` is still set
once, because the impl directory is fixed for the whole run.
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

ARM = "A"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl().QuotaLedger(dict(quotas), path)


def _ordinal(rid: str) -> int:
    digits = "".join(character for character in rid if character.isdigit())
    return int(digits) if digits else 0


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    """Put the model's before-state into the book.

    `available` is STORED on this arm, so it is RECONSTRUCTED from the model's
    own arithmetic rather than copied: the model's `Commit` leaves `available`
    unchanged, so a committed amount stays deducted and
    `available = quota - committed - held`.
    """
    for name in book._quotas:
        book._committed[name] = committed.get(name, 0)
        book._available[name] = book._quotas[name] - book._committed[name]
    book._closed = set(closed)
    book._reservations = {}
    for fallback, (rid, tenant_name, amount) in enumerate(reservations, start=1):
        book._reservations[rid] = _impl()._Reservation(
            reservation_id=rid, tenant=tenant_name, amount=amount,
            seq=_ordinal(rid) or fallback,
        )
        book._available[tenant_name] -= amount
    book._next_seq = next_ordinal


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._reservations.get(rid)
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
