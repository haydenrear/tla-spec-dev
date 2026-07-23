# EP-04 zero host-model delta

EP-04 changes the Python authoring/runtime contract and scaffolding. It adds no
new `tla-spec-dev` CLI command, guard, state transition, or user-visible command
result. The inherited host program model therefore remains unchanged.

- Ticket `current/` and `desired/` are byte-identical.
- TLC completed with no error.
- Generated states: 5,619,356.
- Distinct states: 231,621.
- Search depth: 25.
- States left on queue: 0.

Modeling provider registration as host CLI state would invent a transition the
program does not expose. Repository-specific effect semantics belong in each
repository's program model and generated ports.
