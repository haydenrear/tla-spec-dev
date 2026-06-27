from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


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
