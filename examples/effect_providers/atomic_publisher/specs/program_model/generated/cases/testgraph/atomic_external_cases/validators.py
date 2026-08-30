from __future__ import annotations

from .types import StateGraphCase


def assert_case_replays(case: StateGraphCase) -> None:
    changed = {
        field: {"before": case.before.get(field), "after": case.after.get(field)}
        for field in sorted(set(case.before) | set(case.after))
        if case.before.get(field) != case.after.get(field)
    }
    if hasattr(case.output, "changed"):
        assert case.output.changed == changed
