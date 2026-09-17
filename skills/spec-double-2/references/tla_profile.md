# Constrained TLA+ Profile

Spec Double Compiler supports a practical, annotated profile. It does
not compile arbitrary TLA+ into Python.

## Supported Constructs

- `CONSTANTS`
- `VARIABLES`
- `Init`
- named actions
- `Next` as a disjunction of named actions
- invariants
- finite TLC model configurations
- simple sets
- simple maps/functions
- records
- sequences/tuples
- booleans
- enums encoded as finite sets
- bounded integers
- action guards
- state transitions
- explicit command/result concepts through comments or
  `spec_manifest.yaml`

## Program Modeling Rule

Model centralized semantic state for the program. This does not mean
production must be centralized. The TLA+ model should describe the simplest
state that captures the application-level semantics across components.

For production repositories, prefer one evolving program spec over many
feature-local specs. A feature, worker, adapter, endpoint, or pipeline stage is
a slice through the program model. It should add variables, actions,
invariants, labels, and adapter mappings to the shared spec rather than create
an isolated source of truth.

Examples:

- A Postgres table plus Redis cache plus worker queue can refine to one
  map in the spec.
- A distributed billing workflow can refine to one subscription record.
- A Kafka event stream can refine to a sequence of accepted domain events.
- A distributed training pipeline can refine to one program model containing
  metadata events, topic queues, append-log files, notifications, retrain
  requests, runs, and checkpoints.

The implementation may be distributed; the spec state is centralized.

One program model is normally still split across the three-module accepted
baseline: `Core.tla` (shared constants and helper operators), `Internal.tla`
(fine-grained program state, the spec-unit case source), and `External.tla`
(publicly observable behavior, the Test Graph case source). That is one shared
spec expressed as views, not separate sources of truth.

Beyond that split, use separate TLA+ modules only for tutorial examples,
genuinely separate programs, or explicitly named refinement layers. Avoid a
repository that has a different unrelated spec for every feature.

## Recommended Module Shape

```tla
----------------------------- MODULE Workspace -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
  Users,
  Workspaces,
  Limits

VARIABLES
  owned,
  result

vars == << owned, result >>

Init ==
  /\ owned = [u \in Users |-> {}]
  /\ result = [accepted |-> TRUE, reason |-> None]

\* @command CreateWorkspace
\* @result CreateWorkspaceResult
Create(u, w) ==
  ...

Next ==
  \E u \in Users, w \in Workspaces:
    Create(u, w)

\* @invariant WorkspaceLimitInvariant
WorkspaceLimitInvariant ==
  \A u \in Users:
    Cardinality(owned[u]) <= Limits[u]

Spec ==
  Init /\ [][Next]_vars

=============================================================================
```

## What To Avoid

Avoid putting these in the spec unless they are semantically relevant:

- database schemas
- network protocols
- queue partition details
- cache invalidation implementation
- retry mechanics
- logging
- metrics
- worker deployment topology
- service ownership boundaries

Put those in adapters and refinement mappings.

## Trace-Friendly Specs

When a counterexample matters, make it easy to turn into a Python trace:

- Use one named action per command.
- Keep command parameters explicit.
- Keep reject reasons explicit.
- Keep result records simple.
- Name invariants after the business rule, not the implementation detail.

TLC counterexamples should become named regression traces when they
represent a behavior users must remember.
