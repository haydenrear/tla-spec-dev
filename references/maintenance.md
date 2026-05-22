# Maintenance

The generated Python is not the canonical source of truth. TLA+ defines
the truth. Python makes that truth executable in tests.

## Changing Behavior

1. Update the TLA+ model first.
2. Run TLC.
3. Review invariants and counterexamples.
4. Update the manifest if new commands, state fields, results, or ports
   are needed.
5. Regenerate Python artifacts.
6. Review generated diffs.
7. Run spec-double self-tests.
8. Run adapter conformance tests.
9. Update production adapters only after the new spec boundary is clear.

## Changing Implementation Only

1. Do not change the TLA+ model.
2. Do not change generated spec semantics.
3. Update the production adapter.
4. Run conformance tests.
5. If conformance breaks, decide whether the implementation is wrong or
   the spec needs a formal semantic change.

## Review Checklist

- Does the product narrative explain why the behavior exists?
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
