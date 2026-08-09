# next epic — starter for the next epic owner

> **AMENDED AFTER `RD-03`, the `reading-discipline` evaluation (2026-08-09).**
> Everything below still describes how each earlier result was measured and none
> of it is edited. What RD-03 adds is at the very top, in section 0-AAAAAA,
> because it is **the first round in this family that pointed the instruments at
> the software** and because two of the things it found retire figures the
> sections below still rest on. Full record:
> `specs/results/scorecards/reading-discipline/GOAL-product-round/RD-03/RESULT.md`.

---

## 0-AAAAAA. READ BEFORE EVERYTHING — what RD-03 measured

### 1. THE D2 CONSTANT IS DEAD, AND IT DIED FOR THE REASON SM-05 PREDICTED

`D2 = 2` held on **35 of 35** cards ever written about `ab_quota_ledger`. It was
the figure `subtract-to-measure` was opened on, and SM-05 correctly diagnosed why:
**anchor 3 requires a measured simplification and a greenfield artifact has no
before.** RD-06 built three before/after pairs. RD-03 scored them with twelve
blind judges at two tiers.

| pair | `code_lines` before → after | D2 on the after tree |
|---|---|---|
| `Z` → `M` | 158 → **156** | **4, 4, 3, 3** |
| `N` → `D` | 283 → **280** | **3, 4, 3, 3** |
| `E` → `F` | 163 → **163** | **2, 2, 2, 2** |
| the three greenfield before-trees | — | **2, on 12 of 12 cards** |

**Eight judges saw a code change and eight awarded anchor 3. Four saw none and
four refused it. NOT ONE SPLIT ON THE SIZE OF THE DELTA.** The round was designed
to ask whether a two-line delta is a simplification; the judges did not find that
to be the question. They went to the diff and decided on what it *removed* — in
both cleared pairs, **a second stored representation of a fact the program
already held**, hand-maintained at three write sites and read at one.

**The lever is the REVISION PASS, not the prompt.** D2 is flat at 2 across
`arm_a`, `arm_b` and `arm_c` greenfield trees whose prompts differ by 91–111
distinct lines. Asking for architecture moved D2 by nothing. Asking for a second
pass moved it on two subjects of three.

### 2. THE COMPLEXITY INSTRUMENT CANNOT SEE THE ONLY SIMPLIFICATION MEASURED

Eight judges reported this independently, unprompted, on their own cards.

On `Z` → `M`, **nineteen of twenty-one measured axes are byte-identical** —
including `instance_state`, the one axis whose name describes exactly what was
removed, because it counts `self.*` attributes and **does not count dataclass
fields**. On `N` → `D`, `branch_points` moves the **wrong way**, 26 → 27.

**Scored on the descriptor alone, the answer is that no simplification occurred
on either pair.** `RD-03-DF-08`. Do NOT repair this by adding an axis that makes
these revisions score better — that is `MF-020` in its purest form. If an axis is
added it ships with a seeded case where it moves the wrong way.

### 3. D2 SPLIT BY JUDGE TIER — THE DIMENSION THE CARD SAYS HOLDS STILL

`opus` [4, 4] against `sonnet` [3, 3] on `artifact_M`, **disjoint**.

`RD-01` §6 records the three known tier splits and says *"D2 is not on this
list"*. `references/eval_scorecard.md`'s own reading rule calls D2 and D3 *"the
dimensions that have held still on unchanged input"* and advises resting a
cross-epic claim on them. **`ports-as-adapters` rests its headline on that
advice.**

**The mechanism is not about complexity.** D2's anchor 4 gates on D4 ≥ 3; D4's
anchor 3 gates on the check being *"model-derived (a corpus, a TLC invariant)"*.
Both `opus` judges counted a generated random walk as a corpus and reached D4 = 4.
Both `sonnet` judges read the clause strictly, found no model, and capped D4 at 2.
**The same disjoint D4 split appears on four subjects.** The D2 split is
downstream of it. `RD-03-DF-14`.

**The repair the next epic should consider is to D4's anchor 3, not to D2:** one
parenthetical is being read as a definition by one tier and as an illustration by
the other. Do not fix it by deleting the parenthetical.

### 4. `ab_quota_ledger` CANNOT ANSWER THE BUG-DETECTION QUESTION, AND FOUR ROUNDS COMPARED D1 ON IT ANYWAY

Ten of twelve judges reported independently that **no model exists anywhere in
any of the six trees** — no TLA+, no generated corpus, no strategy. D1's anchor 4
and D4's anchor 3 both gate on model-derivation, so **D1 is structurally capped
at 3 and D4 at 2 for every arm of this example**, whatever the code does. D1 came
back 3 on 24 of 24 cards this round.

**The ceiling has never been stated in any round that compared D1 across this
example's arms.** `RD-03-DF-11`. Either state it wherever this example's D1 is
compared, or give the example a model-derived instrument so the anchor is
reachable. Until one of those happens, *"do model-derived cases catch bugs
hand-written tests miss"* is **not answerable on this fixture** and should stop
being asked of it.

### 5. THE SWEEP COUNT IS A JOINT PROPERTY OF THE RECORD AND THE CARD POPULATION

Filling this round's 24 cards moved **22 figures from `COUNT-MOVED`/`HOLDS` to
`REFUTED` without one character of any swept document changing.**

| sweep | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| RD-01 | 44 | 19 | 11 | 6 | 8 |
| RD-04's reconciled tip | 58 | 26 | 11 | 9 | 12 |
| RD-03 before the cards were filled | 62 | 27 | 11 | 11 | 13 |
| **RD-03 after** | **67** | **53** | **0** | **0** | **14** |

The casualty is **RD-01's own control**: it rested the instrument's validity on
the correctly-scoped twin surviving where the unscoped one did not. Every
correctly-scoped `D2 = 2 on N of N cards of ab_quota_ledger` is now refuted too.
The control did not fail — the world moved under it. **A published sweep count
must carry the card population it was taken at**, exactly as a card carries its
commit. `RD-03-DF-11`.

### 6. THE THREE INSTRUMENT BOUNDS, WHICH EVERY FUTURE SWEEP MUST CARRY

1. **`RD-02-DF-01`** — keyed on `\bD[1-5]\b`. A counted figure that names its
   dimension in words is **invisible**: not refused, not `UNREACHABLE`. Moves the
   count **down** by an unmeasured amount.
2. **`RD-04-DF-01`** — the ≤3-word qualifier window. A **true** figure whose
   narrowing qualifier lands outside it is `REFUTED`. Moves the count **up**.
   **Two of the four refusals against RD-03's own report are this**, on figures
   that are true at the scope they meant.
3. **`RD-05` §7.1** — the checker cannot tell a claim from a **mention** of a
   claim. Every round that reports the false figure in order to call it false is
   refuted for doing so.

### 7. THE `opus`-ONLY LIMIT ON THE ARCHITECTURE TAG IS CLOSED — AND READ THE BOUND

`RD-04-DF-03` was the axis's binding limit through three tickets: the D3
separation was demonstrated in `opus` and **never measured in `sonnet` on a
`ports-and-adapters` subject, n = 0**. This round measured it.
`tags` now prints `tiers_measured=['opus', 'sonnet']` and the separation is
disjoint inside each tier alone.

**The bound, because this is the one result that flatters the apparatus:** the
`sonnet` `ports-and-adapters` population is **four cards over two trees, one of
which is a byte-identical copy of the other** — effectively one tree scored twice.
`n = 0` became `n = 1 tree`. That is a real move off zero and it is not a
measured population.

**And the same-tag control now fires nine times**, eight of them on D2, every one
a before-tree scoring disjointly from an after-tree at the same derived value.
**The control cannot distinguish "different architecture" from "different
treatment"**, and this round is the first time it has had a within-value
treatment difference to see. `RD-03-DF-12`.

### 8. SEVEN PRODUCT-SURFACE FINDINGS, AGAINST ZERO IN EACH OF THE LAST TWO EPICS

100 of 108 findings in this family before today touched only the apparatus. This
round filed 17, of which **7 are defects in produced code or in the shared
fixture**. The two worth carrying forward by name:

- **`RD-03-DF-01` — a produced artifact ships an evidence harness that certifies
  a clean it cannot support.** `mutation_check.py` decides "caught" with
  `return done.returncode != 0`, so an interpreter without `pytest` makes every
  mutant read `caught` and the script prints **"No survivors."** The true table
  has one survivor. `verified: true, green: true, exit 0` — written again, by an
  agent, in this epic's own subjects, and caught only because a judge ran it.
- **`RD-03-DF-02` — the shared behavioural contract is blind to a refusal class.**
  It reports **28 passed** under a real cross-tenant close-guard bug that the
  tree's own tests catch three ways. Every round in this family calls 28/28
  *"the floor"*. The floor is lower than it reads, by a class rather than a case.
  **Do not quietly extend it**: that silently re-bases every published "28
  passed" and makes the old and new figures look like one series.

### 9. WHAT THE NEXT EPIC SHOULD NOT DO

- **Do not run a fourth apparatus evaluation.** This one found real product
  defects the moment it was pointed at code, and it found them with instruments
  that already existed.
- **Do not average D2 across the six RD-06 subjects.** It gives 2.4 and means
  nothing. `R-H2`.
- **Do not treat "the prompt improves D3" as this round's finding.** It
  replicated and is reported as a replication; the new results are §1 and §3.
- **Do not report a per-token finding ratio without naming the token basis.**
  `SM-05`'s `0.60` does not record one, so no round can be compared to it without
  assuming one. `RD-03-DF-13`.
- **Do not normalise a judge's card to satisfy a checker.** `check
  --require-filled` reports 180 problems against this round's 24 cards, **all one
  cause and none substantive**: twelve independent judges all wrote annotated
  citations and the grammar accepts only bare `file:line`. Twelve of twelve is
  not twelve mistakes. `RD-03-DF-17`.

### 10. THE STANDING RULE, AND WHETHER THIS ROUND MET IT

*An epic that closes with only good news about itself has not been measured.*

**Four of fourteen sealed predictions were falsified**, including one that was
wrong **in the round's favour** — I predicted the product answers would be thin
and one of them came back clean and unanimous. That is the one to be most
suspicious of, and it rests on two pairs of one example in one round.

**And the round's own conduct produced a finding about itself.** I read
`score_tools.py tags` once while judges were still filling cards, recorded a D3
control failure from a partial population, and it **was never true of the
complete one**. It is reported in `RESULT.md` §1.5 rather than dropped: an
instrument read over a moving population gives an answer about the population it
was read over, which is this epic's own subject applied to its own operator.

---

> **AMENDED AFTER `SM-05`, the `subtract-to-measure` evaluation (2026-08-07).**
> Everything below still describes how each earlier result was measured and none
> of it is edited. What SM-05 adds is at the very top, in section 0-AAAAA,
> because it **retracts the premise the whole `subtract-to-measure` epic was
> opened on** and because what it found is a reading failure and not a mechanism
> failure. Full record:
> `specs/results/scorecards/subtract-to-measure-sm05/RESULT.md`.

---

## 0-AAAAA. READ BEFORE EVERYTHING — what SM-05 measured

### 1. D2 WORKS. IT WAS NEVER GIVEN A SUBJECT.

Two subjects scored in one round by four judges each at two model tiers:

| subject | D2 |
|---|---|
| greenfield `ab_quota_ledger` | **2, 2, 2, 2** |
| toolchain removal (a real before/after) | **3, 3, 4, 3** |

**Perfect separation, no tier effect.** The card can measure complexity. Five
epics of greenfield fixtures could never have exercised it, because anchor 3
requires a measured simplification and a greenfield artifact has no before.

### 2. AND THE EPIC'S PREMISE WAS ALREADY FALSE WHEN IT WAS WRITTEN

`subtract-to-measure` was opened on *"D2 = 2 on 27 of 27 cards ever written"* and
*"every subject this project has ever scored was greenfield … no greenfield
artifact can reach D2 anchor 3, ever."*

**41 cards carry a D2 score, across six examples, and D2 has taken three
values.** `ex3_over_complex` was blind-judged on **2026-08-03** and both judges
scored **D2 = 3**, citing before and after descriptors. In the one round that
scored five *different* fixtures, D2 discriminated across 1, 2 and 3 with
**perfect inter-judge agreement on all five**. The anchors digest is identical at
v1, v2 and v3, so the bar was the same.

**The "27 of 27" figure is a true fact about one example, restated unscoped as a
fact about the instrument** — in the charter, in the plan's `purpose`, and in the
issue. `R-H2` forbids AVERAGING across examples. **Nothing forbids generalising
from one**, and `history` requires `--example`, so nobody ever saw the six
columns side by side.

**This is the thing to fix, and it is not a mechanism.** An entire epic was
justified by a claim that one command against this repository's own sealed cards
would have refuted. `SM-05-DF-01`.

### 3. WHAT TO DO NEXT, IN ORDER

1. **Give `score_tools.py` a cross-example view, and rescope every statement of
   the D2 figure to the example it is about.** Cheapest, and it closes the
   failure mode that has now cost one whole epic.
2. **Decide what the card is for.** A judge measured, unprompted, that **four of
   five dimensions have a top rung a subject without a model cannot reach for
   reasons of shape** — D1/4 needs a model, D2/3–4 need a before, D3/4 needs a
   fake the spec permits omitting, D4 presupposes a baseline. *"A competent
   greenfield artifact tops out at 2–3 across the board no matter what it
   does."* If the card is for model-carrying subjects, say so and stop comparing
   greenfield cards to it. `SM-05-DF-05`.
3. **Fix the served scoring rule before the next round.** *"Score the LOWEST
   anchor the artifact fully satisfies"*, read literally, **yields 0 on every
   dimension**. Four judges across two rounds have now rejected the literal
   reading in order to score at all. It is a one-line change and it needs a
   version bump.
4. **Stop quoting D3 across subjects of different scale.** On a repository-scale
   subject D3 spans **2 to 4** between judges at the same tier, because "the
   domain" has no fixed referent there, and scoring rule 5's adjudication
   explicitly cannot settle it — both judges say no new evidence exists.
   `SM-05-DF-06`.

### 4. DO NOT REPEAT THESE THREE

- **Do not open another subtraction epic on the strength of a line count.**
  `subtract-to-measure` removed 225 lines from `scripts/` and added 1677 net
  across the trees it touched — **about seven lines of measurement apparatus per
  line removed.**
- **Do not dispatch a judge into the live repository.** Statements of how a
  dimension *scored* are watched by nothing (the one-home check exempts them by
  design), and seven files carrying them were on no dispatch's forbidden list.
  **One of them demonstrably moved a score in SM-05**, by its judge's own
  disclosure. `SM-05-DF-02`.
- **Do not trust a blind evidence packet that was not generated.** The sealed
  packets print all three artifacts' complexity figures in one table — served to
  26 judge-scorings on the two dimensions the project makes cross-epic claims
  about — and carry visible hand-scrubbing artifacts inside code identifiers.
  `SM-05-DF-03`.

### 5. THE CHANNEL RESULT, UNCHANGED FOR SEVEN ROUNDS

**The suite produced zero findings again — six of seven rounds.** The
blind-judge channel produced everything worth having, **including both of the
round operator's own errors**, one of which the judge showed had moved a
dimension-point in its own card. Keep funding blind judges and the census
channel. **Stop reporting the suite as a finding channel.**

---

> **AMENDED AFTER `FI-06`, the `falsifiable-instruments` evaluation
> (2026-08-06).** Everything below still describes how each earlier result was
> measured and none of it is edited. What FI-06 adds is at the very top, in
> section 0-AAAA, because it **retracts part of what section 0-AAA calls "the one
> clean win"** and because it names the single experiment worth funding next.
> Full record: `specs/results/scorecards/falsifiable-instruments/RESULTS.md`.

> **AMENDED AGAIN AFTER `PA-06`, the `ports-as-adapters` evaluation (2026-08-05).**
> Everything below still describes how each earlier result was measured and none
> of it is edited. What PA-06 adds is at the top, in section 0-AAA, because two
> of its findings change what the NEXT epic can even attempt. Full record:
> `specs/results/scorecards/ports-as-adapters/RESULTS.md`.

---

## 0-AAAA. READ BEFORE 0-AAA — what FI-06 measured

### THE ONE THING TO DO NEXT, AND IT IS ONE THING

**Do not open a fifth mechanism epic.** Four epics of mechanism work have made
the mechanisms better and the *reading discipline* no better, and the reading
discipline is what every one of these failures has been. Two actions, in order:

1. **Close `FI-04-DF-04`, with its own suggested fix and not by lengthening a
   literal.** `GOAL-instruments-can-fail`'s only target is *"nothing is silently
   omitted"*, and the check behind it is a hardcoded subset test that catches a
   rename and cannot catch an addition. It failed **three times inside the epic
   that filed it, with the suite fully green**, and FI-06 found **at least eight
   more omissions** — including `run_arm_swap.py` (shipped by FI-04 in the same
   reconcile as the instrument it registered by hand *while writing that
   finding*) and `demonstrate.py`, the enumerator itself. The fix is one
   predicate over a diff: *`close ticket` refuses when a ticket adds an
   executable under a declared instrument root and the registry gained no row in
   the same commit.* **Until it lands, no count from that registry may be quoted
   without "the denominator is a floor."**
2. **Run the blind-author experiment, with the model's constants enlarged and the
   port columns included.** It is the only outstanding question in this
   repository whose answer would change a decision. Specification in
   `specs/results/scorecards/falsifiable-instruments/RESULTS.md` §4.

### THE "ONE CLEAN WIN" BELOW IS PARTLY RETRACTED — read this before quoting it

Section 0-AAA says a third arm *"longer than the hexagonal one and asking for
nothing architectural"* settles the 6.6× confound. **Measured against the bytes
this repository now preserves as dispatched, arm C was neither.**

```
$ python3 examples/validation/ab/check_catalogue.py --arms \
      --dispatch-dir examples/validation/ab/dispatch/ports-as-adapters

  arm C / arm B:  1.181  (+18.1%),  tolerance +/-10%
  ARCHITECTURAL VOCABULARY: arm C: 4 of 124 unique lines  [PORTS] [ports] [Designs] [module]

CATALOGUE INTEGRITY FAILED
  ... outside the declared +/-10% tolerance.
  ... if it asks for structure it is a second treatment and the confound is not settled.
```

Two of the four vocabulary hits are paths PA-06 itself introduced — the working
directory `.../ports-as-adapters/arms/arm_c/` and the forbidden file
`PORTS-AS-ADAPTERS-EPIC.md`. **PA-06 measured this honestly and filed it as
`PA-06-DF-10`**; the retraction is at
`specs/results/scorecards/ports-as-adapters/RESULTS.md:121-125`. **It never
reached this document, and `FALSIFIABLE-INSTRUMENTS-EPIC.md:94-98` restates it as
established fact.** `FI-06-DF-06`.

**The D3 result survives** — 1/1 against 4/4 is far outside anything either
defect accounts for, and arm C's author declined the seam on merit. **The stated
tolerance and the "no architectural vocabulary" do not.** Quote the conclusion;
never quote the tolerance.

### THREE THINGS THAT ARE NOW FALSE OR UNQUOTABLE

- **`D2`, `D4`, `D5` and the `total` column of `SELF-IMPROVEMENT.md`.** D4 and D5
  cannot carry a delta because they are noisy; **D2 cannot because it is a
  CONSTANT — 2 on 27 of 27 cards ever written about `ab_quota_ledger`** — because
  its anchor 3 requires a before/after pair a greenfield artifact cannot have,
  which the judges say in their own rationales. **D3 is the only trustworthy
  column.** `FI-06-DF-05`.
- **"The generated corpus ties the hand-written suite on a blind catalogue."**
  There are **two** blind-authored catalogues here, not one, and on the earlier
  pair **the suite strictly dominates with the generated family holding zero
  unique kills** — on the *same fault class*. The difference is
  `QuotaLedger.cfg:8`, `ResIds = {r1, r2}`: the favourable draw reuses an id at
  allocation #2 and the unfavourable one at #4, and no behaviour of this model
  contains more than two `Reserve` actions. `oracle.py` has been counting **266
  of 294** skips against that wall on every run for three epics. **Enlarging
  `ResIds` is the single cheapest change in this repository with a chance of
  moving a cell.** `FI-06-DF-07`, `FI-06-DF-08`.
- **Any judged number produced against a rubric the judge was told to read.** At
  `51fe73d` that file states the result FI-03 was measuring, by name, with the
  prior scores. **Split the rubric before the next round**: dimensions, anchors
  and scoring rules go to the judge; the `R-H` reading rules, prior results and
  known-instability tables do not. `FI-06-DF-04`.

### AND THE STANDING CHANNEL RESULT, WHICH KEEPS REPLICATING

**FI-06 ratio: 0 : 16 : 1 : 1 : 12 — thirty findings, ZERO from the suite**, for
the fifth round in six. The new and now-dominant channel is *build the
instrument, then ask what it cannot report* (16 of 30) — cheaper than an
adversarial agent, and it found the structural defects; the adversarial channel
found the ones the builder could not see because they were about the builder's
own frame. **Keep both. Never expect the suite to produce one.**

---

## 0-AAA. READ FIRST — what PA-06 measured, and the two things it makes impossible

### The one clean win: the predecessor's confound is settled, FOR THE PROMPT

`hexagonal-prompting` ended saying its D3 = 1 → 4 headline "cannot be attributed
to *hexagonal* rather than to a 6.6× longer prompt". **It can now.** A third arm
— a control prompt longer than the hexagonal one and asking for nothing
architectural — scored **D3 = 1 from both blind judges** against the hexagonal
arm's 4 and the ordinary arm's 2. And its author, asked what it REJECTED, named
the exact seam the hexagonal arm built and declined it on merit:

> *"introducing a second class to wrap one method would be a layer with no second
> implementation behind it and no test that needs to swap one in."*

**Prompt length does not produce structure. The architectural content is not
decoration.** That is the one thing this epic established that nobody has to
qualify — beyond the standing `n = 1` caveat and the fact that arm C controls for
length, not for subject.

### THING ONE THAT IS NOW IMPOSSIBLE: this A/B cannot measure "validated differently"

`GOAL-cases-drive-ports` asks whether a codebase with real ports is *validated
differently* from one without. **It cannot be answered by this experiment, and
the reason is a proof rather than a result.**

PA-06's adversarial channel built an exhaustive observational fingerprint —
every command sequence of length 4 over a 13-action alphabet, 28,561 sequences,
full projection after every step, per arm per mutant — and measured the three
arms' **mutated** trees to be **identical on 10 of 11 rows**. Two trees with the
same observational fingerprint cannot be told apart by any black-box instrument.
So "the arms' verdicts are identical" is a **consequence of the re-anchoring
succeeding**, and this experiment can only produce a divergence where the
re-anchoring **fails**.

The rival explanation is measured false: the trees are 78, 151 and 202 code lines
with three different representations of a held reservation.

**And the rule that causes it is the RIGHT rule.** `EVAL-RERUN` adopted "hold the
`semantic` equal across arms so a per-arm score compares two implementations
rather than two catalogues", and that is correct for comparing **detection**. It
makes comparing **validation shape** impossible in the same table. Three epics'
worth of "the structure arrived and caught nothing" is, in part, this.

**What the next epic must do instead:** stop asking one catalogue to do both
jobs. Keep the same-semantic catalogue for detection. For validation shape,
define the mutant by **where it sits** — one fault per declared region on each
arm, accepting that the two arms' faults are different faults, and reporting the
pair as a *difference* the way `PA-M11`/`PA-M12` are. The goal's own metric ("the
count of comparable cells where the arms AGREE") is what encodes the
impossibility, so the metric moves with the catalogue. `PA-06-DF-08`.

### THING TWO THAT IS NOW IMPOSSIBLE: this card's D2 cannot exceed 2

All six PA-06 cards scored D2 = 2 and both judges gave the same reason
independently: anchor 3 requires *"a simplification was made and its effect
measured — the before and after figures are both recorded"*, and **a from-scratch
implementation of one spec has no before.** One judge stated it as a finding:
*"D2 contributed nothing to this comparison and will contribute nothing to the
next one under the same task design."*

`GOAL-simpler-same-behavior` missed for two epics and this is why. Either the
task changes (give the arms something to simplify) or the anchor does (bump
`scorecard_version`, keep the old anchors, re-score one prior example under both
— the procedure the card already prescribes).

### The instrument's controls are still the part that is lying, and it is worse than red

`M07` is red on twelve control/instrument pairs across three arms. The witness
each one carries — `294 accepting Reserve executed` — **is true and is not the
operative fact**: all 1,855 port-corpus cases compare an `after` of exactly
`{closed, committed, ledger}`, and `M07`'s observable is `available`. The columns
are blind by **projection**, not by reach.

And the repaired control is worse than red. `PA-M14` is measurably **unobservable
in one step** on three of the four trees it is declared on — only the arm that
*derives* `available()` shows it — and every corpus case is single-action, so it
**cannot be killed by any corpus** on the other three. **The probe that certifies
its property cannot fail**: a mutant that replaces a line with itself plus a
comment reports `HOLDS`.

`PA-01-DF-05`'s subject is that nothing ever checked a positive control against
the property that makes it one. PA-01 built the check. **The check is one-sided**,
and the sealed prediction that watches it named this in advance as *"this epic's
worst possible own goal"*. `PA-06-DF-07`, severity blocking. **Fix the probe
before citing any control anywhere: invisible before an accepted reserve AND
observable after one, on the tree under test, in the number of steps the
instruments execute.**

### The port machinery is dominated by four lines and a hand-written suite

`PA-M12` — a fault inside a fake adapter — does die on a generated instrument,
for the first time in this project. **And no instrument in any of the three
8-instrument arm tables has a unique kill at all.** On every arm,
`corpus-action-bound` (the declared pre-binding world) kills exactly what
`corpus-port-swap` kills. And **`suite-fake` strictly dominates
`corpus-port-swap:fake`** — it kills everything that column kills plus `PA-M13`.

The measured "a fault behind a port stops hiding" is produced by the **four-line
`quota_ledger_fake.py` composition point** plus the **pre-existing hand-written
suite**. The `[ports.*]` binding machinery adds a strictly weaker instrument on
this fixture. Before building further on it, find out whether it is weaker
because of the projection (`PA-06-DF-09`) or weaker in principle.

### Two things about the scorecard the next round must decide before it scores

1. **Judging practice moves the top anchors, and nothing records it.** Four
   dimension-points moved on artifacts that did not change by a byte, between
   `EVAL-RERUN` and `PA-06`. The mechanism is in both judges' own words: they
   **seeded their own faults and ran them** instead of scoring the packet, which
   is what D1 anchor 4 and D4 anchor 4 actually require and which nothing
   mandates. **Make it a requirement and put it on the card**, or every
   cross-round delta is a delta in how hard the judge worked. `PA-06-DF-06`.
2. **The blinding leaks through `NOTES.md` and no sanitiser can close it.** An
   author asked to explain its design describes that design. Both PA-06 judges
   found it, both named the tension — *"the instruction to read `NOTES.md` in
   full is in tension with the instruction to be blind to arm"* — and both stated
   what their scores rested on instead. Either judge without the notes, or stop
   calling it blind on the dimensions the notes touch.

### Keep the channel ratio. It is the whole method.

**1 : 12 : 4 : 2.** One finding from re-running the suite, twelve from a fresh
adversarial agent, four from asking the judges what they REJECTED, two from
asking the blind author the same. **Eighteen of nineteen findings came from
asking an agent what it rejected or telling it to attack.**

The suite's one is worth noting because it is the first in four rounds — and it
fired at the measuring ticket's own helper, which is the right direction.


> **SUPERSEDED IN PART, 2026-08-04.** The static architecture scanners this
> charter plans repairs for — `scripts/analyze_architecture.py` and
> `scripts/architecture_reflexion.py`, `tla-spec-dev analyze architecture`, and
> the `architecture_scan` / `architecture_delta` model surface — were REMOVED by
> owner direction. Every finding below is still true; what changed is that the
> answer is not a repair. Read `references/architecture_advice.md` first: it
> carries the nine measured facts from this page forward as instructions to
> follow now and as the acceptance criteria any replacement must satisfy. The
> sections here remain the primary record of HOW each was measured — run
> directories, numbers, reproduction steps — which is why nothing below is
> edited.

You are starting a new epic. The previous one (`architectural-coherence`) was
**measured, not asserted**: EV-01 committed predictions before any dispatch,
EV-02 scored against them, two blind agents who had never seen the predictions
worked on sanitized fixtures, and the answer keys were enumerated by the owner
in advance. Read this before anything.

The rule that produced everything below: **a low or unflattering result is the
preferred outcome.** This epic exists in the shape it does because the
complexity-descriptor epic existed, and that one existed because a validation
agent was told exactly that and then found the suggested moves were confidently
wrong. Keep the standard.

---

## 0-AA. READ FIRST — AMENDED AGAIN AFTER `EVAL-RERUN` (2026-08-04)

**The `hexagonal-prompting` eval was repaired and re-run. Section 0-A below was
written from HP-06's numbers, and EVAL-RERUN overturns four of its statements.**
Each is marked in place there with an `EVAL-RERUN —` note. Full record:
`specs/results/scorecards/hexagonal-prompting-rerun/RESULTS.md`.

**The goal verdicts did not change: two `met`, one `missed`.** What changed is
what they rest on.

### The four overturned

1. **"The positive control is red and has been for two tickets. Fix this before
   anything else" — DONE, and it worked.** Parameter recovery went 0 of 588 →
   **4,028 of 4,028**, 294 accepted `Reserve` cases now execute, and the
   faithfully seeded control arm's M07 has **no `SURVIVED` cell**. Sealed
   prediction P05 flips FAIL → PASS.
2. **"The hand-written suite still beats the generator" — NO LONGER TRUE AS
   STATED, and the old number was partly an artifact.** The replacement negative
   control **survives the hand-written suite too**, so the 10-of-10 that set the
   bar rested on a catalogue with no mutant that suite could miss. On the
   repaired instrument the generated instruments **tie** the suite: 10 of 11 on
   the seeded catalogue and 11 of 15 / 10 of 15 on a fresh blind one, on both
   arms. **But the tie is an aggregate over six instruments — no single generated
   instrument gets past 7 against the suite's 10.** State all three clauses or
   none.
3. **"D2 as written cannot be scored above 2 by an A/B" — REPLICATED, and it now
   has a mechanism.** Four more independent judges rejected the owner amendment.
   The new reason is decisive: the mechanical block reports `mutable_state_count`
   8 vs 8 and `max_writers` 2 vs 2 — **exactly the figures the treatment arm's
   one real simplification would move** — and the block itself says they
   discriminate nothing. **Fix the card's D2 or declare it unreachable for an
   A/B; eight judges across two rounds is enough evidence.**
4. **"N01: the treatment arm's descriptor came out smaller" — DOES NOT
   REPLICATE.** HP-06 measured 123 production lines against 147; EVAL-RERUN
   measures **129 against 122**, the other way, from the *same two prompt files*.
   **A descriptor delta between one pair of artifacts is noise at this scale.**

### The three new facts that should shape the next epic

1. **The `NOT_DECIDABLE` mechanism is an unaudited suppression key.** The shipped
   driver decides it **before** consulting the mutated run, so it can convert a
   demonstrated kill into "not decidable" with `verified: true`, `green: true`
   and exit 0 — proved twice on live data — and a witness naming **an action that
   does not exist in the model** also "verifies", because the check reads
   `counts.get(key, 0)` and cannot distinguish a missing key from a measured
   zero. `scripts/kill_test.py`'s 19 `SUPPRESSION_KEYS` do not include it.
   **This applies to the sealed reference run too. Fix this before trusting any
   scoped control.**
2. **A control can be green and still not be a control.** The treatment arm's
   positive control was seeded as a declared broader-reach substitute; delete
   every `Reserve` case from the corpus — the exact regression the control exists
   to detect — and it **stays green**. A control needs a test that it fails, and
   this project has never run one. **Run the deletion probe on every control
   before citing it.**
3. **The answer key leaks into files blind roles are ALLOWED to read.**
   `examples/validation/ab/model/QuotaLedger.tla`'s header comment names six of
   the ten seeded mutants and where they are seeded; `model/spec_manifest.yaml`
   describes one verbatim and quotes prior scores. Two of a blind author's thirty
   mutants were therefore not independent evidence. **Move the model's prose and
   the manifest behind the forbidden list.**

### What the next epic should do first, revised

- **Audit the suppression path**, per new fact 1. Every `NOT_DECIDABLE` cell this
  project has ever published is currently unaudited.
- **Make every control prove it can fail**, per new fact 2. A deletion probe per
  control, run in the same pass, is cheap and this round shows it is decisive.
- **Fix `eval_scorecard.md`'s D2**, per overturned 3. It is now the only goal
  that has been missed twice on a target no A/B can hit.
- **Seed durability across a failing write.** Both rounds' blind authors named it
  as the class they were least confident about declining, and this round proves
  why: the two arms **differ in unmutated code** on the ordering of the durable
  write against the memory update, each argues for its choice in its notes, and
  **nothing in the fixture can price the difference.** The ported arm *could* be
  made to price it with a raising adapter; the control arm has no injection seam
  at all. **That is the only measurable consequence of the architectural variable
  this A/B is varying, and it is unmeasured.**
- **Still do NOT build an architecture checker**, and now for a second reason:
  the prompt reached D3 = 4 twice with no tool, **and 56 of 56 comparable kill
  cells were identical between the arms both times.** The structure is real and
  it detects nothing.
- **Run the third arm or stop claiming the win is about hexagonality.** 16 unique
  prompt lines against 105 — 6.6x — recomputed and unchanged. Two rounds, two
  D3 = 4s, zero evidence separating "hexagonal" from "longer and more specific".

### The channel ratio, fourth round running

**0 : 15 : 19** — suite re-run, adversarial attack, blind author. The suite
produced nothing again, and for the fourth time the most valuable single section
of the record was an agent's answer to *"what did you reject?"*.

**One counter-example, and it is the first in three rounds.** The hand-written
suite **as a kill-table instrument** caught this round's first defect: a stale
module reference that made all eleven mutants execute against pristine code and
report SURVIVED. Six generated instruments missed it; a green positive control
missed it; **the disagreement between the hand-written column and the generated
columns caught it.** Keep a hand-written instrument in every kill table for that
reason alone.

---

## 0-A. READ FIRST — AMENDED AGAIN AFTER THE `hexagonal-prompting` EPIC (2026-08-04)

**Everything below §0 was written by the `architectural-coherence` epic. A newer
epic has since run and has OVERTURNED four of its conclusions.** Every one is
marked in place with a `HEXAGONAL-PROMPTING —` note; do not read a §1 or §3 claim
without checking whether it carries one. The four:

1. **"A generated corpus cannot see guard relaxation, ever" is FALSE** (§1). A
   generator mode that emits, per reachable state, the actions whose guards are
   DISABLED, asserted REJECTED, took the class **0 of 3 → 3 of 3** on the seeded
   catalogue, **5 of 5** on one fresh catalogue and **1 of 1** on another, on two
   real implementations. It was never a property of corpora; it was a property of
   *positive* corpora.
2. **"Ordering is invisible at every layer" is FALSE as stated** (§1). It is
   invisible when the modelled thing is a **set**. On a model whose ledger is a
   **sequence**, the ordering mutant dies on the whole-view corpus, on an aspect
   slice and under both provider mappings. Any citation now needs the
   set/sequence clause.
3. **"The mapping choice is worth 30% of that instrument's yield" MUST NOT BE
   QUOTED** (§1, §3). The *direction* has replicated five times on five fixtures
   and is solid. The *magnitude* has failed to reproduce four times: 1 of 6 on
   one fixture, **exactly one mutant** on each of two implementations here.
4. **D3 = 4 has been reached** — the first 4 on any dimension but D5 in this
   project's history — by asking for ports and adapters **in a prompt**, with no
   check, no schema and no gate. §2's NE-02 should be read knowing that.

**And the four sentences from the new round that matter most:**

1. **The prompt worked and the structure caught nothing.** D3 went 2/2 → 4/4
   between the control and the treatment arm. Every per-mutant kill verdict is
   **identical on 49 of 49 comparable cells**. A port did not detect one
   additional fault, and the treatment arm's own 41 tests appear in no kill
   table. If you are tempted to build architecture tooling because "modularity
   catches bugs", this round is the counter-evidence.
2. **The hand-written suite still beats the generator, and a catalogue nobody
   tuned beats them both down.** *(**EVAL-RERUN — OVERTURNED IN PART**: the
   corpora now TIE the suite, 10 of 11 on the seeded catalogue and 11 of 15 /
   10 of 15 on a fresh blind one, on both arms — but no single generated
   instrument gets past 7 against the suite's 10, and the old 10-of-10 was partly
   an artifact of a catalogue containing no mutant the suite could miss. See
   §0-AA.)* Seeded catalogue: suite 10 of 10, corpora 9 of
   10. **Fresh independently-authored catalogue: corpora 8 of 13, suite 9 of 13,
   and four whole classes invisible to every instrument including the suite.**
   A catalogue written by the author of the mechanisms flatters both instruments
   by roughly a quarter.
3. **The positive control is red and has been for two tickets.** *(**EVAL-RERUN
   — FIXED**: recovery 0 of 588 → 4,028 of 4,028, and the faithfully seeded arm's
   control has no SURVIVED cell. But a control can be green and still not be a
   control — see §0-AA new fact 2.)* The corpus
   recovers no `Reserve` argument, so no case that calls the primary command
   executes, so a fault seeded in it survives everything. **Fix this before
   anything else** — and know that fixing it turns a *second* control red
   (HP-06-DF-11), because the oracle re-derives a reservation id the model does
   not allocate that way.
4. **Findings by channel: 0 from the suite, 17 from an adversarial pass, 13 from
   a blind author.** Third round running. *(**EVAL-RERUN**: 0 : 15 : 19, fourth
   round running — with the first counter-example in three rounds. See §0-AA.)* **The suite has stopped being
   informative** — 1,329 green assertions produced nothing anybody did not
   already know — and for the third time the most valuable single section of the
   record was an agent's answer to *"what did you reject?"*.

### The best finding of the new round is about a SPECIFICATION, not a tool

A blind author, given only the two implementations and the model, found that
**the model's COMMIT record has three fields where the feature's has four**. R2's
running-total clause is absent from the state machine entirely, and the
manifest's own port description describes a line the model never constructs. The
one mechanism with a measured, replicated edge — the content-asserting provider —
is a hand-written sentence patching a model that does not refine its own
specification.

The same agent found that the two arms **differ in unmutated code on crash
consistency** and that nothing in the fixture can see it; that the fixture
**leaks its own answer key** in files blind roles are permitted to read; and that
two whole fault classes are each held by exactly one assertion.

That is the fourth epic in a row in which the most valuable result came from an
agent READING something and noticing a specification was false of itself. No
metric contains it and no gate reaches it. **Budget for that channel explicitly.**

### What the next epic should probably do first

- **Repair `Reserve` argument recovery, then expect HP-06-DF-11 to fire.** Until
  the positive control is green, no kill number from a whole-view corpus on this
  fixture is a measurement.
- **Make a kill table auditable.** `KILLED` currently means "any exception", the
  failure text for every mutant run is computed and discarded, and 92% of a
  corpus is skipped with the per-case reason dropped. Every kill table this
  project has published shares that driver's ancestry.
- **Do NOT build an architecture checker.** The prompt reached D3 = 4 with no
  tool, and the epic before it proved every static check it shipped was defeated
  cheaply. But do not conclude the prompt "worked" either: 105 unique prompt
  lines against 16 means **this round cannot distinguish hexagonal guidance from
  a longer, more specific ask.** If that distinction matters, run the third arm.
- **Fix `eval_scorecard.md`'s D2, or say it is unreachable for an A/B.**
  *(**EVAL-RERUN — REPLICATED** on four more judges, with a mechanism: the
  mechanical block cannot see the one simplification either arm made.)* Anchor 3
  needs a before and an after of the same artifact; two arms of one specification
  have neither, all four judges said so, and a goal was `missed` on a target no
  A/B could have hit.
- **Seed the class the blind author was least confident about rejecting**:
  durability across a failing write. It said, in the shape of the predecessor's
  wrong rejection, *"I am declining a class because the harness cannot currently
  reach it, not because the fault is unreal"* — and then proved the arms already
  diverge on it.

Full record: `specs/results/scorecards/hexagonal-prompting/RESULTS.md`,
`PREDICTIONS-SCORED.md` (7 PASS, 4 FAIL, and three of the four failures are
negative predictions), `FINDINGS.md`, `UNBLINDING.md`.

---

## 0. READ FIRST — this document was written after round 1 and amended after round 2

EV-02 (round 1) found 14 defects. The owner directed that they be **repaired
inside the epic** rather than deferred here, and six repair tickets landed
(RP-01..RP-05, RP-07). **EV-03 (round 2) then re-ran the whole eval suite against
the repaired tree and re-scored it against the SAME committed predictions**, with
two fresh blind runs on fresh scratch copies. The full comparison is
`examples/validation/runs/ROUND-2-DELTA.md`; the per-arm records are
`runs/ex4-run4..6`, `runs/ex5-run3..4`, `runs/ex6-run2`.

**Several conclusions below were written by round 1 and OVERTURNED by round 2.**
Every one is marked in place with a `ROUND 2:` note. Do not read a §1 or §3 claim
without checking whether it carries one.

The four sentences that matter most:

1. **The false `coherent` is fixed on the declaration path, exhaustively.** All
   203 partitions of the divergent fixture: **12 false cleans → 0**, with **zero
   divergence verdicts lost** and **20 previously-suppressed findings released**.
   The one-component partition that was round 1's headline now reports
   `unmappable` with both basis limits named.
2. **The bug-catching numbers did not move by a single cell.** ARM A 4 of 6, ARM
   B 6 of 6, guard relaxation 0 of 3, ordering 0 of 3 — identical to round 1,
   after a repair that took parameter recovery from 0 of 5 to **5 of 5**. The
   repair worked; the kill rate did not change. **That falsifies round 1's own
   explanation of why guard relaxation is unkillable** (see §1's corrected
   bullet).
3. **Case modules went from "generate" to "generate and run", and that is the one
   place a new detection capability actually appeared.** A blind agent's two
   authored aspects — 89 lines, 74 cases — killed **9 of 16** mutants against the
   330-case whole view's 10 of 16. It is a cost result, not a reach result: the
   bugs are ones the view already caught.
4. **A blind agent found a NEW major defect cheaper than anything round 1 knew
   about**, and the scorer reproduced it independently: `coherent` on a codebase
   with four real divergences, for a 41-line re-export file, with both digests
   unchanged, `blind_spots: []`, `basis_limits: []` and the behavioural suite
   green. **EV-03-DF-03.** It is the strongest argument that NE-02 is the next
   epic's real work, and it is a false clean the epic's own DP-1 scoring rule
   cannot see.

---

## 1. What the last epic learned (do not re-litigate)

`architectural-coherence` shipped four levers: an architecture **descriptor**
(AC-01), a **reflexion check** of code against the model's architecture
(AC-02), an **implementation brief** (AC-03), and an attributable **refactor
delta** (AC-04) — plus case modules (CM-01) and the eval fixtures (EV-01/EV-02).
Every claim below is a measurement with a run record behind it in
`examples/validation/runs/`.

### Survived, and is reliable

- **The divergence check is accurate when its basis is honest.** On the
  enumerated answer key: **precision 1.000, recall 1.000** — all four seeded
  divergences at the exact `file:line`, plus the one absence, plus **zero false
  positives on the coherent twin**. A check that finds divergence everywhere is
  as useless as one that finds it nowhere; this one does neither.
  (`runs/ex5-run1/`)
  **ROUND 2: reproduces exactly — same four `file:line`, same absence, zero false
  positives on the twin (`runs/ex5-run3/`). AND it is now known to be accuracy
  ON AN UNATTACKED TREE ONLY.** A 41-line re-export file through a nested
  first-party package takes the same fixture from `divergent` to `coherent` with
  both digests unchanged and no blind spot (EV-03-DF-03, `runs/ex5-run4/`).
  Never quote 1.000 without that clause again.
- **The refusals hold on real targets.** This repository's own model reports one
  component, Q = 0.000, `unmappable`, and single-writer ownership **NOT
  MEASURABLE** rather than "zero violations". The synthetic Jenga reports
  `unmappable` via `unfalsifiable_coherence`. Both exit 0. (`runs/ex6-run1/`)
  **ROUND 2: holds, and both refusals now name the decomposition basis too
  (`runs/ex6-run2/`). Newly measured: this repository's own DECLARED
  four-component partition does NOT decompose its own model (Q = −0.025,
  crossing 0.6), so `coherent` is not a verdict this repository could earn today
  even with a perfect extractor. The AC-02 note in `ticket_plan.yaml` still says
  otherwise — EV-03-DF-01.**
- **AC-04's delta cannot be gamed, and this was attacked directly.** Against
  the maximal gaming move — collapse the whole partition to one component and
  re-place all eight modules — it reports `direction = unattributable`, names
  every re-placed module, classifies each lost edge `endpoint_reassigned` ("the
  edge did not go away; the boundary it crossed did"), and reports **stable
  basis 0 → 0**. DP-7 predicted the refusal would hold. It holds.
  (`runs/ex5-run2/`)
- **Content-asserting effect providers catch what nothing else catches.**
  Per fault class, per arm, green control both arms:
  **ARM A (corpus alone) 4 of 6; ARM B (corpus + content provider) 6 of 6.**
  The two survivors under ARM A are exactly the two durable-side faults, killed
  under ARM B by `provider_content_assertion` and by nothing else.
  (`runs/ex4-run1/`)
  **ROUND 2: identical, cell for cell, detector for detector, point count for
  point count (`runs/ex4-run4/`). Independently replicated a third time by a
  blind agent on a fresh 16-mutant catalogue: 3 of 3 durable-write mutants killed
  by the checking mapping, 0 of 3 by the silent one — 30% of that instrument's
  entire yield (`runs/ex4-run6/`).**
  **HEXAGONAL-PROMPTING — THE 30% DOES NOT REPRODUCE AS A PROPORTION. DO NOT
  QUOTE IT.** HP-05 measured the mapping worth 1 of 6 under the checking mapping
  and 1 of 10 overall on a second fixture; HP-06 measured it worth **exactly one
  mutant on each of two further implementations** (`map-checking` 2 of 2,
  `map-silent` 1 of 2, plain corpus 1 of 2, identical on both arms). The
  DIRECTION has now replicated five times on five fixtures and is solid. The
  MAGNITUDE is fixture-dependent and is not a property of the mechanism.
- **Determinism, including the half nobody had tested.** Generation is
  byte-identical (the same `cases.py` sha256 EV-01 recorded, across worktrees,
  output paths, and two Python interpreters five minor versions apart).
  Execution is byte-identical across two independently generated corpora over
  **14 executions including twelve FAILING ones** — a corpus deterministic only
  when it passes is not a deterministic corpus. Seeded failures **replay
  exactly** from the command the runner prints: three faults, both arms, each
  replayed twice, all six reproducing the originating error string.
  (`runs/ex4-run2/`)
  **ROUND 2: 38 of 38 executions byte-identical, 24 of them failing ones, plus
  the case-module corpora which round 1 could not even generate in place
  (`runs/ex4-run5/`). The corpus fingerprint MOVED, from `33e07e0de…` to
  `944189052623960aea…` — that is RP-02's recorded content change, not a
  determinism failure, and the fixture's `evidence/corpus_fingerprint.txt`
  carries both with the reason.**
- **Case modules generate, and the tool refuses to oversell them.** 14 authored
  lines → 50 cases; 22 authored lines → 6; the view is 330; and `coverage`
  states unprompted, every run, that the union of aspects is not the view.
  (`runs/ex4-run1/`)
  **ROUND 2: they now also RUN. RP-03 made the checked-in modules generate in
  place (round 1: exit 150) and fixed parameter recovery across `EXTENDS`, which
  round 1 never reached — the slice went 0/50 → 50/50 arguments and the Given
  0/6 → 6/6, and the Given's corpus executes against the project's unchanged
  adapters. A blind agent then used two authored aspects as real instruments and
  measured 9 of 16 mutants from 74 cases (`runs/ex4-run4/`, `runs/ex4-run6/`).**

### Killed, or badly wounded

- **`coherent` can be obtained on a divergent codebase, for about six lines of
  YAML, and nothing flags it.** Enumerating all 203 set partitions of the
  divergent fixture's variables: 12 report `coherent`, and **all 12 fail the
  model's own decomposition criteria while zero of the 12 honest partitions
  produce a clean.** The criteria are a perfect discriminator and the reflexion
  check does not consult them. Worse, the **fully degenerate case is not
  caught**: a declared ONE-component partition on a codebase with four real
  divergences reports `coherent`, exit 0, `blind_spots: []` — because the
  `unfalsifiable_coherence` guard is written `len(names) >= 2` and excludes the
  one blob it exists for. `divergence_detectable` is computed as `false` and no
  consumer reads it. **EV-02-DF-01.** (`runs/ex5-run2/`, `runs/ex6-run1/`)
  **ROUND 2 — FIXED BY RP-01, AND MEASURED ON THE SAME INSTRUMENT. The sweep
  rerun: 12 false cleans → 0, all 203 exit 0, and — the part that had to be
  checked — ZERO divergence verdicts were lost and 20 previously-suppressed
  findings were released (71 → 91 `divergent`).** The mechanism is a
  `basis_limits` list (seen in full, clean withheld) kept SEPARATE from
  `blind_spots` (could not see); verified independently, 67 of round 1's 71
  divergence verdicts carry `partition_does_not_decompose`, so folding the two
  together would have suppressed 67 real findings to remove the same 12 false
  cleans. **DP-2 re-scored MISSED → CAUGHT; DP-2b CONFIRMED → CLOSED on the
  measured path.** (`runs/ex5-run3/`) **This closes the DECLARATION route to a
  false clean. It does not close the CODE route — see EV-03-DF-03 below.**
- **The mitigation already exists and lives in the wrong artifact.** AC-03's
  `prompts/implementation_brief.md` documents this exact defect by name and adds
  Gate B: `V1` refuses a 1-component declared partition, `V3` degrades on
  `crossing_action_fraction > 0.5`. AC-03 is a **prompt**; AC-02 is a
  **program**. The check a human must remember is enforced; the check a program
  could enforce is not. Part of EV-02-DF-01.
  **ROUND 2 — FIXED. The basis now travels with the verdict in both the text and
  the JSON (`basis.partition_decomposes`, `partition_criteria`,
  `partition_failed_criteria`, `clean_result_supportable`,
  `unsupported_clean_reasons`). Round 1 measured that the word "decompose"
  appeared zero times in the reflexion output; it now appears with every
  criterion and its measurement. NE-01(3) was honoured: the declared partition is
  never REFUSED — the comparison runs, findings keep their `file:line`, exit stays
  0, and what is withheld is only the word `coherent`.**
- **The reflexion check measures static import topology, not interaction.**
  Found by the blind agent, verified: the seeded absence proves it from one side
  — `dispatch` and `ledger` interacted the whole time via a parameter, and with
  no import the tool called it dead architecture. In reverse, pass a function as
  an argument or annotate a type as a string and the divergence vanishes while
  the coupling survives. **Nothing in the tool distinguishes a real refactor
  from that dodge.** (`runs/ex5-run1/`)
  **ROUND 2 — NOT FIXED, and now much worse than round 1 understood. This epic
  touched none of it, which was the plan. What round 2 added is the price: a
  blind agent, told only to make the report clean, found that
  `architecture_reflexion.py` decides first-party-outside-`--code` by testing ONE
  path (`code_root.parent / name`), so a first-party package nested at
  `generated/pkg`, `src/pkg` or `vendor/pkg` is silently filed as third-party.
  Consequences, both reproduced independently by the scorer: (a) moving
  `pipeline_contract` up one directory on the COHERENT fixture, changing zero
  bytes of Python, flips `coherent` → `unmappable` — so this epic's only positive
  architecture result is conditional on directory depth; (b) a 41-line re-export
  shim plus one decorative import turns the DIVERGENT fixture into `coherent`,
  0 divergences, 0 absences, `blind_spots: []`, `basis_limits: []`,
  `clean_result_supportable: true`, both digests identical to the answer key,
  8/8 behavioural tests green, runtime coupling fully intact.
  **EV-03-DF-03, major.** DP-1's scoring rule cannot see it: no declaration
  moved. This is NE-02's whole case, made concrete.**
- **Anything outside `--code` is free.** Push cross-component wiring into an
  unscanned composition root and the codebase reads coherent by construction; a
  DI-heavy service passes trivially. The blind run demonstrated this **in its
  own fix** — it edited `tests/driver.py`, outside the scanned root, invisible
  to the check that then scored it clean. The adjacent tricks *are* guarded
  (unmapped modules force `unmappable`; suppression-shaped map keys are reported
  and never honored). Scoping is not.
  **ROUND 2 — NOT FIXED, and the hazard is wider than "scoping". Round 1 recorded
  it as `--code` being POINTED somewhere convenient. EV-03-DF-03 shows the same
  hazard reachable with `--code` unchanged, by ADDING A FILE. Round 2's blind
  agent also edited `tests/driver.py` — outside the scanned root — exactly as
  round 1's did, so that half replicates too.**
- **A generated corpus cannot see guard relaxation, ever.** It replays only
  ENABLED edges, so it contains no rejected inputs: a service that accepts what
  the model forbids passes every case. Compounded by the adapter recovering the
  action argument from the case's after-state — the oracle hands it the
  argument. Found independently by the blind agent (0 of 3 guard mutants) and
  by EV-01 as DF-01. **This is why "4 of 6 beats MF-038's 0 of 9" is an upper
  bound and must never be quoted without it.**
  **ROUND 2 — THE CLAUSE ABOUT THE ADAPTER IS FALSE AND IS RETRACTED.** RP-02
  removed the oracle leakage completely: parameter recovery went **0 of 5 → 5 of
  5**, all 330 cases carry a real argument, and the adapter reads
  `case.input.params` and never touches `case.after`. **Guard relaxation stayed
  at 0 of 3.** Not one cell of the mutant matrix moved, on either arm, on either
  catalogue. RP-02 counted the reason: all 330 recovered arguments are arguments
  the guard ACCEPTS, 0 are rejected inputs, and 220 refusable pairs exist in the
  state space that a TLC state graph can never emit. **So the oracle leak was
  real, is gone, and was NEVER what made guard relaxation unkillable — the whole
  of the remaining failure is the structural half.** Independently replicated a
  third time by a blind agent on a fresh catalogue: **0 of 4 guard-accepts on all
  five corpus instruments, 4 of 4 on the hand-written suite**, with the mechanism
  found from scratch (`330 'status': 'applied'` — the corpus never once asks the
  program to reject a call). (`runs/ex4-run4/`, `runs/ex4-run6/`)
  The "4 of 6 is an upper bound" caveat is now **narrower**: the leak is gone, so
  4 of 6 is a measurement rather than a ceiling. It remains one fixture, six
  faults, and a corpus that cannot see two whole classes.
  **HEXAGONAL-PROMPTING — OVERTURNED. THE HEADLINE OF THIS BULLET IS NOW FALSE.**
  "A generated corpus cannot see guard relaxation, ever" was true of a corpus
  built from ENABLED edges only. HP-03 built a generator mode that emits, at each
  reachable state, the actions whose guards are DISABLED there, asserted
  REJECTED. Guard relaxation went **0 of 3 -> 3 of 3** on HP-01's seeded
  catalogue and **5 of 5** on a fresh independent one, and HP-06 reproduced
  **3 of 3 under `corpus-neg` on two real implementations**, against 0 of 3 for
  every other generated instrument in the same run. The class is not structurally
  unreachable; it was unreachable *from a positive corpus*. The rest of the
  bullet — that recovering the argument does nothing, that the state graph has no
  edge for a transition that did not fire — is still exactly right, and is why
  the fix had to be a new emission mode rather than better recovery.
- **Ordering is invisible at every layer.** `ledger` and `queue` are TLA+ sets;
  the code implements them as ordered lists documented "append-only". The
  projector sorts, the adapter uses `frozenset`, the provider compares
  `sorted()`. A ledger that silently reverses is undetectable by any of the
  three. **Modeling gap, not a tool bug — and no case module can fix it.**
  **ROUND 2 — NOT FIXED, confirmed again, and now confirmed to be invisible to
  the HAND-WRITTEN SUITE as well.** Round 1's blind catalogue: 0 of 3 ordering
  mutants killed by the corpus. Round 2's blind catalogue: **0 of 2 killed by
  ANYTHING — five corpus instruments and the behavioural suite.** The agent
  traced all four layers unprompted and reached round 1's conclusion
  independently: it needs a MODEL change, not a test change. (`runs/ex4-run6/`)
  **HEXAGONAL-PROMPTING — OVERTURNED, AND THE CORRECTED CLAIM IS NARROWER.**
  "Ordering is invisible at every layer" is a property of THIS MODEL, not of
  corpora. It is invisible when the modelled thing is a **set**; `ledger` and
  `queue` here are sets, which is the whole of the reason. On a model that
  represents its ledger as a **sequence**, HP-03's ordering mutant M09 DIED on
  the whole-view corpus, and HP-06 reproduced that on both arms — killed by
  `corpus-whole`, by the ledger aspect slice and by both provider mappings,
  surviving only the negative corpus and the reservations slice, neither of which
  projects the ledger. **Anything citing "ordering is structurally invisible" now
  needs the set/sequence clause.** The second half of round 2's note also stands
  corrected: on a sequence model the hand-written suite kills it easily.
- **X-P3 fails.** Six of eight friction items in the blind aspect run were
  documentation insufficiency, not tool defects, and the root of most of them is
  that **every published command path assumes an external view**. An
  internal-only project has no worked example anywhere in the repo.
  **EV-02-DF-05.** And a checked-in case module **cannot be generated from where
  the convention puts it** (TLC cwd, no module search path, exit 150):
  the shipped convention and the shipped tool disagree. **EV-02-DF-02.**
  **ROUND 2 — EV-02-DF-02 IS CLOSED** (generation resolves the `EXTENDS` closure
  and hands SANY the directories it found; the checked-in modules regenerate in
  place with byte-equal output, and the diagnosis for an unresolvable `EXTENDS`
  is one sentence before the JVM starts). **The internal-view worked example
  exists and runs verbatim end to end. EV-02-DF-05 is PARTLY CLOSED: the
  external-view assumption and the `--out` / `--import-root` frictions are fixed;
  NO INTERPRETER IS PINNED ANYWHERE, and no `python3` on the eval machine's PATH
  carries `yaml`, `pytest` and `tomllib` together — hit again by both round-2
  blind agents. X-P3 still FAILS, with 8 items again — but four of round 1's
  eight are gone and the round-2 items are different ones, including two new
  toolchain defects: `--effect-report PATH` silently writes nothing and exits 0
  (EV-03-DF-04), and `analyze architecture` without `--components` silently
  substitutes an emergent partition for the declared one (EV-03-DF-05).**
- **"A non-author can write an aspect" holds for SLICES and fails for GIVENS.**
  A slice needs action names; a Given must constrain every variable of the view
  and know every guard. The Given is the form with the **best** measured
  result — see below — so the mechanism with the strongest number is precisely
  the one that cannot be written from outside, and no document says so.
  **EV-02-DF-04.**
  **ROUND 2 — DOCUMENTED, not "fixed", because the asymmetry is a FACT and not a
  defect.** `references/case_modules.md` now states it as a table of what each
  form requires and where that knowledge lives, and names the split that makes a
  Given commissionable from outside (the outsider supplies the CLAIM, someone
  with the model writes the predicate). Round 2's blind agent followed exactly
  that split unprompted and said so in its report. Step 0's provenance
  requirement is now LABELLED UNENFORCEABLE with a contract in place of a guard —
  and the round-2 agent opened its report with "No author was in the loop… **This
  decomposition is UNREVIEWED**" before quoting a single number. That is the
  contract working. It is still not a control: `case_modules.py validate` exits 0
  on an authorless decomposition without a murmur. (`runs/ex4-run6/`)
- **CM-F5 — a slice narrower than its view orphans the view's effect providers.
  STILL OPEN, and sharper than RP-03 filed it.** The runner refuses a mapping
  that configures an effect provider no selected case requires. On a whole view
  that is correct; on a slice it is normal, because slicing is what makes an
  aspect narrower. RP-03 said the workaround is "a second mapping file with the
  provider removed" — **but the fixture SHIPS two mappings and both bind the
  port, so the slice has ZERO working configurations and the workaround requires
  a third file that exists nowhere.** Round 2's blind agent hit this without
  knowing it existed, lost 3 of its 15 actions to it, authored the third mapping,
  and made the point nobody else had: **that mapping is a strictly weaker
  instrument** — it has no durable-write oracle, so its slice's kills are a floor
  and a green slice run over-reads unless you read its mapping.
  **So the cheapest outside-in artifact — a slice, the only form writable from
  action names alone — is still the one that cannot run end to end, and the form
  that runs is the one that cannot be written from outside.** EV-03-DF-02.

### Scored against the committed predictions

| prediction | outcome |
|---|---|
| prediction | round 1 | ROUND 2 |
|---|---|---|
| A1-P1..P6 (kill table, per class per arm) | **all PASS**, every per-fault prediction exact | **all PASS, identical numbers** |
| A1-P7 (the wrong-item class is unmeasurable) | stated as a limit | **SUPERSEDED by RP-02** — it was killable all along, before the fix as well as after |
| A2-P1..P3 | PASS | **PASS**, and A2-P3 completed: a module corpus now EXECUTES |
| A2-P4 (aspects not derivable) | PASS, sharpened | **PASS**, and the artifact now carries the caveat |
| A3-P1..P4 (determinism, replay) | **all PASS** | **all PASS**, 38 executions vs 14 |
| AC-P1..P6 (answer keys, refusals, exit 0) | **all PASS** | **all PASS**, unchanged |
| DP-1 (agent redraws the map) | **PASS at n=1** | **PASS at n=1 again** — both digests at answer-key values, 0 deletions — **and the rule is now known not to catch the cheapest attack (EV-03-DF-03)** |
| DP-2 (`unfalsifiable_coherence` catches the degenerate case) | **MISSED** | **CAUGHT** |
| DP-2b (declared partition failing all criteria reports a real-looking clean) | **CONFIRMED**, 12 of 203 | **CLOSED on the measured path**, 0 of 203 |
| DP-3, DP-5, DP-6, DP-7, DP-8 | **PASS** | **PASS** (DP-7 not re-exercised — no `--baseline` delta was taken in round 2) |
| X-P1, X-P2, X-P4 | **PASS** | **PASS** |
| X-P3 (docs suffice) | **FAIL**, 6 of 8 items | **FAIL**, 8 items again — 4 of round 1's 8 are gone, the round-2 items are different ones |

**The DP-1 honesty note.** DP-1 predicted that at least one run would redraw the
map rather than fix the code. One blind run was dispatched; it did not — all
four declarations byte-identical, only production code moved, recall 1.0 on the
answer key, unprompted. That is a real result and it is **n = 1**. DP-1
predicted a rate, and one honest agent is evidence about one agent under one
prompt. Recording it as "DP-1 disproved" would be exactly the overclaim this
epic was built to avoid. Two things must travel with the PASS: **three of the
four divergences were cleared by DELETING dead code, and the metric cannot tell
deletion from refactoring**; and the agent's own report says the cheapest way to
get clean was **editing the model**, which it declined on judgment, not because
anything stopped it.

**ROUND 2's DP-1 note.** A second blind agent, on a differently sanitized copy,
also chose the code. Both declarations byte-identical, both digests at the
answer-key values, `tests/test_behavior.py` untouched, recall 1.0 unprompted,
8/8 green. **Better than round 1 on attribution: zero deletions.** It considered
deleting the three uncalled helpers as the fastest clean and rejected it in
writing ("it makes the check pass by deleting the subject rather than by fixing
it"), then removed each cross-boundary dependency while preserving every
helper's output byte-for-byte. **n = 2, and DP-1 predicted a RATE — still not
falsified.**

And the part that matters more than the PASS: **the agent tested three dishonest
routes and reported them instead of taking one.** One of the three works, is
cheaper than the honest fix, is invisible to the map a reviewer reads, and is
invisible to DP-1's own scoring rule. That is EV-03-DF-03. **The centrepiece
experiment's value in round 2 was not the verdict; it was the report.**

### The finding worth more than any mechanism this epic shipped

Working from the public README alone, the blind aspect author found that
**the public surface is false of the model**:

```
Fail(i)   ==  i \in delivered  /\  delivered' = delivered \ {i}  /\  failed' = failed \cup {i}
Record(i) ==  i \in delivered  /\  i \notin ledger  /\  ledger' = ledger \cup {i}
```

Once an item fails it leaves `delivered`, so it can **never** reach the ledger —
while the README promises "a failed item is recorded as failed" and "the ledger
records each outcome", and the model's own `LedgerIsDownstream` invariant
reserves room for exactly the behavior the model then makes unreachable.

**No case module could ever catch this.** A case module may not add an action,
and there is no action to enter; a corpus can only test behavior the model has.
**The value came from the human-facing act of authoring the aspect, not from the
cases it generated.**

This is the one result in the epic that no prediction contains and no metric
measures. It is the strongest available argument for the manual-test-starter
path **and its strength is not expressible as a kill rate.** Whatever the next
epic builds, it must not optimize the aspect surface for kills and lose this.

**ROUND 2: IT REPLICATES.** A second blind agent, on a differently sanitized
copy, found the same contradiction from the README alone — and added three facts
round 1 did not have: (1) `LedgerIsDownstream` permits a state no action can
reach, so the real invariant is strictly stronger and the written one passes
vacuously on the half that matters; (2) the behavioural suite asserts the same
weak property and therefore cannot fail; (3) `test_two_item_interleaving`
asserts the **negation** of the README sentence, so whoever fixes the promise
must change a passing test. **A result that reproduces across two agents, two
sanitizations and two rounds is not an anecdote.** (`runs/ex4-run6/`)

---

## 2. What the next epic should build

Four pieces, in dependency order. Each one is a fix for something above that was
**measured**, not for something that sounds wrong.

**ROUND 2 STATUS OF NE-01..NE-04, up front:**

| | round-1 charter | status after the repair tickets + EV-03 |
|---|---|---|
| **NE-01** put the basis in the report | the highest-severity finding | **DONE by RP-01**, acceptance met exactly (12 → 0 over 203, 0 findings lost, 20 released). **Remove it from the charter.** |
| **NE-02** measure interaction, not imports | the real work | **UNTOUCHED, and now the top priority** — EV-03-DF-03 gives it the negative fixture it was told to build first, already built |
| **NE-03** the oracle's blind spots | guard relaxation, ordering, parameter recovery | **parameter recovery DONE by RP-02 — and it changed no kill.** Guards and ordering untouched, and both re-confirmed from outside |
| **NE-04** the aspect surface as a design review | docs, an authoring aid, fix DF-02 first | **DF-02 DONE by RP-03**, the asymmetry and Step 0 documented, case-module corpora now EXECUTE. **CM-F5 is the remaining blocker** |

### NE-01 — DONE by RP-01. Do not re-open. *(round-1 text kept for the record)*

~~The highest-severity finding, and the cheapest fix in the epic.~~ **RP-01
landed all three changes and EV-03 measured the acceptance criterion on the
instrument that found the defect: the 203-partition sweep reports 0 `coherent`,
zero divergence verdicts were lost, and 20 previously-suppressed findings were
released. The one thing to carry forward is the design decision RP-01 made and
measured: the refusal is a BASIS LIMIT (withholds a clean, never a finding),
kept separate from a BLIND SPOT (could not see) — filing it as a blind spot
would have suppressed 67 of 71 real divergence verdicts to remove the same 12
false cleans. Keep that distinction; it is load-bearing.** Three changes, all
additive, none of which lets the tool choose a boundary (CD-01 removed
that, permanently):

1. **Delete the `len(names) >= 2` clause** in
   `architecture_reflexion.py:921`. A one-component declared partition is the
   *strongest* case of `unfalsifiable_coherence`, not an exception to it.
   `divergence_detectable == false` must force `unmappable` on its own instead
   of being computed, reported in JSON, and ignored by the verdict.
2. **Move AC-03's Gate B from the prompt into the program.** Carry
   `partition.decomposes`, the failed criteria, and the V1/V3 tests into the
   reflexion text report and into `basis.partition_decomposes` in the JSON.
   `coherent` measured against a partition the model does not support is a
   different claim from `coherent` measured against one it does, and the report
   must say which it is.
3. **Do NOT refuse a declared non-decomposing partition.** Carry the fact, not
   the judgment. A project may have good reasons for a boundary the modularity
   metric dislikes; it may not have them silently.

Acceptance: re-run `runs/ex5-run2/artifacts/df02_blast.py`. The 12 false cleans
must become 0 `coherent` — as `unmappable` or as `coherent (basis: does not
decompose)`, the epic's choice, but never as an unqualified clean.
**MET. The rerun is `runs/ex5-run3/artifacts/df02_blast_round2.py`, and its
output is `runs/ex5-run3/artifacts/blast.json`.**

### NE-02 — measure interaction, not imports. **NOW THE TOP PRIORITY.**

The check's accuracy (precision 1.000, recall 1.000) is real **and is entirely
about static import topology**. **ROUND 2 raised this from "the next epic should
decide" to "the next epic must fix this first", because a fourth evasion was
found, it is cheaper than the other three, and it is invisible to every scoring
rule this epic wrote:**

- **THE ONE TO FIX FIRST — a re-export through a nested first-party package
  (EV-03-DF-03).** `architecture_reflexion.py` decides first-party-outside-
  `--code` by testing exactly one path, `code_root.parent / name`. A package at
  `generated/pkg`, `src/pkg`, `gen/pkg` or `vendor/pkg` is one level too deep and
  is silently filed as third-party. Measured both ways: moving the fixture's
  generated package up one directory, with zero Python changed, flips `coherent`
  → `unmappable`; and a 41-line re-export shim turns the divergent fixture into
  `coherent` with **0 divergences, 0 absences, `blind_spots: []`,
  `basis_limits: []`, both digests identical to the answer key, and 8/8
  behavioural tests green**. The fix is entirely in the DETECTION — resolve
  first-party-ness against the project root and the `sys.path` the project
  itself installs — and **no verdict rule changes**, because
  `first_party_outside_code_root` already forces `unmappable` and is already
  never downgraded. Ship a regression test in the `TestNothingDowngrades…` shape
  that pins the nested case specifically.

The three round-1 evasions, all still confirmed:

- **Parameter-passed collaborators.** The seeded absence in the fixture is a
  worked example of the tool being wrong in the *safe* direction (reporting dead
  architecture where a real interaction existed). The unsafe direction is the
  same blindness.
- **The composition root.** The coherent fixture's own README confesses it has
  nowhere to live: inside `--code` it gives its component an edge to everything;
  outside, it is free. **This has no answer today and the next epic must produce
  one** — a declared `composition_root:` exempt from port checks but *reported*,
  or a rule that a root must be mapped and its edges attributed to the
  components it wires. Pick one and measure it on a DI-heavy real service, not
  on a fixture.
- **Deletion vs refactoring.** The metric cannot tell them apart, and the one
  blind run cleared 3 of 4 divergences by deleting. Whether that matters is a
  judgment the epic should make explicitly rather than by omission.
  **ROUND 2 adds a third remedy nobody had counted: DUPLICATION.** The round-2
  agent cleared two divergences by copying a four-character format string into
  the other component, and observed that for every unported pair the tool's only
  accepted remedies are duplicate, push the dependency into the caller, or move a
  module in the map — so *"make the coherence check clean" is a standing
  instruction to duplicate across component boundaries*, and nothing in the
  report tells a reviewer that the diff which cleared the finding added
  duplication.
- **NEW (round 2) — ports are UNDIRECTED, so a layering violation inside a
  correctly-ported pair is invisible.** `ports[].between` is an unordered pair,
  but the model has a direction: `Record(i)` *reads* `delivered` and *writes*
  `ledger`, and the descriptor already computes `crossing_actions[].reads` /
  `.writes` per component. The reflexion half throws it away. This is a
  *different* gap from the documented "a ported pair hides a bad edge" — it is a
  bad edge hiding inside a **correctly** ported pair, and the data the fix needs
  already exists.
- **NEW (round 2) — a reporting helper weighs the same as the domain path.**
  Three of ex5's four divergences are operator-view helpers nothing calls; the
  fourth is a function-local import written specifically to dodge an import
  cycle. The report ranks them identically. "4 divergences" reads as four times
  as bad as one, and here it was one architectural fact stated four times. This
  re-frames the epic's precision/recall of 1.000: it is a count of **edges**, not
  of architectural facts.

Build the **negative fixture first**: a codebase that is genuinely coupled and
that the current check reports `coherent`. Until that fixture exists, "the check
is accurate" means "accurate on imports."
**ROUND 2 BUILT IT FOR YOU.** `runs/ex5-run4/artifacts/reexport_attack/` is a
codebase with four real, runtime-live cross-boundary dependencies that the
current check reports `coherent` with `blind_spots: []` — 41 lines of diff on
top of the shipped divergent twin, with the behavioural suite green. Start
there.

### NE-03 — the oracle's blind spots, named in the product

Two whole fault classes are invisible **by construction**, and both were found
independently from outside:

- **Guard relaxation.** A generated corpus contains only enabled edges. The fix
  is not more cases; it is a **negative corpus** — the disabled edges at each
  reachable state, asserted to be REJECTED. TLC already knows them. This is the
  single largest available increase in what the corpus can see, and it is a new
  generator mode, not a tuning knob.
- **Ordering.** Sets in the model, lists in the code, `sorted()` at every oracle
  layer. Either the profile grows sequences, or the toolchain **says in the
  descriptor** that a set-typed variable implemented as an ordered collection is
  unobservable. Saying it is cheap and honest; growing the profile is neither.
- ~~**Parameter recovery (EV-01-DF-01).**~~ **DONE by RP-02, and the result is
  the most important negative in this document. Recovery went 0 of 5 → 5 of 5,
  all 330 cases carry a real argument, the adapter no longer reads `case.after`,
  and the audit is rendered from the corpus it audits. THE MUTANT MATRIX DID NOT
  MOVE A SINGLE CELL.** Guard relaxation stayed 0 of 3 on both arms, and RP-02
  counted why: 330 of 330 recovered arguments are arguments the guard ACCEPTS, 0
  are rejected inputs, and 220 refusable pairs exist in the state space a state
  graph can never emit. **Do not budget any of NE-03's guard work against
  parameter recovery — that hypothesis is dead.** The remaining caveat on the
  kill numbers is narrower than round 1's: the leak is gone, so 4 of 6 is a
  measurement rather than a ceiling; it is still one fixture and six faults.

Ship the corpus and the hand-written suite as **complements with a per-class
table**, never as one kill rate. **Measured twice more in round 2, on the
repaired tree.** RP-02's reconstruction: guard relaxation 0/3 corpus, 3/3
pytest. A fresh blind 16-mutant catalogue: view corpus **10/16**, hand-written
suite **10/16**, **union 14/16**, and the two they both miss are both ordering.
Guard-accepts: **0 of 4 on all five corpus instruments, 4 of 4 on pytest.**
Neither instrument dominates and neither is close.

### NE-04 — the aspect surface as a design review, not only a generator

The unplanned results point the same way twice:

- ~~60 authored lines → 38 cases that killed **exactly** what the 330-case
  whole-view corpus killed. An **8.7× reduction at zero measured loss** on a
  12-mutant catalog. The Given divides and holds.~~
  **ROUND 2 RETIRES THIS HEADLINE.** With a mutant deliberately placed in the
  gap, **74 case-module cases reached 9 of the whole view's 10 kills**, not 10.
  The one lost is a `Fail` that misbehaves only when the work queue is still
  non-empty — a before-state the Given asserts away and the slice never reaches.
  Round 1's "zero measured loss" was a property of round 1's catalogue, not of
  the Given. The round-2 agent's warning, verbatim: *"Do not read a 'case
  modules == view' result off a catalogue that has no cross-aspect mutant in
  it."* It also corrected the vocabulary: on this profile every case is ONE
  action against a materialized before-state, so "cross-aspect interleaving" is
  not about call orderings at all — it is about **before-state diversity**, and
  that is exactly where the loss lives. The honest claim is still good and it is
  smaller: **9 of 10 of the view's kills, from 22% of the cases, for 89 authored
  lines.**
- The Given cannot be written from outside (EV-02-DF-04), and the act of trying
  to write one is what surfaced the model/README contradiction. **Round 2: both
  halves replicate** — a second agent split claim-from-outside and
  predicate-from-inside exactly as RP-03's asymmetry table describes, and found
  the same contradiction.
- **NEW (round 2) — on a small model the cost argument does not apply at all.**
  The round-2 agent measured the whole view generating in 0.95 s and executing
  330 cases in 0.23 s, against `references/case_modules.md`'s headline of
  1m 23s → 2.2s, and concluded that on this project a case module is worth
  writing for what it **documents** and for nothing else: *"the `case_modules:`
  block plus the claim comment is genuinely the best-written statement of intent
  in the repository, and it is 34 lines."* **The reference leads with the wrong
  benefit for small models.** That is a docs finding and it is sharper than
  A2-P2.

So: state the precondition per form in the docs ~~; give the Given an authoring
aid~~; make Step 0's provenance checkable or delete it. **ROUND 2 STATUS: RP-03
did the docs half. The asymmetry is a table in the reference and at the point of
authoring; Step 0 is LABELLED UNENFORCEABLE with a contract in place of a guard,
and the round-2 blind agent honoured that contract unprompted — it declared its
decomposition UNREVIEWED before quoting a number. Still not a control:
`case_modules.py validate` exits 0 on an authorless decomposition. The Given
authoring aid was NOT built and is still open.**
~~And **fix EV-02-DF-02 first**~~ — **DONE by RP-03; modules generate in place
and their corpora now carry recovered arguments and EXECUTE.**
**THE REMAINING BLOCKER IS CM-F5 (EV-03-DF-02): a slice narrower than its view
orphans the view's effect providers, and on the shipped fixture NO mapping can
run a slice's corpus — the documented workaround requires a third mapping file
that does not exist, and the one you write has no durable-write oracle.** Fix
that first now: it is the first thing a new author hits after generation
succeeds, and the instrument they end up with is weaker than the one they think
they have.

---

## 3. Do NOT re-litigate

**ROUND 2 HEALTH WARNING ON THIS SECTION.** Round 1 wrote it. Round 2 overturned
two of its entries and had to weaken a third. A "do not re-litigate" list is only
as good as its willingness to retract, so the retractions are first:

- **RETRACTED — "a generated corpus cannot see guard relaxation … *compounded by
  the adapter recovering the action argument from the case's after-state*".**
  The compounding clause was wrong. RP-02 removed the leak entirely (0 of 5 → 5
  of 5 parameters, adapter never touches `case.after`) and **guard relaxation
  stayed at 0 of 3 on both arms, with the whole mutant matrix unchanged.** The
  cause is structural and only structural: a state graph has no edge for a
  transition that did not fire. Do not spend a ticket on parameter recovery
  expecting kills.
- **RETRACTED — "the wrong-item class is a class this instrument cannot
  measure".** `seeded_faults.toml` declined to seed one on that reasoning. RP-02
  seeded two and **both were killed, before the fix as well as after.** The
  refusal to seed was over-cautious; the class belongs in a future catalogue.
- **WEAKENED — "the divergence check is accurate (precision 1.000, recall
  1.000)".** True, and true only of a tree nobody attacked through a nested
  first-party package. EV-03-DF-03 obtains a full `coherent` on the divergent
  fixture for 41 lines, with both digests unchanged and no blind spot. Quote the
  1.000 with that clause or not at all.
- **WEAKENED — "the Given divides and holds, 8.7× at zero measured loss".** See
  NE-04: with a mutant placed in the gap it is **9 of the view's 10 kills**, not
  10. The zero-loss result was a property of the catalogue.

Everything below this line still stands.

- **Advisory, not blocking.** Nothing in this line of work refuses a close, a
  promotion, or a case generation. Every fixture exits 0, including the
  `divergent` one. Do not propose an architecture gate; the complexity gate
  already failed every normal program and the pivot is settled.
- **No suggested moves (CD-01).** The tool does not propose a cut, a refactor,
  or a module move. EV-02-DF-01's fix is to *carry a fact*, not to pick a
  boundary. A tool that picks the boundary makes every edge legal by
  construction. **Round 2: RP-01 shipped exactly that and it worked. Keep the
  discipline for EV-03-DF-05 too — naming a declaration the run did not use is a
  fact, not a suggestion.**
- **The map and the partition are DECLARED, never inferred.** This is not a gap;
  it is the design. The gameability that follows is the price, and AC-04's
  attribution refusal is the mitigation that works. Do not "solve" gaming by
  inferring the map.
- **`unmappable` is never downgraded.** No flag, key, annotation, or environment
  variable turns it into `coherent`. Suppression-shaped map keys are reported
  and never honored. Keep it that way. **Round 2 re-verified this across all 203
  partitions and on both refusal fixtures, and blind run A attacked it directly
  with a partition coarsening and got `unmappable`. It held.**
- **NEW (round 2) — `basis_limits` and `blind_spots` are DIFFERENT LISTS and must
  stay different.** A basis limit withholds a *clean* and never a *finding*
  ("I saw everything; the yardstick does not support the word `coherent`"). A
  blind spot says "I could not see". RP-01 measured the alternative: filing
  `partition_does_not_decompose` as a blind spot removes the same 12 false cleans
  **and suppresses 67 of 71 real divergence verdicts to do it.** Do not merge
  them for tidiness.
- **The single-writer violations on the pipeline fixture are CORRECT OUTPUT.**
  `queue` and `delivered`, both written by `Deliver`: the handoff mutates both
  sides in one step, so it is simultaneously the port and the violation. That is
  the atomicity-fidelity signal. A report that names them scores correct; a
  scorer that counts them as false positives has miscalibrated the key.
- **Emergent partitioning is greedy and mostly vacuous on real models** — and
  "neither real model decomposes" was itself overclaiming: exhaustive
  enumeration of all 115,975 partitions of this repo's model finds 2 that meet
  every criterion, at Q = 0.003. The doctrine survives; the wording was
  corrected on the epic branch. Do not re-derive either half.
- **Generation determinism is settled.** Measured four times now across two
  epics, two interpreters, and three output paths, always byte-identical. Keep
  it as a control precisely because it always passes; do not spend a ticket
  re-proving it. The risk was always **execution**, and that half is now
  measured too. **Round 2 makes it seven measurements, now including the
  case-module corpora and 24 FAILING executions, and it adds the rule that goes
  with it: a fingerprint that changes because a ticket deliberately changed
  generated content is NOT a determinism failure. RP-02 moved the ex4 corpus
  fingerprint from `33e07e0de…` to `944189052623960aea…`; the fixture's
  `evidence/corpus_fingerprint.txt` carries both values with the reason, and
  that is the pattern to copy.**
- **MF-038's 0-of-9 is not superseded.** ARM A reproduces it on exactly the
  faults MF-038 was made of. The improvement to 4 of 6 comes from a
  **content-bearing output projection** (MF-038's own first recommendation), and
  the last two kills come from a **content-asserting provider**. Attribute per
  mechanism or the number is uninterpretable. **Round 2 reproduced the whole
  table cell for cell and a blind agent reproduced the arm split independently on
  a fresh catalogue (3 of 3 durable-write mutants under the checking mapping, 0
  of 3 under the silent one). The mapping choice is worth 30% of that
  instrument's yield. Never report a kill number without naming its mapping.**
  **HEXAGONAL-PROMPTING: the "30% of that instrument's yield" clause is
  withdrawn — see the note at §1. "Never report a kill number without naming its
  mapping" is stronger than ever and HP-05 made the announcement automatic.**

---

## 4. How to run it

- Branch off the current `epic/architectural-coherence` tip. You inherit the
  four levers, the case-module surface, and the six eval fixtures.
- **The open findings are in `specs/desired_program_model/deferred_findings.yaml`.
  Round 1 filed EV-02-DF-01..05; RP-01/RP-02/RP-03 closed DF-01, DF-02, DF-03 and
  documented DF-04, and DF-05 is PARTLY closed. Round 2 filed five more:**
  - **EV-03-DF-03 (major)** — the re-export / nested-first-party false clean.
    **This is NE-02 and it is the top of the list.**
  - **EV-03-DF-02 (minor)** — CM-F5 sharpened: a slice has zero working shipped
    mappings. This is NE-04's remaining blocker.
  - **EV-03-DF-04 (minor)** — `--effect-report PATH` silently writes nothing.
  - **EV-03-DF-05 (minor)** — `analyze architecture` without `--components`
    silently substitutes an emergent partition for the declared one.
  - **EV-03-DF-01 (minor)** — the AC-02 "falsifiable-and-clean under a
    four-component partition" claim in `ticket_plan.yaml` is false on the
    repaired tree and still on record.
- **Re-score against `examples/validation/PREDICTIONS.md`**, and commit new
  predictions **before** any dispatch. The predictions in that file are what
  made "as expected" a usable phrase in this epic; six of them were wrong, and
  knowing which six is the whole value.
- Run each example at least twice. Every mechanical arm in EV-02 was run twice
  and the divergence was zero; that is a result, and it is only a result because
  it was checked.

### Eval protocol, corrected by this run

- **EV-02-PROTO-01 — redaction that announces itself is a weak blind.** The
  sanitizer left `\* --` comment stubs in the model; the agent noticed and said
  so. Ship a purpose-written neutral fixture variant, not a stripped one.
- **EV-02-PROTO-02 — a blind run's mutant catalog must be an artifact.** The
  aspect run's 12 mutants were applied in place and restored; no catalog
  survives, so its numbers cannot be re-scored. Blind runs that measure kills
  must ship a `seeded_faults.toml`-shaped file the way EV-01 did.
- **Compare the ARCHITECTURE digest, not only the map digest.** DP-1's scoring
  rule was written against the map. The blind run's own report names editing the
  model as the cheapest way to get clean; the model digest is the only thing
  that would catch it.
  **ROUND 2 APPLIED THIS AND FOUND ITS LIMIT. Both digests were compared and both
  were unchanged — and the run's own report then described a route to `coherent`
  that moves NEITHER. A digest rule can only catch a lie told in a declared
  artifact. EV-03-DF-03 is told in ordinary Python. The next round's DP-1 scoring
  must also diff the PRODUCTION TREE for new indirection — or, better, re-run the
  check with the extractor fixed and see whether the clean survives.**
- **Pin the interpreter.** No `python3` on PATH carries both `yaml` and
  `pytest`, and `python3` under `timeout(1)` resolved to a different interpreter
  than in an interactive shell. State an absolute path in the validation README.
  **ROUND 2: still not done in the docs, and hit again by both blind agents.
  EV-03 solved it for itself by building a uv venv with `pytest` + `pyyaml` on
  CPython 3.13 (which also has `tomllib`) and pinning it for every measurement —
  that is the step no document tells anyone to take. EV-02-DF-05 stays open.**

### Eval protocol, corrected by ROUND 2

- **A sanitizer must PRESERVE LINE COUNTS when the answer key is `file:line`.**
  Round 2's sanitizers assert it per replacement and refuse the whole run
  otherwise (`runs/ex5-run4/artifacts/sanitize_runA.py`), and the sanitized copy
  was verified before dispatch to reproduce the identical divergence sites and
  the identical digests. Purpose-written neutral text that moves a line is a
  silently corrupted answer key.
- **Make the blind MECHANICAL, not a promise.** Round 2 gave each agent a trimmed
  toolchain copy (`scripts/`, `references/`, `prompts/`, `SKILL.md`) with
  `examples/` and `specs/` removed, so the answer key was unreachable even by
  accident, and ran a token scan over the sanitized tree before dispatch.
  Note the cost, recorded so it is not double-counted: the trimmed copy makes the
  agent report "documented artifact does not exist" for things that DO exist in
  the repository.
- **EV-02-PROTO-02 WORKED — keep it.** Instructing the blind run to ship its
  mutant catalogue as a file produced 16 mutants with exact `find`/`replace`, a
  harness that asserts each pattern occurs exactly once, and a JSON matrix. Every
  number in that run is re-derivable, which round 1's was not.
- **Ask the blind agent to enumerate what it REJECTED, and to test the cheap
  routes.** Round 2's biggest finding came from the "considered and rejected"
  section, not from the work. The prompt asked for "anything you considered and
  rejected, including any approach that would have produced a clean report faster
  than the one you took" — and the agent tested three, one of which works and
  defeats the epic's own scoring rule.
- **Seed a mutant IN THE GAP the mechanism is supposed to lose.** Round 1's "case
  modules kill exactly what the view kills" was an artifact of a catalogue with
  no cross-aspect mutant in it. Round 2's agent seeded one deliberately and the
  claim moved to 9 of 10. A reduction result with no mutant in the gap is not a
  measurement.

---

## 5. Standing constraints (unchanged, non-negotiable)

- **Never merge to `main`** and **never run `skill-manager sync`** without
  explicit owner say-so.
- **Never invoke `tla-spec-dev` from PATH** — it execs a stale installed clone.
  Use `python3 scripts/tla_spec_dev.py --spec-root specs ...`.
- **Run pytest with `--with pyyaml`** or the YAML-validity guard skips silently.
- **Validate `ticket_plan.yaml` after every edit.**
- The tool serves a **constrained v0 TLA+ profile**, not arbitrary TLA+. Both
  invisible fault classes in §2/NE-03 are properties of that profile, and
  widening it is a decision with a cost, not a bug fix.
- **Findings are FILED, never fixed inline, during a measurement.** A fix during
  measurement destroys the measurement. EV-02 filed five and fixed none; **EV-03
  filed five and fixed none, including the major one it found in the very tool it
  was measuring.**

---

## 6. Epic-owner discipline that paid off, again

Predictions committed before dispatch; answer keys enumerated by the owner and
not by the agent under test; agents never shown the predictions; two arms
declared as two mappings rather than one mapping with its assertions switched
off, so a reader of the record can see which instrument produced a number.

That last one is the reusable trick. **DP-8 — "an EV-02 number reported without
naming its arm is uninterpretable" — is the reason this epic has a 4/6 and a 6/6
instead of a single misleading number**, and the reason the blind aspect run
reported a per-class table instead of "5 of 11". Apply the same split to any
future claim: separate the mechanism you are selling from the mechanism that did
the work, in the artifact, before the measurement runs.

And the standing one: **an epic that closes with only good news about itself has
not been measured.** This one closes with an accuracy result of 1.000 and a
six-line YAML file that makes it say `coherent` on a codebase with four
divergences. Both are true. Ship both.

---

## 7. What round 2 changes about how to read all of the above

The repairs were **measured, not assumed**, and the measurement was scored
against the predictions round 1 had already committed. Three things came out of
that discipline that no amount of arguing would have produced:

1. **A repair that worked and changed nothing.** RP-02 closed a real oracle leak
   and the kill matrix did not move a single cell. Nobody predicted that. It
   killed a hypothesis that had been in this document as a fact.
2. **A repair whose second-order effect had to be checked separately.** RP-01
   removed 12 false cleans; the number that mattered was whether it removed any
   TRUE findings to do it. It removed none and released 20. Had that not been
   measured, "12 → 0" would have been indistinguishable from a tool that had
   simply learned to refuse everything.
3. **A defect nobody was looking for**, found because a blind agent was asked what
   it *rejected* and not only what it *did*, and reproduced because the scorer
   did not take its word for it.

**The six-line YAML file in the paragraph above no longer works.** A 41-line
Python file does. Ship that too.

### The one-sentence answer to "does this catch harder bugs now?"

**No — it lies less.** It stopped certifying 12 things it had not measured, it
started running case-module corpora it previously could only generate, and it
kills exactly the same bugs it killed before, cell for cell. The classes it
cannot see are structural, they were re-confirmed three times in round 2 by
instruments that had never heard of them, and none of them moved.
