# Instrument registry -- BEFORE state, at the SM-01 parent commit

Derived by parsing `examples/validation/instruments/instruments.toml` directly,
not by quoting a previous round's prose. SM-05 diffs the after against this.

- enumerated rows: **40**
- classified `not-an-instrument`: **5**
- instruments: **35**
- with a `failing` block: **26**
- without one: **9**
- with a `blind_spot` slot: **12**
- distinct declared paths: **38**

## The 12 pytest failing slots asserting ONLY `expect_exit = 0`

This is the whole population, not a sample: there is no pytest failing slot
in this registry that asserts anything beyond the exit code.

- `effect-oracle`
- `control-property-probe`
- `arms-length-match`
- `divergence-reachability`
- `scorecard-seal`
- `thermometer-tripwire`
- `skill-root-tripwire`
- `complexity-ledger`
- `close-promotion-preconditions`
- `external-channel-enforcement`
- `spec-unit-adapter-conformance`
- `case-modules-validate`

## The 2 rows where `failing.nodes == passing.nodes`

- `complexity-ledger` -- both slots run `['tests/test_complexity_ledger.py']`, both `expect_exit = 0`
- `case-modules-validate` -- both slots run `['tests/test_case_modules.py']`, both `expect_exit = 0`

## The 9 instruments that cannot be shown to fail

- `produced-code-instrument` (demonstrated-cannot-fail)
- `suite-verification` (demonstrated-cannot-fail)
- `port-swap-driver` (demonstrated-cannot-fail)
- `source-citation-tripwire` (no-demonstration-constructible)
- `spec-yaml-tripwire` (no-demonstration-constructible)
- `manifest-self-records-tripwire` (no-demonstration-constructible)
- `port-declaration-tripwire` (no-demonstration-constructible)
- `test-graph-nodes` (no-demonstration-constructible)
- `ticket-state-agreement` (no-instrument-exists)

## The headline, and what SM-03 must not do to it

**26 of 35** is the number on the card.
`denominator_rule`: deleting a hollow demonstration must not quietly improve
the ratio. These are the before figures the after is reported against, with
deletions counted SEPARATELY from repairs. A ratio that rises because the
denominator shrank is MF-020 wearing this epic's clothes.
