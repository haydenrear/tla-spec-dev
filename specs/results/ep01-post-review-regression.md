# EP-01 post-review regression evidence

Date: 2026-07-21 (America/New_York)

This evidence follows external review of PR #80. The append-only close history
at `specs/.history/effect-provider-epic/ticket-000-EP-01` was not changed.

## Hypothesis-first reproduction

One combined red run added six requested failure scenarios before production
code changed:

- outer truthy provider `__exit__` + invalid inner entered binding: no
  `SystemExit` was raised;
- outer truthy provider `__exit__` + inner enter failure: no `SystemExit` was
  raised;
- outer truthy provider `__exit__` + inner exit failure: no `SystemExit` was
  raised;
- adapter teardown + provider cleanup failure: only the teardown error appeared;
- configured schema + absent coverage action: preflight did not raise; and
- configured schema + explicit `Action: null`: preflight did not raise.

Those observations confirmed two lifecycle causes and one schema cause:

1. Raw provider scopes were registered directly in `ExitStack`, so an outer
   truthy `__exit__` could erase a framework/provider-lifecycle exception before
   `escaped_error` observed it.
2. Cleanup reporting was gated on `application_error`, excluding the
   teardown-primary case.
3. Configured lookup used `raw_actions.get(action, {})` and normalized `None` to
   `{}`, silently treating absent/null actions as zero-provider declarations.

## Correction

- Provider scopes now delegate cleanup through a non-suppressing wrapper. Each
  scope still receives the real exception and every exit still runs in reverse,
  but a truthy return cannot suppress it.
- A per-case exit tracker retains the original incoming failure and every
  cleanup exception. Application, teardown, provider-lifecycle, and provider
  cleanup failures are classified and reported independently.
- Configured semantic schemas require every coverage action to exist, require
  its value to be a mapping, and require an explicit `effect_ports` key.
  `effect_ports: []` is the sole zero-provider declaration.

Permanent tests also cover a configured action mapping that omits
`effect_ports`, bringing the post-fix discriminating set to seven cases.

## Validation

- Focused runtime/scaffold/passive matrix:
  `89 passed in 0.78s` (`ep01-post-review-focused.txt`).
- Full repository suite:
  `564 passed, 2 skipped in 7.64s` (`ep01-post-review-full.txt`).
- Test Graph `specWorkflow`: 8/8 nodes passed; run
  `specWorkflow-20260722-025000-233a069f`
  (`ep01-post-review-graphs/specWorkflow-20260722-025000-233a069f/summary.json`).
- Test Graph `cliWorkflow`: 2/2 nodes passed; run
  `cliWorkflow-20260722-025027-fd4e26ca`
  (`ep01-post-review-graphs/cliWorkflow-20260722-025027-fd4e26ca/summary.json`).
- `git diff --check`: clean.

No TLA+, spec ticket, Test Graph, or archived evidence semantics changed.
