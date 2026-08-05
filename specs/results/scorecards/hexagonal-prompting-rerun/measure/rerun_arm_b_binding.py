"""How the stable-controls oracle reaches EVAL-RERUN arm B's internals.

The arm-A binding's docstring carries the shared caveat (a binding is not
blind); it applies here identically.

What this arm looks like:

    quota_ledger.QuotaLedger(quotas, path)  a FACTORY returning a `Ledger`
    Ledger._quota[t]                        the quota
    Ledger._committed[t]                    committed totals
    Ledger._closed                          a set of tenant names
    Ledger._outstanding[rid] -> Reservation(tenant, amount), INSERTION-ORDERED
    Ledger._issued                          the last id ordinal
    Ledger._journal                         the `Journal` port, .append/.records

`available` is DERIVED here (`quota - held - committed`) and this arm stores no
reservations-side quantity at all. That difference is why three of the eleven
mutants cannot be re-anchored onto it by PERTURBING a statement -- see
`catalogue_arm_b.toml`, which seeds them by ADDITION and says so in the row.


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


def _domain():
    return importlib.import_module("quota_ledger.domain")

ARM = "B"


def make(quotas: dict[str, int], path: Path) -> Any:
    return _impl().QuotaLedger(dict(quotas), path)


def install(book: Any, *, committed: dict[str, int], closed: set[str],
            reservations: list[tuple[str, str, int]], next_ordinal: int) -> None:
    book._committed = {name: committed.get(name, 0) for name in book._quota}
    book._closed = set(closed)
    # Insertion order IS the reported order on this arm, and `reservations`
    # arrives in ascending id order.
    book._outstanding = {}
    for rid, tenant_name, amount in reservations:
        book._outstanding[rid] = _domain().Reservation(tenant=tenant_name, amount=amount)
    book._issued = next_ordinal - 1


def reservation(book: Any, rid: str) -> tuple[str, int] | None:
    held = book._outstanding.get(rid)
    return None if held is None else (held.tenant, held.amount)


def install_line_observer(book: Any, observer: Any) -> None:
    """Route the durable append through `observer` AS WELL AS to the journal."""
    journal = book._journal
    original = journal.append

    def append(record: str) -> None:
        observer(record)
        original(record)

    journal.append = append
