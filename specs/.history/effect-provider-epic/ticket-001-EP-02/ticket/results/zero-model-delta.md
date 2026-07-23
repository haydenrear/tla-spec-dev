# EP-02 zero-model-delta decision

EP-02 adds deterministic host-side Python campaign controls, provider helpers,
scaffolding, and documentation. It does not add an observable `tla-spec-dev`
CLI state transition. `--fuzz-runs`, `--seed`, and `--fuzz-iteration` select
host runner execution points; they do not change the modeled ticket-workflow
state machine.

After validation caches were removed,
`diff -qr specs/tickets/EP-02/current specs/tickets/EP-02/desired` exited 0.
No TLA+ state, action, invariant, configuration, projection, or ticket-local
adapter changed. The bounded current-model TLC run generated 5,619,356 states,
found 231,621 distinct states, reached depth 25, and completed with no error in
11 seconds. See `tlc-current.txt`.

The new behavior is exercised at its actual boundary: generated cases, stable
provider seeds, point-isolated adapter/provider scopes, application-only
passive observation, exact replay diagnostics, project-owned response/state,
and generated provider scaffolds. Keeping the TLA+ snapshot unchanged avoids
inventing model state for implementation-only orchestration.
