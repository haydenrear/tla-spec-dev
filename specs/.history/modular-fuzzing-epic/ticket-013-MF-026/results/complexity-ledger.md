# MF-026 complexity ledger narrative — Coverage audit gate

## Delta: ZERO, and required to be

| Metric | Baseline (epic tip 1176aa2) | MF-026 | Delta |
|---|---|---|---|
| Variables | 9 | 9 | 0 |
| Bound | 699,840 | 699,840 | 0 |
| Distinct states (TLC) | 231,621 | 231,621 | 0 |
| Generated states | 5,619,356 | 5,619,356 | 0 |
| Depth | 25 | 25 | 0 |

Zero was not merely acceptable here, it was mandatory. `max_state_space_bound`
sits at 699,840 / 1,000,000 — 70.0%, 1.43x headroom. A single *boolean*
variable, the smallest bounded addition available, multiplies the bound to
1,399,680 and breaches the cap. **No new bounded variable fits at any
cardinality.**

This ticket's deliverable is a prompt, a report template, doctrine, and a ledger
field. None of it is program behavior in the TLA+ sense, so none of it wanted a
variable. The zero delta is a consequence of the ticket being correctly scoped
rather than of restraint applied after the fact. Evidence:
`results/tlc-current.txt`, `results/analyze-complexity.txt`.

## Retention evidence

Recorded as `deferred` against the epic-wide deferral of spec-case execution to
MF-023 (#30) — **not** as passing. Per MF-027's polarity rule and MF-019's
Gate 3, absent evidence is not passing evidence, and an unverified constraint
cannot witness retention.

This is sound here only because the delta is **zero**. MF-019's gates reject
unverified retention when complexity *decreased*, precisely because a reduction
can be bought by deleting behavior. A zero delta claims no reduction, so there
is nothing for retention evidence to license. Had this ticket claimed any
reduction, `deferred` retention would have refused the close, correctly.

## Refinement search — searched, FOUND (not applied)

`analyze complexity` was run against the ticket-local model with the TLC report
attached (`results/analyze-complexity.txt`). It surfaces the standing
recommendation:

> ABSTRACT — no configured invariant reads `[lastCommand, result]`; Move 1
> permits projecting variables no invariant reads. Projected gain: removes both
> from the model.

Recorded as `found`, **not applied**, for two independent reasons:

1. The gain is `[PROJECTED]`, explicitly UNVERIFIED, and the analyzer itself
   requires a transition-level diff plus a TLC rerun before any projected
   reduction may be recorded as a result. MF-020 withdrew a projected -13.1%
   for exactly this reason: it turned out to require deleting a legitimate
   idempotent re-fire transition, and the distinct-state gate was structurally
   blind to it.
2. Legitimacy is conditional on the mutation kill rate holding afterwards
   (MF-016), and spec-case execution is deferred epic-wide to MF-023. The
   evidence that would license the projection is precisely the evidence this
   epic has not yet produced.

Applying an advisory recommendation on projected figures, without the kill-test
evidence, inside a ticket whose model delta is required to be zero, would be
three violations at once. Recommendations are advisory and user-approved, never
auto-applied. The recommendation stands for MF-023, which re-runs it after
decomposition.

**Did MF-019's mechanized ledger work?** Yes, and it did real work rather than
ceremonial work. `open ticket` scaffolded `results/complexity_ledger.yaml`
pre-filled with `TODO` sentinels, and the close path refused until they were
replaced — the sentinel is parsed as an empty value specifically so an unfilled
template cannot be closed through. The refusal is the mechanism. It also
computed the delta table above from `analyze complexity` plus the TLC report
without hand transcription, which is where the previous eleven manual ledgers
were most error-prone (MF-020's retro-correction being the case in point).

## The coverage audit field added to the ledger

MF-026's own acceptance criteria required the audit verdict to be recorded in
this ledger "so an epic that skipped the audit is visible". Implemented as a
`coverage_audit` block, and the design choice worth recording is its
**scope-sensitive asymmetry**:

- At **ticket** scope, `not_run` is recorded, printed, and does **not** refuse.
  The audit is an end-of-epic step by definition; failing it at every ticket
  close would force each ticket either to run a whole-epic audit or to fake a
  verdict. Both are worse than recording the absence honestly.
- At **workflow** scope, anything but `pass` **refuses**. The epic is over and
  there is no later opportunity. A check that silently passes when its input is
  absent is not a check — the exact degeneracy the 2026-07-18 audit found
  across this epic.

`incomplete` refuses alongside `fail`, and unrecognized statuses — including
`justified`, `accept_as_is`, `waived` — normalize to `not_run` rather than
passing. That last case is tested directly
(`test_unrecognized_verdict_never_passes`): the dispositions the prompt forbids
must not become passes by being written into the ledger instead. Closing the
prompt's escape hatch while leaving the ledger's open would have rebuilt the
same degeneracy one layer down.

## Findings about the prompt-only approach

See `results/coverage_audit_report.md` §8 and the ticket report. The worked
example's findings about the procedure itself are recorded there rather than
being smoothed over, per the ticket's explicit instruction that a self-critical
result outranks a tidy one.
