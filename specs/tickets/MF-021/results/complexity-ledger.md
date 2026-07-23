# MF-021 — complexity ledger (standing objective, `references/architecture_tractability.md`)

Recorded **jointly** with behavior-retention evidence, per the standing
objective. Retention first, because a complexity number without it is
meaningless.

## 1. Behavior retention

| Gate | Result | Evidence |
|---|---|---|
| TLC (ticket-local current, 120s cap) | 919 distinct / 3664 generated / depth 21 / 0 errors | `tlc-current.txt` |
| Spec-unit tests (MF-021) | passed, 2 targets (13 + 12 tests) | `spec-unit-tests.txt` |
| Repository unit tests | **123 passed** (117 baseline + 6 new) | `repository-unit-tests.txt` |
| Test Graph `specWorkflow` | 8/8 steps, BUILD SUCCESSFUL | `testgraph-specWorkflow/` |
| Test Graph `cliWorkflow` | 2/2 steps, BUILD SUCCESSFUL | `testgraph-cliWorkflow/` |
| Regression gate (pre-fix must fail) | 4 failed / 2 passed pre-fix; 6 passed post-fix | `prefix-failure.txt`, `postfix-pass.txt` |

## 2. Model complexity delta: **zero, and that is the correct outcome**

| Metric | Baseline (MF-020) | MF-021 | Delta |
|---|---|---|---|
| State variables | 11 | 11 | 0 |
| Distinct states | 919 | 919 | 0 |
| Depth | 21 | 21 | 0 |
| Generated states | 3664 | 3664 | 0 |

This ticket is a defect fix in file-promotion mechanics. It introduces no new
program state or action, so the model must not move — see `design-decision.md`
§ "Model impact". The identical figures are the retention proof, not a null
result.

## 3. Refinement search — findings

Searched, and **found two**, both recorded rather than applied.

**(a) `replace_tree` is now single-use — applied reduction in reasoning, not code.**
After this ticket, `replace_tree` (the `rmtree`-then-copy primitive) has exactly
one remaining caller: `accept_new_ticket_current`, where source and destination
are both ticket-local trees seeded identically at `open`. No filtered/unfiltered
asymmetry can exist there, so `rmtree` is sound on that path and the function is
correctly retained. The dangerous *use* was removed; the primitive was not,
because it is still the right tool for a symmetric replace. Net: one less
unsound call site, no dead code introduced.

**(b) Duplicate script entrypoints — RECOMMENDATION, owner approval required.**
`scripts/close-ticket.py` (8 lines) and `scripts/close-spec-workflow.py` are
hyphenated compatibility shims delegating to the underscore modules. They are
still referenced by `README.md:162` and `scripts/scaffold_spec_workflow.py:48`,
so removal is a user-visible surface change. **Not applied** — architectural
moves are recommendations, never unilateral. Estimated reduction: 2 files, ~16
lines, one naming convention.

**Deferred, not touched:** the `setup_phase` ordinal collapse (11 -> 7
variables, declared bound 393,216 -> 73,728 at identical 919/21) remains
deferred by owner decision. Not implemented here, per the ticket's explicit
instruction.

## 4. Complexity added by this ticket, stated honestly

The fix is not free. It adds ~95 lines of production code across two files and
one new persisted field (`ticket.yaml:seed_manifest`), replacing a 4-line
`replace_tree` call. That is a real increase in mechanism.

It is justified because the 4-line version was *silently* wrong in a repository
whose stated purpose is mechanized behavior retention: a deleted test cannot
fail, so the suite reported green while shrinking, twice. The added mechanism
buys an explicit, inspectable record of what each ticket was given and what
promotion did with it — enumerated on every close. Trading four lines of silent
data loss for ninety-five lines of auditable provenance is the correct
direction for this repository.
