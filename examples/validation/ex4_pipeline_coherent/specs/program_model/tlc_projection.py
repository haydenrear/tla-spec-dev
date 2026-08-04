"""State and output projections for the EV-01 decomposable fixture.

The output projection is deliberately CONTENT-BEARING, and the reason is the
MF-038 finding: that probe's oracles read directory existence and exit codes,
nothing read a value, a field, a count, or an enum, and all nine content bugs
survived. Its own first recommendation was "project file/field content into
model variables". This fixture takes that recommendation, so that the
seeded-fault table has a real corpus-side arm to measure instead of a
foregone conclusion.

The expected adapter output for every action is:

    {"action": <name>, "status": "applied",
     "ledger_size": int, "queue_size": int, "delivered_size": int}

`status` is always "applied" because every generated transition is an enabled
action -- so a program that returns a rejection where the model says the action
fired is caught here, and only here. The three counts are the off-by-one
detectors.
"""

from __future__ import annotations

from typing import Any


def _as_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (set, frozenset, list, tuple)):
        return {str(item) for item in value}
    if isinstance(value, dict):
        return {str(item) for item in value}
    return {str(value)}


def project_visible_state(state: dict[str, Any]) -> dict[str, Any]:
    """Identity over the six model variables, normalized to sorted lists.

    Nothing is hidden: the model has no representation-only state, so a
    projection that dropped a variable would be trimming the oracle.
    """
    return {
        name: sorted(_as_set(state.get(name, [])))
        for name in ("inbox", "accepted", "queue", "delivered", "failed", "ledger")
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
    return {
        "action": action,
        "status": "applied",
        "ledger_size": len(_as_set(after.get("ledger", []))),
        "queue_size": len(_as_set(after.get("queue", []))),
        "delivered_size": len(_as_set(after.get("delivered", []))),
    }
