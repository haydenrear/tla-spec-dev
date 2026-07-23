# External Channel Enforcement

Status: Open

Test Graph adapters degenerate into unit test adapters because External-ness
is asserted structurally but never verified. An adapter that imports the
production package in-process is not driving the deployed program.

Enforce channel authenticity for Test Graph adapters.

Acceptance criteria:

- `testgraph_bindings.yml` requires a `channel` field per binding: one of
  http, cli, fs, queue, k8s (extensible).
- The runner verifies Test Graph adapters cannot import the production
  package: either static import analysis or execution in an interpreter
  where the package is not installed.
- Violations report the adapter, the import, and the remediation (rebind as
  a spec-unit adapter or drive the declared channel).
- Port binding configurations (double vs real per port) are declarable, so
  graph runs can express integration-ladder rungs.
