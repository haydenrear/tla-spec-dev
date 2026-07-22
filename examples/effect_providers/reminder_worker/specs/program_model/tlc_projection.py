from __future__ import annotations

from typing import Any


STATE_FIELDS = (
    "scenario",
    "queueState",
    "outboxState",
    "notificationCount",
    "receiptState",
    "result",
)


def project_state(state: dict[str, Any]) -> dict[str, Any]:
    return {field: state[field] for field in STATE_FIELDS}


def project_output(*, projected_after: dict[str, Any], **_kwargs: Any) -> dict[str, str]:
    return {"status": str(projected_after["result"])}
