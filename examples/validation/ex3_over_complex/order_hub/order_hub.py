#!/usr/bin/env python3
"""order_hub -- a small order processor built around one shared hub.

Every operation routes through HUB, stamping the shared mode, audit log,
and dirty flag on its way. Mirrors specs/program_model/OrderHub.tla.
"""

from __future__ import annotations

MAX_ORDERS = 3
MAX_RETRIES = 2
MAX_AUDIT = 12


def new_hub() -> dict:
    return {
        "mode": 0,
        "orders": 0,
        "shipped": 0,
        "retries": 0,
        "audit_log": 0,
        "dirty": False,
    }


def _stamp(hub: dict, mode: int) -> None:
    hub["mode"] = mode
    hub["audit_log"] += 1
    hub["dirty"] = not hub["dirty"]


def place_order(hub: dict) -> bool:
    if hub["orders"] >= MAX_ORDERS or hub["audit_log"] >= MAX_AUDIT:
        return False
    hub["orders"] += 1
    _stamp(hub, 1)
    return True


def ship_order(hub: dict) -> bool:
    if hub["shipped"] >= hub["orders"] or hub["audit_log"] >= MAX_AUDIT:
        return False
    hub["shipped"] += 1
    _stamp(hub, 2)
    return True


def retry_sweep(hub: dict) -> bool:
    if hub["retries"] >= MAX_RETRIES or hub["audit_log"] >= MAX_AUDIT:
        return False
    hub["retries"] += 1
    _stamp(hub, 3)
    return True


def audit_sweep(hub: dict) -> bool:
    if hub["audit_log"] >= MAX_AUDIT:
        return False
    _stamp(hub, 4)
    return True
