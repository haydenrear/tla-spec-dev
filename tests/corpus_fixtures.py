"""The pathological ecommerce corpus, reconstructed as a test fixture.

`references/examples.md`, `references/edge-cases.md`, `references/testgraph_adapters.md`
and `examples/distributed_history/README.md` all document that the bounded
ecommerce model emits **732 external Test Graph cases across 11 actions**, of
which **69% are duplicate-submission variants**, with the tail bottoming out at
4 and 2 cases. That corpus is regenerated under a validation report at run time
and is NOT committed as artifacts -- the committed
`examples/distributed_history/specs/generated/` packages hold 4 internal and 4
external placeholder cases. Regenerating it needs a TLC run over the reachable
state graph, which the epic-wide spec-case execution deferral forbids.

So this module reconstructs the documented distribution exactly:

    200  SubmitDuplicateAddCartItem   \\
    184  SubmitDuplicateCheckout       > 504 = 68.9% duplicate-submission
    120  SubmitDuplicateCreateAccount /
     84  RunFulfillmentWorkerNoop
     60  SubmitCheckout
     40  SubmitAddCartItem
     24  RunFulfillmentWorker
      8  SubmitAddCartItemOutOfStock
      6  SubmitCheckoutUnknownClient
      4  SubmitCheckoutEmptyCart
      2  SubmitCreateAccount
    ----
    732  across 11 actions

The counts are the documented ones. The *shape* of each redundant group is
constructed so the three representation defects the diagnostics must tell apart
are each present and each attributable:

- `SubmitDuplicateAddCartItem` replays one no-op transition from 200 distinct
  reachable before-states -> **action enabled across equivalent states**.
- `SubmitDuplicateCheckout` sweeps a client x sku parameter domain while the
  transition shape stays fixed -> **interchangeable values**.
- `SubmitDuplicateCreateAccount` differs only in the order of the same pending
  queue elements -> **unconstrained ordering**.

That is a fixture, not evidence about the real ecommerce model. Findings about
the real corpus belong to MF-023, which regenerates it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import permutations
from typing import Any

# The documented distribution: (action, count, label class).
DOCUMENTED_DISTRIBUTION: tuple[tuple[str, int, str], ...] = (
    ("SubmitDuplicateAddCartItem", 200, "duplicate_submission"),
    ("SubmitDuplicateCheckout", 184, "duplicate_submission"),
    ("SubmitDuplicateCreateAccount", 120, "duplicate_submission"),
    ("RunFulfillmentWorkerNoop", 84, "worker_noop"),
    ("SubmitCheckout", 60, "happy_path"),
    ("SubmitAddCartItem", 40, "happy_path"),
    ("RunFulfillmentWorker", 24, "worker_progress"),
    ("SubmitAddCartItemOutOfStock", 8, "rejected"),
    ("SubmitCheckoutUnknownClient", 6, "rejected"),
    ("SubmitCheckoutEmptyCart", 4, "rejected"),
    ("SubmitCreateAccount", 2, "happy_path"),
)

DOCUMENTED_TOTAL = 732
DOCUMENTED_ACTIONS = 11
DUPLICATE_SUBMISSION_ACTIONS = frozenset(
    a for a, _, cls in DOCUMENTED_DISTRIBUTION if cls == "duplicate_submission"
)


@dataclass(frozen=True)
class FakeInput:
    action: str
    source_node: str
    target_node: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FakeCase:
    """Structurally what `generate_cases_from_tlc_dump` emits."""

    name: str
    before: dict[str, Any]
    input: FakeInput
    output: Any
    after: dict[str, Any]
    labels: frozenset[str]
    view: str = "external"
    layer: str = "external"


def _case(
    index: int,
    action: str,
    label_class: str,
    before: dict[str, Any],
    after: dict[str, Any],
    params: dict[str, Any],
    extra_labels: tuple[str, ...] = (),
) -> FakeCase:
    return FakeCase(
        name=f"case_{index:04d}_{action}",
        before=before,
        input=FakeInput(
            action=action,
            source_node=str(1000 + index),
            target_node=str(2000 + index),
            params=params,
        ),
        output={"changed": {}},
        after=after,
        labels=frozenset({action, label_class, *extra_labels}),
    )


def _abstraction_group(action: str, label_class: str, count: int, start: int) -> list[FakeCase]:
    """One no-op transition, replayed from `count` distinct before-states.

    Every case changes exactly the same field set (none of the domain state --
    a duplicate submission is rejected), but the reachable state it fires from
    differs each time. That is the abstraction fingerprint.
    """
    cases = []
    for i in range(count):
        before = {
            "accounts": i % 7,
            "cart_items": i % 5,
            "orders": i % 3,
            "inventory": 100 - (i % 11),
            "seen_request": True,
        }
        after = dict(before)  # duplicate submission is a no-op
        cases.append(
            _case(start + i, action, label_class, before, after, {"request_id": "req-1"})
        )
    return cases


def _symmetry_group(action: str, label_class: str, count: int, start: int) -> list[FakeCase]:
    """A client x sku parameter sweep over a fixed transition shape.

    The parameters take a distinct value in every case; the change shape is
    identical throughout. That is the interchangeable-values fingerprint.
    """
    cases = []
    for i in range(count):
        params = {"client": f"c{i // 8}", "sku": f"sku-{i % 8}"}
        before = {"submitted": True, "rejected": False}
        after = {"submitted": True, "rejected": True}
        cases.append(_case(start + i, action, label_class, before, after, params))
    return cases


def _ordering_group(action: str, label_class: str, count: int, start: int) -> list[FakeCase]:
    """The same pending queue, in every order TLC could reach it in.

    Each before-state holds a permutation of one multiset. Nothing else
    differs. That is the unconstrained-ordering fingerprint.
    """
    elements = ["a", "b", "c", "d", "e"]
    orders = [list(p) for p in permutations(elements)][:count]
    while len(orders) < count:  # pragma: no cover - 5! = 120 covers the count
        orders.extend(orders[: count - len(orders)])
    cases = []
    for i, order in enumerate(orders):
        before = {"pending_queue": order, "accounts": 1}
        after = {"pending_queue": order, "accounts": 1, "rejected": True}
        cases.append(_case(start + i, action, label_class, before, after, {}))
    return cases


def _plain_group(action: str, label_class: str, count: int, start: int) -> list[FakeCase]:
    """A well-behaved group: few cases, each doing something different."""
    cases = []
    for i in range(count):
        before = {"step": i, "accounts": i}
        after = {"step": i + 1, "accounts": i + 1}
        cases.append(
            _case(start + i, action, label_class, before, after, {"client": f"c{i}"})
        )
    return cases


_SHAPE_FOR_ACTION = {
    "SubmitDuplicateAddCartItem": _abstraction_group,
    "SubmitDuplicateCheckout": _symmetry_group,
    "SubmitDuplicateCreateAccount": _ordering_group,
}


def ecommerce_corpus() -> list[FakeCase]:
    """The full reconstructed 732-case external corpus."""
    cases: list[FakeCase] = []
    for action, count, label_class in DOCUMENTED_DISTRIBUTION:
        build = _SHAPE_FOR_ACTION.get(action, _plain_group)
        cases.extend(build(action, label_class, count, len(cases) + 1))
    return cases


def regression_trace_case(index: int = 9001) -> FakeCase:
    """A promoted counterexample. Always retained, never dropped."""
    return _case(
        index,
        "SubmitCheckout",
        "happy_path",
        {"step": 0},
        {"step": 1},
        {"client": "c0"},
        extra_labels=("regression:issue-41-double-charge",),
    )
