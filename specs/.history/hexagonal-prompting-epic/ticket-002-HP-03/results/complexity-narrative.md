# HP-03 complexity narrative

## The measured delta is zero, and that was the design

`analyze complexity` measures the TLA+ representation. HP-03 changed no TLA+:
no action, no variable, no constant, no config. `TlaSpecDevCli.tla`, `MC.cfg`
and `MCsmall.cfg` are byte-identical to the epic tip
(`results/zero-model-delta.txt`), so `direction=zero` is the correct reading and
not an unmeasured one.

That is the whole point of `surface_cost_rule`. The plan's
`model_delta_expectation` explicitly permitted a new action if the generation
mode needed one. It did not need one: `--negative-cases` is a per-flag variant
of the existing `GenerateCases` action, which `semantic_model_rule` places
out-of-model, and it performs no effect that action does not already declare —
same `.tla` and `.cfg` reads, same `spec_tree` writes, and **no second TLC run**.
The predecessor's measured price for a surface-adding ticket was ~1.5 new
coverage gaps and 8x state space. This ticket pays 0 and 1x.

## Where complexity actually went down, by six thousand times

The number this ticket moved is not in the descriptor, because the descriptor
does not measure it. `generate cases` on `MCsmall.cfg` — the config that exists
so that a corpus is tractable — produced **3,678,217 cases and a 7.4 GB
`cases.py` CPython cannot import**, 18,391x the manifest's own cap. It is now
**541 cases and 667 KB**. That is 6,799x fewer cases and roughly 11,000x less
generated Python, on an unchanged model.

The lever is `specs/current/tlc_projection.py`, which this model was the only
one in the repository not to have. It moves two kinds of variable out of the
STATE and into the asserted OUTPUT:

- `lastCommand` and `result` — pure outputs every action writes and no guard
  reads. While they sit in the state, every case's before-state records which
  command happened to run before it, so the corpus enumerates one case per
  predecessor command. Measured: removing `lastCommand` alone takes 3,678,217
  transitions to 2,964,421.
- the six recorded verdicts — a six-dimensional independent product every
  action carries through unchanged, so the corpus otherwise enumerates each
  command once per combination of five verdicts it never reads and never writes.
  The output projection carries back exactly the verdicts the action **itself
  changed**, so what a command records is still checked; what it merely
  coexisted with is not.

**Nothing was deleted, and that distinction is the MF-020 trap.** A count that
improved because an oracle was dropped is not an improvement. The measured
ladder is in `results/mcsmall-tractability.txt`; the module's own docstring
names the single thing genuinely lost (a fault whose only symptom is that a
command wrongly PRESERVES a verdict it should not have touched — an obligation
that belongs to, and is discharged by, TLC on the unprojected model).

## The reduction that was available and was refused

**Raising the cap.** 541 is still 2.7x `max_internal_cases_per_component: 200`,
and the cap gate's own accept path prints the fix: set the cap to 541 with a
recorded rationale. `budgets.source` is still `defaults` and
`budgets.rationale` is still `{}`, so 200 was never negotiated for this program
either — both numbers are unowned and the change would have been defensible.

It was not taken. The value the tool suggests is the number this ticket just
produced, and a budget fitted to the result it must admit is not a budget. It
would also have turned an acceptance assertion from PARTIALLY MET into MET by
editing the threshold rather than the artifact, three tickets before the
evaluation ticket reads it. Filed as HP-03-DF-02 with three dispositions, for
someone who is not also being measured by the number.

## The reduction that was available and was taken

**`--negative-dedupe guard-reads`**, and it was measured before it was trusted.
The exact negative corpus is 39,966 cases; collapsing cases that agree on the
action, the arguments, the violated conjunct and every state variable that
conjunct reads gives 118 — a 339x reduction. Those are the same test by
construction, but "by construction" is an argument, not a measurement, so both
corpora were run against both catalogues. They kill **identically**: 3 of 3 and
5 of 5 guard relaxation, 0 elsewhere, on 118 cases and on 39,966
(`results/kill-table-dedupe-cost.json`). The tractability lever costs zero
kills. `--negative-dedupe none` remains available and both counts are printed
on every run.

## A complexity result that is not flattering

The generator is still **worse than a suite written in an afternoon** on this
fixture. The hand-written behavioral suite kills 10 of 10; the whole-view corpus
kills 5 of 10 and both corpora together 8 of 10. More pointedly, only 3,440 of
43,128 positive cases (8.0%) are executable at all, and `M07` — a positive
control the catalogue declares must die on every instrument on every arm —
SURVIVES the whole-view corpus, because `Reserve` contributes zero executable
cases.

The 90.7% that cannot execute are the fixture's seven `Refuse*` actions: the
PROFILE CHANGE. Each takes `(t, a, r)` and mentions none of them in its body, so
no recovery mechanism can recover an argument — the state pair does not contain
one. 39,100 cases each saying that A rejection happened and never which call was
rejected. The generator produces the same refusals as 118 cases carrying exact
arguments. That comparison is the ticket's real complexity finding: **the
profile change is the more expensive route and the one that does not work**, and
it is filed as HP-03-DF-03 rather than fixed, because the fixture is HP-01's and
must not move before HP-06 reads it.
