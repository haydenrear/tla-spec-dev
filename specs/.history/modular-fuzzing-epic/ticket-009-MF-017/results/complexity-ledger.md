# MF-017 complexity ledger and retention evidence

Standing objective, `references/architecture_tractability.md`: record the
complexity delta **jointly** with behavior-retention evidence, or record
"searched, found none".

## Model delta: zero, and that is the correct answer

| Metric | Before (MF-022 tip) | After (MF-017) | Delta |
|---|---|---|---|
| State variables | 8 | 8 | 0 |
| Declared state-space bound | 221,184 | 221,184 | 0 |
| TLC distinct states | 2,923 | 2,923 | 0 |
| TLC search depth | 23 | 23 | 0 |
| States generated | 18,720 | 18,720 | 0 |
| Actions | 10 | 10 | 0 |

Measured, not asserted: `specs/tickets/MF-017/results/tlc-current.txt`.

### Why no `EmitSkillFeedback` action / `skill_feedback` variable was added

The plan entry's `desired_actions: [EmitSkillFeedback]` and
`current_increment.model_state: [skill_feedback]` were written when this ticket
sat at promotion_order 70. Implementing it showed the change does not reach the
state machine, and adding state anyway would have been representation inflation:

- **No new command.** Close-out already exists in the model as `CloseTicket`.
  The retro is emitted *by* that command, not as a separate user-invoked step.
- **No new guard or sequencing.** Nothing about when `CloseTicket` may fire
  changed. Feedback filing is **recorded**, not **enforced** — the acceptance
  criterion is "history entries record whether feedback was filed", and gating
  close on a filled-in retro would have been invented scope that blocks every
  future close.
- **No new externally-visible branch.** "Filed" vs "not filed" is content of an
  emitted document read back at close time, the same category as the history
  manifest itself, which the model has never represented.

Direct precedent, same close path, accepted at post-merge review: **MF-021**
("Model delta zero — preserve-and-enumerate changes promotion's file effect,
not the command state machine"). MF-017 changes close-out's file effect in
exactly the same way.

A 3-valued `skill_feedback` fact would have multiplied the declared bound by 3
(221,184 -> 663,552) to represent a document field. That is the "gaming the
metric" failure in reverse — paying real complexity for no behavior.

**This is a recommendation surfaced for owner review, not a unilateral scope
change:** if the owner wants the filing status to be modeled state (e.g. as a
precursor to *gating* workflow close on a resolved retro), that is a genuine
behavior change and should be an amendment ticket, not a silent addition here.

## Retention evidence

| Check | Result | Evidence |
|---|---|---|
| TLC, ticket-local current | No error; 2,923 distinct, depth 23 | `tlc-current.txt` |
| Repository unit tests | 171 passed (151 baseline + 20 new) | `pytest-repository.txt` |
| Spec-unit tests (MF-017) | 2 targets, 21 + 18 passed | `spec-unit-tests.txt` |
| `specWorkflow` graph | BUILD SUCCESSFUL, 8/8 steps | `graph-specWorkflow.txt` |
| `cliWorkflow` graph | BUILD SUCCESSFUL, 2/2 steps | `graph-cliWorkflow.txt` |

No pre-existing test was modified or deleted. The 20 new repository tests and 3
new spec-unit tests are additive.

## Complexity reduction search: searched, found none

Surfaces examined this ticket, and why no reduction was taken:

- **`TlaSpecDevCli.tla`** — the two known reductions are explicitly deferred and
  out of scope: the `ticket_state` collapse
  (`active_tickets`/`closed_tickets`/`ticket_phase` -> one ordinal, projecting
  221,184 -> 11,664) and projecting `lastCommand`/`result`. No third reduction
  found in the remaining 8 variables.
- **The close path (`spec_evolution.py`)** — ticket close and workflow close
  already shared `commit_recommendation` / `write_manifest`; the feedback emit
  reuses one function from both rather than duplicating, and
  `print_skill_feedback_report` hangs off the existing
  `print_commit_recommendation` seam. No duplication was introduced and none was
  available to remove.
- **`close_ticket.py` / `close_spec_workflow.py` / `close_tickets.py`** — all
  three are thin argparse fronts over `spec_evolution`; the new
  `--no-skill-feedback` flag threads through the existing keyword-argument
  pattern. Merging the three entry points is an architectural move requiring
  owner approval and is not proposed here.

Per the MF-020 lesson recorded in the plan notes: no projected reduction is
claimed anywhere in this ledger, because a projection is unverified until the
transition-level diff is inspected.
