# Effect Conformance Harness

Status: Closed (MF-013 on epic/modular-fuzzing)

**Criteria amended 2026-07-18 after the degeneracy audit.** This ticket was the
audit's worst offender: "fail *or* be recorded as a representation gap" made
the failure optional, and the out-of-contract justification table let a
representation stay blind to real behavior provided someone wrote a sentence
about it. Both escapes are WITHDRAWN. The amended criteria are below; the
original wording is preserved in git history rather than restated here.

Adapters can materialize files, transports, and stores that the model never
represents, which is how representations go blind to real behavior. Ticket
007 made resource boundaries first-class; this ticket makes the check
mechanical.

Add declared-effect conformance to the adapter runner.

Acceptance criteria:

- Components can declare effects (typed emissions on named ports) in the
  manifest / `actions.yml`.
- The runner can execute a component adapter in a sandbox (temp dirs, fake
  transports, recorded boundaries) and collect observed side effects.
- Observed effects are diffed against declared effects per case.
- **An undeclared observed effect FAILS.** The gap is recorded *and* the run
  fails; recording is not an alternative to failing. The model is blind to
  real behavior, which is the one thing a representation may not be. Declare
  the port, or change the program so it no longer emits the effect. There is
  no third option.
- **Nothing suppresses a gap report** — not a manifest entry, not an
  annotation, not a recorded rationale. There is no suppression mechanism, not
  even opt-in. `scripts/effect_conformance.py` scans for suppression-shaped
  keys and reports them as IGNORED rather than honoring them, so a
  reintroduction attempt is visible instead of silent.
- **A declared-but-never-observed effect across the corpus must be removed or
  exercised by a case.** Prose explaining why it is unobserved does not
  resolve dead model surface.
- The diff report is writable as ticket evidence.

Implementation: `scripts/effect_conformance.py` (schema, sandbox, diff),
`scripts/effect_conformance_report.py` (`tla-spec-dev run effect-conformance`),
the sandbox wiring in `scripts/run_generated_case_adapters.py`, and the
`effects:` block in `spec_manifest.yaml`. The regression guard against
reintroducing the withdrawn escape is
`tests/test_effect_conformance.py::TestNothingSuppressesAGap`, which proves a
recorded justification does NOT prevent the failure.
