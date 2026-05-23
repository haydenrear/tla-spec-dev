# Maintenance

The generated Python is not the canonical source of truth. TLA+ defines
the truth. Python makes that truth executable in tests.

## Changing Behavior

1. Treat `specs/desired_program_model` as both the target formal model and the
   plan of action. Keep phases, tickets, steps, dependencies, status metadata,
   acceptance criteria, validation commands, and adapter coverage expectations
   there.
2. Ensure `specs/current` starts from the accepted `specs/program_model`
   behavior for the slice being changed.
3. Implement one ticket or slice.
4. Update `specs/current` to represent the behavior now implemented.
5. Run TLC for `specs/current`.
6. Review invariants and counterexamples.
7. Update the manifest or adjacent status files if new commands, state fields,
   results, ports, adapters, invariants, or plan metadata are needed.
8. Regenerate Python artifacts for the current model.
9. Review generated diffs and the baseline/current/desired relationship.
10. Run spec-double self-tests.
11. Run adapter conformance tests.
12. When `specs/current` equals `specs/desired_program_model`, promote the
    converged model to `specs/program_model` and remove
    `specs/desired_program_model` once it no longer carries distinct planning
    state.

## Changing Implementation Only

1. Do not change the TLA+ model.
2. Do not change generated spec semantics.
3. Update the production adapter.
4. Run conformance tests.
5. If conformance breaks, decide whether the implementation is wrong or
   the spec needs a formal semantic change.

## Review Checklist

- Does the product narrative explain why the behavior exists?
- Does `specs/desired_program_model` contain the current plan breakdown with
  phases, tickets, steps, dependencies, status, and acceptance criteria?
- Does each completed ticket update `specs/current` to the implemented
  repository state?
- Does the TLA+ model capture the canonical state machine?
- Does the manifest expose the minimum reproducible contract?
- Do generated files have deterministic diffs?
- Are production concerns kept out of the fake?
- Are refinement mappings explicit and reviewable?
- Do adapter tests compare against the spec double rather than only
  checking interactions?
- Did TLC counterexamples become traces when useful?
- Did production bugs become model changes, validator changes, or
  regression traces?

## Drift Warnings

- Do not edit generated files directly unless a file marks an extension
  point.
- Do not let generated code drift from the TLA+ model.
- Do not treat Python as replacing TLA+.
- Do not let tests bypass the spec double when conformance is the point.
- Do not confuse centralized semantic state with centralized production
  architecture.

## Useful Slogans

- The spec should generate the mock.
- TLA+ defines the truth; Python makes it executable in tests.
- The spec double is the minimum reproducible contract.
- The implementation may be distributed; the spec state is centralized.
- Production adapters are free to optimize, not reinterpret.
- The fake is not a shortcut around the spec. The fake is generated from
  the spec.
- Code is not automatically truth; reviewed executable contracts are
  truth-bearing artifacts.
