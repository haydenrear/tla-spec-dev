# Corpus Diagnostics And Hard Caps

Status: Open

Supersedes the former "Corpus Distillation" scope. Renamed from
`tickets/014-corpus-distillation.md`.

## What changed and why

The original ticket transcribed the "Corpus Discipline" section of
`references/modular_fuzzing.md`, which said to distill the corpus: stratify by
`(action, label class)`, cap, and record what was dropped. **Owner direction
2026-07-18 withdraws that.** Both the doctrine section and this ticket were
wrong in the same way.

Filtering cases to fit a budget under-represents the program, which the
standing objective forbids outright. The `kill_rate_floor` does not make it
safe: the kill test seeds one fault per port and per invariant, so it only
*samples* for damage — a dropped case that no mutant happens to probe is
invisible to it. Recording the drop rule does not fix this either; a recorded
deletion is still a deletion.

And dropping is the wrong response to the signal. In the committed example
corpus:

| Cases | Action |
|---|---|
| 200 | `submit_duplicate_add_cart_item` |
| 184 | `submit_duplicate_checkout` |
| 120 | `submit_duplicate_create_account` |
| … | … |
| 4 | `submit_checkout_empty_cart` |
| **2** | `submit_create_account` |

732 cases across 11 labels; 69% of them are duplicate-submission variants.
That lopsidedness is **evidence about the representation**, not noise to be
trimmed. A model emitting a hundredfold more interleavings for one action than
another is enumerating redundancy — interchangeable values wanting symmetry
reduction, unconstrained orderings wanting a state constraint, or an action
enabled across many equivalent states wanting abstraction.

**The corpus is the symptom; the diagram is the defect.** Write the diagram so
the redundant cases are never generated, rather than deleting them afterward.

## Acceptance criteria

- **Nothing is ever dropped, filtered, sampled, or truncated to satisfy a
  budget.** Not silently, and not with a recorded drop rule either. If the
  implementation contains a code path that removes a case to fit a cap, this
  ticket has failed.
- `max_internal_cases_per_component` and `max_external_cases_per_action` become
  **hard gates**, in the same shape as MF-011's state-space bound: over budget
  exits nonzero and reports. They are read through `scripts/budgets.py`.
- Caps stay per-program and negotiable. Raising one with a recorded one-line
  rationale is a legitimate, reviewable decision — that is the "accept" path.
  Make it explicit and easy; silent trimming must not exist as an option.
- On a cap failure the diagnostics report, at minimum: the count per
  `(action, label class)`, which strata dominate, which are starved, and
  **what varies across the redundant group** — the actionable part, since it
  points at symmetry, ordering, or abstraction as the cause.
- Labelers are retained and repurposed from selection criteria to diagnostic
  strata. No labeler output chooses which cases survive.
- Remediation output is a **recommendation requiring user approval**, never
  auto-applied — the same rule as `analyze complexity`'s suggested move.
- Named regression traces (promoted counterexamples, Hypothesis failures,
  production bugs) are always retained. This part of the original doctrine was
  right and is unchanged.
- `references/modular_fuzzing.md` "Corpus Discipline" is amended in this same
  change so doctrine and implementation cannot diverge. (The amendment has
  already landed; verify it matches what you ship, and correct it if not.)

## Validation note

This ticket is unusually well served by fixtures despite the epic-wide
spec-case execution deferral. The 732-case corpus in
`examples/distributed_history/specs/generated/testgraph/traces/` is committed,
real, and exactly the pathological distribution the diagnostics exist to
describe. Use it. You do not need to run case generation to validate this
ticket, and per the deferral you must not.

## Watch for

The temptation to "helpfully" offer an opt-in `--distill` flag. Do not. An
opt-in filter is still a filter, and it will be reached for under budget
pressure — which is precisely when losing coverage is most dangerous.
