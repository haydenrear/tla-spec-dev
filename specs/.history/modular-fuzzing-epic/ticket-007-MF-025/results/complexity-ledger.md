# MF-025 complexity ledger

Recorded **jointly with retention evidence**, per the standing objective: a
reduction is only reportable next to proof that behavior was retained.

## Retention (the gate)

| Measure | Pre-collapse baseline | Post-collapse | Verdict |
|---|---|---|---|
| Distinct reachable states | 9,011 | 9,011 | **equal** |
| Depth of complete state graph | 24 | 24 | **equal** |
| States generated | 87,464 | 87,464 | equal |
| Average / max / p95 outdegree | 1 / 8 / 6 | 1 / 8 / 6 | equal |
| Invariants checked (`MC.cfg`) | 12 | 12 | equal |
| TLC verdict | no error | no error | equal |

The baseline was **measured on this branch before any edit**
(`tlc-baseline-precollapse.txt`), not quoted from MF-014. The generated-state
count and the full outdegree distribution match as well as the distinct/depth
gate, which is stronger evidence than the gate alone: a deleted self-loop shows
up as a generated-states drop at constant distinct states, and there is none.

## Reduction

| Measure | Before | After | Factor |
|---|---|---|---|
| Declared state-space bound | 663,552 | **34,992** | **18.96x** |
| Bounded dimensions | 7 | 5 | -2 |
| Model variables | 9 | 7 | -2 |
| Per-ticket declared representation | 8 x 8 x 64 = 4,096 | 6^3 = 216 | 18.96x |

The derived projection in the ticket was ~34,992. The **measured** value is
34,992 exactly. Projection and measurement agree; the measured value is the one
recorded.

Budget headroom: 34,992 against `max_state_space_bound` 1,000,000. At the
previous 663,552 a single further 3-valued gate would have breached
(1,990,656). Post-collapse the same gate lands at 104,976, and three more
after it still fit.

## Refinement search

Searched for further reduction beyond the collapse; recorded outcome:

- **`lastCommand` / `result` projection** — `analyze complexity` reports these
  are read by no configured invariant, so Move 1 permits projecting them. They
  are already unconstrained by `TypeInvariant` and therefore excluded from the
  bound, so projecting them would not move the 34,992 figure. **Deferred to
  MF-016**, and legitimate only if the mutation kill rate holds afterwards. Not
  implemented here.
- **Further collapse of `ticket_state`** — none available. All six ordinals
  were individually shown reachable, so the domain is exactly the reachable set
  and cannot shrink without deleting behavior.
- **`setup_phase`, `spec_root`, `complexity_gate`, `corpus_gate`** — each is
  already at its reachable cardinality (6, 3, 3, 3).
- **Residual slack** — actual reachable states are 9,011 against a bound of
  34,992, i.e. 25.8% density. The remaining gap is *cross-variable correlation*
  (for example `spec_root = NoRoot` only while `setup_phase < 3`), not
  single-variable over-declaration. Removing it would need a dependent
  representation rather than a product of independent domains; that is the
  deferred research direction in MF-018, not something this ticket can take.

**Conclusion: searched, found no further reduction in scope.**

## New finding, referred to MF-023 (not worked around)

The collapse changed the component decomposition, and this is reported rather
than engineered away:

| | Before | After |
|---|---|---|
| Components | C1 (6 vars, 12 actions), C2 (3 vars, 5 actions) | C1 (7 vars, 12 actions) |
| Modularity Q | 0.022 | 0.000 |
| Budget verdict | FAIL: C1 touched by 12 actions > 8 | FAIL: C1 has 7 vars > 6; C1 touched by 12 actions > 8 |

C2 previously consisted of exactly `active_tickets`, `closed_tickets` and
`ticket_phase` — the three variables that were one lifecycle. Collapsing them
to a single variable leaves nothing for a 3-variable community to form from, so
`ticket_state` joins C1 and `max_component_variables` (6) is now breached.

This is a **metric artifact of the merge, not an increase in coupling**: three
mutually coupled variables became one, so the underlying interaction went down,
not up. The modularity score simply has no structure left to find in a model
that is now genuinely one component.

Both C1 findings — the pre-existing 12-actions breach and this new 7-variables
breach — are C1 decomposition problems, which is precisely MF-023's scope
(`analyze complexity` proposing the cut from the R/W matrix and modularity
score). Per that ticket's "the finding outranks the migration" doctrine, this
is recorded with evidence and left for MF-023 rather than hand-patched here.
The model already failed the budget gate before this ticket, so the gate's
pass/fail state is unchanged.

## Validations deferred to MF-023

Spec-case execution is deferred epic-wide to MF-023 and was not run here:

- generated spec-case corpus generation
- corpus run and `analyze corpus` verdict over a fresh corpus
- effect conformance harness
- mutation kill test

The known `C1 is touched by 12 actions` finding was **not** worked around, per
the epic-wide instruction, and the new `C1 has 7 variables` finding is referred
to the same ticket.
