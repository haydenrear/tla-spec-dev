# Reminder worker: correlated, ordered effect providers

This experiment asks whether generated TLA+ cases plus four project-owned
providers can find bugs in an outbox worker without turning TLA+ into a call-by-
call response scripting language. It is deliberately the highest-cost example
in this set: the providers share one immutable concrete bundle and one monotonic
journal so they can validate relationships and ordering across clock, queue,
outbox, and notification effects.

The prediction, fixed mutant catalog, seed schedule, detector attribution, and
stop/go threshold were committed before the experiment in
[`../PREREGISTRATION.yaml`](../PREREGISTRATION.yaml). A scored run must not edit
that file or any framework source.

## Semantic split

`Internal.tla` selects one of seven semantic outcomes and fixes the case's
before state, action, output, and after state. Generated cases therefore say
things such as "a retryable notification failure releases the claimed job";
they do not contain a list of provider calls or concrete HTTP-like responses.

For each generated case and fuzz iteration, the four providers deterministically
choose correlated concrete representatives inside that outcome:

- a Unicode-bearing job id, recipient, body, and idempotency key;
- a clock value and, for `not_due`, a positive due-time offset;
- an opaque receipt;
- one of two exception subclasses in the modeled retryable or permanent class.

The shared journal checks cross-provider order, while each provider checks its
own command values and cardinality. The adapter returns real application output
and a projection of provider state; the standard generated-case runner compares
those with the TLA-derived oracle. Providers never mutate or replace a case.

The boundary is intentional. A materially different outcome belongs in TLA+.
A concrete value within an already modeled outcome belongs in the providers.
An implementation property absent from both the TLA state and provider checks
needs an independent oracle; merely adding more fuzz values cannot create it.

## Layout

- `specs/program_model/`: Internal and External models, TLC configs,
  projection, generated-contract manifest, adapter mapping, and Test Graph
  bindings.
- `generated/reminder_contract/`: generated typed command and port contracts.
- `generated/cases/`: runnable case packages generated from TLC state graphs.
- `app.py`: the real worker, written only against the four typed ports;
  `reminder_cli.py` is a process boundary with file-persisted queue/outbox state.
- `providers.py`: point-local providers, correlated bundle, journal, cleanup,
  deterministic concretization, and provider-owned assertions.
- `adapter.py`: the thin in-process bridge from bound effects to application
  execution and TLA state projection; `external_adapter.py` validates all seven
  external cases across the process boundary.
- `run_experiment.py`: green control, fixed mutants, separate hand-written
  baseline, exact replay, capability probes, costs, and machine-readable result.
- `test_reminder_worker.py`: fast contract, runner, cleanup, baseline, and patch
  restoration checks.

## Run it

From the repository root, with the repository's `tlc2` command available:

```sh
python3 examples/effect_providers/reminder_worker/regenerate.py
python3 examples/effect_providers/reminder_worker/test_reminder_worker.py
python3 examples/effect_providers/reminder_worker/run_experiment.py --run-id local-1
python3 examples/effect_providers/reminder_worker/run_experiment.py --run-id local-2
```

Each scored command regenerates both models first, runs a 25-iteration control
through `scripts/run_generated_case_adapters.py`, and only scores mutants if
all 175 control points and cleanup records are green. Evidence is written under
`evidence/runs/<run-id>/`; an existing run id is never overwritten. Each failed
point emits the runner's replay command, and the experiment re-executes the
first failure for every killed mutant to compare both failure text and journal
digest.

The separately reported hand-written baseline covers four ordinary scenarios
with one concrete point each. Its mutation score is not combined with the
generated/effectful score.

## What this does not prove

Explicit injection observes only code that uses the four ports. The non-scored
capability probes demonstrate that a direct `datetime` read is invisible and a
direct socket call needs a separate passive guard. The providers explore a
finite deterministic schedule; this is neither exhaustive fuzzing nor
shrinking. A green campaign means the generated semantic cases and these
provider-owned checks detected the preregistered catalog—not that all reminder
worker implementations or all effects are correct.
