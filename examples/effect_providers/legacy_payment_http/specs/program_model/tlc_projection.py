from __future__ import annotations

from typing import Any


FIELDS = ("completed", "outcome", "decision", "reason", "referenceClass", "attempts")


def project_state(state: dict[str, Any]) -> dict[str, Any]:
    return {field: state[field] for field in FIELDS}


def project_output(*, after: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
    return {
        "decision": str(after["decision"]),
        "reason": str(after["reason"]),
        "authorization_reference": str(after["referenceClass"]),
        "attempts": int(after["attempts"]),
    }

