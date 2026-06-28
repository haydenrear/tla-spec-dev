# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ecommerce_backend.domain import EcommerceStore


def test_checkout_is_idempotent_and_projectable():
    store = EcommerceStore()
    try:
        assert store.create_account("acct-1").status == 201
        assert store.add_cart_item("acct-1", "sku-1").status == 202
        assert store.checkout("acct-1", "order-1").status == 202
        assert store.checkout("acct-1", "order-1").body["idempotent"] is True
        assert store.process_outbox().body == {"processed": 1}

        assert store.snapshot() == {
            "accounts": ["acct-1"],
            "carts": {"acct-1": ["sku-1"]},
            "orders": {
                "order-1": {
                    "account": "acct-1",
                    "items": ["sku-1"],
                    "status": "accepted",
                }
            },
            "outbox": [],
            "projections": {"order-1": "ready_to_ship"},
        }
    finally:
        store.close()


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
