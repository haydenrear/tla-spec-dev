#!/usr/bin/env python3
"""Scaffold a standalone tutorial/example spec-double project.

This is the TUTORIAL path. It creates a small, self-contained spec whose
manifest drives the spec-double codegen in ``scripts/generate_python.py``.

For onboarding a real repository, use ``tla-spec-dev scaffold project``
instead, which creates ``specs/program_model`` as the accepted baseline.

Both paths emit the SAME baseline shape, because there is only one accepted
shape: Core.tla + Internal.tla/.cfg + External.tla/.cfg + actions.yml +
adapters.py + case_adapters.toml + testgraph_bindings.yml. A single-module spec
with no External view cannot generate Test Graph cases, so it can never be
validated against its public surface. See references/testgraph_adapters.md.

While a spec workflow is open, the active desired overlays DesiredCore.tla,
DesiredInternal.tla, and DesiredExternal.tla sit alongside the baseline. They
are promoted into the baseline and deleted at closeout; an accepted, closed
model must not retain them.
"""

from __future__ import annotations

import argparse
from pathlib import Path


# Both views, always. A view-less scaffold is not a supported output.
DEFAULT_VIEWS = frozenset({"internal", "external"})


def title_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_") if part)


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def parse_views(value: str | None) -> set[str]:
    """Parse --views. Both views are always included; extras are additive.

    The external view is a projection of the internal one, so asking for
    external always implies internal.
    """
    if not value:
        return set(DEFAULT_VIEWS)
    views = {part.strip().lower() for part in value.split(",") if part.strip()}
    unknown = views - {"internal", "external"}
    if unknown:
        raise SystemExit(f"unsupported views: {', '.join(sorted(unknown))}")
    return set(DEFAULT_VIEWS | views)


CORE_TLA = """------------------------------- MODULE Core -------------------------------
\\* Shared constants and operators. Internal.tla and External.tla both EXTEND
\\* this module.
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
  Actors,
  Items,
  LimitOneActors,
  LimitTwoActors,
  NoReason

\\* Per-actor capacity. The bounded model puts each actor in exactly one of the
\\* limit sets below.
Limit(a) ==
  IF a \\in LimitOneActors THEN 1
  ELSE IF a \\in LimitTwoActors THEN 2
  ELSE 0

Result(accepted, reason) == [accepted |-> accepted, reason |-> reason]

=============================================================================
"""

INTERNAL_TLA = """----------------------------- MODULE Internal -----------------------------
\\* INTERNAL VIEW: fine-grained program state.
\\* Actions here generate spec-unit cases, executed by the spec-unit adapters in
\\* adapters.py and mapped by case_adapters.toml.
EXTENDS Core

VARIABLES owned, limits, result, lastInternalAction

InternalVars == << owned, limits, result, lastInternalAction >>

InternalInit ==
  /\\ owned = [a \\in Actors |-> {}]
  /\\ limits = [a \\in Actors |-> Limit(a)]
  /\\ result = Result(TRUE, NoReason)
  /\\ lastInternalAction = [name |-> "Init", params |-> <<>>]

\\* @action Create
\\* @layer internal
\\* @controllability unit_direct
Create(a, i) ==
  /\\ i \\notin owned[a]
  /\\ Cardinality(owned[a]) < limits[a]
  /\\ owned' = [owned EXCEPT ![a] = @ \\cup {i}]
  /\\ result' = Result(TRUE, NoReason)
  /\\ UNCHANGED limits
  /\\ lastInternalAction' = [name |-> "Create", params |-> [actor |-> a, item |-> i]]

\\* @action CreateRejected
\\* @layer internal
\\* @controllability unit_direct
CreateRejected(a, i) ==
  /\\ Cardinality(owned[a]) >= limits[a]
  /\\ result' = Result(FALSE, "LIMIT_REACHED")
  /\\ UNCHANGED << owned, limits >>
  /\\ lastInternalAction' = [name |-> "CreateRejected", params |-> [actor |-> a, item |-> i]]

InternalNext ==
  \\/ \\E a \\in Actors, i \\in Items : Create(a, i)
  \\/ \\E a \\in Actors, i \\in Items : CreateRejected(a, i)

\\* @invariant LimitInvariant
LimitInvariant ==
  \\A a \\in Actors : Cardinality(owned[a]) <= limits[a]

InternalSpec == InternalInit /\\ [][InternalNext]_InternalVars

=============================================================================
"""

INTERNAL_CFG = """SPECIFICATION InternalSpec
INVARIANT LimitInvariant

\\* The bounded model is intentionally terminating: once every actor is at its
\\* limit only rejections remain. That is exhaustion of the finite model, not a
\\* bug.
CHECK_DEADLOCK FALSE

CONSTANTS
  Actors = {a1, a2}
  Items = {i1, i2, i3}
  LimitOneActors = {a1}
  LimitTwoActors = {a2}
  NoReason = NoReason
"""

EXTERNAL_TLA = """----------------------------- MODULE External -----------------------------
\\* EXTERNAL VIEW: what a harness can drive or observe from outside. This is a
\\* projection of the internal semantics, not an independent model.
\\*
\\* Actions here generate Test Graph cases, executed by the Test Graph adapters
\\* in adapters.py and mapped by testgraph_bindings.yml.
\\*
\\* External does NOT mean distributed. For a CLI it is command invocations and
\\* filesystem assertions; for a library, the public API surface.
EXTENDS Internal

CONSTANTS Clients

VARIABLES responses, lastExternalAction

ExternalVars == << InternalVars, responses, lastExternalAction >>

ExternalInit ==
  /\\ InternalInit
  /\\ responses = [c \\in Clients |-> [status |-> 0, body |-> <<>>]]
  /\\ lastExternalAction = [name |-> "Init", params |-> <<>>]

MarkExternal(actionName, params) ==
  lastExternalAction' = [name |-> actionName, params |-> params]

\\* @action Submit
\\* @layer external
\\* @controllability e2e_direct
Submit(c, a, i) ==
  /\\ c \\in Clients
  /\\ Create(a, i)
  /\\ responses' = [responses EXCEPT ![c] = [status |-> 201, body |-> [actor |-> a, item |-> i]]]
  /\\ MarkExternal("Submit", [client |-> c, actor |-> a, item |-> i])

\\* @action SubmitRejected
\\* @layer external
\\* @controllability e2e_direct
SubmitRejected(c, a, i) ==
  /\\ c \\in Clients
  /\\ CreateRejected(a, i)
  /\\ responses' = [responses EXCEPT ![c] = [status |-> 409, body |-> [error |-> "LIMIT_REACHED"]]]
  /\\ MarkExternal("SubmitRejected", [client |-> c, actor |-> a, item |-> i])

\\* @action SubmitDuplicate
\\* @layer external
\\* @controllability e2e_direct
SubmitDuplicate(c, a, i) ==
  /\\ c \\in Clients
  /\\ i \\in owned[a]
  /\\ UNCHANGED InternalVars
  /\\ responses' = [responses EXCEPT ![c] = [status |-> 200, body |-> [actor |-> a, item |-> i, idempotent |-> TRUE]]]
  /\\ MarkExternal("SubmitDuplicate", [client |-> c, actor |-> a, item |-> i])

\\* @action HiddenInternalProgress
\\* @layer internal
\\* @controllability hidden
HiddenInternalProgress ==
  /\\ InternalNext
  /\\ UNCHANGED << responses, lastExternalAction >>

ExternalNext ==
  \\/ \\E c \\in Clients, a \\in Actors, i \\in Items : Submit(c, a, i)
  \\/ \\E c \\in Clients, a \\in Actors, i \\in Items : SubmitRejected(c, a, i)
  \\/ \\E c \\in Clients, a \\in Actors, i \\in Items : SubmitDuplicate(c, a, i)
  \\/ HiddenInternalProgress

\\* @invariant ExternalInvariant
ExternalInvariant ==
  /\\ LimitInvariant
  /\\ \\A c \\in Clients : responses[c].status \\in {0, 200, 201, 409}

Spec == ExternalInit /\\ [][ExternalNext]_ExternalVars
Invariant == ExternalInvariant

=============================================================================
"""

EXTERNAL_CFG = """SPECIFICATION Spec
INVARIANT Invariant

\\* See Internal.cfg: the bounded model is intentionally terminating.
CHECK_DEADLOCK FALSE

CONSTANTS
  Clients = {c1}
  Actors = {a1, a2}
  Items = {i1, i2, i3}
  LimitOneActors = {a1}
  LimitTwoActors = {a2}
  NoReason = NoReason
"""

ACTIONS_YML = """# Which view each action belongs to, and what it generates.
#
#   layer: internal -> spec-unit cases  (case_adapters.toml)
#   layer: external -> Test Graph cases (testgraph_bindings.yml)
#   controllability: hidden -> generates nothing.
#   effect_ports: typed semantic ports required while this case executes.
actions:
  Create:
    layer: internal
    controllability: unit_direct
    generates:
      - spec_unit
    effect_ports: []
  CreateRejected:
    layer: internal
    controllability: unit_direct
    generates:
      - spec_unit
    effect_ports: []
  Submit:
    layer: external
    controllability: e2e_direct
    generates:
      - testgraph
    effect_ports: []
  SubmitRejected:
    layer: external
    controllability: e2e_direct
    generates:
      - testgraph
    effect_ports: []
  SubmitDuplicate:
    layer: external
    controllability: e2e_direct
    generates:
      - testgraph
    effect_ports: []
  HiddenInternalProgress:
    layer: internal
    controllability: hidden
    generates: []
    effect_ports: []
"""

CASE_ADAPTERS_TOML = """# SPEC-UNIT ADAPTERS (internal view).
# Every Internal.tla action with `generates: [spec_unit]` needs an entry.
# Semantic effects are separate from passive `effects:` observation. For each
# manifest port with `role: effect` named by an action's `effect_ports`, add:
#
# [effect_providers.FilesystemPort]
# provider = "providers:filesystem_provider"

[adapters.Create]
adapter = "adapters:CreateInternalAdapter"
kind = "tutorial-internal"

[adapters.CreateRejected]
adapter = "adapters:CreateInternalAdapter"
kind = "tutorial-internal"
"""

TESTGRAPH_BINDINGS_YML = """# TEST GRAPH ADAPTERS (external view).
# Every External.tla action with `generates: [testgraph]` needs an entry.
# Read references/testgraph_adapters.md before editing this file.
#
#   channel             -> HOW the program is driven: http/cli/fs/queue/k8s
#   adapter             -> drives the public action
#   projector           -> observes real state, projected into the TLA shape
#   expected_projection -> expected state, usually a projection of case.after
#   assertion           -> compares the two and writes per-case evidence
#
# MF-015 external channel enforcement (hard gate, no override):
#   * every binding declares a `channel`;
#   * no adapter/projector/expected_projection/assertion module imports
#     `external.production_package`, directly or via a first-party helper;
#   * `external.port_bindings` names each port double or real, at least one
#     real -- all-doubles is a spec-unit run, never a Test Graph node.
external:
  production_package: REPLACE_ME_program_package
  port_bindings:
    REPLACE_ME_Port: real

actions:
  Submit:
    view: external
    channel: http
    layer: external
    controllability: e2e_direct
    kind: tutorial-external
    adapter: adapters:SubmitExternalAdapter
    projector: adapters:ProgramStateProjector
    expected_projection: adapters:ExpectedProgramProjection
    assertion: adapters:ProjectedStateAssertion
  SubmitRejected:
    view: external
    channel: http
    layer: external
    controllability: e2e_direct
    kind: tutorial-external
    adapter: adapters:SubmitExternalAdapter
    projector: adapters:ProgramStateProjector
    expected_projection: adapters:ExpectedProgramProjection
    assertion: adapters:ProjectedStateAssertion
  SubmitDuplicate:
    view: external
    channel: http
    layer: external
    controllability: e2e_direct
    kind: tutorial-external
    adapter: adapters:SubmitExternalAdapter
    projector: adapters:ProgramStateProjector
    expected_projection: adapters:ExpectedProgramProjection
    assertion: adapters:ProjectedStateAssertion
"""

ADAPTERS_PY = '''"""Adapters for this tutorial spec.

Carries BOTH executable views. Neither is optional:

- Spec-unit adapters (internal view) drive real internal boundaries for cases
  generated from Internal.tla. Mapped by case_adapters.toml.
- Test Graph adapters (external view) drive the real public surface for cases
  generated from External.tla, then project observed state back into the model
  shape. Mapped by testgraph_bindings.yml.

Read references/testgraph_adapters.md for the hook order and the
projected-state assertion contract. Worked reference implementation:
examples/distributed_history/specs/program_model/adapters.py

SCAFFOLD: replace each NotImplementedError with a call into the real boundary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spec_double_compiler.runtime import CaseRunResult


def _state(value: Any) -> dict[str, Any]:
    return json.loads(json.dumps(value, sort_keys=True))


# --- Spec-unit adapters (internal view) -> case_adapters.toml ---------------
# Hook order per batch: setup_all -> (run per case) -> teardown_all.


class _InternalAdapter:
    def setup_all(self, context: Any) -> None:
        """Suite-wide internal setup."""

    def teardown_all(self, context: Any) -> None:
        """Suite-wide internal teardown."""

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        store = self.load(case.before)
        output = self.apply(store, case.input.params)
        return CaseRunResult(output=output, after=self.snapshot(store))

    def load(self, before: dict[str, Any]) -> Any:
        raise NotImplementedError("load the TLA `before` state into the real component")

    def snapshot(self, store: Any) -> dict[str, Any]:
        raise NotImplementedError("project real internal state back into the Internal.tla shape")

    def apply(self, store: Any, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class CreateInternalAdapter(_InternalAdapter):
    def apply(self, store: Any, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("call the real Create boundary")


# --- Test Graph adapters (external view) -> testgraph_bindings.yml ----------
# Hook order per batch:
#   setup_all -> for each case: setup -> run -> assertion -> teardown
#             -> teardown_all
#
# `setup` must establish the abstract pre-state before each case. That is what
# makes leftover residue from a previous case visible instead of silently
# passing.


class _ExternalAdapter:
    def setup_all(self, context: Any) -> None:
        """Suite-wide external setup: start/await the app, reset shared state."""

    def teardown_all(self, context: Any) -> None:
        """Suite-wide external teardown."""

    def setup(self, context: Any) -> None:
        raise NotImplementedError(
            "materialize the TLA `before` state on the real public surface "
            "(debug/admin endpoint, fixture files, seeded DB, ...)"
        )

    def teardown(self, context: Any) -> None:
        """Clear per-case state so the next case starts from its own `before`."""

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        return CaseRunResult(output=self.apply(case.input.params))

    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class SubmitExternalAdapter(_ExternalAdapter):
    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("drive the real public Submit surface")


# --- Projected-state assertion (external view) ------------------------------
# expected = ExpectedProgramProjection.expected_state(context)  (from case.after)
# actual   = ProgramStateProjector.observe(context)             (from real system)
# compare  = ProjectedStateAssertion.assert_state(context)


class ExpectedProgramProjection:
    def expected_state(self, context: Any) -> dict[str, Any]:
        return _visible_projection(context.case.after)


class ProgramStateProjector:
    def observe(self, context: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "observe the real system's visible state and pass it through "
            "_visible_projection so it can be compared with case.after"
        )


class ProjectedStateAssertion:
    def assert_state(self, context: Any) -> None:
        expected = _state(context.expected)
        actual = _state(context.actual)
        artifact = context.work_dir / "program-state.json"
        payload = {
            "case": context.case.name,
            "action": context.case.input.action,
            "params": dict(context.case.input.params),
            "expected_program_state": expected,
            "actual_projected_program_state": actual,
            "matched": actual == expected,
        }
        artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
        if actual != expected:
            raise AssertionError(
                f"projected program state mismatch for {context.case.name}; wrote {artifact}"
            )


def _visible_projection(state: dict[str, Any]) -> dict[str, Any]:
    """Keep only what a caller can observe.

    Both the expected projection and the live projector go through this, so the
    two sides are always compared in the same shape.
    """
    return {"owned": {str(actor): sorted(items) for actor, items in dict(state.get("owned", {})).items()}}
'''

TLC_PROJECTION_PY = '''"""Project raw TLC states into the shapes the generated cases use.

SCAFFOLD: mirror the responses declared in External.tla. Reference:
examples/distributed_history/specs/program_model/tlc_projection.py
"""

from __future__ import annotations

from typing import Any


def project_visible_state(state: dict[str, Any]) -> dict[str, Any]:
    owned = {
        str(actor): sorted(str(item) for item in _as_list(items))
        for actor, items in _as_dict(state.get("owned", {})).items()
    }
    return {"owned": dict(sorted(owned.items()))}


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
    if action == "Create":
        return {"accepted": True, "reason": None}
    if action == "CreateRejected":
        return {"accepted": False, "reason": "LIMIT_REACHED"}
    raise ValueError(f"no adapter output projection for {view} action {action}")


def _response_for(state: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    response_key = params.get("client")
    responses = _as_dict(state.get("responses", {}))
    if response_key not in responses:
        raise ValueError(f"response for {response_key!r} not found in TLC state")
    return _as_dict(responses[response_key])


def _as_dict(value: Any) -> dict[Any, Any]:
    if isinstance(value, dict):
        return value
    raise TypeError(f"expected TLC mapping, got {value!r}")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=repr)
    return [value]


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _plain(inner) for key, inner in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (tuple, set, frozenset)):
        return [_plain(inner) for inner in sorted(value, key=repr)]
    return value
'''


def manifest(module: str, package: str) -> str:
    return f"""module: {module}
package: {package}

views:
  internal:
    module: Internal.tla
    config: Internal.cfg
    spec: InternalSpec
    generates: spec_unit
    adapter_mapping: case_adapters.toml
  external:
    module: External.tla
    config: External.cfg
    spec: Spec
    generates: testgraph
    adapter_mapping: testgraph_bindings.yml

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
    role: application
    methods:
      create_item:
        command: CreateItem
        result: CreateItemResult
      snapshot:
        result: {module}State

invariants:
  - LimitInvariant
  - ExternalInvariant

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

case_codegen:
  style: explicit_transition_cases
  projection: tlc_projection.py
"""


def readme(module: str) -> str:
    return f"""# {module} (tutorial spec)

A standalone example spec-double project. For onboarding a real repository use
`tla-spec-dev scaffold project` instead.

This uses the one accepted baseline shape. It is not complete until it has:

- `Core.tla` — shared constants and operators
- `Internal.tla` / `Internal.cfg` — internal view -> spec-unit cases
- `External.tla` / `External.cfg` — external view -> Test Graph cases
- `actions.yml` — per-action layer, controllability, what it generates
- `adapters.py` — spec-unit adapters AND Test Graph adapters/projector/assertion
- `case_adapters.toml` — internal action -> spec-unit adapter
- `testgraph_bindings.yml` — external action -> Test Graph adapter
- `tlc_projection.py` — TLC state -> generated-case shapes
- `spec_manifest.yaml` — ports, invariants, finite model, codegen config

Test Graph adapters are foundational to every project. Without the External
view and its adapters, the public surface is never validated.

`Desired*.tla` are active overlays for an open spec workflow. Promote them into
the baseline and delete them at closeout.

Validate both views:

```bash
scripts/run_tlc.sh Internal.tla Internal.cfg
scripts/run_tlc.sh External.tla External.cfg
```
"""


def scaffold(name: str, root: Path, views: set[str] | None = None) -> Path:
    slug = name.replace("-", "_").lower()
    module = title_name(name)
    package = f"{slug}_spec"
    target = root / slug
    views = set(DEFAULT_VIEWS | (views or set()))

    write_if_missing(target / "README.md", readme(module))
    write_if_missing(target / "Core.tla", CORE_TLA)
    write_if_missing(target / "Internal.tla", INTERNAL_TLA)
    write_if_missing(target / "Internal.cfg", INTERNAL_CFG)
    write_if_missing(target / "External.tla", EXTERNAL_TLA)
    write_if_missing(target / "External.cfg", EXTERNAL_CFG)
    write_if_missing(target / "actions.yml", ACTIONS_YML)
    write_if_missing(target / "adapters.py", ADAPTERS_PY)
    write_if_missing(target / "case_adapters.toml", CASE_ADAPTERS_TOML)
    write_if_missing(target / "testgraph_bindings.yml", TESTGRAPH_BINDINGS_YML)
    write_if_missing(target / "tlc_projection.py", TLC_PROJECTION_PY)
    write_if_missing(target / "spec_manifest.yaml", manifest(module, package))

    scaffold_desired_overlays(target, module)

    (target / "generated").mkdir(exist_ok=True)
    (target / "tests").mkdir(exist_ok=True)
    write_if_missing(
        target / ".history" / "README.md",
        "# Spec Workflow History\n\nThis directory is append-only history for close records.\n",
    )
    return target


def scaffold_desired_overlays(target: Path, module: str) -> None:
    """Active desired overlays for an open spec workflow.

    Promoted into Core/Internal/External at closeout, then deleted. An accepted,
    closed model must not retain them.
    """
    write_if_missing(
        target / "DesiredCore.tla",
        f"""-------------------------- MODULE DesiredCore --------------------------
EXTENDS Core

\\* Active desired semantic overlay for {module}. While a spec workflow is open,
\\* put shared target semantics here. When the workflow closes, promote the
\\* converged contents into Core.tla and delete DesiredCore.tla.

=============================================================================
""",
    )
    write_if_missing(
        target / "DesiredInternal.tla",
        """------------------------ MODULE DesiredInternal ------------------------
EXTENDS DesiredCore, Internal

\\* Active desired internal projection. While a spec workflow is open, put
\\* unit-level target transitions/assertions here. When the workflow closes,
\\* promote the converged contents into Internal.tla and delete this module.

DesiredInternalSpec == InternalSpec

=============================================================================
""",
    )
    write_if_missing(
        target / "DesiredExternal.tla",
        """------------------------ MODULE DesiredExternal ------------------------
EXTENDS DesiredInternal, External

\\* Active desired external projection. This should wrap/project desired
\\* internal semantics, not redefine independent business behavior. When the
\\* workflow closes, promote the converged contents into External.tla and delete
\\* this module.

DesiredExternalSpec == Spec

=============================================================================
""",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--root", type=Path, default=Path("examples"))
    parser.add_argument(
        "--views",
        help="Views to scaffold. Both internal and external are always emitted; this flag is additive.",
    )
    args = parser.parse_args()
    target = scaffold(args.name, args.root, parse_views(args.views))
    print(f"scaffolded {target}")
    print(
        "\nBoth views emitted. Implement the adapters in adapters.py and map every action in\n"
        "case_adapters.toml (internal) and testgraph_bindings.yml (external).\n"
        "Read references/testgraph_adapters.md."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
