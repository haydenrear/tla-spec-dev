# FI-03 — can the scorecard carry a delta?

**The measurement `SELF-IMPROVEMENT.md` has never had.** Three sealed,
byte-identical artifacts, re-scored by two fresh blind judges under the current
card, and again by two more under a card that records what the judge did. Every
number below is re-derived from the cards by
`measure/derive_movements.py`; none is typed in.

Byte-identity is verified in `BYTE-IDENTITY.md`, not assumed. The judges' prompt
is committed in `JUDGE-DISPATCH-v1.md` and `JUDGE-DISPATCH-v2.md`, which is the
first time this repository has preserved one.

---

## THE ANSWER

**Against the sealed row it was told to compare with — PA-06 — every dimension
moved by at most 1 per judge, in both arms. The target is met on that
comparison.**

**Against the round before it — EVAL-RERUN, the same bytes, the same card
version, one more round back — D4 moves 2 in BOTH arms, and D5 moves 2 in the
version 2 arm. The target is missed.**

These are the same measurement over the same artifacts, and the second is not an
extension anyone had to be talked into: it is the comparison
`SELF-IMPROVEMENT.md` already prints in the same table.

> **`GOAL-scorecard-carries-a-delta` is MISSED. It is missed on D4, and on D5.**

> **AND THE OTHER HALF OF THE SAME MEASUREMENT: D2 AND D3 MOVED ZERO POINTS.**
> Not "within target" — **zero**, on every one of the 60 judge-scores, across
> four independent pairs of judges, two card versions, three artifacts and two
> sealed baselines. Not one point, in either direction, in any comparison.
>
> **This is the strongest stability evidence this project has ever produced
> about anything**, and it is what makes `ports-as-adapters` resting its
> headline on D3 a safe decision rather than a lucky one: D3 = `4 / 2 / 1`
> across the three artifacts has now been produced by four independent pairs on
> byte-identical bytes, two of whom executed the adapter swap themselves and two
> of whom did not.
>
> **A reader skimming for the missed goal must not skim past this.** The card
> works. It works on the two dimensions that are about the artifact's shape, and
> it fails on the two that are about what the judge did.
> Arm A's D4 has now taken **2, 4, 3 and 4** from four independent pairs of
> same-family blind judges on a tree nobody touched. **D1, D2 and D3 moved zero
> points on 40 of 40 judge-scores against EVAL-RERUN, and D2 and D3 moved zero
> on all 60 judge-scores measured in this ticket.**

`SELF-IMPROVEMENT.md` can carry a delta on **D1, D2 and D3**. It cannot carry
one on **D4 or D5**.

**And the mechanism `PA-06-DF-06` named is confirmed rather than merely
repeated.** It said the movement tracks judging practice and could not test it,
because nothing recorded the practice. FI-03 recorded it, and:

- PA-06's judges executed their own faults. FI-03's **v2** judges executed
  theirs. FI-03's **v1** judges did not.
- **The arm whose practice matches PA-06 is the arm whose numbers match PA-06**:
  5 dimension-points of total movement against 9, on the same artifacts, on the
  same day, from the same model.
- **FI-03's v2 pass-2 judge reproduced PA-06's sealed pass-2 row exactly — 15 of
  15 dimension-scores across all three artifacts.**

So recording the practice explains the instability. **It does not remove it**,
and it cannot remove it retroactively: every movement from a version 1 row has
one end that never said what its judge did, which is why `R-H5` marks all of
them `readable = false` permanently. **The card becomes able to carry a D4 or D5
delta only between two version 2 rounds, and exactly one version 2 round
exists.**

---

## 1. The headline: FI-03 v1 against the sealed PA-06 row

Same card (`scorecard_version 1`, rubric digest `sha256:e33638087c4191da`, the
digest PA-06's own cards carry). Two blind judges. Three artifacts. Thirty
independent judge-scores.

`positional` pairs pass 1 with pass 1, which is what the sealed baseline table
means when it writes "2/2 → 4/4"; `to band` scores each new judge against the
interval the sealed pair spans and is immune to which of two same-round cards is
listed first. **A result that holds under only one of them has to say which.**

| artifact | dim | sealed PA-06 | FI-03 v1 | positional | to band |
|---|---|---|---|---|---|
| `T` (arm B) | D1 | 4 / 3 | 3 / 3 | -1 / +0 | +0 / +0 |
| `T` | D2 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `T` | D3 | 4 / 4 | 4 / 4 | +0 / +0 | +0 / +0 |
| `T` | D4 | 4 / 4 | 3 / 4 | -1 / +0 | -1 / +0 |
| `T` | D5 | 4 / 4 | 3 / 3 | -1 / -1 | -1 / -1 |
| `U` (arm A) | D1 | 4 / 3 | 3 / 3 | -1 / +0 | +0 / +0 |
| `U` | D2 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `U` | D3 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `U` | D4 | 4 / 4 | 3 / 4 | -1 / +0 | -1 / +0 |
| `U` | D5 | 4 / 4 | 3 / 3 | -1 / -1 | -1 / -1 |
| `W` (arm C) | D1 | 3 / 3 | 3 / 3 | +0 / +0 | +0 / +0 |
| `W` | D2 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `W` | D3 | 1 / 1 | 1 / 1 | +0 / +0 | +0 / +0 |
| `W` | D4 | 3 / 3 | 3 / 4 | +0 / +1 | +0 / +1 |
| `W` | D5 | 4 / 4 | 4 / 4 | +0 / +0 | +0 / +0 |

| dimension | worst per judge | judge-scores moved | verdict |
|---|---|---|---|
| **D1** | 1 | 2 of 6 | within target |
| **D2** | **0** | **0 of 6** | within target |
| **D3** | **0** | **0 of 6** | within target |
| **D4** | 1 | 3 of 6 | within target |
| **D5** | 1 | 4 of 6 | within target |

**Worst single judge-dimension movement: 1. Sum of |movement| over 30
judge-scores: 9.** On this comparison the target is met on every dimension.

---

## 2. The same measurement, one round further back — and it fails

`SELF-IMPROVEMENT.md` prints EVAL-RERUN's rows and PA-06's rows in the same
table. They are the same two arms, the same bytes, the same card version. So the
question "does this card carry a delta" is not answered by one adjacent pair.

Labels differ between rounds by design, so this pairing required both unblinding
keys and is recorded rather than inferred: `T` = arm B = EVAL-RERUN's `Q`,
`U` = arm A = EVAL-RERUN's `P`. Arm C did not exist yet.

| artifact | dim | EVAL-RERUN | FI-03 v1 | positional | to band |
|---|---|---|---|---|---|
| `T` | D1 | 3 / 3 | 3 / 3 | +0 / +0 | +0 / +0 |
| `T` | D2 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `T` | D3 | 4 / 4 | 4 / 4 | +0 / +0 | +0 / +0 |
| `T` | **D4** | 3 / 2 | 3 / 4 | **+0 / +2** | +0 / +1 |
| `T` | D5 | 4 / 3 | 3 / 3 | -1 / +0 | +0 / +0 |
| `U` | D1 | 3 / 3 | 3 / 3 | +0 / +0 | +0 / +0 |
| `U` | D2 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `U` | D3 | 2 / 2 | 2 / 2 | +0 / +0 | +0 / +0 |
| `U` | **D4** | 2 / 2 | 3 / 4 | **+1 / +2** | +1 / +2 |
| `U` | D5 | 3 / 2 | 3 / 3 | +0 / +1 | +0 / +0 |

**Worst single judge-dimension movement: 2, on D4, and it survives the band
test.** Sum of |movement| over 20 judge-scores: 7.

### And the baseline re-derives, which is how you know the harness is not the story

The same script, pointed at PA-06 against EVAL-RERUN, reproduces the number the
epic was opened on:

| artifact | dim | EVAL-RERUN | PA-06 | positional |
|---|---|---|---|---|
| `U` (arm A) | **D4** | 2 / 2 | 4 / 4 | **+2 / +2** |
| `U` (arm A) | **D5** | 3 / 2 | 4 / 4 | +1 / **+2** |
| `T` (arm B) | **D4** | 3 / 2 | 4 / 4 | +1 / **+2** |
| `T` (arm B) | D1, D5 | 3 / 3 · 4 / 3 | 4 / 3 · 4 / 4 | +1 / +0 · +0 / +1 |
| both | D2, D3 | | | **+0 everywhere** |

**Four judge-scores moved by 2** — which is the "four dimension-points" the
epic's baseline names — with a summed |movement| of **13 over 20 judge-scores**.
FI-03's v1 arm measures **7 over the same 20**. The card is quieter than it was
and it is not quiet.

---

## 3. D4 is the dimension that cannot carry a delta, and the reason is in its text

`U`'s D4 across four pairs of same-family blind judges on **byte-identical
code**:

```
EVAL-RERUN    2 / 2     practice unrecorded
PA-06         4 / 4     both judges executed their own faults (disclosed)
FI-03 v1      3 / 4     neither judge executed one       (disclosed)
FI-03 v2      4 / 4     both judges executed        (RECORDED ON THE CARD)
```

A two-point range with no artifact underneath it. D4's anchor 4 asks for
*"a deliberate behavior-breaking change shown to be caught — the check is
demonstrated to be capable of failing."* Nothing in the card said whose
demonstration, so a judge who ran one awarded it and a judge who read a kill
table did not, and both were reading the same sentence correctly.

**And the two FI-03 v1 judges said so, independently and unprompted**, in the
REJECTED section of their own cards:

> *"A D4 of 4 anywhere. The rubric records that PA-06's inflation came from
> judges executing breaks themselves. I did not execute one."* — v1 pass 1
>
> *"Seeding my own fault to settle D4. All three D4 = 4 rest entirely on the
> packet's kill table, executability counts and control status."* — v1 pass 2

Note what that second one is: a judge that declined to execute **and awarded D4
= 4 on all three artifacts anyway.** Under `scorecard_version 2` that exact card
is rejected by `check`. It is the clearest possible demonstration that the gate
added in section 5 is not hypothetical.

### D5 misses too, and NOT for the same reason — which is why it is a separate finding

`U`'s D5, same four pairs of judges, same bytes:

```
EVAL-RERUN   3 / 2
PA-06        4 / 4
FI-03 v1     3 / 3     both judges packet-only
FI-03 v2     3 / 4     BOTH judges executed
```

**Practice does not explain this one.** Both v2 judges executed their own faults
and they still split, 3 against 4, on the same artifact under the same card. The
disagreement is entirely about anchor 4, which asks that *the record contain at
least one result unflattering to the thing being scored*: one judge counted an
artifact's own disclosure of a limitation as an unflattering result, and the
other ruled that a disclosure is anchor 2 and anchor 3 material and that anchor 4
needs a result the artifact **measured** against itself. Both readings are
defensible from the anchor's text.

So D5's instability is an **ambiguous anchor**, where D4's was an **unrecorded
practice**. The second had a mechanism available and this one does not — the fix
would be rewriting D5 anchor 4, which changes what the card measures on a
dimension that is not this ticket's subject and would put a second discontinuity
in the same version bump. **Not done, and named rather than absorbed.**

---

## 4. What did NOT move, which is the load-bearing half

**D2 and D3 moved zero points on every judge-score this ticket measured — all
60 of them**, across two fresh judge pairs, two card versions, three artifacts
and two sealed baselines. Not one point, in either direction, in any comparison.

`T`'s D3 = 4, `U`'s D3 = 2 and `W`'s D3 = 1 have now been produced by **four**
independent pairs of judges on the same bytes, two of whom executed the swap
themselves and two of whom did not. **`ports-as-adapters` rested its headline on
D3 and that decision is vindicated by measurement rather than by argument.**

**D1 moved zero against EVAL-RERUN and by 1 on two of six against PA-06** — and
both of those were PA-06's pass-1 judge giving a 4 where every other judge in
three rounds gave a 3. The ledger's list of "what would count as self-improvement"
says *"D1 crossing 3 on any example — this has never happened"*; PA-06 recorded
it happening; **it has not replicated.** Read PA-06's `D1 = 4` as one judge's
crediting rule, exactly as PA-06's own report said to.

---

## 5. What changed on the card, and what that cost

`scorecard_version 2`. **The anchors are byte-unchanged** — the rubric's version
history declares an anchors-only digest for both versions and
`score_tools.py check` recomputes it, so "keep the old anchors" is a machine
statement rather than a promise.

What is new:

1. **`judging_practice` is a required field on every filled card.**
   `executed_own_faults` is a boolean and `what_was_run` is a list.
2. **`false` is legal and is recorded as `PACKET-ONLY`.** A field that only one
   answer passes collects the answer it wants, not the practice.
3. **D4 = 4 requires `executed_own_faults: true`**, and `check` rejects the
   combination. This is D4's own anchor text made checkable, not a new bar.
4. **D1 and D5 are deliberately NOT gated**, though both moved. D1's anchor 4
   asks that the cases be model-derived and that the record name a class it
   cannot reach; D5's asks that the record contain an unflattering result.
   Neither needs the judge to run anything. Gating them would be inventing a
   requirement rather than executing one.
5. **The instability caveat is now `R-H5`**, with a check `audit` runs.

### The discontinuity between the versions, measured rather than assumed

Two more blind judges, same day, same three artifacts, same dispatch text except
for one section, scoring under `scorecard_version 2`. **Both recorded
`executed_own_faults: true`** — seven and eight items in `what_was_run`.

| dimension | v1 → v2, worst per judge | judge-scores moved |
|---|---|---|
| D1 | 0 | **0 of 6** |
| D2 | 0 | **0 of 6** |
| D3 | 0 | **0 of 6** |
| D4 | 1 | 2 of 6 |
| D5 | 1 | 2 of 6 |

**Summed |movement| across the version bump: 4 over 30 judge-scores. Worst: 1.**
The bump is small and it is measured, which is what the card's change rule asks
for.

### And the v2 arm lands CLOSER to the sealed row than the v1 arm did

| comparison | judge-scores | worst per judge | summed \|movement\| | D4 |
|---|---|---|---|---|
| EVAL-RERUN → PA-06 — **the epic's baseline** | 20 | **2** | **13** | MISS |
| PA-06 → FI-03 **v1** (both judges packet-only) | 30 | 1 | 9 | met |
| PA-06 → FI-03 **v2** (both judges executed) | 30 | 1 | **5** | met |
| EVAL-RERUN → FI-03 **v1** | 20 | **2** | 7 | **MISS** |
| EVAL-RERUN → FI-03 **v2** | 20 | **2** | 10 | **MISS** |
| FI-03 v1 → FI-03 v2 — the version bump | 30 | 1 | **4** | met |

**PA-06's judges executed. FI-03's v2 judges executed. FI-03's v1 judges did
not. The arm that matches PA-06's practice is the arm that matches PA-06's
numbers** — 5 points of movement against 9, on the same artifacts, on the same
day, from the same model.

And the strongest single result in this ticket:

> **FI-03's v2 pass-2 judge reproduced PA-06's sealed pass-2 row EXACTLY —
> 15 of 15 dimension-scores, on all three artifacts.** `T` 3/2/4/4/4, `U`
> 3/2/2/4/4, `W` 3/2/1/3/4, identical. A round apart, blind, a fresh agent, and
> a card that made it say what it did.

`PA-06-DF-06` diagnosed the mechanism as judging practice and could not test it,
because nothing recorded the practice. **It is now recorded and the diagnosis
holds.** Arm A's D4, across four measurements on byte-identical code:

```
EVAL-RERUN   2 / 2    practice unrecorded
PA-06        4 / 4    both judges executed (disclosed in UNBLINDING.md)
FI-03 v1     3 / 4    both judges packet-only (disclosed in REJECTED)
FI-03 v2     4 / 4    both judges executed  (RECORDED ON THE CARD)
```

**What that does NOT buy.** Recording the practice explains the movement; it does
not remove it. A reader comparing a v2 row to any row measured before version 2
still has one end with no practice recorded, which is why `R-H5` marks every one
of those movements `readable = false` and will keep doing so forever. **The card
becomes able to carry a D4 delta only between two version 2 rounds, and there is
exactly one of those in existence.**

---

## 6. What the four judges found that nobody asked them for

The REJECTED question produced more than the scores did, for the fifth round
running.

- **Both v2 judges executed faults that all three artifacts' own suites missed**,
  and one changed a score because of it: `W` was on course for D4 = 4 off the
  packet, and its own eleven cases reported **11 passed** under a cross-aspect
  fault the other two suites caught. **That is D4's anchor 4 doing exactly what
  it says, and it is only reachable by a judge that runs one.**
- **v2 pass 1 replayed `U`'s flagship 400-command randomized sweep on its own
  seed** and measured 1 accepting reserve, 1 accepting commit, 0 accepting
  releases and 3 accepting closes — so the single COMMIT line it writes is
  `COMMIT acme 7 7`, and a transposition of amount and running total is
  structurally invisible to it. **EVAL-RERUN found the same degeneracy
  independently a round earlier**; it has now replicated.
- **Three of the four judges independently reported that `artifact_U/EVIDENCE.md`
  and `artifact_W/EVIDENCE.md` differ in exactly two lines, both header.** Two
  materially different artifacts, one evidence packet.
- **All four reported the same blinding leak from inside the blind directories**:
  `T`'s and `W`'s `NOTES.md` quote numbered sections of their own prompts and
  `U`'s does not. Unchanged from HP-06, EVAL-RERUN and PA-06, and it is now four
  rounds of the same disclosure with no fix.
- **A contradiction in the control block of all three packets** — `"positive":
  {"deciding": [], "green": false}` on one line and `polarities with no deciding
  control: []` on the next. Filed as `FI-03-DF-03`.

## 7. Five things that go against this result

1. **The v1 arm is not a replication of PA-06's card, and the digest says it
   is.** The rubric gained the "Known instability" section at `d3f483d`, *after*
   PA-06's judges scored — and the parsed rubric digest is **identical on both
   sides**, `sha256:e33638087c4191da`, because it covers the anchors and the
   numbered rules and no prose. **Both v1 judges cited that section as their
   reason for not executing.** So part of the stability reported in section 1
   was bought by a paragraph the digest cannot see, and **any comparison that
   treats the v1 arm as a replication of PA-06's card is comparing two different
   rubrics under one hash.** `FI-03-DF-02` — carry this to FI-06.
2. **No round before this one preserved its judge prompt.** FI-03 reconstructed
   its dispatch from `UNBLINDING.md`'s prose. Every point of movement therefore
   carries an unmeasurable component: the difference between PA-06's prompt and
   FI-03's reconstruction of it. The artifact is verified byte-identical; the
   instruction is not, and cannot be. `FI-03-DF-01`.
3. **Four judges of one model family are not four independent judges.** All
   twelve cards here and all six of PA-06's ran on `claude-opus-5[1m]`.
   Agreement is weaker evidence than it looks, and this is the fourth round in a
   row that has had to say so. The exact reproduction of PA-06's pass-2 row is
   the strongest result in section 5 **and** the strongest illustration of this
   objection.
4. **The repository was modified while blind judges were reading it.** FI-03
   edited `INSTRUMENT-LOG.toml` and `SELF-IMPROVEMENT.md` during the v2 pass,
   and the v2 pass-2 judge noticed and reported it, unprompted, as something
   outside its control. Neither file is a scored artifact and both were on its
   forbidden list, so nothing it scored moved — but a measurement should not
   have a moving floor and this one did.
5. **One accidental read, self-disclosed.** The v2 pass-1 judge chose a scratch
   filename already occupied by a leftover script from the v1 round, and read
   fifteen lines of it — docstring, imports and a constant naming
   `falsifiable-instruments-rescore-v1` — before stopping and choosing another
   name. It saw no score and no label. So one v2 judge knew a v1 round existed.
   Recorded, not re-run: discarding a card after seeing its score is the one
   move a round may not make.

## What this ticket REJECTED

- **Gating D1 = 4 and D5 = 4 on judging practice.** Both moved; neither anchor
  asks the judge to run anything. Gating all three would have made the numbers
  move and would have been the card being edited to match a result.
- **Re-running the v1 judges after seeing that they had both declined to
  execute.** That is the one move a round may not make.
- **Averaging the two comparisons**, or reporting the adjacent-round comparison
  alone. The first hides the miss and the second is the flattering half.
- **Relabelling the artifacts to keep the no-label-reuse mechanism intact.** It
  would have required editing five lines of each evidence packet, and a
  measurement premised on byte-identity cannot start by editing its subject. The
  blinding cost is recorded in `BYTE-IDENTITY.md` §3 instead.
- **Fixing the two defects the judges found in the sealed evidence packets**
  (`FI-03-DF-03`, and the U/W packets differing in two header lines). They are
  the subject of the measurement that was running.
- **Widening the rubric digest to cover prose**, which is the obvious response
  to `FI-03-DF-02` and would have changed the instrument between the v1 and v2
  arms of this ticket's own comparison — and would make every editorial pass
  invalidate every scaffolded card.

## Reproducing every number here

```
python3 measure/derive_movements.py --emit all                       # section 1
python3 measure/derive_movements.py --sealed hexagonal-prompting-rerun \
        --rescore falsifiable-instruments-rescore-v1 \
        --label-map T=Q,U=P --emit all                               # section 2
python3 measure/derive_movements.py --sealed hexagonal-prompting-rerun \
        --rescore ports-as-adapters --label-map T=Q,U=P --emit all   # the baseline
python3 measure/derive_movements.py --sealed falsifiable-instruments-rescore-v1 \
        --rescore falsifiable-instruments-rescore-v2 --emit all      # section 5
python3 ../../../../../examples/validation/scorecards/score_tools.py audit
```
