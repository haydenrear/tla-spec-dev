# Ticket snapshot: SS-07

- Workflow: `stabilize-substrate-epic`
- Entry: `ticket-003-SS-07`
- Ticket: `SS-07`

## Summary

Four standing results verified at 48f9c7e and re-checked at every reconciled tree through 8c3d258. THREE HALVES WERE GENUINELY RE-EXECUTED -- test_journal_conformance.py (14 passed, 70/70 across three wirings), check_catalogue.py --arms (arm C +3.8% longer, 0 of 109 architectural terms, against W=arm C at D3 1/1), and architecture_tags.py derive (16 of 21; NUMERATOR fell 17->16, DENOMINATOR held at 21). THE REST, INCLUDING RESULT 3 ENTIRELY, IS index/history RE-RENDERING SEALED CARDS: proof they open and still say what the record claims, not a recomputation, and no judge was re-run. Result 3 has no re-execution available; result 4 is the one with a real re-run. STRANDED DISPROOF INSTRUMENT DECIDED: DISCLOSE, written where a reader of the claim meets it, editing nothing in that directory. CA-02-DF-04's restore command had never been run; run in a throwaway checkout it reproduces BYTE-IDENTICAL to the sealed transcript -- a PURE REPLAY over inputs frozen at 37ab155 that AUTHENTICATES the transcript and does NOT re-derive the claim against today's record, so CA-08's decision stands. Both withdrawn overstatements struck by name. EIGHT FINDINGS, NOTHING REPAIRED, THREE AGAINST THIS TICKET'S OWN WORK: index mutates 16 of 18 sealed card trees when used to verify them; two sealed-record classifiers overwrite their own evidence; SV-03's no-card demonstration is a SECOND stranded instrument, stranded by success; the check CA-02-DF-04 asked for now exists and nothing runs it; my own published cell exit-code claim was FALSE because I measured it through a pipe (fifth such figure in this epic); my own --selftest was partly vacuous and the vacuity hid a crash on any --root outside the repo; disposition.py --ticket is blind to reviewer-credited rows; and stranded_loaders.py WOULD FAIL SS-02's absent-input check on 2 of 3 states, one being the exact set[str] vs set[str] | None shape the charter uses to define the class. Independent review returned CHANGES with eleven findings and all eleven held. Suite PRE-CLOSE at ab9a244: 7/1554/0/1/1562, they sum. THIS SEALED FIGURE CANNOT DESCRIBE THE TREE THIS CLOSE PRODUCES -- close seals the entry and deletes the workspace in one operation, so the post-close figure is in the live RESULT.md and is the authoritative one for a reader standing in the merged tree.

## Snapshots

- `program_model`: `specs/.history/stabilize-substrate-epic/ticket-003-SS-07/snapshots/program_model`
- `desired_program_model`: `specs/.history/stabilize-substrate-epic/ticket-003-SS-07/snapshots/desired_program_model`
- `current`: `specs/.history/stabilize-substrate-epic/ticket-003-SS-07/snapshots/current`
- `ticket_workdir`: `specs/.history/stabilize-substrate-epic/ticket-003-SS-07/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
