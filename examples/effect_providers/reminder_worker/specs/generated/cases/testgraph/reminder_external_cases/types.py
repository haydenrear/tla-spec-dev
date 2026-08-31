from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


class Unchecked:
    """An action argument this corpus could not recover from the state pair.

    MF-029. It is NOT None, "" or 0 -- those are values a model could
    legitimately produce, so an adapter comparing against one could pass by
    coincidence. UNCHECKED equals only itself, so any check expecting a
    concrete argument fails against it instead of passing vacuously.

    A case carrying UNCHECKED is still a real case and is never dropped: the
    sentinel marks the argument, it does not disqualify the transition.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNCHECKED"

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        return other is self

    def __ne__(self, other: Any) -> bool:
        return other is not self

    def __hash__(self) -> int:
        return hash("tla-spec-dev.UNCHECKED")


UNCHECKED = Unchecked()


@dataclass(frozen=True)
class StateGraphInput:
    action: str
    source_node: str
    target_node: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionMetadata:
    layer: str = "internal"
    controllability: str = "unit_direct"
    generates: frozenset[str] = frozenset(("spec_unit",))
    tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class StateGraphOutput:
    changed: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class StateGraphCase:
    name: str
    before: dict[str, Any]
    input: StateGraphInput
    output: Any
    after: dict[str, Any]
    labels: frozenset[str]
    schema_version: str = 'tla-testgraph.trace.v1'
    view: str = "internal"
    layer: str = "internal"
    controllability: str = "unit_direct"
    generates: frozenset[str] = frozenset(("spec_unit",))
    tags: frozenset[str] = frozenset()
    metadata: ActionMetadata = field(default_factory=ActionMetadata)
