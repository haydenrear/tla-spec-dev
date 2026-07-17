# Effect Conformance Harness

Status: Open

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
- Observed effects are diffed against declared effects per case; undeclared
  observed effects fail or are recorded as representation gaps, and
  declared-but-never-observed effects across the corpus are reported as dead
  model surface.
- Out-of-contract justifications can be recorded in the manifest and
  suppress the corresponding gap report.
- The diff report is writable as ticket evidence.
