# External Edge Cases

External cases are generated from the public or harness-driven view of the
program. They are not limited to distributed systems.

For an HTTP service, External actions may be requests. For a CLI, they may be
command invocations. For a file processor, they may be writes, renames, and
process runs. For a distributed service, they may include API calls, worker
drains, queue operations, or fault injection.

The useful rule is:

```text
Internal defines legal program state changes.
External defines what the outside harness can drive and observe.
```

## What To Generate

Generate External edge cases for behavior that a user, operator, or integration
harness can actually trigger:

- duplicate or idempotent commands;
- invalid preconditions that must not mutate state;
- empty input or empty work queues;
- boundary values;
- authorization or ownership rejection;
- retry after an accepted operation;
- stale, missing, or already-completed resources;
- fault or recovery actions when those are part of expected behavior.

Do not emit hidden internal progress as an external step. If a worker, retry
loop, cache refresh, or leader election can happen between external actions,
model it as hidden progress and assert the externally visible result.

## Setup And Teardown

Each External case should carry a modeled `before` state and an expected
observable `after` state. The Test Graph adapter batch should use hooks to make
those states meaningful:

- `setup_all`: prepare suite-level state, such as health checks, clearing
  shared tables, draining queues, or committing offsets.
- `setup`: reset the target and load the case's `before` state through an
  admin/debug/test fixture boundary.
- `teardown`: clear per-case residue.
- `teardown_all`: clear suite-level residue.

This is what prevents a running cluster, CLI workspace, local database, or
filesystem directory from carrying invalid residue between generated cases.

## Assertions

External assertions should compare a model-derived expected state to an actual
state projected from the system under test:

```text
expected = projection(case.after)
actual = observe(system)
assert expected == actual
```

For a CLI, `observe(system)` may read files, stdout artifacts, a database, or a
workspace manifest. For a service, it may call debug/admin endpoints. For a
cluster, it may combine API responses, SQL rows, queue metadata, and logs into
the abstract state shape.

Response assertions and projected-state assertions should both run. A command
can return the right status while mutating the wrong state.

## Ecommerce Example

`examples/distributed_history/` regenerates its external Test Graph cases from
TLC, then exports them to JSON traces:

```bash
uv run examples/distributed_history/scripts/regenerate_tlc_cases.py \
  --out examples/distributed_history/test_graph/build/generated/manual
```

The generated Python package and exported traces are a materialized TLC edge
list used by the adapter runner, not hand-authored fixtures. Test Graph runs
regenerate them under the validation report. The current bounded model exports
17 external Test Graph cases after projected dedupe. Read the exact list from:

```text
examples/distributed_history/test_graph/build/validation-reports/<run>/generated/testgraph/traces/manifest.json
```

Several generated trace ids share the same action name, such as
`SubmitDuplicateCreateAccount` or `RunFulfillmentWorkerNoop`, because TLC found
that public action in different reachable projected `before` states. Those are
distinct integration cases even though they use the same adapter.

All external cases run through the same `ecommerce-http` adapter batch. The
batch hooks reset the service, load each case's `before` state, execute one
external action, project `/debug/state` back into the TLA state shape, write
`program-state.json`, and fail if projected state differs from the expected
`after` projection.

Run the local validation:

```bash
python3 examples/run_distributed_history_validation.py
```

Run the k3d validation:

```bash
python3 examples/run_distributed_history_validation.py --mode k3d
```

The wrapper also runs a deliberate negative check that replaces the expected
projection with a wrong one and requires the projected-state assertion to fail.
