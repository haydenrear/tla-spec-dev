# HP-06 goal verdicts — baseline -> measured -> target

Evaluation ticket. `local_signal` is `N/A: this ticket is the measurement` for
all three goals, per the plan.

| goal | baseline | measured | target | verdict |
|---|---|---|---|---|
| **GOAL-catch-bugs** | D1 = 2 / 2 / 2 / 1 / 0 across five fixtures at `ab0dfee`; **nothing reached 3 on either judge on any example**. Guard relaxation 0 of 3 on both arms and 0 of 4 on a blind catalogue. | **D1 = 3 from BOTH blind judges on arm B** (arm A 3 / 2). Guard relaxation **3 of 3 under `corpus-neg`** on the seeded catalogue and **1 of 1** on a fresh independently authored one, on both arms; 0 of 3 under every other generated instrument. | at least one example scores D1 >= 3 from BOTH judges, and guard-relaxation kills > 0 on both the seeded catalogue and a fresh blind one | **met** |
| **GOAL-simpler-same-behavior** | highest D2 in the set is 3 (ex3), and both judges withheld 4 for the same reason | **D2 = 2 from all four judges, on both arms.** Mechanically: arm B 123 significant production lines / 4 modules / 21 public names; arm A 147 / 1 / 17. | an arm-B artifact scores D2 = 4 from both judges, which by the rubric requires D4 >= 3 | **missed** |
| **GOAL-hexagonal-in-fact** | D3 = 1 / 1-2 / 3 / 1 / 0-1; only one fixture ever reached 3 and **nothing ever reached 4** | **arm B: D3 = 4 from BOTH judges.** Arm A: 2 from both. | the prompt arm scores D3 >= 3 from both judges on the majority of produced artifacts, with at least one 4 | **met** |

**No target was edited. No instrument was re-run selectively. The run that
happened is the run reported.**

## The caveats that travel with the two `met` verdicts

**GOAL-catch-bugs.** The catalogue's positive control M07 is RED on arm A — it
survives every one of the six generated instruments, because the corpus recovers
no `Reserve` argument and no case that calls `reserve` executes. The D1 = 3
anchor is not carried by those rows; it is carried by `corpus-neg`, whose
controls are green on both arms and which does not depend on a positive `Reserve`
case. Both judges reached 3 by that route and both refused 4 for control reasons.
Separately, HP-06-DF-10: this model spells refusals out as first-class actions,
so the whole-view corpus does contain refusal cases and HP-06's own oracle skips
39,688 of them — the 3-of-3 survives adversarial tracing, the framing of the
zeros beside it does not.

**GOAL-hexagonal-in-fact.** 105 unique prompt lines against 16 — 6.6x. **This
round cannot distinguish "hexagonal guidance helped" from "a longer, more
specific ask helped."** n = 1 feature. And the blinding leaked on arm A
(HP-06-DF-03), though in the direction that would have hurt rather than helped
the treatment.

## Why the `missed` is a finding about the card

All four judges gave the same account: neither arm made a simplification and
measured one, because both implemented one specification from scratch. D2 anchor
3 requires a before and an after **of the same artifact**. The owner's
`schedule_revision: 2` amendment proposed reading the arm pair as the
before/after and that reading was supplied to every judge; none accepted it.
**D2 as written cannot be scored above 2 by an A/B at all.** HP-06-DF-05.

## Findings by channel

**0 (suite re-run) : 17 (fresh adversarial attack) : 13 (blind author).** Sealed
prediction N06 passes for the third round running. Twelve `HP-06-DF-*` filed,
**none fixed**; six of HP-06's own written claims were falsified by the
adversarial channel and are corrected in place with the correction marked.

## Sealed predictions

**7 PASS, 4 FAIL, 0 SUPERSEDED, 0 UNMEASURED**, and three of the four failures
are negative predictions. `PREDICTIONS-HP.md` was not amended.
