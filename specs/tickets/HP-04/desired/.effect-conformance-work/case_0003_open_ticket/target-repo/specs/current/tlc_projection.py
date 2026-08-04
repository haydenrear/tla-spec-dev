"""Project raw TLC states into the shapes the generated cases use.

`project_visible_state` turns a TLC state into the externally observable
projection. `project_adapter_output` derives the output a correct adapter run
should produce for a given action, so generated cases carry an expected output
as well as an expected state.

SCAFFOLD: mirror the placeholder responses in External.tla. Reference:
examples/distributed_history/specs/program_model/tlc_projection.py
"""

from __future__ import annotations

from typing import Any


def project_visible_state(state: dict[str, Any]) -> dict[str, Any]:
    owners = sorted(str(owner) for owner in _as_list(state.get("owners", [])))
    records = {
        str(record_id): {
            "owner": str(_as_dict(record)["owner"]),
            "status": str(_as_dict(record)["status"]),
        }
        for record_id, record in _as_dict(state.get("records", {})).items()
        if _as_dict(record).get("status") != "none"
    }
    projections = {
        str(record_id): str(status)
        for record_id, status in _as_dict(state.get("projections", {})).items()
        if status != "none"
    }
    return {
        "owners": owners,
        "records": dict(sorted(records.items())),
        "projections": dict(sorted(projections.items())),
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
    if view == "external":
        response = _response_for(after, params)
        return {"status": int(response["status"]), "body": _plain(response["body"])}
    if action == "RegisterActor":
        return {"status": 201, "body": {"actor": params["actor"]}}
    if action == "AcceptRecord":
        return {"status": 202, "body": {"record": params["record"], "status": "accepted"}}
    if action == "PublishRecord":
        return {"status": 200, "body": {"processed": 1}}
    raise ValueError(f"no adapter output projection for {view} action {action}")


def _response_for(state: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    response_key = params.get("client")
    responses = _as_dict(state.get("responses", {}))
    if response_key not in responses:
        raise ValueError(f"response for {response_key!r} not found in TLC state")
    response = _as_dict(responses[response_key])
    if "status" not in response or "body" not in response:
        raise ValueError(f"malformed TLC response for {response_key!r}: {response!r}")
    return response


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
