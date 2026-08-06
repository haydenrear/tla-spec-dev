# FI-04 — the fixture or the goal, decided

`PA-06-DF-08` said a goal whose null is entailed by its fixture is not a
measurement, and that either the fixture changes or the goal does. This is the
decision, with the reasoning, and it is the ticket's headline.

## The decision

**Both, and each in one specific part.**

1. **`GOAL-cases-drive-ports`'s METRIC is retired.** Not the question — the
   metric. *"The count of comparable cells where the arms AGREE"* cannot move
   for any reason that is about architecture, and this is provable rather than
   observed.
2. **The fixture is amended in the one place the entailment leaves open**, and a
   divergence is demonstrated there. **Measured: one cell, on the column whose
   instrument is a function of the arm's architecture, with a third independent
   re-anchoring landing on the non-hexagonal side.**

## Why the metric had to go, in two clauses and a corollary

The null needs two things, and both were measured before this ticket:

- **E1 — the instrument is the same on every arm.** A corpus is a pure function
  of `(model, manifest, flags)`. The A/B holds one model and one manifest across
  every arm *by design*, and for a good reason: `README.md` states it —
  *"If each arm generated its own, a D1 difference between arms could be a
  difference between their models and nobody could tell which produced it."* So
  no change confined to generation can make two arms' corpora differ. PA-03
  reached this independently.
- **E2 — the subjects are the same under that instrument.** `AD-F1`'s exhaustive
  observational fingerprint — 28,561 command sequences, 13-action alphabet, full
  projection after every step, per arm per mutant — measured the three arms'
  **mutated** trees observationally identical on **10 of 11 rows**.

E1 and E2 together entail the answer: an identical instrument on observationally
identical subjects returns identical verdicts. The 64 of 64 was arithmetic.

**And the corollary is what actually kills the metric.** The catalogue holds the
`semantic` equal across arms — the right rule, adopted at EVAL-RERUN for the
right reason, *"so that a per-arm score compares two implementations rather than
two catalogues"*. A fault that satisfies that rule is re-anchorable onto both
arms, and a fault re-anchorable onto both arms is one both arms have somewhere.
So:

> **Any fault that could move the metric is, by construction, not comparable.**
> It would have to live somewhere one arm has and the other does not — and a row
> with no home on one arm is excluded from the comparable set before it is
> scored.

That is not a fixable denominator. The metric asks a question its own
comparability rule forbids the answer to. Reporting `MISSED` against it a third
time would be reporting arithmetic.

## What replaces it

Not *"do the arms' verdicts differ"*. That was always a proxy. The question the
goal was reaching for is **whether the architecture changes what a verdict is
ABOUT**, and that has a well-posed metric:

> **For one semantic fault, per arm: the number of DISTINCT COMPOSITIONS under
> which one shared instrument returns different verdicts.**

- Arm A: **0**, and it is 0 by construction — one implementation of the durable
  side, always wired, nothing a `--wiring` flag can substitute.
- Arm C: **0**, and this one is stronger, because `arm_c/REJECTED.md` records its
  author considering arm B's seam and declining it **on merit**.
- Arm B: **1**, measured.

**Its null is not entailed, and the same run proves it.** `FI-M15`, seeded in arm
B's *domain*, gives the same verdict under both of arm B's compositions — count
**0** on the arm whose count is 1. So the metric can come out zero on a
hexagonal arm, and does, for a fault that is not behind the port.

It is also **direction-neutral**, which the old metric was not. It says the
architecture changed what a verdict is about; it says nothing about whether that
is good. On this fixture it points **against** the port on the comparable row.

## The demonstrated divergence

One semantic — *"the ledger's read-back silently drops every line beginning
`CLOSE`"* — re-anchored **by the property, not by the bytes** onto four sites
whose `find` strings have nothing in common. Predictions sealed at `4697687`,
before `run_arm_swap.py` was pointed at any of them.

| row | arm | homes | action-bound | port-swap `:real` | port-swap `:fake` | suite-real | suite-fake |
|---|---|---|---|---|---|---|---|
| `FI-M18` | A | 1 | KILLED | KILLED | **KILLED** | KILLED | *no such column* |
| `FI-M19` | C | 1 | KILLED | KILLED | **KILLED** | KILLED | *no such column* |
| `FI-M16` | B | 2, wired | KILLED | KILLED | **SURVIVED** | KILLED | SURVIVED |
| `FI-M17` | B | 2, unwired | SURVIVED | SURVIVED | **KILLED** | SURVIVED | KILLED |

**The divergence is the `corpus-port-swap:fake` column on the comparable row:
arm A `KILLED`, arm C `KILLED`, arm B `SURVIVED`.** The comparable row on each
arm is the one the default composition wires, declared per row in the catalogue
before the run.

**The architectural reason, measured rather than asserted.** `divergence.py`
computes the composition count from the runs themselves — two columns whose
evidence block is identical on every row ran the same program, whatever their
names say. Arms A and C: **1**. Arm B: **2**. That is `AD-F6` mechanised, and it
is the only variable that tracks the verdict.

**Arm C is the check PA-04 asked for.** A skeptic can call any such divergence a
property of the re-anchoring rather than of the port. Arm C is a third,
independent re-anchoring — onto a tree length-matched to arm B, carrying zero
architectural vocabulary — and it lands on **arm A's** verdict. A re-anchoring
artefact had an even chance of producing a third answer. It did not.

**Read which way the cell points, because it is not a win.** Swapping in arm B's
own fake took a real durable fault off the executed path, and **no instrument
reported that it had.** This reproduces `M09`'s direction with a content fault
instead of an ordering one, on a fault class the predecessor never seeded on an
arm at all.

## The two structural asymmetries, which are not divergences and are not folded in

- **`FI-M17` has no counterpart anywhere.** *"A second implementation that
  disagrees with the first"* is not a fault a tree with one implementation can
  host. Its arm-A and arm-C cells are `NOT_APPLICABLE`. Giving it a
  nearest-bytes stand-in there is precisely the re-anchoring artefact
  `PA-06-DF-08` is about, and the catalogue row says so in its own
  `re_anchoring_rule`.
- **`suite-fake` does not exist on arms A and C.** They have no second
  composition point. Declaring one would silently re-run `suite-real` and report
  a duplicated cell as an independent measurement — `AD-F6` with the sign
  flipped. `REACHABLE_BY_ABSENCE` is the strongest form of *"one arm
  structurally cannot"*: the arms cannot give the same answer because one of
  them cannot be asked.

## What this closes, and what it does not

**Closes `PA-06-DF-04`.** The adapter-internal class is now carried by an arm.
`FI-M17` is `PA-M11`/`PA-M12` on an artifact a prompt produced rather than on a
fixture the epic authored, and it is the row that finding names as the only
thing that would let the port-reach claim be stated about an arm.

**Does not close the shared-author bias.** FI-04 wrote these mutants and FI-04
is measuring them. The `blind_author` channel is the only instrument in this
repository that controls for that, and it was not re-run here.

**Does not make the port machinery look better.** See `generator_vs_suite.py`
and the ticket's report. On this row `suite-real` and `suite-fake` decide
exactly what the two corpus columns decide, and neither corpus column has a kill
the suite lacks.
