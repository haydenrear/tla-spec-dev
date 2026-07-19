# MF-027: negotiated budget retention across promotion

## The hazard

`max_distinct_states` was negotiated 50000 -> **500000** on 2026-07-19 (owner
decision), with its derivation recorded as comments in
`specs/current/spec_manifest.yaml`. That block lives ONLY in `specs/current`,
which ticket close **overwrites** from the ticket's `desired/` tree. This is the
known SF-003 blind spot (#32): a ticket that does not carry the negotiated value
forward silently reverts it, and the next ticket then breaches a cap nobody
noticed had moved.

## What was done

1. `open ticket MF-027` seeded `desired/` and `current/` from `specs/current`,
   so the value AND its comment block were carried in automatically. Verified
   immediately after open rather than assumed:
   - `specs/tickets/MF-027/desired/spec_manifest.yaml:98` -> `max_distinct_states: 500000`
   - `specs/tickets/MF-027/current/spec_manifest.yaml:98` -> `max_distinct_states: 500000`
2. No edit was made to the `budgets:` block in either tree.
3. **Verified again AFTER promotion**, which is the check that actually matters:

```
$ grep -n "max_distinct_states" -B 12 specs/current/spec_manifest.yaml
86-budgets:
87-  tlc_seconds: 120                          # hard external timeout per TLC run
88-  # NEGOTIATED 2026-07-19 (owner decision), raised from the documented default
89-  # 50000. Derived, not chosen to fit: TLC completes this model in 2s at ~19,120
90-  # distinct/sec, so ~2,294,400 are reachable inside the 120s tlc_seconds budget
91-  # -- halved to ~1,147,200 for throughput decay as the model grows. The epic's
92-  # remaining worst case (two further 3x gates on 38,241) is ~344,169. 500000
93-  # sits 1.5x above that trajectory and 4.6x under the measured ceiling, running
94-  # in ~26s. The 50000 default was MF-012's generic value, never calibrated to
95-  # this program, and the real constraint (TLC wall time) is nowhere near
96-  # binding. REVISIT AT MF-023: decomposition gives each component its own much
97-  # smaller state space, and this should drop back toward the default then.
98:  max_distinct_states: 500000               # reachable states TLC may find, per component model
```

**Value and all twelve lines of derivation rationale survived promotion intact.**

## Consumption

MF-027 uses 49,875 of the 500,000 budget (10.0%). `analyze complexity` confirms:

```
INFO: TLC-measured 49,875 distinct reachable states is within max_distinct_states 500,000.
```

## Also verified across promotion

`specs/current/tests/` was captured before the close and diffed after. The
listing is **identical** — twelve files, including
`test_current_ticket_workflow.py`, which the promoter explicitly reported as
`preserved 1 current-only path(s) the ticket never carried`. That is the MF-021
preservation behavior working as intended.

The full repository suite was re-run AFTER promotion as well as before, since
`specs/current/tests` reads the promoted model directly. Both runs green.
