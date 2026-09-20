SI-08 (#341) PR #376 -> merge commit 308d2732. Sole ticket in wave 10, promotion 120.
EVALUATION A: the reading is frozen. 12 clauses -- 6 MET, 4 NOT MET, 1 SPLIT, 1 UNDECIDED.
Planned order equals actual. No reconciles. Second wave under per_ticket_backlog:
11 rows to specs/results/deferred/SI-08.yaml, 0 to the cumulative file.

24 files, ALL under specs/results/, +3753/-0. Measurement only, no target edited.

IT CORRECTED THE EPIC AGENT ON THE GOAL IT WAS SENT TO FREEZE. GOAL-one-unit
clause 1 reads "zero standalone copies ... in root OR project home". I reported
it as holding on the project home alone; the root home still carries all 8
substrate skills standalone with no plugin. NOT MET. Verified by me afterwards.

FRONT DOOR: failed again (9th occurrence, FIRST ROOT CAUSE) -- skt ticket.py:150
resolves bootstrap-home.sh only at the standalone rung. My fix (skt PR #54) went
into the PROJECT home; the dispatch command defaults to the ROOT home shim,
which is still unfixed. The agent caught it by TESTING THE PATH -- through a
pipe the exit code read 0. Fell back to git worktree add.

FIRST EVER SCORED EVAL CASE RUN: 1 case, $0.54, 106s, score 0.67.

DCO failed; owner ruled it irrelevant 2026-09-19.
