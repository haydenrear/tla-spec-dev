# GOAL-simpler-same-behavior — the run record

| | |
|---|---|
| **baseline** | highest D2 anywhere is 3 (ex3), and **both judges withheld 4 for the same reason** — the reduction was not shown behavior-preserving |
| **measured** | **D2 = 2 from all four judges, on both arms.** D4 = 2 / 2 on arm A and 3 / 2 on arm B. |
| **target** | an arm-B artifact scores D2 = 4 from both judges, which by the rubric requires D4 ≥ 3 |
| **verdict** | **`missed`** |

**The target was not moved.** It is the same sentence the owner wrote at
`schedule_revision: 2`, which said in advance that it was not up for amendment
and that this goal was on track to be missed.

## Every judge rejected the owner's amendment, again, and gave a new reason

The amendment — read the arm PAIR as the before/after that D2 anchor 3 requires
— was supplied verbatim to all four judges, with the mechanical block for both
artifacts, neutrally labelled, so that a judge who accepted it had two columns to
work from. **Four of four rejected it.** The reasons, in their own terms:

1. **Anchor 3 says a simplification *was made*.** Two independent
   implementations of one specification are a difference between artifacts, not
   the effect of an intervention. Nothing was refactored, so there is no
   "before".
2. **The card's own D2 rule requires the judge to say WHAT got simpler and HOW
   the behavior survived it.** A judge holding one tree cannot do that about the
   other, and certifying an uninspectable reduction is precisely the false clean
   the card exists to prevent.
3. **A new one, and it is the sharpest.** The mechanical block reports
   `mutable_state_count` **8 vs 8** and `max_writers_of_one_attribute` **2 vs
   2** — exactly the figures arm B's one genuine simplification (deriving
   `available` instead of storing it) would move, and the block itself says they
   discriminate nothing. **The amendment asks for a before/after out of a block
   that does not measure the thing.**
4. **It would not have helped anyway**: on every figure that differs, arm B is
   the *larger* column.

**HP-06-DF-05 is therefore not a one-round accident.** D2 as written cannot be
scored above 2 by an A/B, on two independent rounds, across eight independent
judges. The finding is about the card, not about the arms, and it now has enough
replication to act on.

## The mechanical block — RECORDED, NEVER SCORED

| figure | arm A (ordinary ask) | arm B (hexagonal + minimize-complexity) |
|---|---|---|
| modules | 1 | **4** |
| production lines (significant) | **122** | 129 |
| its own test lines | 252 | 190 |
| its own tests | 32 | 53 |
| public names | **20** | 25 |
| pieces of mutable state | 8 | 8 |
| max writers of one attribute | 2 | 2 |
| branches | **10** | 11 |
| imports | `__future__`, `dataclasses`, `pathlib`, `typing` | `__future__`, `dataclasses`, `os`, `pathlib`, `typing` |
| I/O imports | `pathlib` | `os`, `pathlib` |

**Arm B is larger on every figure that differs.** That reverses HP-06, where the
treatment arm came out smaller on lines and branches and sealed prediction N01
was scored FAIL for it. See `../PREDICTIONS-SCORED.md` — the same prediction
reads PASS on this round's artifacts and FAIL on HP-06's, from the same prompt
text, which is the strongest single piece of evidence in either round that **one
pair of artifacts is n = 1 and the descriptor delta is noise at this scale.**

## Where measurement and judgement disagree — and the block loses again

`references/eval_scorecard.md` rule 7 exists for this. Two disagreements:

- **`mutable_state_count` and `max_writers_of_one_attribute` are identical (8/8,
  2/2) across two designs that differ structurally as much as these two do.**
  Arm A stores `_available` and maintains it in three commands; arm B derives it
  and stores nothing on that side. The block cannot see the difference, because
  arm B's port implementations contribute `_path` and `_records` and make the
  totals coincide. **A judge caught this and used it against the amendment.** The
  block is wrong; the judgement is right.
- **`branches` differs by one (10 vs 11) and carries no information.** HP-06's
  adversarial pass already decomposed its arm-pair branch delta into behavior one
  arm does not implement plus a predicate written on the other side of a `for`.
  A one-branch gap between two programs that agree on 3,599 of 3,600 observation
  slots (measured independently by the blind author's 600-step sweep) is noise.

## The behaviour half, which is where the round is least flattering to arm B

D4 is 2 / 2 on arm A and **3 / 2 on arm B**, and both judges who capped it at 2
capped it on *provenance*: nothing in either tree is model-derived, so anchor 3
("the check is model-derived rather than only hand-written assertions") is
unreachable by an artifact that ships only pytest files. One judge said it was
torn between 3 and 4 on substance and took the lower per the card.

Two independent judges also *refuted* anchor 4 on arm A rather than merely
finding it unmet. Arm A's flagship
`test_rules_hold_through_a_long_random_sequence` advertises 400 randomized
commands checked against an independent model. Instrumented on **unmutated**
code it accepts, depending on the seed the judge reproduced, **1 reserve, 1
commit, 0–1 releases and 3 closes**; all tenants close within the first ~30
steps and every remaining step bounces off a closed ledger. Its own
anti-degeneracy guard passes on exactly the degenerate run it was written to
prevent, and two `release` mutants survive all 32 of its tests as a result.

**That is a false self-certification found by reading and running an artifact,
not by any instrument this project ships**, and it is the fourth consecutive
round in which the most valuable finding has that shape.
