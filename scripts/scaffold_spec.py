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


def scaffold(name: str, root: Path) -> Path:
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
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--root", type=Path, default=Path("examples"))
    args = parser.parse_args()
    target = scaffold(args.name, args.root)
    print(f"scaffolded {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
