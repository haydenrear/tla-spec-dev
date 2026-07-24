# The Coverage Audit Gate (MF-026)

The executable procedure is `prompts/coverage_audit.md`; the report shape is
`templates/coverage_audit_report.md`. This document is the doctrine: why the
gate exists, when it runs, and what its findings may and may not be closed by.

## The structural hole

Every oracle in this toolchain is bounded to what is **already modeled**:

| Oracle | Bounded to |
|---|---|
| Output conformance | cases that exist |
| Projected-state conformance | cases that exist |
| Effect conformance | the corpus — generated *from the model* |
| Mutation kill test | faults seeded one per port and one per invariant — **modeled boundaries only** |

Unmodeled program surface is never generated into a case, never adapted, never
mutated. **A subsystem with no representation is invisible to all four gates,
and all four report green.** A model can be perfectly faithful about everything
it covers and blind to half the program.

Before MF-026, "coverage" appeared in `modular_fuzzing.md` and
`architecture_tractability.md` only as an assertion — "a new unjustified
coverage gap", "external coverage is rejected, not celebrated", "a harness that
reaches 2% coverage is rejected". Nothing measured it.

The four oracles check **fidelity of what is modeled**. This gate checks
**completeness of what is modeled**. Neither implies the other, and a green
oracle run carries no information about this question.

## Ordering — a required end-of-epic step

The audit runs **once per epic**:

> **after every mechanism ticket has landed, and before final end-to-end
> integration.**

The ordering is load-bearing in both directions.

- **After the mechanisms**, because the audit is measured against the model as
  the epic actually leaves it. Running it earlier audits a model that is still
  being built and reports gaps that later tickets were always going to close.
- **Before final integration**, because it is a *promotion gate*. Its whole
  purpose is to block promotion of a model that does not represent the program.
  An audit run after integration is a report, not a gate.

An epic that promotes without a recorded audit verdict is a visible defect, not
a silent one — see "Recording" below.

## Gate semantics

**In-scope gaps are HARD.** An uncovered behavior or effect inside the epic's
declared scope fails promotion. Per the fourth governing rule in
`architecture_tractability.md`: **model it, or change the program.** There is no
third option.

**Out-of-scope surface is inventoried and reported, and does not gate.** An
epic scoped to one subsystem is not blocked by surface elsewhere. The inventory
still gets written down — a gap nobody recorded is a gap nobody can schedule.

**Scope is declared once, in the plan, and reviewed once.** It is never waived
per finding. **This distinction is the entire design.** A gate whose findings
can each be closed by a recorded justification is precisely the out-of-contract
suppression that was purged from MF-013, rebuilt one level up. One reviewable
boundary decision is a boundary; N per-finding justifications are an escape
hatch. See "No Degenerate Escapes".

Concretely, the prompt **forbids** any "justified" or "accept as-is"
disposition for an in-scope gap. The dispositions are exactly three:

1. **Model it** (in scope, hard),
2. **Change the program** (in scope, hard),
3. **Inventory it** (out of scope, per a *quoted plan line*, does not gate).

An agent that believes an in-scope gap should not be modeled does not have a
disposition available. What it has is an argument that the **plan's scope is
wrong** — which it escalates, and which the owner amends once, visibly. It is
not resolved row by row.

**The scope is read from the plan, never chosen by the auditing agent.** An
agent that picks its own scope can define every gap out of existence, which
would make the gate worthless. The prompt requires the plan text to be quoted
verbatim with line numbers, and requires every in/out classification to name
the plan line that produced it. A classification that cannot be traced to a
quoted line is an escalation, not a classification. Where the plan is silent or
ambiguous, the procedure **HALTS** and asks the owner to amend the boundary.

**Remediation is advisory; the gap is not.** The agent proposes *how* to close
each gap; the owner approves, adjusts, or vetoes the approach — consistent with
"Recommendations, Never Verdicts". The **existence** of an in-scope gap is not
negotiable.

## Why the discipline lives in the prompt

The deliverable is **prompt-only, by owner decision** — no inventory tooling.
That tradeoff was taken deliberately, and it has a consequence worth stating
plainly: there is no mechanical completeness guarantee from the inventory side,
so the entire discipline lives in the prompt's structure.

A prompt that says "look for uncovered behavior" returns whatever the agent
happened to notice, formatted as though it were a survey — which is worse than
no audit, because it *reads* like completeness. The prompt therefore imposes:

- **Row sets produced by commands, not by attention.** Each sweep names the
  enumeration command; the table must carry exactly as many rows as the command
  returned, and the report reconciles `N == M` explicitly.
- **Per-row verdicts with `file:line` evidence** — `represented` / `partial`
  (with the uncovered part named) / `unrepresented`.
- **Default polarity `unrepresented`.** Coverage is granted only on cited
  positive evidence. This is MF-027's polarity lesson: absence of evidence is
  never evidence of coverage.
- **Effects enumerated by category** — filesystem, network, subprocess,
  environment, clock, randomness, persistent store — so the sweep is checkable
  rather than impressionistic.
- **Internal and External reported separately.** A merged verdict is not
  acceptable output; a behavior may be covered in one view and absent from the
  other, and merging hides exactly that. A project with only one view module
  reports the missing view's whole surface as unrepresented — never "N/A".
- **A required attestation** naming what was *not* walked, which rows were
  dispositioned from a path rather than from code, and whether a reader could
  reproduce the row set from the recorded commands.
- **`INCOMPLETE` as a first-class verdict.** It is not a `PASS`.

Attestation item 6 requires the auditing agent to report findings **about the
prompt** — specifically, any way the procedure let it produce a plausible report
without walking the surface. That requirement is not a courtesy. If the prompt
is insufficient, a follow-up ticket for a mechanical inventory is the honest
outcome, and a more valuable one than a clean report.

## What the first run established, including about itself

The prompt was validated by execution against this repository (MF-026,
2026-07-19): verdict `INCOMPLETE`, **19 in-scope gaps**, 145 of 160 rows
escalated for want of a plan closure rule. It found real defects in the prompt,
which were fixed in response — a regex that silently omitted every parameterized
action, sweeps searching a narrower surface than they claimed (hiding 233 hits
including every network call), unanchored patterns at a 95% false-positive rate,
and a missing grouping allowance that forced swept categories to report
INCOMPLETE.

**One limit survives, and no wording change closes it:**

> **The row-count reconciliation is self-reported.** `N == M` is an assertion
> the auditing agent makes about its own diligence. Run 1 reported `N != M`
> against itself three times — the behavior the prompt wants — but nothing
> *forces* that.

Writing raw sweep output to `results/sweep-raw/` narrows it, because a reviewer
can recount. Closing it requires a **mechanical inventory that produces the row
set independently of the agent**, tracked as
[issue #48](https://github.com/haydenrear/tla-spec-dev/issues/48). The intended
split is worth preserving when it lands: **tooling owns enumeration; the agent
owns disposition.** Mapping a row to a spec action is judgment and should remain
judgment; producing the row set is not.

Until then, this gate's strength is bounded by the honesty of the agent running
it, and a reader of any report it produces should treat the attestation as more
load-bearing than the tables. The prompt-only choice was deliberate and it
worked — the gate found 19 real gaps, including three model/manifest desyncs no
oracle checks. It is not a completeness guarantee, and this section exists so it
is never mistaken for one.

## Recording

The audit's verdict is recorded in two places:

1. **Ticket evidence** — the filled report under the ticket's `results/`
   directory.
2. **The complexity ledger** (MF-019), in the `coverage_audit` block of
   `results/complexity_ledger.yaml`, which flows into the append-only
   `complexity_ledger.json`.

The ledger block exists so that **an epic which skipped the audit is visible**.
It defaults to `not_run`, which is recorded and reported as such — never
omitted, and never inferred to be a pass. At workflow-scope close (end of
epic), any verdict other than `pass` — `not_run`, `fail`, or `incomplete` —
**refuses the close**, in keeping with every other gate in this toolchain: a
check that silently passes when its input is absent is not a check, and
`incomplete` refuses alongside `fail` because a sweep that did not walk the
surface carries no information about it.
