from __future__ import annotations

from typing import Any


def project_state(state: dict[str, Any]) -> dict[str, Any]:
    """Keep exactly the semantic fields exercised by the application adapter."""

    return {
        "scenario": str(state["scenario"]),
        "done": bool(state["done"]),
        "record": _plain(state["record"]),
        "result": _plain(state["result"]),
        "trace": _plain(state["trace"]),
        "outcome": str(state["scenario"]) if bool(state["done"]) else "not_run",
    }


def project_output(*, after: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
    return _plain(after["result"])


def outcome_label(*, after: dict[str, Any], **_kwargs: Any) -> str:
    return f"outcome:{after['outcome']}"


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _plain(inner) for key, inner in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (tuple, list)):
        return [_plain(inner) for inner in value]
    if isinstance(value, (set, frozenset)):
        return [_plain(inner) for inner in sorted(value, key=repr)]
    return value
