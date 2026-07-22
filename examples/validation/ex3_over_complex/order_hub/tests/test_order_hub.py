import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import order_hub


def test_place_then_ship():
    hub = order_hub.new_hub()
    assert order_hub.place_order(hub)
    assert order_hub.ship_order(hub)
    assert hub["orders"] == 1
    assert hub["shipped"] == 1


def test_cannot_ship_more_than_ordered():
    hub = order_hub.new_hub()
    assert not order_hub.ship_order(hub)
    assert order_hub.place_order(hub)
    assert order_hub.ship_order(hub)
    assert not order_hub.ship_order(hub)


def test_order_cap():
    hub = order_hub.new_hub()
    for _ in range(order_hub.MAX_ORDERS):
        assert order_hub.place_order(hub)
    assert not order_hub.place_order(hub)


def test_retry_cap():
    hub = order_hub.new_hub()
    assert order_hub.retry_sweep(hub)
    assert order_hub.retry_sweep(hub)
    assert not order_hub.retry_sweep(hub)


def test_audit_grows_with_every_operation():
    hub = order_hub.new_hub()
    assert order_hub.place_order(hub)
    assert order_hub.audit_sweep(hub)
    assert order_hub.retry_sweep(hub)
    assert hub["audit_log"] == 3


def test_audit_cap_stops_everything():
    hub = order_hub.new_hub()
    while order_hub.audit_sweep(hub):
        pass
    assert hub["audit_log"] == order_hub.MAX_AUDIT
    assert not order_hub.place_order(hub)
    assert not order_hub.retry_sweep(hub)
