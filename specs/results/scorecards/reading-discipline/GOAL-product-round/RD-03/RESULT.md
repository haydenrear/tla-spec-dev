# RD-03 — the instruments pointed at the software, and what they saw

**Ticket:** [#190](https://github.com/haydenrear/tla-spec-dev/issues/190) ·
**epic:** `reading-discipline` · **role:** `evaluation` ·
**branch point:** `8f3741f`, verified against the work order ·
**scored at:** `f52be89`.

**Goals owned and decided here:** `GOAL-product-round`,
`GOAL-scope-loss-catchable`, `GOAL-tags-earn-their-place`,
`GOAL-apparatus-priced`.

**Findings filed: 22. Fixed: 0.** Nothing in the record was edited to clear a
result. No artifact tree was touched. The one suite failure this round produced
is left red and filed rather than repaired, and the 180 schema problems the
checker reports against this round's own cards are filed rather than normalised
away.

---

## 0. The one paragraph

**Three pairs were scored blind by twelve judges at two tiers. Eight judges saw a
code change and eight awarded D2 anchor 3. Four judges saw no code change and
four refused it. Not one judge split on the SIZE of the delta.** The
`Z`→`M` pair moved two lines and the `N`→`D` pair moved three; both cleared the
anchor unanimously, and every judge gave the same reason — the delta removed a
*second stored representation of a fact the program already held*, not lines.
**And every one of those eight judges independently reported that the complexity
instrument cannot see the thing they scored.** On `Z`→`M` nineteen of
twenty-one measured axes are byte-identical; on `N`→`D` `branch_points` moves the
**wrong way**, 26 → 27. The measured figures say nothing happened. The judges say
something did, and they agree on exactly what the instrument is blind to.

**`D2 = 2` on `ab_quota_ledger` is over.** It held on 35 of 35 cards ever written
about that example and it was the figure an entire epic was opened on. Six cards
in this round read 3 and three read 4. It did not break because the card changed
— the served rubric digest is byte-identical — **it broke because a subject was
finally given a before.**

---

## 1. THE PRODUCT SCORES — twelve judges, six subjects, two tiers

Every judge scored a **pair**, because D2 anchor 3 cannot be awarded by a judge
who does not hold the before. Passes 1–2 are `claude-opus-5[1m]`, passes 3–4 are
`claude-sonnet-5`. `judge.tier` is derived from `judge.model`; no tier was
declared by hand.

| subject | | p1 `opus` | p2 `opus` | p3 `sonnet` | p4 `sonnet` |
|---|---|---|---|---|---|
| **`Z`** (before, effectful) | D1 D2 D3 D4 D5 | 3 **2** 1 1 4 | 3 **2** 2 4 3 | 3 **2** 1 2 4 | 3 **2** 0 2 3 |
| **`M`** (after, effectful) | | 3 **4** 1 4 4 | 3 **4** 2 4 4 | 3 **3** 1 2 4 | 3 **3** 0 2 3 |
| **`E`** (before, ports-and-adapters) | | 3 **2** 4 2 3 | 3 **2** 4 2 3 | 3 **2** 4 2 2 | 3 **2** 4 2 2 |
| **`F`** (after, ports-and-adapters) | | 3 **2** 4 2 4 | 3 **2** 4 2 4 | 3 **2** 4 2 4 | 3 **2** 4 2 4 |
| **`N`** (before, effectful) | | 3 **2** 1 4 4 | 3 **2** 1 4 4 | 3 **2** 0 2 4 | 3 **2** 0 2 4 |
| **`D`** (after, effectful) | | 3 **3** 1 4 4 | 3 **4** 1 4 4 | 3 **3** 0 2 4 | 3 **3** 0 2 4 |

**No dimension is summed and no row is averaged.** `R-H2`. Every subject is the
same example (`ab_quota_ledger`), the same unchanged instrument
(`served_digest sha256:694280073db988fe`, identical to every version 3 card in
the record), and the architecture tag is printed beside each row.

### 1.1 D2 — DOES A TWO-LINE DELTA CONSTITUTE A SIMPLIFICATION? **YES, UNANIMOUSLY, AND THE LINE COUNT IS NOT WHY**

| pair | `code_lines` before → after | D2 on the after tree | verdict |
|---|---|---|---|
| `Z` → `M` | 158 → **156** (2 lines) | **4, 4, 3, 3** | anchor 3 cleared, 4 of 4 |
| `N` → `D` | 283 → **280** (3 lines) | **3, 4, 3, 3** | anchor 3 cleared, 4 of 4 |
| `E` → `F` | 163 → **163** (0 lines) | **2, 2, 2, 2** | anchor 3 refused, 4 of 4 |

**8 of 8 judges who saw a code change awarded anchor 3. 4 of 4 who saw none
refused it. The split is on EXISTENCE, not on SIZE.** The question the work order
posed — whether a two-line delta with branch counts, state counts and public
surface unchanged is a simplification — was not the question the judges found
themselves answering. Every one of them went to the diff first and to the figures
second, and every one of them decided on what the diff *removed*.

**The reason, and it is the same reason twice, reached independently by eight
judges who could not see each other:**

- `Z` → `M` deleted `_Tenant.outstanding` and `_Tenant.quota`.
  `outstanding` was a running counter written by hand at **three** sites
  (`artifact_Z/quota_ledger.py:164`, `:174`, `:187`) and read at **one**
  (`:198`), tracking a fact `self._reservations` already fully determined.
  `quota` was written once at `:104` and **read by nothing**.
- `N` → `D` deleted `_held`, a per-tenant running total written at three sites
  (`artifact_N/quota_ledger.py:62`, `:74`, `:111`, `:122`, `:136`) and read in
  exactly one place, equal at every instant to
  `sum(r.amount for r in _outstanding.values() if r.tenant == t)`.

Both are the identical shape: **one number stored twice and kept in agreement by
hand.** Four judges made the argument in its strongest available form — that what
was removed is a **fault class rather than a fault**. Two of them seeded the
mistake the before tree makes available (release forgets its decrement) and
showed it produces wrong behaviour in the before tree and **cannot be expressed
at all** in the after tree. That is the concrete content of "simpler" here, and
it is not a line count.

**`F` is the informative refusal, and it is the one the work order said would be.**
`artifact_F` is **byte-identical** to `artifact_E` — verified independently by all
four of its judges with `diff -ru` and `md5`, and by its own author, who wrote
*"I changed nothing"*. It ships a ten-candidate audit that examines each
over-engineering pattern and leaves each standing with a checkable reason. Every
judge read that audit, several verified its claims by execution, and every one
scored 2.

> **The finding one judge asked to have recorded loudest, and it is an anchor
> defect rather than an artifact defect:** *"the correct decision scores 2, and an
> author who had deleted the redundant sort purely to have something to report
> would have scored 3. D2 anchor 3 pays for motion."* Filed as `RD-03-DF-09`.
> Two other judges reached the same objection independently and both rejected
> crediting the deliberation, on the ground that doing so would make anchor 3
> unfalsifiable — any artifact could reach it by writing a document arguing it is
> already optimal, which is the "perfect score by asserting more" failure that
> scoring rule 3 exists to block.

**`D2 = 4` was awarded three times and blocked eight times, and the blocker is
structural.** Anchor 4 requires D4 ≥ 3, and D4 anchor 3 requires the check be
**model-derived**. Ten of twelve judges reported, independently, that **no model
exists anywhere in any of the six trees** — no TLA+, no generated corpus, no
Hypothesis strategy, only hand-written pytest. Several said plainly that they had
run the strongest evidence available to them (judge-seeded faults shown caught,
thousand-step differentials) and refused to let it substitute for the derivation
clause. **The ceiling is the rubric's, not the artifacts'.**

### 1.2 The mechanical block and the judgement disagree, and that is the round's second result

Scoring rule 7: the mechanical block is recorded, never scored, *"so a reader can
see when the two disagree — and a disagreement is a finding."* It disagreed.

| | `Z` → `M` | `N` → `D` |
|---|---|---|
| `code_lines` | 158 → 156 | 283 → 280 |
| `branch_points` | 11 → 11 | **26 → 27 (UP)** |
| `callables` | 14 → 14 | 19 → 19 |
| `classes` | 5 → 5 | 3 → 3 |
| `instance_state` | **4 → 4** | 7 → 6 |
| `public_surface` | 15 → 15 | 25 → 25 |
| `max_depth` | 1 → 1 | 4 → 4 |

**On `Z`→`M`, nineteen of twenty-one measured axes are byte-identical**, and
`instance_state` — the one axis whose name describes exactly what was removed —
does not move at all. Two judges established why by reading the instrument's
behaviour rather than its source: it counts `self.*` attributes on the class and
**does not count dataclass fields**, which is what shrank. Four judges wrote some
form of the same sentence: *"scored on the descriptor alone, the answer is that
no simplification occurred."*

**On `N`→`D` a column moves the wrong way.** `branch_points` rises 26 → 27
because the derivation adds a filtered comprehension. Two judges noted this is a
real, small, honestly-priced cost that the artifact names itself — and that a
reader scoring the descriptor would read the revision as a mild regression.

`RD-03-DF-08`. This is the disagreement the mechanical block exists to make
visible, and it is the first time in this project that it has fired on the
product rather than on the toolchain.

### 1.3 The tier split — THREE existed, this round produced FIVE MORE, and one is on D2

`R-H6`. Recorded on every card; `judge.tier` derived, never declared.

| subject | dim | `opus` | `sonnet` | |
|---|---|---|---|---|
| **`M`** | **D2** | **[4, 4]** | **[3, 3]** | **disjoint, `opus` higher by 1.0** |
| `M` | D4 | [4, 4] | [2, 2] | disjoint, `opus` higher by 2.0 |
| `N` | D4 | [4, 4] | [2, 2] | disjoint, `opus` higher by 2.0 |
| `D` | D4 | [4, 4] | [2, 2] | disjoint, `opus` higher by 2.0 |
| `N` / `D` | D3 | [1, 1] | [0, 0] | disjoint, `opus` higher by 1.0 |
| `E` | D5 | [3, 3] | [2, 2] | disjoint, `opus` higher by 1.0 |

**D2 HAS NEVER SPLIT BY TIER BEFORE.** `RD-01` §6 records the three known splits
— D3, D4 and D5 — and says in terms: *"D2 is not on this list: on the same four
toolchain cards the two tiers overlap, exactly as the epic said."*
`references/eval_scorecard.md`'s own reading rule calls D2 and D3 *"the
dimensions that have held still on unchanged input"* and says a cross-epic claim
is safest on those. **On `M` the two tiers do not overlap on D2**, and the
mechanism is visible in the rationales: both `opus` judges reached D4 = 4 by
executing their own behaviour-breaking change, which unlocks D2 anchor 4; both
`sonnet` judges declined D4 above 2 on the model-derivation clause, which caps
D2 at 3. **The D2 split is downstream of the D4 split, and the D4 split is a
judging-practice split** — exactly the mechanism `R-H5` identified and which
version 2 was written to record rather than remove. Recording it did not remove
it. `RD-03-DF-14`.

**A cross-tier D2 comparison is now covered by nothing measured here**, and any
future claim about D2's stability must name the tier. Filed.

### 1.4 `contested` fired six times, against once in the entire prior record

`R-H6`, computed from the cards and never declared. Over the 49 sealed cards
`contested` fired on **one** judge group. This round it fires on **six**:

| group | dim | scores | spread |
|---|---|---|---|
| `Z` | D3 | 1, 2, 1, 0 | 2 |
| `Z` | D4 | 1, 4, 2, 2 | **3** |
| `M` | D3 | 1, 2, 1, 0 | 2 |
| `M` | D4 | 4, 4, 2, 2 | 2 |
| `N` | D4 | 4, 4, 2, 2 | 2 |
| `D` | D4 | 4, 4, 2, 2 | 2 |

**Five of the six are D4 and the sixth pair is D3.** `D2` is contested nowhere —
its within-group spread never exceeds 1 on any subject, including `M` where the
tiers are disjoint. That is a real and slightly awkward property of the two
instruments read together: **a disjoint tier split can sit entirely inside the
`contested` threshold and never fire it.** `RD-03-DF-15`.

**Rule 5's third pass: RECORDED AS NOT RUN, with the reason.** `RD-01-DF-03`
binds this ticket to either run it or say why not. Six `[[contested]]` entries
are written into `INSTRUMENT-LOG.toml` with `third_pass = "none"` — which the
card calls *"a legal and useful answer while silence is not"* — and the reason
is on each: five of the six are D4 spreads of exactly 2, and `R-H5` establishes
that **a D1/D4/D5 delta of ≤ 2 points per judge is within demonstrated noise**.
A third pass dispatched to adjudicate a spread the card already declares
unreadable would be measuring the noise and reporting it as a finding. The one
that is not D4 — `Z`/`M` D3, spread 2 — is a genuine disagreement about whether
a private `_append` method is a boundary, and it is left contested and named
rather than resolved by a third judge whose vote would break a tie without
adding evidence. **Recording is not repairing**; nothing was edited to clear a
flag and all six remain visible in every `contested` run.

### 1.5 D3 and the architecture tag — USED, not re-litigated

`R-H1` clause 3. The derived values are RD-06's, taken from `tags-rd06.json` and
printed in each card's mechanical block. Nothing here re-derives them.

| derived value | subjects | D3 range this round |
|---|---|---|
| `ports-and-adapters` | `E`, `F` | **4, 4, 4, 4, 4, 4, 4, 4** — a single point |
| `effectful` | `Z`, `M`, `N`, `D` | **0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2** |

**The separation holds and it widened.** The demonstration row declares
`effectful [1, 2]`; these subjects take it to **[0, 2]**, and `audit` reports the
declared row as a **VIOLATION** for exactly that reason — the re-derivation
clause `RD-05` built doing its job on the first outside data it ever saw.
`RD-03-DF-12`.

**The same-tag control holds on D3 — and fails nine times elsewhere, eight of
them on D2.** `score_tools.py tags` reports **81 holds and 9 FAILS**, and not one
of the nine is on D3:

```
control FAILS  ab_quota_ledger D2 arm_a/rd06_artifact_M (effectful): [2, 2] vs [3, 4]
control FAILS  ab_quota_ledger D2 rd06_artifact_M/rd06_artifact_Z (effectful): [3, 4] vs [2, 2]
   ... six more D2 pairs, all of the same shape ...
control FAILS  ab_quota_ledger D5 rd06_artifact_E/rd06_artifact_F (ports-and-adapters): [2, 3] vs [4, 4]
```

**Every one of the eight D2 failures is a before-tree scoring disjointly from an
after-tree carrying the SAME derived value.** The control is detecting a real
heterogeneity inside `effectful` and attributing it to nothing — because it
cannot: it is keyed on the architecture value and the thing that actually moved
is *whether the subject had a before*. **A control that fires on any within-value
heterogeneity cannot distinguish "different architecture" from "different
treatment", and this round is the first time it has had a within-value treatment
difference to see.** `RD-03-DF-12`.

> **Disclosed round conduct.** I read `tags` once while judges were still filling
> cards and recorded a D3 control failure from a partial population. **It is not
> in the final run and it was never true of the complete one** — with all four
> judges in, `Z`'s D3 range is `[0, 2]` and overlaps `arm_a`'s `[1, 2]`. Reported
> rather than quietly dropped: an instrument read over a moving population gives
> an answer about the population it was read over, which is this epic's own
> subject applied to its own conduct.

---

## 2. THE THREE ORIGINAL PRODUCT QUESTIONS

### Q1 — Do model-derived cases catch bugs hand-written tests miss?

- **Baseline (`946b1ee`):** *"No generated instrument has a unique kill;
  suite-fake strictly dominates on author-written catalogues, is COMPLEMENTARY on
  one blind catalogue and DOMINATED on another, so that comparison turns on a
  model constant."*
- **Measured, TWO WAYS, and they answer two different questions. Do not read them
  as one.**

  **(a) Inside the produced trees: the column is ABSENT, not zero.** Ten of twelve
  judges reported independently and unprompted that **none of the six trees
  contains anything model-derived** — no TLA+, no generated corpus, no strategy,
  no TLC invariant. This is why `D1` is structurally capped at 3 and `D4` at 2 for
  **every arm of this example**, and four rounds have compared D1 across its arms
  without ever stating that ceiling. `RD-03-DF-11`.

  **(b) Bound from the FIXTURE's model, which is a different claim: the round
  built the column and ran it.** `examples/validation/ab/model/QuotaLedger.tla`
  exists, so a model-derived corpus is obtainable even though no tree ships one.
  RD-03's cross-tree probe generated one per tree and ran four model-derived
  instruments (`corpus-whole`, `corpus-neg`, `map-silent`, `map-checking`)
  against every re-anchored mutant on all six trees, beside three hand-written
  ones (`own-tests`, `shared-suite`, `shared-suite-fake`).

  | | model-derived unique kills | hand-written unique kills |
  |---|---|---|
  | over all six trees | **0** | **4** |

  A *unique kill* is a mutant one channel kills while **every runnable instrument
  of the other channel misses it**. The four hand-written unique kills are
  `PA-M12` and `PA-M13` on `E` and `F` — **the fake-adapter class, which exists
  only on the `ports-and-adapters` trees**, which is Q3's answer arriving inside
  Q1's measurement. Cell counts over the same runnable population:
  `own-tests` 77 killed / 2 survived, `shared-suite` 75 / 4, against
  `map-checking` 57 / 21, `corpus-whole` 51 / 27, `corpus-neg` 23 / 55.

  **AND THE REACH, WITHOUT WHICH THOSE COUNTS ARE NOT READABLE.**
  `corpus-whole`, `map-checking` and `map-silent` execute **ZERO cases on all
  seven `Refuse*` actions** on every one of the six trees. The positive corpus is
  structurally blind to the entire refusal surface; `corpus-neg` is the only
  model-derived instrument that drives it. A large `SURVIVED` count on an
  instrument that never executed the action is not a miss — it is a
  non-observation, and the two must not be added together.
- **VERDICT: NO — model-derived cases catch nothing the hand-written tests miss,
  on these six trees, and the unique kills run the other way.** This **REPLICATES
  the `946b1ee` baseline** (*"no generated instrument has a unique kill"*) on six
  new subjects, from a different producing model, in a round that built the
  generated instrument specifically to give it a chance to win. **It is a
  replication and it is reported as one, not as a new result.**
- **AND THE REASON IS SATURATION, WHICH WEAKENS THE VERDICT AND IS REPORTED AS
  DOING SO.** On all four `effectful` trees **both hand-written instruments
  killed all 13 measured mutants**. A table where every cell reads the same has
  no resolving power, so the `effectful` half of this comparison carries almost
  no signal. The probe checked this was not a broken harness before reporting it:
  baselines green everywhere, and **84 of 84 measured cells passed a two-sided
  semantic witness — False on pristine, True on mutated — before any verdict was
  recorded.** `RD-03-DF-22`.
- **The question the fixture cannot answer, stated separately so it is not read as
  answered:** whether model-derived cases would win on a subject whose refusal
  surface the positive corpus could reach, or against faults subtler than this
  catalogue's. Nothing here measures either.
- **And one hole in the hand-written channel with nothing on the other side:** a
  fault making `available("nobody")` return `0` instead of raising survived
  **both** hand-written suites on **both** trees of a pair, and the model-derived
  instruments do not drive unknown-tenant queries either. Neither channel sees it.

### Q2 — Does the prompt produce simpler code at equal behaviour?

- **Baseline (`946b1ee`):** *"the prompt is the ONE lever with a replicated,
  confounder-controlled effect — D3 1 → 4, with arm C longer and scoring 1/1.
  D2 = 2 on every greenfield card because anchor 3 was structurally unreachable
  for a subject with no before."*
- **Measured:** **The D2 half of that baseline is now retired, and the answer is
  NO FOR THE PROMPT AND YES FOR THE REVISION.** The three greenfield trees score
  **D2 = 2 on 12 of 12 cards** — unchanged, across all three arms, at both tiers.
  **The prompt moved D2 by nothing.** What moved D2 was *being asked to revise*:
  two of the three revisions cleared anchor 3 unanimously. The lever that works is
  not the architecture prompt; it is the second pass.
- **VERDICT: NO — the prompt does not produce simpler code at equal behaviour, on
  D2, on this example, at either tier.** D2 is flat at 2 across `arm_a`, `arm_b`
  and `arm_c` greenfield trees whose prompts differ by 91–111 distinct lines and
  whose architectural-vocabulary densities differ by 45-of-107 against 1-of-111.
  **The reason D2 was ever constant is now measured rather than assumed:** it was
  the unreachable anchor, and unblocking the anchor moved the number while
  changing the prompt did not.
- **The D3 half of the baseline REPLICATES and is not this round's contribution.**
  `E`/`F` score D3 = 4 on 8 of 8 cards and the effectful trees 0–2 on 14 of 14,
  which is the same separation at a wider bottom. It is reported, not claimed as
  new.
- **"AT EQUAL BEHAVIOUR" IS NOT AN ASSUMPTION HERE — IT WAS MEASURED, AND IT IS
  THE STRONGEST NUMBER IN THE ROUND.** The cross-tree probe ran a randomised
  differential over **all fifteen pairs of the six trees** — every arm against
  every other arm, and every before against its after — comparing the full
  observable surface after every operation. **Zero divergences on all fifteen
  pairs.** The six implementations are observationally equivalent to each other:
  the three arms produced *the same program* behaviourally, and both revisions
  preserved behaviour exactly. So the D2 and D3 differences between them are
  differences of **shape at identical behaviour**, which is precisely the
  condition the question asks about and which no prior round measured directly.

### Q3 — Does the effectful vs ports-and-adapters choice change what validation can see?

**Using the tag. Not re-litigating it.**

- **Baseline (`946b1ee`):** not measured since `ports-as-adapters`; the choice was
  not taggable, and D3's contested spread came from judges disagreeing about
  *what the artifact is*.
- **Measured:** **YES, and it is visible three ways in this round's raw data.**
  1. **Judging practice diverges by tag.** Every judge of `E`/`F` performed a
     **runtime adapter swap** as part of scoring — one wrote a *third*,
     sqlite-backed adapter and a call recorder and confirmed the domain's durable
     interaction was exactly `['append', 'append', 'lines']` on the port object.
     **No judge of any `effectful` tree could do this**, and four said so
     explicitly: there is no seam, no interface and nothing injected.
  2. **A fault class is expressible on one side and not the other, and it is now
     counted rather than argued.** The catalogue's `PA-M12` and `PA-M13` mutate a
     *fake adapter's* behaviour. The cross-tree probe reports **8 INEXPRESSIBLE
     mutant-cells, ALL of them on `effectful` trees and ALL of them these two
     mutants — and ZERO on `ports-and-adapters`.** On `E`/`F` both are
     expressible and both are killed. On `Z`, `M`, `N`, `D` there is no fake to
     mutate. **Reported as a hole, never as a survivor** — the distinction the
     whole table turns on.
     **And these same two mutants are the ONLY unique kills in the entire
     probe** (§Q1): the one fault class the hand-written channel catches that the
     model-derived channel does not is the one class that only exists when the
     architecture supplies a seam.

  > **THE HEADLINE COUNT IS NEAR-TAUTOLOGICAL AND THE MEASURER SAID SO BEFORE I
  > ASKED.** `PA-M12` and `PA-M13` are *defined* as mutations of a fake adapter,
  > so counting where they cannot be applied largely restates which trees have a
  > fake. The probe predicted the result cell-for-cell before running and
  > disclosed it as a prediction that passed too cleanly. **"The effectful trees
  > have 8 holes" is not an empirical discovery** and must not be reported as
  > one. `RD-03-DF-22`.
  >
  > **The informative cell is the one nobody predicted:** on `E`/`F` both mutants
  > are killed by the trees' **own tests**, survive the **shared suite**, and
  > survive **all four model-derived instruments**. The region behind a port is
  > invisible to every instrument in this epic except a hand-written parity suite
  > somebody chose to write.

  4. **A three-cell hole cuts ACROSS the split and must not be read as an
     architecture effect.** `M07` is inexpressible on `artifact_D`, `artifact_E`
     and `artifact_F` — one `effectful`, two `ports-and-adapters`. The cause is
     **representation, not layering**: all three *derive* `available`, so the only
     line that can move it also moves the reservation's own amount. The probe did
     not declare this — it seeded the nearest candidate on each and ran it, and
     reports the moved-observable set as the witness. `absent` and
     `checked, none found` are different claims.
  3. **The D3 ranges do not overlap** and have not overlapped on any subject ever
     measured.
- **VERDICT: YES — the choice changes what validation can see, and the effect is
  on the INSTRUMENT'S REACH rather than on the code's quality.** The
  `ports-and-adapters` trees admit a class of check the `effectful` trees cannot
  state. **What it does NOT change, measured:** D1 is 3 on 24 of 24 cards this
  round regardless of tag, and D2 is 2 on all four greenfield-and-`F` cards on
  both sides. `R-H1`'s table still grants a refusal on D3 and on nothing else, and
  this round adds no dimension to it.
- **The bound, stated with the verdict:** this is one example, one round, one
  producing model, and the `ports-and-adapters` population is **two trees, one of
  which is a byte-identical copy of the other**. Eight of the sixteen
  `ports-and-adapters` cards in this round score the same bytes twice.

---

## 3. THE THREE APPARATUS GOALS, EACH WITH ITS INSTRUMENT'S BOUNDS

### 3.1 `GOAL-scope-loss-catchable` — DECIDED: MET, and the count is a function of the population

**Baseline: ZERO.** Nothing had ever refused an unscoped claim.

| sweep | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| RD-01, at its tip | 44 | 19 | 11 | 6 | 8 |
| RD-04's reconciled tip | 58 | 26 | 11 | 9 | 12 |
| **RD-03, before this round's cards were filled** | **62** | **27** | **11** | **11** | **13** |
| **RD-03, after this round's 24 cards were filled** | **62** | **49** | **0** | **0** | **13** |
| **RD-03 final, including this report's own figures** | **67** | **53** | **0** | **0** | **14** |

**THE COUNT IS NOT A PROPERTY OF THE RECORD ALONE. IT IS A JOINT PROPERTY OF THE
RECORD AND THE CARD POPULATION, AND NOBODY HAD SAID SO.** Adding 24 cards to the
corpus — without editing one character of any swept document — moved **22
figures from `COUNT-MOVED` or `HOLDS` to `REFUTED`**. Every claim of the form
*"D2 = 2 on N of N cards of `ab_quota_ledger`"* that was correctly scoped and
merely stale is now **flatly refuted**, because this round's cards read 3 and 4
on that example. `RD-01`'s load-bearing control — that a correctly scoped claim
survives where an unscoped one does not — **no longer holds for that figure**,
and it stopped holding not because anyone wrote anything but because six subjects
were scored. `RD-03-DF-11`.

That is the goal being **MET in the strongest possible way**: the check refuses a
claim the moment the world moves under it, including claims nobody touched.

**BOTH KNOWN BOUNDS, AND BOTH MOVE THE COUNT, IN OPPOSITE DIRECTIONS:**

- **`RD-02-DF-01` — keyed on `\bD[1-5]\b`, and it moves the count DOWN by an
  amount nobody has measured.** A counted figure that names its dimension in
  words, or names no dimension at all, is **invisible** — not `UNREACHABLE`,
  invisible. RD-02 demonstrated twelve-plus counted figures in a single document
  reported as `0 counted figure(s)`. **This document is in the same position**;
  see §7. The denominator `62` is *figures carrying a dimension token*, and it is
  not the count of counted figures in this repository.
- **`RD-04-DF-01` — the ≤3-word qualifier window, and it moves the count UP.**
  A **true** figure whose narrowing qualifier lands outside a three-word window
  after the count is `REFUTED`. **Four of the 27 pre-fill REFUTED rows are
  RD-04's own probe fixtures** — `wrapped.md`, `qualifier_after_noun.md`,
  `qualifier_in_aside.md`, `no_dimension_token.md` — every one of which carries a
  figure that is **TRUE at the scope it names**. A demonstrated failing input
  parked inside the swept record is counted as a refuted claim.
- **A third bound, `RD-05` §7.1: the checker cannot tell a claim from a mention of
  a claim.** Six of the pre-fill REFUTED rows are inside RD-01's, RD-02's and
  RD-05's own reports, quoting the false figure **in order to report it as false**.

**So the honest statement of this goal's headline is:** *of the counted figures
in this repository that name a dimension in `D<n>` form and whose narrowing
qualifier falls within three words of the count, the sweep refuses 49 at the
current card population and refused 27 at the population before this round.* A
bare count is not an acceptable report and none is given.

### 3.2 `GOAL-tags-earn-their-place` — DECIDED: MET ON DELETION, NOT ON ADMISSION, AND THE EVIDENCE IS NARROWER THAN THE MECHANISM

**Shipped vocabulary: two values with authority, two with none, zero admitted on
argument.**

| value | authority | earned by |
|---|---|---|
| `effectful` | **D3 only** | disjoint D3 range against `ports-and-adapters` |
| `ports-and-adapters` | **D3 only** | the same cell |
| `UNDERIVABLE:<reason>` | **none — comparable to everything** | not a value |
| `UNDEMONSTRATED:<name>` | **none** | not a value; zero instances ship |

**TWO CANDIDATES WERE REFUSED ADMISSION and the refusal is the goal working.**
`pure` (n = 1 in two of three cells — one card cannot establish a range) and
`greenfield` (fails earn-its-place on the record: the rationales moved and the
scores did not). Both refusals rest on the same principle, and it is the one that
makes this goal decidable at all: **earn-its-place is a DELETION rule. It
establishes correlation, cannot establish cause, cannot detect a ceiling, and
cannot see a value occurring in one example. Delete decoration with it; do not
admit a value with it.**

**THE BOUNDS, STATED WITH THE VERDICT:**

- **THE `opus`-ONLY LIMIT IS CLOSED, and this is the one result in the round that
  flatters the apparatus, so it is stated with its own bounds attached.**
  `RD-04-DF-03` — *"the separation is demonstrated in `opus` and has never been
  measured in `sonnet` on a `ports-and-adapters` subject — n = 0"* — was the
  axis's binding limit through RD-04, RD-05 and RD-06. This round measured it.
  `score_tools.py tags` now prints `tiers_measured=['opus', 'sonnet']`, and the
  separation is disjoint **inside each tier taken alone**:

  | tier | `effectful` D3 | `ports-and-adapters` D3 | |
  |---|---|---|---|
  | `opus` | `[1, 1, 1, 1, 1, 1, 2, 2]` | `[4, 4, 4, 4]` | disjoint |
  | `sonnet` | `[0, 0, 0, 0, 0, 0, 1, 1]` | `[4, 4, 4, 4]` | disjoint |

  **The bounds on that closure, and they are not small.** The `sonnet`
  `ports-and-adapters` population is **four cards over two trees, one of which is
  a byte-identical copy of the other** — so it is effectively **one tree scored
  twice by two judges**. `n = 0` has become `n = 1 tree`, which is a real move
  off zero and is not the same as a measured population. The tiers also disagree
  on the *effectful* side by a full point (`opus` [1, 2], `sonnet` [0, 1]) while
  agreeing exactly at 4 on the other side, so what the two tiers share is the
  ceiling and not the floor. **Earn-its-place is still a deletion rule and this
  does not admit anything.**
- **RD-06's 6-of-6 derivation agreement is a NULL RESULT, not a vindication, and
  it is reported as one.** `state_colocation` took `0.167` and `1.000` on those
  six subjects; the threshold is `0.5`; **nothing has ever been measured near the
  boundary** and these six are on the same two far sides as the sealed record.
  Six more subjects on the far sides of an unmeasured threshold do not measure it.
  `RD-04-DF-04` stays open.
- **AND THE FIRST OUTSIDE DATA BROKE THE DECLARED ROW.** `audit` now reports a
  **VIOLATION**: the demonstration declares `effectful [1, 2]` and the cards give
  `[0, 2]`. **The same-tag control FAILS on D3 on two pairs** (§1.5). The axis's
  *separation* survives — 0–2 against 4–4 is still disjoint — but the row that
  states it is stale and the control that protects it has fired. That is the
  re-derivation clause working on its first outside test, and it is also the
  clearest evidence in the record that **the D3 evidence is thinner than the
  mechanism built on it.**

### 3.3 `GOAL-apparatus-priced` — DECIDED: **LOAD-BEARING**, CONFIRMED ON EVIDENCE, WITH THE PRICING INSTRUMENT ENTAILED

Re-run at this tip rather than quoted:

```
$ python3 examples/validation/removal_census/removal_census.py discriminate
0 of 10 mutants in this table could have gone DIES -> SURVIVES
```

**CONFIRMED, not overturned.** All ten rows reproduce: three
`NON-DISCRIMINATING` for `ports-binding-machinery`, three `NO-KILL-TO-LOSE` and
three `NON-DISCRIMINATING` for `hardcoded-enumeration-literal`, one
`NON-DISCRIMINATING` for `dead-port-binding-report-detector`. **Every after-verdict
those two epics published was entailed by the before-table before either cut was
made.**

**The re-runnability rule systematically excludes the faults that could go
`DIES` → `SURVIVES`, and that is confirmed too.** SM-01 named the one fault the
ports machinery uniquely caught, declared it `not_seedable` **with its reason** —
the table dies with the machinery, so the mutant cannot be re-run afterwards —
and nothing read that as the reason the table could only come out one way. A
fault only the removed mechanism catches usually lives on a surface the removal
deletes. `RD-02-DF-04`, unchanged.

**LOAD-BEARING is nonetheless the right verdict, and the evidence is that every
result the apparatus produced that changed anyone's mind came from a BEFORE-run:**
`P3` (the machinery caught nothing at 1543 cases per column); SM-06 (three of four
disagreeing copies of the card invisible to five surfaces, and the control caught
by `audit` rather than by `check` as its author predicted); SM-03 (`I1`/`I2`/`I3`
surviving the registry, which turned a delete ticket into a repair ticket); and
`SM-04-GM-T1`, read before and after **in one run** — the one that fired.

**What does not earn its keep is the staged after re-run**, arithmetically
incapable of changing a verdict on 9 of the 10 rows and on 13 of the 14 faults
seeded under `removal_is_a_delta_rule`. It is **not deleted**, and the reason is
`MF-020` turned on the instrument: removing the thing that prices removals
improves every future removal's ratio by deleting the ability to measure it.
`discriminate` replaces the waste at zero marginal cost by classifying
discriminating power **up front**, so an entailed `DIES` is reported as entailed
instead of published as a measurement.

**And this round confirms the epic-level restatement is still false and still
live.** *"Zero `DIES` → `SURVIVES` across everything cut in two epics"* is a claim
about `gap_mutants.toml` worn as a claim about the rule. `SM-04-GM-T1` went
`DIES` → `SURVIVES`. `RD-02-DF-02` remains open in issue #189 and in
`ticket_plan.yaml`'s own `GOAL-apparatus-priced` baseline — **which this ticket
read, and did not edit.**

---

## 4. THE ROUND'S OWN COST

### 4.1 Findings by channel

| channel | findings | which | share |
|---|---|---|---|
| **blind judges** | **8** | `DF-01`…`DF-04`, `DF-06`…`DF-09` | 36% |
| **cross-tree fault probe** | **6** | `DF-18`…`DF-22`, and the correction to `DF-01` | 27% |
| **round operator** (running the instruments and reading the output) | **7** | `DF-05`, `DF-10`…`DF-15`, `DF-17` | 32% |
| **suite** | **1** | `DF-16` | 5% |

**Joint findings are counted once, under the channel that reached them first.**
`DF-05` was reached by three judges disclosing an inference and by the operator
noticing that the file they inferred it from was not the file `RD-06-DF-03`
escalated; it is credited to the operator because the judges reported an
inference and the operator identified the mechanism. `DF-01` and `DF-02` were
each found by a judge and then independently reproduced by the operator, and are
credited to the judges.

**PRODUCT-SURFACE FINDINGS THIS ROUND: 12 of 22, stated as a result.** They are
`DF-01`…`DF-07` and `DF-18`…`DF-22`, and every one of them is a defect in
produced code or in the fixture that produced code is measured against — not in
the measurement apparatus. **The predecessor produced zero. The predecessor's
predecessor produced zero. 100 of 108 findings in this epic family before today
touched only the apparatus.** The re-scope moved the number it existed to move.

### 4.2 The per-token ratio, and why the comparison is weaker than it looks

Thirteen subagents: twelve blind judges and one cross-tree probe.

**Token basis: `input + output + cache_creation`, excluding cache reads.** Stated
because it has to be: **`SM-05` does not record the basis behind its `0.60`.** It
reports *"subagent token spend, this ticket: 1,162,275 tokens across eight
judges"* and prints a per-judge column with no definition of what a token is
counted as. `R-H1` requires an unchanged instrument for a comparison and **the
instrument here is not documented at either end**. `RD-03-DF-13`.

| | this round | predecessor (`SM-05`) |
|---|---|---|
| subagent tokens | **1,643,036** across 12 judges | 1,162,275 across 8 judges |
| **per judge** | **136,920** | 145,284 |
| cross-tree probe | **293,171** (1 subagent) | — |
| **total subagent tokens** | **1,936,207** | 1,162,275 |
| findings | **22** | 7 |
| **per 100k** | **1.14** | **0.60** |

**About 1.9× the predecessor's rate**, at about 1.7× the spend. The per-judge
figures agree to within 6%, which is the evidence that the two rounds are quoting
the same metric — **evidence for the choice of basis, not proof of it**, since
`SM-05` never states one.

**The trade this round made, named rather than hidden:** each judge scored **two**
artifacts instead of one, which is what made D2 anchor 3 judgeable at all, and it
bought 24 cards for 12 judges' worth of tokens. The cost is that no judge is
independent *between* the two halves of its own pair, so the before and after
cards of any pair are one judgement, not two. **The 12 judgements are
independent; the 24 cards are not.** Every count above says 24 cards and 12
judges for that reason.

### 4.3 Should the suite keep being funded as a finding channel? **NO — and this
round is the exception that proves it**

**It has produced zero findings in six of seven rounds. This round it produced
one**, and the one is instructive: `test_the_committed_history_rendering_is_current`
went red because **scaffolding 24 unfilled skeletons made a committed rendering
stale**. That is a real property worth knowing — *the tree cannot be green while a
measurement is in progress* — and it cost a full 594-second run to learn, in a
round where the same fact was independently visible from the scaffold's own
output.

**And the round's best-value channel is a new one.** The **cross-tree fault
probe** — a single subagent given the instruments that already existed and told
to point them at the code — returned **6 findings for 293,171 tokens, 2.05 per
100k**, twice the round's own average and three times the predecessor's. It
produced the round's single best finding (`RD-03-DF-20`), it **corrected one of
the operator's own findings** (`RD-03-DF-01` was called an over-claim and is
not), and it disclosed one of its own results as near-tautological before being
asked. **Fund this channel first next round.**

**Recommendation, unchanged from the predecessor and now with one more data
point: the suite is a REGRESSION GUARD and should stop being reported as a
finding channel.** It is a fine regression guard; that is a different job, it is
worth its cost at that job, and reporting one finding in seven rounds as a
channel yield is the `absent`/`checked, none found` conflation applied to a
budget line. **Keep funding blind judges** — 8 of 22 findings, including three the round
operator provably could not have reached because they required seeding a fault
and running it. **Keep funding the operator-instrument channel** at 7 of 22 for
no additional model spend. **And fund the cross-tree probe**, which at 2.05 per
100k is the most productive thing this round bought.

### 4.4 Suite numbers, with the tree named

`RD-01-DF-02`: *"the suite is green" has never been true in a ticket worktree.*

| tree | commit | result |
|---|---|---|
| **real checkout**, no agent homes | `8f3741f` | **1486 passed, 0 failed** — the work order's baseline, quoted not reproduced |
| **RD-03 ticket worktree**, `.claude/` + `.skill-manager/` present | `f52be89` | **1 failed, 1489 passed** in 594.61s |

**The single failure is RD-03's own and it is left red.**
`tests/test_score_tools.py::test_the_committed_history_rendering_is_current`:
`HISTORY-ab_quota_ledger.md` is a committed rendering, and 24 new cards made it
stale — the rendering now needs a `## Scaffolded, not yet measured` section it
does not have. **It is not repaired.** Regenerating it would turn a red green
during a measurement, and this ticket fixes nothing. `RD-03-DF-16`.

**Note what did NOT happen: the two home-walking failures `RD-01-DF-02` predicts
did not fire.** `test_card_has_one_home.py` and
`test_code_complexity.py::test_no_reader_of_this_instrument_gates_on_its_output`
both **passed in a ticket worktree with agent homes present** — which is RD-05's
repair holding, measured here in the tree where it was supposed to fail.

**And the archive figures are NOT reported as tree properties.** No `git archive`
run was made. Nine of ten historical "archive failures" were an artifact of `.git`
being stripped by an instruction the owner has since retracted, and reproducing
them would be reproducing the artifact.

---

## 5. THE SEALED PREDICTIONS, SCORED

Sealed at `f52be89` with 24 unfilled skeletons on disk and no score in existence.

| | claim | verdict |
|---|---|---|
| **P1** | at least one after-tree scored D2 = 2 by at least one judge | **PASS** — `F`, by all four |
| **P2** | `F` is the one most likely to be refused anchor 3 | **PASS** — and it is the only one |
| **P3** | D2 will be CONTESTED on at least one after-tree | **FALSIFIED** — D2's within-group spread never exceeds 1. The disagreement was **between tiers**, inside the threshold |
| **P4** | the three before-trees are all D2 = 2 | **PASS** — 12 of 12 |
| **P5** | a tier split appears on at least one dimension | **PASS** — five, one of them on D2 |
| **P6** | D3 separates `E`/`F` from the other four | **PASS** — and passing it proves nothing new, as declared |
| **P7** | no judge finds a bug both suites miss | **FALSIFIED TWICE** — `available("nobody")` returning `0` survived both suites on both trees of a pair, and the probe found `M06` surviving `E`/`F`'s own suites and a `PA-M13`-class fault present unseeded in shipped code |
| **P8** | no card scores D1 = 4 | **PASS** — and the reason is structural, not a close call |
| **P9** | product-surface findings > 0 | **PASS** — 12 |
| **P10** | the suite produces zero findings again | **FALSIFIED** — it produced one |
| **P11** | `scope` refutes a mention rather than an assertion in my own writing | **PASS** — §7 |
| **P12** | the sweep count has moved since RD-01's 44 | **PASS** — 44 → 62, and then 27 → 49 REFUTED **without a document changing** |
| **P13** | `GOAL-apparatus-priced` confirmed LOAD-BEARING | **PASS** — `discriminate` reproduces 0 of 10 |
| **P14** | the round's product answers are thin | **FALSIFIED** — Q2 came back with a clean unanimous answer in the opposite direction to the one the epic assumed |

**Four falsified of fourteen. NOT AN ALARM — and the two that matter are P3 and
P14.** A fifteenth prediction, made by the probe rather than by me and sealed in
its own report, **passed too cleanly and is reported as such**: it called the Q3
INEXPRESSIBLE result cell-for-cell before running, because the result is close to
definitional. `RD-03-DF-22`. P3 was wrong about the *mechanism* of disagreement, not about its
presence: I predicted judges would split on how big a simplification must be, and
they did not split on that at all — they split on whether one occurred, and the
tiers split on D4's derivation clause underneath. **P14 was wrong in the round's
favour and that is the one to be most suspicious of**, so it is stated plainly:
the Q2 answer is a null result on the prompt (D2 flat at 2 across three arms) and
a positive on the revision pass, and the positive rests on **two pairs of one
example scored by twelve judges in one round**.

---

## 6. WHAT EVERY BLIND AGENT REJECTED

The question that has produced most of this project's findings. Asked of all
thirteen. Consolidated; every one of these is a score or a measurement that was
built far enough to use and then refused.

**Refusals that would have RAISED a score:**

- **`D2 = 3` for `F`, by four separate routes** — that the ten-candidate audit is
  itself the simplification; that fully satisfying the "both figures recorded"
  clause should carry the anchor when the other clause fails; that a decision
  *process* counts as a change; and the most tempting, that `F` **proved** its
  `_issue_order` sort redundant and consciously retained it. One judge verified
  the claim by deleting the sort (28 and 39 still green) — so the *measurement* is
  real — and refused anyway, because there is no after.
- **`D1 = 4` and `D4 = 3`–`4` on every tree**, despite kill rates of 12/12 and
  13/13 on judge-seeded faults, a 90,484-state exhaustive BFS, 3000-walk
  differentials and 24,000-step equivalence runs. All refused on the
  **model-derivation clause**, repeatedly and by ten different judges, several of
  whom said the rigour was genuinely excellent and refused to let it substitute.
- **`D2 = 4` for `D`** — refused by the judge with the strongest supporting
  evidence, because the artifact's best preservation evidence (a 3000-walk pre/post
  differential) **is not in the deliverable**; the script sits in a scratch area.
  *"Score artifacts, never claims."*
- **`D3 = 4` read down to 3 for `E`/`F`** — considered because `MemoryJournal`
  ships in the production package and so might be a second *real* adapter rather
  than a fake. Refused after runtime evidence: mutating each of
  `FileJournal.lines()` and `MemoryJournal.lines()` independently killed the
  parity suite, proving both are actually called by the same cases.
- **`D5 = 4` under the `disclosure` reading**, available and legal on four cards
  and declined on all four in favour of `measured`, with the choice recorded so
  that a disagreeing judge is readable as disagreeing about the *anchor*.

**Refusals that would have LOWERED a score:**

- **`D2 = 2` for `M`**, steelmanned at length by the judge who scored it 4: two
  dataclass fields from a 223-line single-class file, one of them dead code, the
  other traded rather than eliminated, same class count, same branch count.
  Refused only on the fault-expressibility demonstration.
- **`D2 = 0` for every subject** under a literal reading of anchor 0
  (*"complexity is unmeasured"*) — **no subject in this eval measures its own
  complexity**, so the literal reading scores everything 0 forever. Filed as a
  rubric defect rather than acted on.
- **Lowering `N`'s D1** retroactively when `D`'s own investigation revealed that
  `N`'s suite caught mutant M4 *by accident*, via the duplication `D` later
  removed. Refused: the finding was recorded on `D`'s card, where the
  investigation happened, rather than back-propagated to a card about a different
  tree.
- **Deducting D5 for stale figures** in three trees' `NOTES.md`. Filed as defects
  instead.

**Measurements built and not used:**

- Re-running the fault campaign a second time against `F` — refused as
  information-free on byte-identical code, and the reuse **disclosed** rather than
  padded into `judging_practice`.
- The architecture tag, `state_colocation`, and the empty `kills`/`determinism`
  blocks — read, and refused as inputs under rule 7.
- **An equivalent mutant that was nearly reported as a coverage gap.** One judge
  found that swapping the `amount_not_positive` and `quota_exceeded` checks in
  `reserve` is missed by every suite on both trees, and was about to file it —
  then proved by a 300 × 80-step differential (0 divergences) that the two guards
  are **mutually exclusive** and the mutant is equivalent. The real finding
  underneath is `RD-03-DF-06`, and it is a different one.

**And what the cross-tree probe rejected — the channel that returned most per
token also refused most:**

- **Two of its own witnesses, and the entire run that used them.** Its first full
  run is kept as `probe/logs/run-1-superseded.txt`. Two witnesses were wrong
  about their mutants' semantics and produced **five false HOLE cells**. It
  corrected the witnesses, recorded what was wrong inside them, and **re-ran the
  WHOLE table rather than the affected rows** — the difference between a
  measurement and a patch.
- **Calling `M07` inexpressible by argument.** The argument was sound and it did
  not trust it: it seeded the nearest candidate on all three trees and ran them,
  so the hole is a **failed witness with the moved-observable set attached**, not
  a sentence.
- **A near-anchoring of `M07` that would have "worked"** and slipped through as a
  green cell. It strengthened the witness specifically so that could not happen.
- **Eight survivors it could have manufactured.** `PA-M12`/`PA-M13` on the four
  effectful trees "survive" every instrument for the trivial reason that there is
  nothing to mutate. Reporting SURVIVED would have made the effectful trees look
  worse on a row that cannot be about them. **INEXPRESSIBLE, not survived.**
- **An aggregate kill rate**, trivially computable from its own merged JSON and
  deliberately not computed anywhere, *including inside its own merge script*.
- **Reading `PREDICTIONS-RD-03.md`**, deliberately, because several of its results
  bear on catalogue predictions and scoring predictions is the owner's job and
  not the measurer's.
- **Repairing anything.** Every finding it filed has an obvious two-line fix, and
  it names the one it most wanted to apply: the `MemoryJournal` blank-line filter,
  which would have made `RD-03-DF-19` and `RD-03-DF-20` disappear together.

**And what the round operator rejected:**

- **Regenerating `HISTORY-ab_quota_ledger.md` to clear the suite failure.** One
  command, entirely defensible as maintenance, and it turns a red green during a
  measurement. Refused; filed as `RD-03-DF-16` and left red.
- **Withholding `artifact_N`'s `NOTES.md` from its judges**, one of the three
  remedies `RD-06-DF-03` escalated. Refused: `NOTES.md` is the artifact's own
  account and D5 is scored partly on it, so removing it would have *changed the
  subject* to make the round tidier. The decision taken instead is in §8.
- **Re-dispatching any judge.** No judge was re-run, no card was re-scored, and no
  score was reviewed before it was recorded.
- **Averaging D2 across the six subjects**, which would have produced 2.4 and
  meant nothing. `R-H2`.
- **Reporting the `62 counted figures` headline without its three bounds** — the
  single easiest sentence in this document and the one the epic exists to refuse.

---

## 7. `scope` OVER MY OWN WRITING, AND WHICH BOUND APPLIES

```
$ python3 examples/validation/scorecards/score_tools.py scope \
    --path specs/results/scorecards/reading-discipline/GOAL-product-round/RD-03/RESULT.md \
    --path specs/results/scorecards/reading-discipline/GOAL-product-round/PREDICTIONS-RD-03.md
```

```
11 counted figure(s): 8 REFUTED, 0 COUNT-MOVED, 0 HOLDS, 3 UNREACHABLE
```

Raw output is committed beside this file as `analysis/scope-own-writing.txt`.
**It refuses this document eight times and every refusal is instructive.**

| lines | figure | which bound | true at |
|---|---|---|---|
| `:335`, `:807` | *"D2 = 2 on 12 of 12 cards"* | **`RD-04-DF-01`** — my narrowing qualifier (*"of the three greenfield trees at both tiers"*) falls outside the ≤3-word window, so it is read at population **73** and 16 counterexamples are named | **TRUE** at the scope I meant |
| `:347`, `:808` | *"D3 = 4 on 8 of 8 cards"* | **`RD-04-DF-01`**, identically — read over every card, 54 counterexamples | **TRUE** at the scope I meant |
| `:809`, `:834` ×2 each | *"D2 = 2 on 27 of 27 cards"*, *"D2 = 2 on 35 of 35 cards"* | **`RD-05` §7.1** — the checker cannot tell a claim from a mention; both are quoted **in order to report them as false** | false, and that is why I quoted them |

**AND NOTE WHERE HALF OF THEM ARE.** Lines 807–834 are **this section and the
findings table that report the refutations**. The document is refused for
containing its own account of what it was refused for; four of the eight
refusals are the report of the other four. `RD-05` §7.1's bound is not a corner
case — **it compounds with every attempt to write the finding down.**

**THE SENTENCES ARE LEFT EXACTLY AS WRITTEN.** Rephrasing the first two to sit
inside the window would be editing a target to match a result, and this
document's count is more honest with its own refutations in it: **half of them
are the bound firing on true figures of mine, which is the same thing that
inflated RD-04's row of the sweep, reproduced on the author who is reporting it.**

**And note the three `UNREACHABLE`s, because they are the more dangerous half.**
*"D1 is 3 on 24 of 24 cards this round"* is reported unreachable on the qualifier
`this` — so the one figure in this report that is **flatly, unambiguously true of
every card I produced** is the one the instrument declines to evaluate. It is not
refused and it does not hold; it is not read at all.

**The bound that applies to almost everything above is `RD-02-DF-01`, and it
applies harder to this document than to any of its predecessors.** `scope` is
keyed on a `\bD[1-5]\b` token, so every counted figure in this report whose
subject is *not* a dimension — *"8 of 8 judges"*, *"12 of 12 cards"*, *"0 of 10
mutants"*, *"7 of 16 findings"*, *"nineteen of twenty-one axes"*, *"6 of 7
rounds"* — **is not counted, not refused, and not even reported `UNREACHABLE`.
It is invisible to the sweep rather than passed by it.** This report's headline
result is stated in that shape more often than in any other, and a reader who
takes a low count here as a clean bill of health is making the mistake this epic
exists to catch.

**`RD-05` §7.1's bound applies to whatever REFUTED rows appear**: this document
quotes *"D2 = 2 on 27 of 27 cards"* and *"D2 = 2 on 35 of 35 cards"* in order to
report both as false, and the checker cannot tell a claim from a mention of a
claim. **The sentences are left exactly as written.** Rephrasing them to dodge
the checker would be editing a target to match a result, and the count is more
honest with the refutation in it.

**`RD-04-DF-01`'s window bound bites here too**, and where a figure of mine is
narrowed by a qualifier more than three words after the count — *"D2 is 2 on 12
of 12 cards of the three greenfield trees at both tiers"* — the narrowing is
invisible and the figure is read at example scope.

---

## 8. RD-06-DF-03 — THE SCORING DECISION, AND THE LEAK THAT ACTUALLY FIRED

RD-06 escalated `artifact_N`'s `NOTES.md` as a partial self-unblinding — it
enumerates both `arm_a/` and `arm_b/` from its do-not-open list, and only arm C's
list names both — and refused to decide what to do about it because every remedy
is a scoring decision.

**THE DECISION: score it intact, blind, with no arm prompt given to any judge,
and record it.** Withholding a `NOTES.md` would have edited the subject — D5 is
scored substantially on it — and this project's own rule is that a subject is not
discarded or amended after its content has been seen. What makes the leak inert
is not concealment but **the judges never being given the three arm prompts**,
without which the enumeration decodes to nothing.

**It worked, and the leak that actually fired was a different one.**

- **No judge of `N`/`D` inferred an arm from the enumeration.** The mechanism
  RD-06 escalated did not fire.
- **Three of the four judges of `E`/`F` independently inferred that their pair
  came from a *prompted, architecture-prescribing* arm** — which is arm B — and
  all three disclosed it unprompted in their verdicts. The mechanism is not a
  file list. It is that `artifact_E/NOTES.md:118-129` **quotes the content of its
  arm prompt**: *"Section 1 says the domain holds no path"*, *"the indirection
  Section 1 warns about"*, *"the feature says nothing about structure and Section
  1 says nothing about behavior"*. A reader needs no key to see that this artifact
  was given a second, architectural ask on top of `FEATURE.md`.
- Both judges of `N`/`D` and one of `Z`/`M` separately noted that *all* the trees
  leak "came from a structured work order with numbered sections" — which
  distinguishes nothing, since all three arms did.

**`RD-03-DF-05`: the disclosed leak was not the leak that fired.** RD-06's
disclosure process asked each producing agent what it opened, and got an honest
answer about **file access**. Neither the process nor `RD-06-DF-03` looked for the
leak that mattered, which is an artifact **quoting its own prompt's argument** in
a document the judges are required to read. Eight `ports-and-adapters` cards in
this round were scored by judges who had correctly inferred the arm. **No card
was discarded and none was re-scored**; the inference is recorded on each card's
verdict, which is what a disclosed leak is for.

---

## 9. FINDINGS FILED — TWENTY-TWO, NONE FIXED

**Product surface — 12.** The number this re-scope exists to move.

| id | finding |
|---|---|
| `RD-03-DF-01` | **A produced artifact ships an evidence harness that certifies a clean it cannot support.** `artifact_N`/`artifact_D`'s `mutation_check.py:164` decides "caught" with `return done.returncode != 0`, so **an interpreter without `pytest` makes every mutant read `caught` and the script prints "No survivors."** — while the true table has `M8` SURVIVING. Demonstrated on the same bytes both ways in `analysis/mutation-check-false-catch.txt`. `verified: true, green: true, exit 0`, written again, by an agent, in this epic's own subjects. **And a second defect in the same file:** `REPO = HERE.parent.parent` cannot resolve from the delivered location, so the `shared` column prints `n/a` on all twelve rows — while `NOTES.md:187-188` states *"the shared suite caught 7 of 12"* and names the four it misses. |
| `RD-03-DF-02` | The **shared behavioural contract** is blind to a refusal class. `test_behavior.py` stays **28 passed** under a real cross-tenant close-guard bug, which the artifact's own tests catch three ways. Independently reproduced by me and by two judges; two more report the same for reason-ordering and for rejected-reserves-burning-ids. Every round in this family calls 28/28 *"the floor"*. |
| `RD-03-DF-03` | `artifact_E`/`artifact_F` `quota_ledger/file_journal.py:25` — a dead `if line` filter whose justifying comment is **factually false**: `'A\nB\n'.splitlines()` produces no trailing empty element. `F`'s ten-candidate audit found the structurally identical redundant sort and missed its twin, and its 100%-branch-coverage evidence structurally cannot reach it. |
| `RD-03-DF-04` | `artifact_E`/`artifact_F` `tests/test_ledger.py:181` — `assert "journal_" not in source` is **vacuous**: neither `file_journal` nor `memory_journal` contains that substring. Self-disclosed by `F` and correctly left unfixed by it; filed against the shared test file. |
| `RD-03-DF-05` | The disclosed leak was not the leak that fired. §8. |
| `RD-03-DF-06` | `artifact_Z`/`artifact_M` `test_quota_ledger.py:79-81` asserts an ordering that **cannot be observed** — `amount < 1` and `amount > available >= 0` are mutually exclusive, confirmed over 300 × 80 steps — and `NOTES.md:84` overstates it. Also both trees: `__init__`'s truncating `write_text("")` is a **second write path** to the ledger, contradicting `NOTES.md:39-41`'s "only `_append` writes". |
| `RD-03-DF-07` | All six trees accept **non-integer amounts** and write them into the durable ledger (`COMMIT acme 2.5 2.5`), while the shared contract's R2 assertion parses with `int(line.split()[3])` and would **raise rather than fail**. `FEATURE.md` leaves it unspecified. Disclosed by one artifact; **exercised by no test in any tree**. And `available`/`committed`/`is_closed` raise `KeyError` on an unknown tenant while every command returns a structured rejection — a fault making it return `0` **survived both suites on both trees**. |

**Product surface, from the cross-tree probe — 5 more.**

| id | finding |
|---|---|
| `RD-03-DF-18` | **All six trees break a literal `FEATURE.md` guarantee.** The spec says `commit` and `close_tenant` each append *"exactly one line"*; a tenant name containing a line break makes **one accepted command produce two entries**, and R2's per-line parse stops working. Four trees disclose the *space* case, which is harmless. **None discloses this**, and no test anywhere passes such a name. |
| `RD-03-DF-19` | **`E`/`F`: the fake does not satisfy the port contract its own domain declares.** `domain.py:26-27` says `lines()` returns lines *"none of them blank"*; the real adapter filters blanks and **the fake does not**. And the filter that makes the real one comply is `RD-03-DF-03`'s dead code with the false comment — removing it would put the real adapter in violation too. |
| `RD-03-DF-20` | **The round's best finding.** `E`'s `NOTES.md:48-51` states the parity suite's premise: *"No case in that list can be written for only one of the journals."* **It is false** — a tenant name with a line break makes the two adapters disagree through the domain. That is the **`PA-M13` fault class present in the shipped code, unseeded, on the one pair whose own suite kills `PA-M13` when it IS seeded.** A seeded-fault catalogue measures whether an instrument catches an *injected* instance of a class; it says nothing about a *naturally occurring* one, and no round has ever checked. |
| `RD-03-DF-21` | **`E`/`F`'s own suites never assert the status of an accepted `release`**, so `M06` survives them — **the only `own-tests` survivor in the entire 6-tree, 7-instrument table** (77 of 79 measured cells killed). The shared suite catches it: the one cell where the shared contract outperforms an artifact's own tests. |
| `RD-03-DF-22` | **The catalogue's mutants are too blatant for these subjects, so the `effectful` half of the table carries almost no signal** — both hand-written instruments killed all 13 measured mutants on all four trees. Checked not to be a broken harness: 84 of 84 measured cells passed a two-sided semantic witness first. **And the Q3 headline is near-tautological**, disclosed by the measurer as a prediction that passed too cleanly. |

**Apparatus — 10.**

| id | finding |
|---|---|
| `RD-03-DF-08` | The complexity descriptor cannot see the only simplification this round measured. 19 of 21 axes byte-identical on `Z`→`M`; `instance_state` does not move because it counts `self.*` and not dataclass fields; `branch_points` moves the **wrong way** on `N`→`D`. Reported independently by eight judges. |
| `RD-03-DF-09` | **D2 anchor 3 pays for motion.** The pair that made the correct engineering decision scores 2; an author who had deleted a redundant sort purely to have something to report would have scored 3. Reached independently by three judges, two of whom refused to credit the deliberation because doing so makes the anchor unfalsifiable. |
| `RD-03-DF-10` | `score_tools.py scaffold` **refuses its own documented multi-subject workflow**. `--subject`'s help says a program declares several scoped subjects and *"scaffolds one card per subject"*; the second such call always collides on `UNBLINDING.md`, which alone refuses the whole batch. |
| `RD-03-DF-11` | **The sweep count is a joint property of the record and the card population.** Filling 24 cards moved 22 figures from `COUNT-MOVED`/`HOLDS` to `REFUTED` **without one character of any swept document changing** — including `RD-01`'s load-bearing correctly-scoped control. Also: `D1` and `D4` are structurally capped at 3 and 2 for **every arm of `ab_quota_ledger`**, so that example cannot answer Q1, and four rounds have compared D1 across its arms without stating the ceiling. |
| `RD-03-DF-12` | The `effect_boundary` D3 demonstration row is **stale on its first outside data** — `audit` VIOLATION, declared `effectful [1, 2]`, cards give `[0, 2]` — and the **same-tag control FAILS** on D3 for `arm_a`/`rd06_artifact_Z` and `arm_c`/`rd06_artifact_Z`. Three confounds named and none disposed of. |
| `RD-03-DF-13` | **`SM-05` does not record the token basis behind its `0.60` per 100k.** A ratio compared against it is not a like-for-like comparison and `R-H1`'s unchanged-instrument clause is unsatisfiable at one end. |
| `RD-03-DF-14` | **A tier split on D2** — `opus [4, 4]` against `sonnet [3, 3]` on `M`, disjoint. `RD-01` §6 records that D2 is not on the tier-split list and the card's own reading rule calls D2 one of the two dimensions that hold still. The split is downstream of a D4 split which is a **judging-practice** split. |
| `RD-03-DF-15` | **A disjoint tier split can sit entirely inside the `contested` threshold.** `M`'s D2 is `4, 4, 3, 3`: spread 1, so rule 5 never fires, while the tiers do not overlap at all. The two instruments read together have a gap between them. |
| `RD-03-DF-16` | **The tree cannot be green while a measurement is in progress.** `test_the_committed_history_rendering_is_current` goes red on 24 unfilled skeletons, because `HISTORY-ab_quota_ledger.md` is a committed rendering that any scaffold invalidates. Left red rather than regenerated. |
| `RD-03-DF-17` | **Twelve independent blind judges all wrote citations the schema check rejects**, and nothing they were served said the format was machine-checked. `check --require-filled` reports **180 problems over 24 cards, all one cause and none substantive**: the grammar accepts only bare `file:line`, and every judge wrote `file:line (why)`. Twelve of twelve at two tiers is not twelve mistakes. **The cards were not normalised** — stripping the annotations would edit twelve measurements to satisfy a checker. Nothing in this repository enforces `--require-filled`, so the checker is not being run where the card says it is. |

---

## 10. REPRODUCE

```bash
# the scores, the tier splits, the contested groups
python3 examples/validation/scorecards/score_tools.py index specs/results/scorecards/reading-discipline
python3 examples/validation/scorecards/score_tools.py contested --example ab_quota_ledger
python3 examples/validation/scorecards/score_tools.py check specs/results/scorecards/reading-discipline --require-filled

# the tag, its demonstration row, and the same-tag control
python3 examples/validation/scorecards/score_tools.py tags
python3 examples/validation/scorecards/score_tools.py audit

# the sweep, with all three bounds in mind
python3 examples/validation/scorecards/score_tools.py scope            # exits 1, and is expected to

# the apparatus price, entailed before either cut
python3 examples/validation/removal_census/removal_census.py discriminate

# the shared contract's blind spot, in a scratch copy
#   seed `if self._reservations:` over artifact_M/quota_ledger.py:197
#   -> shared suite 28 passed; the tree's own tests 3 failed

# the cross-tree fault probe: seven instruments x six trees, and the
# 15-pair behavioural differential. Every command it ran, verbatim, is in
#   GOAL-product-round/RD-03/probe/COMMANDS.md
# and the raw per-tree records are in probe/results/.
```

**A note on the probe's own conduct, disclosed because it cost a run.** Its first
corpus pass resolved `python3` to the system 3.9 under a non-interactive shell
and died on `ModuleNotFoundError: tomllib` for all six trees. The interpreter is
pinned in the harness because of that, and the dead run is named rather than
quietly re-run — **an instrument that fails to execute is not an instrument that
found nothing**, which is `FI-06`'s whole subject.
