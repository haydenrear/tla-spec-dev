from __future__ import annotations

from typing import Any


def project_visible_state(state: dict[str, Any]) -> dict[str, Any]:
    accounts = sorted(str(account) for account in _as_list(state.get("accounts", [])))
    carts = _project_carts(state.get("carts", {}))
    orders = _project_orders(state.get("orders", {}))
    outbox = [
        {"order_id": str(order_id), "event": "OrderAccepted"}
        for order_id in sorted(str(item) for item in _as_list(state.get("outbox", [])))
    ]
    projections = {
        str(order_id): str(status)
        for order_id, status in _as_dict(state.get("projections", {})).items()
        if status != "none"
    }
    return {
        "accounts": accounts,
        "carts": carts,
        "orders": orders,
        "outbox": outbox,
        "projections": projections,
    }


def project_adapter_output(
    *,
    after: dict[str, Any],
    projected_before: dict[str, Any],
    action: str,
    params: dict[str, Any],
    view: str,
    **_kwargs: Any,
) -> dict[str, Any]:
    if action == "RunFulfillmentWorker":
        return {"status": 200, "body": {"processed": len(projected_before.get("outbox", []))}}
    if action == "ProjectOrder":
        return {"status": 200, "body": {"processed": 1}}
    if action == "RunFulfillmentWorkerNoop":
        return {"status": 200, "body": {"processed": 0}}
    if view == "external":
        response = _response_for(after, params)
        return {
            "status": int(response["status"]),
            "body": _plain(response["body"]),
        }
    if action == "CreateAccount":
        return {"status": 201, "body": {"account": params["account"]}}
    if action == "AddCartItem":
        return {"status": 202, "body": {"account": params["account"], "sku": params["sku"]}}
    if action == "Checkout":
        return {"status": 202, "body": {"order": params["order"], "status": "accepted"}}
    raise ValueError(f"no adapter output projection for {view} action {action}")


def _response_for(state: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    response_key = params.get("client", params.get("account"))
    responses = _as_dict(state.get("responses", {}))
    if response_key not in responses:
        raise ValueError(f"response for {response_key!r} not found in TLC state")
    response = _as_dict(responses[response_key])
    if "status" not in response or "body" not in response:
        raise ValueError(f"malformed TLC response for {response_key!r}: {response!r}")
    return response


def _project_carts(value: Any) -> dict[str, list[str]]:
    carts: dict[str, list[str]] = {}
    for account, items in _as_dict(value).items():
        rendered = sorted(str(item) for item in _as_list(items))
        if rendered:
            carts[str(account)] = rendered
    return dict(sorted(carts.items()))


def _project_orders(value: Any) -> dict[str, dict[str, Any]]:
    orders: dict[str, dict[str, Any]] = {}
    for order_id, raw_order in _as_dict(value).items():
        order = _as_dict(raw_order)
        if order.get("status") == "none":
            continue
        orders[str(order_id)] = {
            "account": str(order["account"]),
            "items": sorted(str(item) for item in _as_list(order.get("items", []))),
            "status": str(order["status"]),
        }
    return dict(sorted(orders.items()))


def _as_dict(value: Any) -> dict[Any, Any]:
    if isinstance(value, dict):
        return value
    raise TypeError(f"expected TLC mapping, got {value!r}")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=repr)
    return [value]


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _plain(inner) for key, inner in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, tuple):
        return [_plain(inner) for inner in value]
    if isinstance(value, (set, frozenset)):
        return [_plain(inner) for inner in sorted(value, key=repr)]
    return value
