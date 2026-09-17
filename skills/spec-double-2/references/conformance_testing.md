# Conformance Testing

A production adapter conforms when it preserves the generated spec
double behavior at the port boundary.

## Adapter Requirements

An adapter conforms if:

- It implements the generated Protocol.
- It exposes `snapshot()` or an observation function returning generated
  spec state.
- It returns results that normalize into generated result types.
- It passes generated conformance tests.
- It passes generated validators over observed states and transitions.

## Refinement Mapping

Production state rarely looks like spec state. The mapping is first
class:

```python
def observe_adapter_state(adapter) -> WorkspaceState:
    ...

def normalize_adapter_result(result) -> CreateWorkspaceResult:
    ...

def normalize_event(event) -> SpecEvent:
    ...
```

Review these mappings with the same care as adapter code. They are where
distributed machinery is related back to centralized semantic state.

## Reusable Harness

Generated contract tests compare a real adapter with the spec double:

```python
def assert_workspace_port_conformance(adapter_factory, initial_state, commands):
    expected = WorkspaceSpecDouble(initial_state)
    actual = adapter_factory(initial_state)

    for command in commands:
        before = actual.snapshot()

        expected_result = expected.create_workspace(command)
        actual_result = actual.create_workspace(command)

        after = actual.snapshot()

        assert actual_result == expected_result
        validate_create_workspace_transition(
            before=before,
            command=command,
            result=actual_result,
            after=after,
        )
```

## Test Layers

Spec-double self-tests:

- Generated fake satisfies generated validators.
- Generated traces replay correctly.
- Generated strategies produce valid states and commands.

Adapter conformance tests:

- Real adapters produce the same results as the spec double for
  generated traces.
- Real adapters preserve invariants.
- Real adapters expose observable state that validates against the spec.

Regression tests from counterexamples:

- TLC counterexamples become named Python regression traces.
- Hypothesis failures are shrunk and preserved as replayable traces.
- Production bugs become TLA+ model changes, generated traces, or
  validator improvements.

## Anti-Patterns

- Do not use interaction mocks when semantic conformance is the goal.
- Do not let the fake import production services.
- Do not let a Test Graph adapter import the production package. On the
  External path this is verified, not asserted: the runner and exporter
  statically check every adapter, projector, expected-projection, and
  assertion module — transitively — against the declared
  `external.production_package` and refuse on violation. See "External
  Channel Enforcement" in `references/testgraph_adapters.md`.
- Do not make generated spec doubles production dependencies.
- Do not hide refinement mappings behind broad integration helpers.
