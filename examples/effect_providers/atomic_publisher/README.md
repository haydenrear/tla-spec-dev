# Atomic publisher effect-provider experiment

This is the low-coupling experiment from EP-03: a versioned canonical-JSON
publisher receives one generated, runtime-checkable `FilesystemPort` by
explicit dependency injection. TLA+ fixes one of seven semantic outcomes;
the point-local provider deterministically chooses Unicode paths, record data,
unrelated files, and an `OSError` subclass inside that outcome.

The immutable AP-01..AP-12 catalog, seed `20260721`, 16 iteration indices,
detector attribution, and stop/go threshold live in
[`../PREREGISTRATION.yaml`](../PREREGISTRATION.yaml). This directory does not
modify those values or any framework source.

## Semantic boundary

`Internal.tla` has seven nondeterministic initial scenarios and seven distinct
terminal action edges. Regeneration refuses a helper-action collapse: the
generated corpus must contain seven different `case.input.action` values and
seven action/outcome pairs. The checked provider then maps each symbolic
record token (`record`, `old`, `new`) to one deterministic concrete
representative. Exact bytes are projected back to those tokens, so omitted or
truncated content cannot pass by copying `case.after`.

One measured duplication remains: the adapter maps the scenario to an expected
revision because the case does not carry a normalized application command
plan. The evidence reports that as an abstraction cost rather than treating it
as provider-owned fuzz data.

The application only knows the generated port. The provider owns its strict
in-memory filesystem, protocol journal, fault class, bypass audit, and cleanup.
The separate real-filesystem conformance run uses `TemporaryDirectory` and
the same generated command/result types. The External view drives a subprocess
CLI and observes its filesystem/result artifacts without importing production
code in the external adapter.

## Commands

From this directory:

```bash
python regenerate.py --tlc2 tlc2
python test_atomic_publisher.py
python run_experiment.py --repetitions 2 --run-label local
```

`regenerate.py` has a hard 120-second timeout for each TLC case-generation
view. It regenerates the typed contract under
`specs/program_model/generated/atomic_publisher_contract`, the seven internal
cases, the seven external cases, and digest-bound provenance.

`run_experiment.py` invokes the repository's real
`scripts/run_generated_case_adapters.py` with `--batch --fuzz-runs 16
--seed 20260721`; ordinary fixtures are used only for the separately reported
hand-written baseline. Every first discovered mutant failure is replayed with
the runner's emitted absolute command and must return nonzero with the same
structured failure, transcript digest, and clean provider exit.

## Evidence

- `specs/program_model/generated/provenance.json`: model/config digests, TLC
  counts/timing, action names, outcomes, and case counts.
- `evidence/atomic-publisher-raw.json`: both local repetitions, all concrete
  point transcripts, structured failures, replays, mutation attribution,
  runtime statistics, conformance, cleanup, costs, and the stop/go decision.
- `evidence/retrieval.json`: exact files/ranges read and project files/line
  counts changed during implementation.
- `FINDINGS.md`: measured cost/benefit and follow-up recommendations.

The experiment deliberately keeps survivors and extra detectors visible. A
framework edit, stale generated provenance, red control, missing action, weak
existence-only oracle, replay divergence, or resource leak makes the decision
`no-go` rather than being normalized away.
