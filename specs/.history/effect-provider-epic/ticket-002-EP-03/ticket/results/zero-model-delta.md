# EP-03 host zero-model delta

EP-03 adds no observable host CLI state, action, invariant, generated host
case, or host adapter mapping. The semantic changes are three independent
example programs, each with its own `Internal.tla`, `External.tla`, generated
cases, providers, and adapters under `examples/effect_providers/`.

The only ticket-local host-model edit is the identical explanatory paragraph
in `current/README.md` and `desired/README.md`. The executable host model and
all host adapters/tests are byte-identical between ticket current and desired.

Validation command after synchronization:

```text
diff -qr specs/tickets/EP-03/current specs/tickets/EP-03/desired
```

Expected and observed result: exit 0 with no output.
