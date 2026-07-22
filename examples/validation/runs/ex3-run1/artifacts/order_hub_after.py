#!/usr/bin/env python3
"""order_hub -- a small order processor built around one shared hub.

Every operation routes through HUB and is counted in the audit log; the
audit cap stops the world. Mirrors specs/program_model/OrderHub.tla.
"""

from __future__ import annotations

MAX_ORDERS = 3
MAX_RETRIES = 2
MAX_AUDIT = 12


def new_hub() -> dict:
    return {
        "orders": 0,
        "shipped": 0,
        "retries": 0,
        "audit_log": 0,
    }


def _record(hub: dict) -> None:
    hub["audit_log"] += 1


def place_order(hub: dict) -> bool:
    if hub["orders"] >= MAX_ORDERS or hub["audit_log"] >= MAX_AUDIT:
        return False
    hub["orders"] += 1
    _record(hub)
    return True


def ship_order(hub: dict) -> bool:
    if hub["shipped"] >= hub["orders"] or hub["audit_log"] >= MAX_AUDIT:
        return False
    hub["shipped"] += 1
    _record(hub)
    return True


def retry_sweep(hub: dict) -> bool:
    if hub["retries"] >= MAX_RETRIES or hub["audit_log"] >= MAX_AUDIT:
        return False
    hub["retries"] += 1
    _record(hub)
    return True


def audit_sweep(hub: dict) -> bool:
    if hub["audit_log"] >= MAX_AUDIT:
        return False
    _record(hub)
    return True
