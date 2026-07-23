# EP-06 zero host-model delta

EP-06 adds project-owned example models, provider implementations, validation
entrypoints, evidence, and a Test Graph consumer. It adds no `tla-spec-dev`
CLI state, guard, transition, or command result.

- Ticket `current/` and `desired/` are byte-identical.
- Full host TLC completed with no error.
- Generated states: 5,619,356.
- Distinct states: 231,621.
- Search depth: 25.
- States left on queue: 0.

Each example independently regenerated and checked its own Internal and
External model with a 120-second bound. Those artifacts validate arbitrary
repository consumers; they are not changes to the host CLI model and are not
claims of complete application coverage.
