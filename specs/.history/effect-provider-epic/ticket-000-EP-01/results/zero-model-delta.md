# EP-01 zero-model-delta decision

EP-01 adds a host Python runtime contract; it does not add an observable
`tla-spec-dev` CLI transition. Accordingly, no TLA+ state, action, invariant,
configuration, or ticket-local spec adapter changed.

`diff -qr specs/tickets/EP-01/current specs/tickets/EP-01/desired` exited 0 after
validation-only caches were removed. The bounded current-model TLC run still
generated 5,619,356 states, found 231,621 distinct states, reached depth 25, and
completed with no error in 11 seconds. See `tlc-current.txt`.

The observable behavior is exercised at its actual boundary: generated Python
cases, runtime-checkable generated port Protocols, provider configuration, and
the adapter runner. This keeps the shared TLA+ workflow honest instead of adding
model state for an implementation-only lifecycle.
