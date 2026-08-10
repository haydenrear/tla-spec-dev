# RM-04 — the toolchain scored, and what replicated

**The one sentence: D3's separation replicated on a second example and D2's
movement did not.** The dimension the epic was least worried about is the one
that failed to travel, and it failed on the only clean before/after this epic
produced.

Everything below re-derives from the repository:

```
python3 examples/validation/scorecards/score_tools.py tags
python3 examples/validation/scorecards/score_tools.py contested
python3 examples/validation/scorecards/score_tools.py audit
python3 specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/analysis/threshold_probe.py
```

**Scope, stated first (`R3`).** This round is **6 cards on one example,
`eval_toolchain`**, three artifacts, two judges each. Every figure here is a
figure about those 6 cards. Nothing here is a claim about `ab_quota_ledger` and
no number here may be read across to it (`R-H2`). The predictions were sealed in
[`SEALED-BEFORE-DISPATCH.md`](SEALED-BEFORE-DISPATCH.md) before any judge
existed. §8 records what `scope` made of this page.

---

## 1. The round

| artifact | subject | declared scope | derived | judges |
|---|---|---|---|---|
| `LL` | `rm04_scripts` | `scripts` | `effectful` | opus p1, sonnet p2 |
| `GG` | `rm04_eval_harness` | `examples/validation` | `ports-and-adapters` | opus p1, sonnet p2 |
| `JJ` | `rm04_removal_pricer` | `examples/validation/gap_mutants` | `effectful` | opus p1, sonnet p2 |

Only `JJ` was given a before tree. `LL` and `GG` were given none and were not
meant to have one.

| artifact | D2 opus | D2 sonnet | D3 opus | D3 sonnet | opus seeded a fault | sonnet seeded a fault |
|---|---|---|---|---|---|---|
| `LL` | 1 | 2 | 1 | 0 | yes | no |
| `GG` | 2 | 1 | 2 | **4** | yes | no |
| `JJ` | 1 | 2 | 1 | 0 | yes | no |

## 2. D2 did NOT replicate off `ab_quota_ledger`, and this is the ticket's main result

**Prediction P2 failed.** `JJ` is the one subject in this round with a genuine
before and after — 1209 lines of `gap_mutants.toml` and `run_gap_mutants.py`
replaced by 899 lines of `price_removal.py`, `altered_score_probe.py` and
`residual_faults.toml`, same job. D2's anchor 3 was reachable. **Both judges
refused it**, at 1 and at 2, and each gave a reason about the artifact rather
than about the evidence:

- opus scored **1** on a fact stored twice *that already disagrees*: the sha a
  removal landed at is in `removal_census/removals.toml:423` as `bfd04af` and
  again in a hand-typed literal at `gap_mutants/price_removal.py:362` as
  `"HEAD"`, three lines from the code that opens that same manifest.
- sonnet scored **2** and refused 3 on behaviour: the artifact's own census
  records this cut as *"the one removal with a non-zero price"*, its seeded gap
  mutant reads `ENTAILED-SURVIVES`, so a capability was lost rather than
  redesigned away.

**Max D2 across all 6 cards is 2.** D2 has now moved above 2 in exactly one
round, on one example, and the first attempt to reproduce that anywhere else
returned nothing. **The honest reading is not that D2 is broken — it is that
D2's movement is still a result about `ab_quota_ledger`, and this round bounds
it rather than widening it.**

**And the descriptor was no help again, in the direction that matters.** Over
`JJ`, Python lines went **633 → 706** and modules **1 → 2** while the directory
went 1209 → 899, because the before tree's 633-line runner left the scope
entirely. The opus judge named it: *"literal MF-020"*, and rejected the falling
figures as evidence unprompted. **No axis was added.** See §7.

## 3. D3's separation DID replicate, on a second example

```
SEPARATES  eval_toolchain D3 effectful/ports-and-adapters:
             effectful [0, 1] n=4   ports-and-adapters [2, 4] n=2
             tiers_measured=['opus', 'sonnet']
does not separate  eval_toolchain D2:  effectful [1, 2]   ports-and-adapters [1, 2]
```

Disjoint, in the same direction as `ab_quota_ledger`'s 58-card row, on an
example that shares no code with it, with both tiers measured on both sides —
which `ab_quota_ledger` still cannot say. **D2 overlaps on the same six cards,
so this is D3 and not a general "the tag predicts scores" effect.**

**Three limits, and the second one is large.**

1. **n = 4 against n = 2, one round.** This is enough to say the separation was
   *reproduced*; it is nowhere near enough to say how often it reproduces.
2. **The `ports-and-adapters` side is one artifact whose two judges disagree by
   2**, and it is contested (`rm04-GG-d3-spread-2`). Its 4 rests on a 5-module
   subtree of an 85-module declared scope. See §5.
3. **No `[[demonstration]]` row was declared for it, deliberately.** `audit`
   reports it `OPEN` and it therefore refuses nothing. An authority nobody
   declared is not an authority, and a separation this thin should not become
   one on the strength of the round that found it. **Declaring it is the next
   epic's decision, not this ticket's.**

**P4 held:** no `effectful` card in this round scored D3 ≥ 3. RM-02's §7 open
question — whether D3 discriminates *inside* `effectful` — is still open, and
now with 4 more cards of evidence that it does not: `LL` and `JJ` are different
programs with different jobs and both land at 0–1.

## 4. Does RM-03's `D3 = 4` survive a clean, unleaked round? BOUNDED, not reproduced

RM-03 measured `D3 = 4 on 4 of 4` on `arm_b` — the arm famous for scoring 4 —
with `subject.name: "arm_b"` and `declared_effect_boundary:
"ports-and-adapters"` visible on the card.

This round is clean on both counts and the answer is split:

- **The value reproduces off `arm_b`.** `GG-p2` scored **D3 = 4** on
  `examples/validation`, a subject that is not `arm_b`, from a card carrying no
  subject name and no declared value. So 4 is reachable elsewhere and is not an
  artifact of that arm's identity.
- **The unanimity does not.** `GG-p1` scored **2** on the same bytes and said
  why: the anchor-4-shaped evidence holds *"only for `ab/reference_ports`, 5
  modules of 85"*, and it took the lower anchor citing the artifact's own
  `scope_drift()` and `reference_ports/README.md:3` — *"THIS IS NOT AN ARM … It
  is a fixture."*

**So RM-03's number is bounded rather than overturned.** What this round shows
is that `D3 = 4` unanimous on four cards has not been seen again once the
identity was removed, and that the first artifact judged blind at anchor 4
produced a spread of 2 instead. **It does not show that RM-03's round was
anchored.** Deciding that would need a re-score of `arm_b` with the leak fixed,
which is one command now and was not possible before this ticket.

## 5. Every artifact tier-split, on both dimensions — and the split is unattributable

**6 of 6 dimension-artifact cells are disjoint by tier.**

| | D2 | D3 |
|---|---|---|
| `LL` | opus 1 / sonnet 2 | opus 1 / sonnet 0 |
| `GG` | opus 2 / sonnet 1 | opus 2 / sonnet **4** |
| `JJ` | opus 1 / sonnet 2 | opus 1 / sonnet 0 |

The card's `R-H5` says D2 and D3 *"are the dimensions that have held still on
unchanged input"* and advises resting cross-epic claims on them. That advice is
about unchanged input **within a tier**. RM-02 already corrected it for D3
across tiers (`RM-02-DF-02`); this round extends the correction to **D2 as
well, on every artifact it scored**.

**And nothing here can attribute those splits to tier, because the round
confounded it.** Every `opus` judge seeded a fault of its own and ran it; no
`sonnet` judge did — **3 of 3 against 0 of 3, perfectly separated.** `R-H5`
exists because judging practice moves scores. In this round tier and practice
are the same variable, so **a "tier split" here is equally well a "practice
split" and the data cannot tell them apart.** Filed as `RM-04-DF-05`. A future
round that wants to read tier must cross the two: two judges per tier, one
seeding and one not.

## 6. The threshold at `state_colocation = 0.5`: the interval is NOT empty

`RD-04-DF-04` recorded the constant as *chosen, not measured*, on the grounds
that every declared subject sits at 1.0 or at 0.0–0.167 — *"a chasm"* — so any
threshold in between gives the same answer. **That is true of the declared
subjects and false of the repository.**

A census over every directory in this tree that the shipped instrument can
parse (`analysis/threshold_probe.py`, excluding `.skill-manager`, which is a
mirror of installed skills and appeared twice in the first run):

| `state_colocation` | scopes |
|---|---|
| 0.0 | 43 |
| (0.0, 0.2) | 6 |
| **[0.2, 0.8)** | **8** |
| [0.8, 1.0) | 0 |
| 1.0 | 14 |

**113 scopes walked, defined on 71, and 8 of them sit in the interval the
record calls empty** — including one at **exactly 0.5**. Sweeping the threshold
over the 31 scopes the derivation actually decided: moving it from 0.5 to 0.45
changes 1 scope's derived value, to 0.55 changes 1, to 0.7 changes 2, to 0.2
changes 3. **The constant is load-bearing on real code and has never been
measured there.**

**And this round produced the independent judgement RD-04 asked for.**
`rm04_eval_harness` derives `ports-and-adapters` at **0.412**, the closest to
the boundary any subject this project has declared. Its two blind judges scored
D3 **2 and 4**. **At the nearest-to-boundary artifact ever measured, the tag's
value is contested by the dimension the tag exists to make comparable** — one
judge at 4 agreeing with it, one at 2 saying the harness's own domain performs
its I/O with no port. That is one artifact and it decides nothing on its own;
it is the first evidence of any kind at the boundary, and it does not support
the clause.

**No threshold was changed.** Moving a constant to make this round's answers
tidier is `MF-020`, and the census is the finding rather than the repair.

## 7. What was rejected

- **Adding a complexity axis.** The clearest case for one arrived on its own:
  `JJ`'s Python lines went **up** across a removal that took 310 lines out of
  the directory, and a judge called it MF-020 unprompted. An axis that counted
  non-Python declarative lines would have made this round's known answer look
  better and is `MF-020` in its purest form. Nothing was added.
- **Moving `STATE_COLOCATION_MAX`.** §6 measures it; it does not repair it.
- **Declaring a `[[demonstration]]` for `eval_toolchain` D3.** It separates,
  `audit` reports it OPEN, and it refuses nothing. Six cards from the round
  that found it are not grounds to grant a refusal authority.
- **Re-declaring the `ab_quota_ledger` row's `ranges` as `[0, 2]`.** That is
  repairing a control by re-deriving it from the record it controls. See §9.
- **Discarding `GG-p1` for its disclosure.** It read the blinding key that sits
  inside its own declared scope and said so in detail. Discarding a card after
  seeing its score is the one move a round may not make; the exposure is
  measured in §9 instead.
- **Re-deciding D4 and D5.** RM-03 cut them. The work order double-assigned it
  and then corrected itself. Nothing here reverses that.
- **A third pass on `GG`'s contested D3.** Rule 5 asks for one. Running it
  inside the round that produced the spread is a measurement made during a
  measurement; `third_pass = "none"` is recorded, which is the legal answer.

## 8. The predictions, scored

| | prediction | outcome |
|---|---|---|
| P1 | D2 = 2 on every card of `LL` and `GG` | **FAILED** — 1, 2, 2, 1. The anchor bound the top; it did not pin the value. |
| P2 | D2 ≥ 3 on at least one `JJ` card | **FAILED** — 1 and 2. This is §2. |
| P3 | D3 separates `LL` from `GG` | held — disjoint, both tiers |
| P4 | no `effectful` card reaches D3 ≥ 3 | held — max 1 over 4 cards |
| P5 | at least one dimension tier-splits | held — 6 of 6 cells |
| P6 | a judge cites the blinding key inside `GG`'s scope | held — see §9 |

**Two of six failed, and both are about D2.** Four passing would have been an
alarm; the two that failed are the result.

## 9. The blinding leak, fixed — and the one this round could not remove

**What was fixed.** `scaffold --subject` wrote the real arm name and the
declared axis value into a blinded card: RM-03's cards read `arm: "T"`,
`subject.name: "arm_b"`, `declared_effect_boundary: "ports-and-adapters"`. From
this ticket a blinded card carries `name: null`, `blinded: true`, the scope, and
no declared value; `check` resolves it BY SCOPE against `subjects.toml`, so
attack A5's defence — the scope was declared before scoring and has not moved —
is unchanged. The demonstrated failing input is `arm_b` itself: its scope is
`.../ports-as-adapters/blind/artifact_T` and `T` is published, so a blinded
scaffold of it is **refused**, because withholding a name cannot hide a label
the path spells.

**What could not be removed, measured rather than hoped about.** `GG`'s declared
scope is `examples/validation`, and `examples/validation/scorecards/subjects.toml`
is inside it. `GG-p1` found it, stopped, and disclosed it on the card: it names
the entry declaring its own scope with `ports-and-adapters`, and the sealed
prediction that D2 is bounded at 2 for its artifact. **It also recorded that its
D3 went against the declared value's direction**, and that a reader should treat
the agreement as contaminated. `GG-p2` did not find it. The other four cards
cite nothing from the key.

**So: 1 of 6 cards is contaminated, it is the card that scored D3 = 2, and it
scored BELOW the value it was leaked.** The leak, where it landed, did not push
in the direction it would have pushed. That is one card and it is not a general
result about leaks.

**The unremovable part is the finding.** A round in which the subject contains
the instrument cannot be blinded by that instrument. This is the first thing
this project has measured that says something about adopting the substrate
which is not about the anchors: **an adopter scoring their own tooling inherits
this, and there is no version of `scaffold` that fixes it.**

## 10. The `[[demonstration]]` row — `RM-06-DF-02`, settled

**The declared numbers do not change and the row loses two fields.** Full
reasoning is in `specs/results/scorecards/INSTRUMENT-LOG.toml` above the row;
the short form:

- RM-06 proved the row is **scoped, not wrong** — `effectful = [1, 2]`,
  `tiers_measured = ["opus"]` reproduce exactly over the 49 cards sealed before
  `reading-discipline`, which is RD-04's population.
- **`ranges` and `tiers_measured` grant nothing.** `authority()` admits an entry
  iff `separates` is true and keys it on `(dimension, {value, value})`;
  `verdict()` reads the re-derived entry, not the declaration. So the widening
  RM-06 and the owner were protecting against was not available in either
  direction. `RM-04-DF-03`.
- **And they cannot be pinned.** `[[movement]]` names two cards and
  `[[contested]]` names one judge group; both populations are closed. `ranges`
  is a figure over an open one, so it can only be re-affirmed forever.

So both fields are removed, RD-04's figures move into the row's `why` with their
population named, and the control is kept as an executed assertion at a
population that cannot grow
(`tests/test_architecture_tags.py::test_the_committed_demonstration_re_derives_from_the_cards`).
`separates`, `dimension` and `example` are still re-derived against the current
record on every `audit`, so the authority still falls if the cards stop
supporting it.

**`audit` now reports 0 violations.** It reported exactly 1 for three tickets.

## 11. The label pool — `RM-02-DF-01`, solved

Four labels remained of seventeen. **The property is opacity; global
single-character uniqueness was only the mechanism**, and it had a bounded
lifetime baked into a constant.

A label is now a **string over the characters this record has never published**
— `G J L V` today — at the narrowest width of at least 2 that can serve the
round. Two properties hold by construction rather than by counting:

1. no label emitted has ever been published (exclusion is on the whole string);
2. **no character of one has been published on its own either**, so a judge who
   saw `T` last round meets nothing sharing a character with it.

16 labels at width 2, 64 at width 3, without bound. This round drew `LL`, `GG`
and `JJ`. **The limit, said plainly: width multiplies an alphabet and cannot
create one.** With a single character left, every width yields one label, and
the scaffold refuses — which is the correct answer and is tested.

**And the hole found while widening it.** `--labels` wrote whatever it was
handed, with no exclusion check at all — the one route an operator reaches for
when the pool refuses was the one route with nothing on it. It now costs
`--reason`, exactly as undoing blinding does, and the reason goes into
`UNBLINDING.md`. **It is a price, not a ban:** FI-03, SM-04 and RM-03 each
re-scored one arm under two card versions and kept its label on purpose, which
is correct and was recorded nowhere.

## 12. What this ticket could not settle

- **Whether RM-03's round was anchored.** §4 bounds it. Settling it needs
  `arm_b` re-scored with the leak fixed, which is now possible.
- **Whether D2 can move at all outside `ab_quota_ledger`.** One before/after,
  two judges, both refusing anchor 3 for reasons about the artifact. A second
  before/after would say more than a second judge on this one.
- **Whether the tier splits are tier splits.** §5 — the round confounded tier
  with judging practice, 3 of 3 against 0 of 3.
- **What `state_colocation` should be.** §6 shows the interval is not empty and
  that the constant moves real answers. It does not show which value is right,
  and one contested artifact at 0.412 cannot.

## 13. `scope` over this page, and the bound that applies

```
python3 examples/validation/scorecards/score_tools.py scope
```

Run at `dbf355c` + this ticket. The applicable bound is the **first**,
`RD-02-DF-01`: most of this page's load-bearing figures are **invisible to the
checker rather than checked by it**, and they are named here rather than left
for a reader to find:

- every cell of §1's and §5's score tables — a table cell carries no
  bind-and-value form;
- `8 of them sit in the interval` and the whole distribution table in §6 —
  those count directories, not cards;
- `3 of 3 against 0 of 3` in §5 — counts judges;
- `6 of 6 dimension-artifact cells` — counts cells.

`RM-02-DF-05` applies to this page as it did to RM-02's: **`eval_toolchain`
contains an underscore**, so `scope`'s counted-noun pattern cannot admit it as
a counted noun and the example has to be established in the lines before every
figure instead. Every adopter naming their example `order_service` inherits it.

The figures this page contributes that the checker CAN reach are stated at the
example: **D2 = 2 or below on 6 of 6 cards** of `eval_toolchain`, and
**D3 = 4 on 1 of 6 cards** of `eval_toolchain`.
