"""CA-06 — one regression, expressed as an adapter conformance case.

THE SHAPE IS `SV-04`'s, deliberately: a small conformance suite that exercises
the implementation directly and asserts the outcome **out of band** — not
through the generated corpus's own `after`-state comparison, which is the
oracle that cannot see this class.

THE REGRESSION, chosen MECHANICALLY and disclosed under `MF-020`: it is the
first NON-STRING mutant, in source order, from the 36 that **neither** instrument
in this ticket's kill table kills — `INT:95:35:404` in
`examples/distributed_history/ecommerce_backend/domain.py`:

    95:            return OperationResult(404, {"error": "account_not_found"})   ->   405

**THIS FILE IS EXCLUDED FROM THE KILL TABLE IN `RESULTS.md` §2** and was written
AFTER that population was enumerated and run. It is a demonstration that the
class is EXPRESSIBLE, not evidence that any instrument catches it.

WHY NEITHER INSTRUMENT SEES IT, which is the point:

* the hand-written test never calls `add_cart_item` on an unknown account;
* the 93-case generated corpus **cannot**: `Internal.tla`'s `AddCartItem(a, sku)`
  guards on `a \\in accounts`, so no reachable transition expresses the refusal.
  The corpus that WOULD express it is `--negative-cases`, and both halves of that
  mechanism are broken — `CA-06-DF-01` (zero cases emitted on this model) and
  `CA-06-DF-02` (the emitted cases cannot execute against the shipped adapters).

So the regression is expressible **as a TLA+ negative case in principle and as
an adapter conformance case today**, and this file is the second.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(EXAMPLE_ROOT))

from ecommerce_backend.domain import EcommerceStore  # noqa: E402


@pytest.fixture()
def store():
    store = EcommerceStore()
    try:
        yield store
    finally:
        store.close()


def test_cart_mutation_on_an_unknown_account_is_refused_as_not_found(store):
    """The refusal the model guards on, asserted on the implementation.

    `Internal.tla:22` — `AddCartItem(a, sku) == /\\ a \\in accounts /\\ ...`.
    The guard is what makes this call refusable; this case asserts the refusal
    the guard implies, which no reachable transition of the model can carry.
    """
    result = store.add_cart_item("no-such-account", "sku-1")

    assert result.status == 404, (
        "a cart mutation against an account that does not exist must be refused "
        f"as not-found; got {result.status}"
    )
    assert result.body == {"error": "account_not_found"}


def test_the_refusal_leaves_the_store_inert(store):
    """The other half of a refusal case: nothing modelled may change.

    This is the assertion the generated negative corpus makes for free and the
    positive corpus cannot make at all.
    """
    before = store.snapshot()
    store.add_cart_item("no-such-account", "sku-1")
    assert store.snapshot() == before
