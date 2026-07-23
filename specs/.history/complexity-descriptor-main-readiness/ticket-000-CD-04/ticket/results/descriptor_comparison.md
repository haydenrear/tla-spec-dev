# CD-04 descriptor comparison (before/after)

Zero TLA+ model delta by design and verified:

- `specs/tickets/CD-04/current/TlaSpecDevCli.tla` is byte-identical to
  `specs/program_model/TlaSpecDevCli.tla` (`cmp` clean), and ticket
  `current/` equals ticket `desired/` (`diff -r` clean).
- TLC after: 6,209,780 states generated, **283,805 distinct**, depth 25
  (`specs/tickets/CD-04/results/tlc_current.txt`) — identical distinct-state
  count to the sealed CD-11 baseline run
  (`specs/.history/complexity-descriptor-epic/ticket-005-CD-11/results/tlc_current.txt`,
  283,805 distinct). `max_distinct_states: 500000` with its negotiated
  rationale is carried through ticket desired/ (`spec_manifest.yaml` budgets
  block) — 56.8% headroom.
- Descriptor after: `specs/tickets/CD-04/results/descriptor_after.txt`
  (`analyze complexity` over the ticket-current model with the ticket
  manifest and the recorded TLC report). With a byte-identical model the
  before-descriptor is the same by construction; no complexity decrease or
  increase is claimed.

CD-04 changed only output/help/doc/test wording (corpus gate finding +
redesign question) — no state, action, invariant, or budget change.
