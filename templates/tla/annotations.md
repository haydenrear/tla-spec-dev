# TLA+ Annotation And Manifest Pattern

Raw TLA+ is not always enough to generate clean Python APIs. Use comments
and `spec_manifest.yaml` to map formal concepts to generated Python
concepts.

## Recommended TLA+ Shape

- `EXTENDS Naturals, FiniteSets, Sequences, TLC` as needed.
- Define finite `CONSTANTS` for model domains.
- Define `VARIABLES` for centralized semantic state.
- Define `Init`.
- Define one action per command.
- Define explicit accept/reject behavior when useful.
- Define `Next` as a disjunction of actions.
- Define invariants.
- Define trace-friendly state labels when useful.
- Avoid production infrastructure concerns unless semantically relevant.

## Comment Hints

Use stable comments above actions and invariants so agents can retrieve
small relevant regions:

```tla
\* @command CreateWorkspace
\* @result CreateWorkspaceResult
\* @port WorkspacePort.create_workspace
Create(u, w) ==
  ...

\* @invariant WorkspaceLimitInvariant
WorkspaceLimitInvariant ==
  ...
```

These comments are hints. The manifest is the API contract.

## Manifest Shape

```yaml
module: Workspace
package: workspace_spec

state:
  WorkspaceState:
    fields:
      owned:
        type: dict[UserId, frozenset[WorkspaceId]]
        tla: owned
      limits:
        type: dict[UserId, int]
        tla: limits

types:
  UserId:
    python: str
    source: Users
  WorkspaceId:
    python: str
    source: Workspaces

commands:
  CreateWorkspace:
    action: Create
    fields:
      user_id:
        type: UserId
        tla: u
      workspace_id:
        type: WorkspaceId
        tla: w

results:
  CreateWorkspaceResult:
    fields:
      accepted:
        type: bool
      reason:
        type: str | None
        default: None

ports:
  WorkspacePort:
    methods:
      create_workspace:
        command: CreateWorkspace
        result: CreateWorkspaceResult
      snapshot:
        result: WorkspaceState

invariants:
  - WorkspaceLimitInvariant

generators:
  users:
    source: Users
  workspaces:
    source: Workspaces
  traces:
    max_depth: 8
```

## Optional Codegen Extensions

The v0 generator is manifest-driven. Add explicit templates instead of
expecting arbitrary TLA+ expression compilation:

```yaml
finite_model:
  Users:
    values:
      - u1
      - u2
  Workspaces:
    values:
      - w1
      - w2
      - w3
  Limits:
    values:
      u1: 1
      u2: 2

fake:
  class: WorkspaceSpecDouble
  initial_state:
    owned:
      u1: []
      u2: []
    limits:
      u1: 1
      u2: 2
  actions:
    create_workspace:
      template: bounded_set_add
      state_field: owned
      limit_field: limits
      owner_command_field: user_id
      item_command_field: workspace_id
      reject_reason: WORKSPACE_LIMIT_REACHED

invariant_templates:
  WorkspaceLimitInvariant:
    template: bounded_set_size
    collection_field: owned
    limit_field: limits
```

These explicit mappings are reviewable. They are part of the minimum
reproducible contract.
