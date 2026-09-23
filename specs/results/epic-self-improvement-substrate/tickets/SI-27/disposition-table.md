# SI-27 — every row it settled

120 rows in the ledger. SI-27 wrote a disposition on 86 of them:
the 80 that were open, a note on `SI-12-DF-05` (whose `answered` was terminal
with no note and whose suggested fix must NOT be applied), and its own 5.


## fixed — 24

- **SIS-KICKOFF-F-01** — `SI-07 (#340), validate_assignment.py:402-425`: FIXED.
- **SIS-W2-F-05** — `SI-11 (#351), skill-manager-plugin.toml:61-75`: FIXED HERE, and the cause it names survives one level up as SI-11-DF-01.
- **SI-02-DF-05** — `integration-lib.sh:42,51,95-96,105-106`: FIXED.
- **SI-04-DF-03** — `skt _bootstrap_script two-rung probe (skills/skt/src/skt/ticket.py:165-178)`: FIXED, both halves, and SI-27 is the proof of use: `skt ticket new 382-complete-the-findings --base 2c21e609 --path ../wt-382-complete-the-findings` created this worktree.
- **SI-06-DF-02** — `skt two-rung _bootstrap_script + non-zero propagation (measured exit 128)`: FIXED, both defects.
- **SI-06-DF-03** — `bootstrap-home.sh ensure_run_artifacts_ignored() tracked-path guard`: FIXED, and the damage is cleaned up.
- **SI-11-DF-04** — `skt entry point propagates the wrapper's exit (measured 128)`: FIXED.
- **SI-12-DF-01** — `SI-12 successors; complete.md:116, integration-fanout.md:41, provision.md:160, skill-manager.toml:36`: FIXED, all four sites.
- **SI-12-DF-04** — `skills/discovery/skill-project.toml: the coord declaration removed`: FIXED.
- **SI-13-DF-01** — `SI-13; test_graph/README.md:34-44 and test_graph/run-graphs.py`: FIXED: the correction landed where the row said it should.
- **SI-13-DF-02** — `skill-manager .github/scripts/select-graph-set.py:200,220-270`: FIXED in skill-manager, and the fix is present in that checkout.
- **SI-13-DF-03** — `skills/test-graph/scripts/run.py nargs="*"; skill-manager de-vendored the copy`: FIXED by removing the second copy rather than by syncing it.
- **SI-13-DF-05** — `case_coverage.json `source` is repository-relative in all six files`: FIXED.
- **SI-14-DF-04** — `project home reconciled; the five standalone install records removed`: FIXED.
- **SI-08-DF-03** — `skills/skt/src/skt/ticket.py:165-178 (two-rung _bootstrap_script)`: FIXED, at the line the row named.
- **SI-08-DF-04** — `root home: eight standalone substrate skills removed, the tla-spec-dev plugin installed`: FIXED, and by the operator action the row said it needed.
- **SI-08-DF-11** — `SI-27 (#382): the per-ticket partition absorbed into deferred_findings_final.yaml`: FIXED BY THIS TICKET, and by the other of the two available fixes.
- **SI-15-DF-01** — `ticket_plan.yaml:295,314,1111,1124 (corrected at wave 9)`: FIXED: the plan was corrected.
- **SI-15-DF-03** — `evals/run.sh:200-201,375-376 compute and print the count; SI-14-DF-03 superseded`: FIXED, both halves.
- **SI-15-DF-04** — `skt two-rung _bootstrap_script + non-zero propagation (measured exit 128)`: FIXED.
- **SI-16-DF-02** — `evals/README.md:236-257`: FIXED, by the second of the two options the row offers.
- **SI-16-DF-03** — `eb740669 (evals/lib/toolchain.lock.toml: [units.skt] retired)`: FIXED OUTRIGHT by eb740669 ("evals: point the toolchain at the plugin and the branch under test"), which took the first of the two fixes the row itself offered.
- **SI-16-DF-04** — `the eight blocks deleted from the four nested skill-project.toml files`: FIXED.
- **SI-17-DF-02** — `skills/skt/skill-project.toml: the [project] table restored`: FIXED.

## still-true — 58

- **SIS-KICKOFF-F-02**: STILL TRUE.
- **SIS-KICKOFF-F-03**: STILL TRUE in the half that matters, and the half that was repaired was repaired by hand rather than by an instrument.
- **SIS-KICKOFF-F-04**: STILL TRUE, verbatim.
- **SI-01-DF-01**: STILL TRUE and unchanged.
- **SI-01-DF-02**: STILL TRUE.
- **SI-02-DF-01**: STILL TRUE in cause (a), which is the same defect SI-25-DF-08 measures more sharply: skills/plugin-repository/scripts/verify.sh:133 is still `grep -rl --exclude-dir=.git .
- **SI-02-DF-02**: STILL TRUE; the line moved from 581 to 589 and is otherwise identical.
- **SI-02-DF-04**: NOT REPRODUCIBLE TODAY, and the row stays open only because the stager was never changed.
- **SI-04-DF-01**: STILL TRUE.
- **SI-04-DF-02**: STILL TRUE, to the exact counts the finding recorded.
- **SI-04-DF-04**: STILL TRUE, AND SI-27 GOT THIS WRONG ONCE BEFORE GETTING IT RIGHT -- both readings are recorded because the second is only credible with the first beside it.
- **SI-10-DF-01**: STILL TRUE.
- **SI-06-DF-01**: STILL TRUE, with the instrument half corrected.
- **SI-11-DF-01**: STILL TRUE upstream.
- **SI-11-DF-02**: STILL TRUE upstream, symptom retired here.
- **SI-11-DF-03**: STILL TRUE; the line moved from 354 to 369.
- **SI-11-DF-05**: STILL TRUE as a measurement-design defect.
- **SI-07-DF-01**: STILL TRUE.
- **SI-07-DF-02**: STILL TRUE, and shipped deliberately.
- **SI-12-DF-03**: STILL TRUE, unchanged.
- **SI-12-DF-06**: STILL TRUE in the half that is a CLI defect.
- **SI-09-DF-01**: STILL TRUE, and it RECURRED on SI-27 itself, which is the strongest evidence the row could have.
- **SI-09-DF-02**: STILL TRUE.
- **SI-09-DF-03**: STILL TRUE, and the gap widened.
- **SI-13-DF-04**: STILL TRUE.
- **SI-14-DF-01**: STILL TRUE upstream; guarded here.
- **SI-14-DF-02**: STILL TRUE.
- **SI-14-DF-05**: STILL TRUE and slightly worse.
- **SI-25-DF-01**: STILL TRUE for three of the four wrappers; one is fixed.
- **SI-25-DF-02**: STILL TRUE and MEASURABLY WORSE than the row records.
- **SI-25-DF-03**: STILL TRUE.
- **SI-25-DF-04**: STILL TRUE, and the unrepairable one is still unrepairable.
- **SI-25-DF-05**: STILL TRUE.
- **SI-25-DF-06**: STILL TRUE.
- **SI-25-DF-07**: STILL TRUE.
- **SI-25-DF-08**: STILL TRUE.
- **EA-DF-01**: STILL TRUE, reproduced today.
- **SI-08-DF-01**: STILL TRUE.
- **SI-08-DF-02**: STILL TRUE.
- **SI-08-DF-05**: STILL TRUE, partially mitigated.
- **SI-08-DF-06**: STILL TRUE.
- **SI-08-DF-07**: STILL TRUE.
- **SI-08-DF-08**: STILL TRUE and deliberately NOT re-measured: re-running it is operator spend ($0.54 and ~106s per run) and the row's own instruction is to read the trace with `--keep-tem.
- **SI-08-DF-09**: STILL TRUE as a recurring condition, though the specific hashes moved.
- **SI-08-DF-10**: STILL TRUE: the correction was not made.
- **SI-15-DF-02**: STILL TRUE, and correctly so.
- **SI-15-DF-05**: STILL TRUE, and it is still the honest declaration the row says it is.
- **SI-16-DF-01**: STILL TRUE as a record: the issue body was never corrected.
- **SI-16-DF-05**: STILL TRUE upstream; NOT REPRODUCIBLE in this home, and the difference is worth recording.
- **SI-17-DF-01**: STILL TRUE, and the control has moved again, which makes the row's point twice.
- **SI-17-DF-03**: STILL TRUE, unchanged.
- **SI-17-DF-04**: STILL TRUE.
- **SI-17-DF-05**: STILL TRUE.
- **SI-27-DF-01**: Filed by SI-27 from the epic agent's measurement of 2026-09-23.
- **SI-27-DF-02**: Filed and measured by SI-27 on 2026-09-23 while re-testing SI-02-DF-04.
- **SI-27-DF-03**: Measured by SI-27 on 2026-09-23 on a PRE-EDIT run of the base, before any file in this ticket was touched, so it is not this ticket's.
- **SI-27-DF-04**: Filed and measured by SI-27 on 2026-09-23 as a blocker met at its own close-out.
- **SI-27-DF-05**: Filed and measured by SI-27 on 2026-09-23, after it had already published the wrong conclusion in a PR body and had to retract it.

## superseded — 2

- **SI-02-DF-03** — by SI-06-DF-01: SUPERSEDED by SI-06-DF-01, which names the same instrument with the exact command, the spend and the sibling-repo mutation.
- **SI-14-DF-03** — by SI-15-DF-03: SUPERSEDED by SI-15-DF-03, which re-measured the figure and found it not reproducible: 6,712 entries before the toolchain and 6,848 after, not 17,370 -- the 17-18k readin.

## not-a-defect — 1

- **SI-12-DF-02**: CONFIRMED NOT A DEFECT, and four of the six lines are gone anyway.

## answered — 1

- **SI-12-DF-05**: NOTE ADDED BY SI-27, because `answered` was terminal with no note and THIS ROW'S SUGGESTED FIX MUST NOT BE APPLIED.
