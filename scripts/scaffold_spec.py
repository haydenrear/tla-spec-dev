#!/usr/bin/env python3
"""Scaffold a new constrained TLA+ spec-double project."""

from __future__ import annotations

import argparse
from pathlib import Path


def title_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_") if part)


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def parse_views(value: str | None) -> set[str]:
    if not value:
        return set()
    views = {part.strip().lower() for part in value.split(",") if part.strip()}
    unknown = views - {"internal", "external"}
    if unknown:
        raise SystemExit(f"unsupported views: {', '.join(sorted(unknown))}")
    if "external" in views:
        views.add("internal")
    return views


def scaffold(name: str, root: Path, views: set[str] | None = None) -> Path:
    slug = name.replace("-", "_").lower()
    module = title_name(name)
    package = f"{slug}_spec"
    target = root / slug

    tla = f"""----------------------------- MODULE {module} -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
  Actors,
  Items,
  LimitOneActors,
  LimitTwoActors,
  NoReason

VARIABLES
  owned,
  limits,
  result

vars == << owned, limits, result >>

Init ==
  /\\ owned = [a \\in Actors |-> {{}}]
  /\\ limits = [
      a \\in Actors |->
        IF a \\in LimitOneActors THEN 1
        ELSE IF a \\in LimitTwoActors THEN 2
        ELSE 0
    ]
  /\\ result = [accepted |-> TRUE, reason |-> NoReason]

\\* @command CreateItem
\\* @result CreateItemResult
Create(a, i) ==
  IF Cardinality(owned[a]) >= limits[a]
  THEN
    /\\ result' = [accepted |-> FALSE, reason |-> "LIMIT_REACHED"]
    /\\ UNCHANGED << owned, limits >>
  ELSE
    /\\ owned' = [owned EXCEPT ![a] = @ \\cup {{i}}]
    /\\ result' = [accepted |-> TRUE, reason |-> NoReason]
    /\\ UNCHANGED limits

Next ==
  \\E a \\in Actors, i \\in Items:
    Create(a, i)

\\* @invariant LimitInvariant
LimitInvariant ==
  \\A a \\in Actors:
    Cardinality(owned[a]) <= limits[a]

Spec ==
  Init /\\ [][Next]_vars

=============================================================================
"""

    cfg = """SPECIFICATION Spec

CONSTANTS
  Actors = {a1, a2}
  Items = {i1, i2, i3}
  LimitOneActors = {a1}
  LimitTwoActors = {a2}
  NoReason = NoReason

INVARIANTS
  LimitInvariant
"""

    manifest = f"""module: {module}
package: {package}

state:
  {module}State:
    fields:
      owned:
        type: dict[ActorId, frozenset[ItemId]]
        tla: owned
      limits:
        type: dict[ActorId, int]
        tla: limits

types:
  ActorId:
    python: str
    source: Actors
  ItemId:
    python: str
    source: Items

commands:
  CreateItem:
    action: Create
    fields:
      actor_id:
        type: ActorId
        tla: a
      item_id:
        type: ItemId
        tla: i

results:
  CreateItemResult:
    fields:
      accepted:
        type: bool
      reason:
        type: str | None
        default: None

ports:
  {module}Port:
    methods:
      create_item:
        command: CreateItem
        result: CreateItemResult
      snapshot:
        result: {module}State

invariants:
  - LimitInvariant

finite_model:
  Actors:
    values:
      - a1
      - a2
  Items:
    values:
      - i1
      - i2
      - i3
  Limits:
    values:
      a1: 1
      a2: 2

generators:
  users:
    source: Actors
  workspaces:
    source: Items
  traces:
    max_depth: 8

fake:
  class: {module}SpecDouble
  actions:
    create_item:
      template: bounded_set_add
      state_field: owned
      limit_field: limits
      owner_command_field: actor_id
      item_command_field: item_id
      reject_reason: LIMIT_REACHED

invariant_templates:
  LimitInvariant:
    template: bounded_set_size
    collection_field: owned
    limit_field: limits
"""

    write_if_missing(target / f"{module}.tla", tla)
    write_if_missing(target / "MC.cfg", cfg)
    write_if_missing(target / "spec_manifest.yaml", manifest)
    (target / "generated").mkdir(exist_ok=True)
    (target / "tests").mkdir(exist_ok=True)
    write_if_missing(
        target / ".history" / "README.md",
        "# Spec Workflow History\n\nThis directory is append-only history for close records.\n",
    )
    if views:
        scaffold_views(target, module, views)
    return target


def scaffold_views(target: Path, module: str, views: set[str]) -> None:
    model_dir = target / "model"
    write_if_missing(
        model_dir / "Core.tla",
        f"""----------------------------- MODULE Core -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
  Actors,
  Items,
  NoReason

Result(accepted, reason) ==
  [accepted |-> accepted, reason |-> reason]

=============================================================================
""",
    )

    if "internal" in views:
        write_if_missing(
            model_dir / "Internal.tla",
            """----------------------------- MODULE Internal -----------------------------
EXTENDS Core

VARIABLES
  owned,
  result,
  lastInternalAction

InternalVars == << owned, result, lastInternalAction >>

InternalInit ==
  /\\ owned = [a \\in Actors |-> {}]
  /\\ result = Result(TRUE, NoReason)
  /\\ lastInternalAction = [name |-> "Init", params |-> [ ]]

\\* @action AcceptRequest
\\* @layer internal
\\* @controllability unit_direct
AcceptRequest(a, i) ==
  /\\ owned' = [owned EXCEPT ![a] = @ \\cup {i}]
  /\\ result' = Result(TRUE, NoReason)
  /\\ lastInternalAction' = [
       name |-> "AcceptRequest",
       params |-> [actor |-> a, item |-> i]
     ]

InternalNext ==
  \\E a \\in Actors, i \\in Items:
    AcceptRequest(a, i)

InternalSpec ==
  InternalInit /\\ [][InternalNext]_InternalVars

=============================================================================
""",
        )

    if "external" in views:
        write_if_missing(
            model_dir / "External.tla",
            """----------------------------- MODULE External -----------------------------
EXTENDS Internal

VARIABLES
  visibleResult,
  lastExternalAction

ExternalVars == << owned, result, lastInternalAction, visibleResult, lastExternalAction >>

ExternalInit ==
  /\\ InternalInit
  /\\ visibleResult = [a \\in Actors |-> NoReason]
  /\\ lastExternalAction = [name |-> "Init", params |-> [ ]]

\\* @action Submit
\\* @layer external
\\* @controllability e2e_direct
Submit(a, i) ==
  /\\ AcceptRequest(a, i)
  /\\ visibleResult' = [visibleResult EXCEPT ![a] = "accepted"]
  /\\ lastExternalAction' = [
       name |-> "Submit",
       params |-> [actor |-> a, item |-> i]
     ]

\\* @action HiddenInternalProgress
\\* @layer internal
\\* @controllability hidden
HiddenInternalProgress ==
  /\\ InternalNext
  /\\ UNCHANGED << visibleResult, lastExternalAction >>

ExternalNext ==
  \\/ \\E a \\in Actors, i \\in Items:
      Submit(a, i)
  \\/ HiddenInternalProgress

ExternalSpec ==
  ExternalInit /\\ [][ExternalNext]_ExternalVars

=============================================================================
""",
        )

    write_if_missing(
        model_dir / "DesiredCore.tla",
        f"""-------------------------- MODULE DesiredCore --------------------------
EXTENDS Core

\\* Active desired semantic overlay for {module}. While a spec workflow is open,
\\* put shared target semantics here. When the workflow closes, promote the
\\* converged contents into Core.tla and delete DesiredCore.tla.

=============================================================================
""",
    )
    if "internal" in views:
        write_if_missing(
            model_dir / "DesiredInternal.tla",
            """------------------------ MODULE DesiredInternal ------------------------
EXTENDS DesiredCore, Internal

\\* Active desired internal projection. While a spec workflow is open, put
\\* unit-level target transitions/assertions here. When the workflow closes,
\\* promote the converged contents into Internal.tla and delete this module.

DesiredInternalSpec == InternalSpec

=============================================================================
""",
        )
    if "external" in views:
        write_if_missing(
            model_dir / "DesiredExternal.tla",
            """------------------------ MODULE DesiredExternal ------------------------
EXTENDS DesiredInternal, External

\\* Active desired external projection. This should wrap/project desired
\\* internal semantics, not redefine independent business behavior. When the
\\* workflow closes, promote the converged contents into External.tla and delete
\\* this module.

DesiredExternalSpec == ExternalSpec

=============================================================================
""",
        )
    write_if_missing(
        model_dir / "actions.yml",
        """actions:
  AcceptRequest:
    layer: internal
    controllability: unit_direct
    generates:
      - spec_unit
  Submit:
    layer: external
    controllability: e2e_direct
    generates:
      - testgraph
  HiddenInternalProgress:
    layer: internal
    controllability: hidden
    generates: []
""",
    )

    if "external" not in views:
        return

    testgraph_dir = target / "testgraph"
    write_if_missing(
        testgraph_dir / "bindings.yml",
        """actions:
  Submit:
    layer: external
    controllability: e2e_direct
    kind: request-http
    adapter: replace_with_project.adapters.e2e:SubmitHttpAdapter
    projector: replace_with_project.adapters.e2e:RequestStateProjector
""",
    )
    write_if_missing(
        testgraph_dir / "selectors.yml",
        """suites:
  smoke:
    view: external
    max_traces: 10
    include_tags: []
  fault:
    view: external
    include_actions: []
""",
    )
    write_if_missing(
        testgraph_dir / "assertions.yml",
        """defaults:
  mode: eventually
  timeout_seconds: 15
  poll_interval_seconds: 0.25
actions:
  Submit:
    immediate_response:
      status_in: [200, 201, 202]
""",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--root", type=Path, default=Path("examples"))
    parser.add_argument("--views", help="Optional comma-separated views to scaffold, for example internal,external")
    args = parser.parse_args()
    target = scaffold(args.name, args.root, parse_views(args.views))
    print(f"scaffolded {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
