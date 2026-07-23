"""Agent-authored effect provider for the OrderCancellationPort boundary.

One migrated boundary (references/effectful_onboarding.md, "Migrating an
existing onboarded repository"): the EcommerceStore mutation behind the
internal CancelOrder action. Everything else stays on the preserved legacy
path (effect_ports: [] everywhere else, no other [effect_providers.*] table).

The provider owns the concrete representation of the modeled before-state
(sqlite backing choice, row insertion order), binds a real EcommerceStore,
lets the adapter drive the real cancel_order boundary through the generated
typed port, and asserts CONTENT on exit: the store/outbox after-state must
equal the modeled after-state carried by the generated case (the oracle).
The provider never rewrites the generated case.
"""

from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from random import Random
from collections.abc import Iterator
from typing import Any

_GENERATED_ROOT = Path(__file__).resolve().parent / "generated"
if str(_GENERATED_ROOT) not in sys.path:
    sys.path.insert(0, str(_GENERATED_ROOT))

from ecommerce_backend.domain import EcommerceStore
from ecommerce_history_contract.types import CancelOrder, CancelOrderResult
from spec_double_compiler.runtime import EffectProviderContext


def _plain(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True))


class OrderCancellationBinding:
    """Implements the generated OrderCancellationPort against a real store."""

    def __init__(self, context: EffectProviderContext) -> None:
        self.context = context
        rng = Random(context.derived_seed)
        # Fuzz dimension 1: sqlite backing (in-memory vs on-disk under the
        # point-qualified work_dir). Interchangeable representations of the
        # same modeled state.
        self.backing = rng.choice(["memory", "file"])
        if self.backing == "file":
            context.work_dir.mkdir(parents=True, exist_ok=True)
            db_path: str | Path = context.work_dir / f"cancel-{context.iteration}.db"
        else:
            db_path = ":memory:"
        self.store = EcommerceStore(db_path)
        # Fuzz dimension 2: row insertion order. The store's snapshot is
        # order-insensitive (sorted queries), so a shuffled load of the same
        # modeled before-state is representation, not behavior. Build shuffled
        # copies; never mutate the generated case.
        before = _plain(self.context.case.before)
        shuffled = {
            "accounts": _shuffled_list(before.get("accounts", []), rng),
            "carts": _shuffled_dict(before.get("carts", {}), rng),
            "orders": _shuffled_dict(before.get("orders", {}), rng),
            "outbox": _shuffled_list(before.get("outbox", []), rng),
            "projections": _shuffled_dict(before.get("projections", {}), rng),
        }
        self.store.load_state(shuffled)
        self.calls: list[dict[str, Any]] = []

    def cancel(self, command: CancelOrder) -> CancelOrderResult:
        result = self.store.cancel_order(command.account, command.order)
        self.calls.append(
            {
                "account": command.account,
                "order": command.order,
                "status": result.status,
                "body": dict(result.body),
            }
        )
        return CancelOrderResult(status=result.status, body=dict(result.body))

    def snapshot(self) -> dict[str, Any]:
        return self.store.snapshot()

    def assert_after_state(self) -> None:
        """CONTENT assertions: real store/outbox state vs the modeled after-state."""
        case = self.context.case
        params = dict(case.input.params)
        if not self.calls:
            raise AssertionError(
                f"provider bound for {case.name} but the adapter never drove the "
                "cancel boundary; the migrated path was bypassed"
            )
        for call in self.calls:
            if call["account"] != params["account"] or call["order"] != params["order"]:
                raise AssertionError(
                    f"cancel called with {call['account']!r}/{call['order']!r} but the "
                    f"generated case models {params['account']!r}/{params['order']!r}"
                )
        expected_after = _plain(case.after)
        actual_after = _plain(self.store.snapshot())
        order_id = params["order"]
        expected_order = expected_after.get("orders", {}).get(order_id)
        actual_order = actual_after.get("orders", {}).get(order_id)
        if actual_order is None or actual_order.get("status") != "cancelled":
            raise AssertionError(
                f"modeled after-state has {order_id} cancelled, store has {actual_order!r}"
            )
        if actual_order != expected_order:
            raise AssertionError(
                f"cancelled order content mismatch for {order_id}: "
                f"store {actual_order!r} != modeled {expected_order!r}"
            )
        actual_outbox_ids = [event["order_id"] for event in actual_after.get("outbox", [])]
        if order_id in actual_outbox_ids:
            raise AssertionError(
                f"cancelled order {order_id} still present in the store outbox {actual_outbox_ids!r}"
            )
        if actual_after.get("outbox") != expected_after.get("outbox"):
            raise AssertionError(
                f"outbox content mismatch: store {actual_after.get('outbox')!r} "
                f"!= modeled {expected_after.get('outbox')!r}"
            )
        if actual_after.get("projections") != expected_after.get("projections"):
            raise AssertionError(
                f"projection content mismatch after cancel: store "
                f"{actual_after.get('projections')!r} != modeled {expected_after.get('projections')!r}"
            )
        if actual_after != expected_after:
            raise AssertionError(
                f"full after-state mismatch for {case.name}: store {actual_after!r} "
                f"!= modeled {expected_after!r}"
            )

    def close(self) -> None:
        self.store.close()


def _shuffled_list(items: list[Any], rng: Random) -> list[Any]:
    copy = list(items)
    rng.shuffle(copy)
    return copy


def _shuffled_dict(mapping: dict[str, Any], rng: Random) -> dict[str, Any]:
    keys = list(mapping.keys())
    rng.shuffle(keys)
    return {key: mapping[key] for key in keys}


class OrderCancellationProvider:
    @contextmanager
    def bind(self, context: EffectProviderContext) -> Iterator[Any | None]:
        binding = OrderCancellationBinding(context)
        try:
            yield binding
            binding.assert_after_state()
        finally:
            binding.close()


effect_provider = OrderCancellationProvider()
