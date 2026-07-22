# EP-03 fresh-checkout validation

Validated code/docs candidate: `c46aef126600312daf20210448c7b844ef3e5996`.
Each validator used a separate disposable clone. Generated experiment evidence
was written only inside that clone; this record carries the immutable content
hashes and exact outcomes. Project-subtree identity checks connect each clone's
validated commit to the final candidate.

## Atomic publisher

- Clone: `/private/tmp/tla-spec-dev-ep03-fresh-atomic-final-43905c3`
- Checked-out commit: `985ef20c146559650806046329b924f4debc589b`.
  `git diff --quiet 985ef20 c46aef1 --
  examples/effect_providers/atomic_publisher` returned 0.
- Regeneration: exit 0; Internal and External each 14 generated / 14 distinct,
  depth 2, seven cases. Only provenance wall-time fields changed.
- Tests: 6/6 passed.
- Full campaign: two repetitions GO; 12/12 and 12/12 versus baseline 10/12;
  transcript digest `784a96c…`, verdict digest `35b89899…`; cleanup green and
  every first-repetition first discovery replayed exactly.
- Fresh artifact SHA-256:
  `4d33163ce1a4dd99d369dde3e93f8c48d2e36385bb68bf989e60d9338b41bfc4`.

## Reminder worker

- Clone: `/private/tmp/tla-spec-dev-ep03-fresh-reminder-final-258e169`
- Validated project commit: `258e169513c2e95a455436d96d06a3c776726bfa`.
  `git diff --quiet 258e169 c46aef1 --
  examples/effect_providers/reminder_worker` returned 0.
- Environment: Python 3.14.6, PyYAML absent.
- Regeneration: exit 0 and byte-clean; Internal and External each 14/14,
  depth 2, seven cases.
- Tests: 6/6 passed, including typed signatures and active/`-S` generated-tree
  reproduction.
- Full campaign: GO; 175 controls, 12/12 versus green 8/12 baseline, exact
  replay/cleanup/framework audit, stable digest `9c5131bb…`.
- Fresh artifact SHA-256:
  `14c7a7810cbd6e7f01c2851a03798be3643192fabb1f469c4f7e4b848af0f488`.

## Legacy payment HTTP

- Clone: `/private/tmp/ep03-http-final.0KCKA1/repo`
- Validated project commit: `43905c3c6abca9d5bbe42e9d546b09a53bca3e88`.
  `git diff --quiet 43905c3 c46aef1 --
  examples/effect_providers/legacy_payment_http` returned 0.
- Full campaign command: `uv run --project . python scripts/run_experiment.py
  --label final-fresh-43905c3 --output evidence/final-fresh-43905c3.json
  --tlc2 /Users/hayde/.skill-manager/bin/cli/tlc2`.
- Campaign: GO; 1,792 green control points, 12/12, baseline 12/12, every
  expected detector, exact nonzero structured replay, clean patches/provider
  state, zero outbound sockets, zero framework changes.
- Unit/loopback tests: 9/9 passed.
- External runner: all 56 real loopback/process cases passed.
- Fresh JSON SHA-256:
  `b4be50977c8ba1133ea17e8203d46b5363343fb90177b36a3a8afc6b9b16e007`.

## Aggregate Test Graph

- Run: `effectProviderExamples-20260722-065116-d50c50d0`.
- Status: passed; 22/22 assertions and all four subprocesses exit 0.
- Metrics: 36/36 effectful mutants, 2,079 control points per accepted
  repetition, 70 external cases, 36,707 ms node duration.
- The new parser assertion passed for every Python-contract input section
  through both PyYAML and the constrained fallback, including five null result
  methods. Budgets are deliberately outside that raw-tree comparison because
  their loader has a separate coercion contract.

The earlier graph runs remain diagnostic evidence: the first corrected an
over-strong atomic repetition-two replay assertion; the later raw whole-manifest
parity attempt correctly failed on the separately-coerced decimal budget and
was narrowed to the contract generator's actual inputs.
