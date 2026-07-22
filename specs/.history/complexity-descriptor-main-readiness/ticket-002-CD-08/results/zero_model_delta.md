# CD-08: zero TLA+ model delta — descriptor comparison record

CD-08 changes only the shipped `examples/distributed_history` example, the
example validation wrapper, and `scripts/export_testgraph_cases.py` manifest
resolution. It makes no change to this repository's TLA+ program model.

Verified after reconciling the epic tip 5b7d09f (CD-04 and CD-05 merged):

- `specs/tickets/CD-08/current/TlaSpecDevCli.tla` is byte-identical to the
  promoted `specs/current/TlaSpecDevCli.tla` (empty diff), as is `MC.cfg`.
- Ticket `current/` == ticket `desired/` == project `specs/current` for every
  seeded path (production_adapters.py, spec_manifest.yaml, and the corpus
  adapter test were resynced to the CD-05-promoted current during
  reconciliation; no ticket-local edits exist on any of them).
- TLC before (CD-05 close, `specs/.history/complexity-descriptor-main-readiness/ticket-001-CD-05/ticket/results/tlc_current.txt`):
  6,209,780 states generated, 283,805 distinct, 0 on queue, depth 25.
- TLC after (`specs/tickets/CD-08/results/tlc_current.txt`):
  6,209,780 states generated, 283,805 distinct, 0 on queue, depth 25.
  Identical counts on an identical model.
- Budget `max_distinct_states: 500000` is carried through ticket `desired/`
  and project `specs/current` `spec_manifest.yaml` with its recorded rationale
  comment (single-module baseline; REVISIT AT MF-023 note intact), and
  283,805 < 500,000.

Because the model is byte-identical, the complexity descriptor is identical by
identity: no state variables, actions, R/W matrix rows, bounds, or clusters
changed. No complexity increase to justify, no decrease to license.

The only budget change anywhere in this ticket is in the EXAMPLE's manifest
(`examples/distributed_history/specs/program_model/spec_manifest.yaml`):
`max_external_cases_per_action` 50 -> 200, set to the measured worst action of
the example's own pristine corpus (VAL-08) with a recorded rationale under
`budgets.rationale`. That is example content, not this repository's model.
