# SS-04 — the recogniser reaches the record, and here is exactly what it misses

**Issue #277. Branch `feature/SS-04`, base `8dd044230a09013b3ea912bfead2cc97e0f8a321`
(the resolved OID of `origin/epic/stabilize-substrate`, not the symbolic ref).**

Every figure below names the tree it was measured in, because a `scope` verdict
is a joint property of the file **and the tree it is swept in** (`SS-01-DF-03`),
and because this epic has now caught four parties quoting one without the other.

---

## 0. The result in one table

| | base `8dd0442`, re-derived here | tip |
|---|---:|---:|
| whole-record counted figures | **103** | **2,939** |
| — REFUTED | **81** | **81** |
| — COUNT-MOVED | **0** | **39** |
| — HOLDS | **2** | **2** |
| — UNREACHABLE | **20** | **2,817** |
| files swept | 367 | 368 |
| files carrying a figure | **37** | **257** |
| `scope` process exit code | **1** | **1** |
| counted figures over the 10 named work-directing documents | **3** | **271** |
| documents in that list reading ZERO | **9 of 10** | **0 of 10** |

**REFUTED did not move and HOLDS did not move.** That is the point, not an
aside: `FORM P` **cannot produce either verdict**, so nothing that had an answer
before has a different one, and no exit code anywhere changed.

**The 2,939 − 103 = 2,836 new figures are all FORM P's, and 6 of them are mine.**
`PROSE-FORM-SPEC.md`, which this ticket added, is matched by
`specs/results/scorecards/**/*.md` and contributes 6 UNREACHABLE rows and the
+1 in `files swept` (367 → 368). **2,933 of the 2,939 are the record's.**

---

## 1. What moved, with numerator and denominator named

- **Whole-record figures 103 → 2,939.** *Numerator and denominator both, and
  they are the same movement*: the recogniser reads a form it could not read
  before, so figures that were always in those files are now counted. **No file
  was added to `DEFAULT_SWEEP`** and `sweep_paths` is untouched.
- **Files carrying a figure 37 → 257** over a swept population of 367 → 368.
  The **denominator** rose by 1 (my own spec document). The **numerator** rose by
  220 because the recogniser reaches those files' sentence forms now.
- **REFUTED 81 → 81, HOLDS 2 → 2, exit code 1 → 1.** Flat by construction and
  asserted by `test_no_bound_figure_changed_its_verdict` and
  `test_the_exit_code_is_unchanged_for_an_input_that_resolves`.
- **COUNT-MOVED 0 → 39.** All 39 are FORM P's, all name cards, and **none is a
  refutation**: the finding is that the card population moved under a figure, not
  that the figure is false. See §5 for the 39.
- **The register's absent-input population 2 of 56 → 3 of 56.** **Numerator
  only** — no row was added or deleted, `scorecard-scope` gained a contract.
- **The base whole-record figure is 103 at `8dd0442`, and its REFUTED split is
  81, not the 80 in the sealed baseline.** The sealed baseline is 102 / 80 / 0 /
  2 / 20 at the predecessor's tree; `SS-01` added the relocated ledger and took
  it to 103. **I re-derived 103 / 81 / 0 / 2 / 20 in a clean clone of `8dd0442`
  rather than quoting either figure.** The +1 REFUTED against the sealed
  baseline's 80 is inherited, not mine, and it is stated here because the
  next reader will otherwise attribute it to this ticket.

---

## 2. Clause (a) — the named, committed list

`specs/results/scorecards/stabilize-substrate/SS-04/work-directing-documents.txt`,
ten documents, measured by the same script over the same list in the same tree
with the tool swapped: `measure-documents.sh`. Sealed at `docs-base.txt` and
`docs-tip.txt`.

| document | base | tip |
|---|---:|---:|
| `STABILIZE-SUBSTRATE-EPIC.md` — **this epic's own charter** | **0** | **15** |
| `CUT-THE-APPARATUS-EPIC.md` — the predecessor's | **0** | **7** |
| `NEXT-EPIC.md` | 3 (3 REFUTED) | 157 (3 REFUTED, 3 COUNT-MOVED, 151 UNREACHABLE) |
| `specs/desired_program_model/ticket_plan.yaml` | **0** | **48** |
| `GOAL-four-results-still-stand/baseline.md` | **0** | **4** |
| `cut-the-apparatus/CA-02/PRICE-TABLE.md` | **0** | **12** |
| `GOAL-counted-figures-reach-the-record/baseline.md` | **0** | **3** |
| `GOAL-tree-stabilizes/baseline.md` | **0** | **3** |
| `GOAL-absent-input-consumed/baseline.md` | **0** | **4** |
| `GOAL-judged-goals-compliant/baseline.md` | **0** | **18** |
| **total** | **3** | **271** |

**Every exit code on that list is identical at base and tip** (0 everywhere
except `NEXT-EPIC.md`, which was 1 and is 1).

---

## 3. Clause (b) — UNREACHABLE is the default, and it is a closed verdict set

**FORM P's verdicts are `{UNREACHABLE, COUNT-MOVED}`.** Not "we were careful":
`test_form_p_never_refutes_and_never_holds_over_the_whole_record` computes the
verdict set over all 2,836 FORM P rows in this tree and asserts it against
`PROSE_VERDICTS`.

- **`REFUTED` is unavailable** because a prose figure binds no value to a
  dimension, so there is no proposition to contradict. **A false REFUTED is worse
  than an UNREACHABLE.**
- **`HOLDS` is unavailable too**, and that asymmetry is deliberate. A card-noun
  figure whose denominator re-derives *exactly* is still `UNREACHABLE`, reason
  **`numerator has no predicate`** — the denominator was checked and the
  numerator was not, and calling that HOLDS would be the instrument claiming to
  have checked a claim it only half-read.

FORM P's 2,797 UNREACHABLE rows, by named reason:

| reason | count |
|---|---:|
| `non-card noun` | 1,841 |
| `no counted noun` | 931 |
| `unresolved qualifier` | 18 |
| `numerator has no predicate` | 4 |
| `anaphoric scope` | 3 |

---

## 4. Clause (c) — it is not a gate

`cmd_scope` returns 1 iff some figure is REFUTED. FORM P cannot produce one.
Therefore **no invocation over any tree exits differently than it did**, and
`test_the_exit_code_is_unchanged_for_an_input_that_resolves` runs both and
compares. Nothing refuses, no close path consults it, and no check over an
adopter's code was added.

**One exit code did change and it is the opposite of a gate**: an **absent,
unreadable or empty** input now answers `UNDECIDED` at exit **2** instead of
`0 REFUTED` at exit **0**. That is `SS-02`'s extension to `R1`, and §6 is the
demonstration.

---

## 5. Clause (e) and the standing rule — what the rule REFUSES over the sealed record

Run against the sealed record before shipping, as `every_research_ticket_runs_its_own_rule`
requires. **FORM P's only non-UNREACHABLE answer fires 39 times**, every one a
`COUNT-MOVED` on a figure counting **cards**, in documents this ticket did not
write:

- `27 of 27 cards ever written` (3 places), `35 of 35 cards` (4), `12 of 12
  cards` (2), `10 of 10 cards` (7), `0 of 87 cards` (4), `52 of 87 cards`,
  `55 of 59 cards` (2), `56 of 63 cards of` (2), `58 of 59 cards`,
  `59 of the 73 sealed cards`, `44 of 49 sealed cards`, `37 of 37 cards` (2),
  `Two of the four cards`, `three of four cards` (2), `0 of 95 cards`,
  `ONE OF THOSE 25 IS A CARD`, and the `wrap_probe` fixtures (4).

**One of those 39 is wrong and it is named rather than patched.**
`ONE OF THOSE 25 IS A CARD` is not `1 of 25 cards`; the counted noun heuristic
took `IS A CARD` as a noun phrase. **1 of 39 = 2.6%.** Special-casing it would
be a rule written around a single known sentence.

The full sweep is sealed at `scope-whole-record-TIP.txt` /
`scope-whole-record-TIP.json`; the base at `scope-whole-record-BASE-8dd0442.txt`.

---

## 6. `SS-02`'s extension, executed on this instrument

**At the base, five distinct absent inputs produced five byte-identical
confident PASSes at exit 0**, and the tool could not tell any of them from
"checked, none found". Sealed at `absent-input-base.txt`; after, at
`absent-input-demo.txt`.

| input | base | tip |
|---|---|---|
| document not in the tree | `0 counted figure(s): 0 REFUTED …` **exit 0** | `UNDECIDED: [absent]` **exit 2** |
| document of 0 bytes | same, **exit 0** | `UNDECIDED: [empty]` **exit 2** |
| document of whitespace only | same, **exit 0** | `UNDECIDED: [empty]` **exit 2** |
| document that does not decode as UTF-8 | same, **exit 0** | `UNDECIDED: [unreadable]` **exit 2** |
| `--scorecards` naming nothing | same, **exit 0** | `UNDECIDED: [absent]` **exit 2** |
| `--scorecards` naming a corpus with no cards | same, **exit 0** | `UNDECIDED: [empty]` **exit 2** |
| a sweep selecting 0 files | same, **exit 0** | `UNDECIDED: [empty]` **exit 2** |
| **a real document that genuinely counts nothing** | `0 counted figure(s)`, exit 0 | `0 counted figure(s)` + **`CHECKED, NONE FOUND`**, exit 0 |

**The last row is the control and it is why the other seven are a repair rather
than a refusal reflex.** An instrument that answers UNDECIDED to everything has
not been fixed. `absent` and `checked, none found` are different claims, and now
the output says which one it is.

**Registered and executed**, not only demonstrated: `scorecard-scope` carries a
three-state `[instrument.absent_input]` block and
`score_tools.py absent-input --only scorecard-scope` reports **SATISFIED**,
`contract EXECUTED and holding 1`, exit 0 (`absent-input-register.txt`). The
register population moves **2 of 56 → 3 of 56**, numerator only.

**Disclosed: `examples/validation/instruments/instruments.toml` is outside this
ticket's declared conflict keys.** The edit is confined to the `scorecard-scope`
row — a contract describing the change this ticket made to that instrument, plus
its stale `blind_spot` figures — and touches no other row.

---

## 7. `MF-020` — how I know it is not fitted

**The issue names five counted figures and I know all five answers.** A
recogniser tuned until those five parse is fitted and fails clause (d) *even if
it works*. Four things, in order:

1. **The shape was sealed in a commit before the code existed.** `2933549`,
   2026-08-17T03:25:10Z, `PROSE-FORM-SPEC.md`. **That commit carries no regex.**
   §5 of it lists the declared misses, §9 lists eight predictions.
2. **It was built against a written specification of what an English counted
   figure is, not against a corpus of known answers.** At sealing time I had read
   this epic's charter — **mandatory, and therefore contaminated and disclosed
   as such** — and the `scope` section of `score_tools.py`. I had **not** read
   `CUT-THE-APPARATUS-EPIC.md`, `NEXT-EPIC.md`, any goal baseline, the price
   table, or any sealed `RESULT.md`. Those were opened only to measure.
3. **Recall is measured against a separate, deliberately over-broad scanner**
   (`recall_audit.py`), so "what it misses" has a denominator I did not choose
   and a category for every miss. §8.
4. **Three of the five were declared misses before measuring, and a test asserts
   they still miss.** `test_the_declared_misses_still_miss`. Widening FORM P to
   catch one of them **breaks a test**. That is the only mechanical protection
   against fitting this ticket can ship, and it is the one that costs something.

**The five, looked at last** (`five-named-figures.txt`):

| figure | FORM P |
|---|---|
| `0 of 9` | parses |
| `1 of 38` | parses |
| `four rounds' claims` | **misses** — declared, sealed at `2933549` |
| `8 failed, 1490 passed` | **misses** — declared, sealed at `2933549` |
| `seven epics, zero bugs` | **misses** — declared, sealed at `2933549` |

**2 of 5.** A recogniser fitted to that list would have five.

### The sealed predictions, scored

| | prediction | outcome |
|---|---|---|
| P1 | FORM P finds >20 and <400 figures over the default sweep | **FAILED** — 2,836. I was wrong by an order of magnitude about how much counted prose this record carries. |
| P2 | >85% of them are `non-card noun` | **FAILED** — 64.9% (1,841 of 2,836). The bucket I did not anticipate is `no counted noun`, 931 of them: the figure ends a line, or its noun sits outside the three-token window. |
| P3 | FORM P produces zero REFUTED | passed |
| P4 | the charter moves off 0 and reads >10 | passed — 15 |
| P5 | `CUT-THE-APPARATUS-EPIC.md` moves off 0 | passed — 7 |
| P6 | whole-record REFUTED and the exit code are unchanged | passed — 81 and 1 |
| P7 | the superset finds ≥15% more shapes than FORM P takes | passed — 76% more (5,697 vs 3,234) |
| P8 | ≥2 of the five named figures do not parse | passed — 3 |

**6 of 8. Not an ALARM** (`measurement_rule`: an ALARM is every prediction
passing). The two that failed are the two about the record's own density, and
they failed in the direction that says the blindness was worse than I estimated.

---

## 8. WHAT IT MISSES — the product

Measured by `recall_audit.py` against a separate over-broad scanner. **A superset
hit is not necessarily a counted figure**; the denominator is "shapes a reader
might have to check" and the numerator is "shapes the recogniser reaches".

**Over the whole default sweep: 3,234 of 5,697 = 56.8%. It misses 2,463, and
every one of them is in a declared category.**

| missed | shape | declared? |
|---:|---|---|
| 1,394 | `n/m` ratio or movement notation — `17 / 1483`, `2/2 -> 4` | §5, yes |
| 842 | `n:m` colon form — `3 : 1` | §5, yes |
| 117 | **split across a line break** | §5, yes |
| 59 | distributive `every one of the N` — **deliberately refused** | §5, yes |
| 37 | `n in m` rather than `n of m` — `1 in 38` | §5, yes |
| 14 | spelled-out numbers above twenty — `thirty-one of forty` | §5, yes |
| **0** | unclassified | — |

**Over the three charters: 180 of 256 = 70.3%**, missing 39 `n/m`, 17 `n:m`,
14 line-break splits, 4 `n in m`, 1 distributive, 1 spelled-out.

**And the largest miss is not in that table at all**, because no superset can
contain it: **a counted figure with no `<n> of <m>` in it.** `8 failed, 1490
passed` is two counts and a denominator that must be added. `seven epics, zero
bugs` is a numerator over a population named nowhere. `four rounds' claims` has
no denominator. **Reaching those means inventing the population behind the
sentence**, which is the failure `prediction-seal` declined to commit one layer
down, and it is why the shape was drawn where it was.

### Precision, hand-audited

**40 FORM P matches sampled deterministically (`random.seed(277)`) from the
whole-record run and adjudicated by hand, one at a time. 38 are genuine counted
figures.** The two failures are one class:

- `every one of the 10 was inspected` — distributive; that is 10 of 10, not 1 of
  10, and reading the numerator as 1 **inverts the claim**. **Repaired**
  (`_DISTRIBUTIVE`, 59 occurrences over the record), and pinned by a test.
- `one of the two highest honesty scores` — the partitive cousin. A **membership**
  statement, not a count over a population. **Not repaired and reported instead**:
  no rule I can write separates it from `one of the two rounds that failed`
  without guessing at the sentence.

### Two defects in my own recogniser, both found by measurement

1. **42 of the first 88 COUNT-MOVED rows counted LEDGER ROWS, not cards.**
   `39 of 49 rows` was answered with *"the population is 95 rather than 49"* — a
   category error in the voice of a re-derivation. `_CARD_NOUN` includes `rows`
   and `judges`, which is right for a dimension-bound figure (the `D<n>` token
   has already established the subject) and wrong in bare prose. FORM P now
   claims only `card` / `scorecard`. **88 → 39, and 42 of the 49 removed were
   this.**
2. **A greedy noun capture ate the next figure's numerator.** `44 of 105, and
   two of those four are paths` matched once, with the noun consuming `and two
   of`, and `finditer` never tried the second figure. Four whole-record misses,
   found by the recall audit as its only unclassified rows. The noun is a
   lookahead now.

---

## 9. The two findings routed to this ticket, consumed rather than cited

**`SS-01-DF-03` — a `scope` verdict is a joint property of the file and the tree
it is swept in, and the output recorded nothing about the tree.** Every run now
prints, in text and JSON:

```
## The tree this was swept in — SS-01-DF-03
  root            /Users/hayde/IdeaProjects/wt-epic-stabilize-substrate-SS-04
  root HEAD       5fb0c459124ccf2661c95e67cef4d4c24fe38093  (WORKING TREE DIRTY)
  scorecard root  …/specs/results/scorecards
  cards           95
  files swept     368  (DEFAULT_SWEEP)
```

and a root that is **not a git checkout** says so in those words, so the
`21/18/3`-under-a-bare-`--root` figure can no longer be mistaken for the
`20/17/3` the repository gives. Pinned by two tests.

**`SS-00-DF-04` — never publish a joint claim from separate marginals.** The
owner had `by file 20/3` and `by verdict 20 REFUTED / 3 UNREACHABLE`, assumed
they cross-tabulated, and published *"20 REFUTED, all from the ledger"*. They do
not: it is 17+3 / 3. **`scope` now computes and prints the `file × verdict`
JOINT distribution**, and `test_the_joint_distribution_is_computed_not_inferred`
asserts every joint column sums to its marginal. **The sentence that produced
that error cannot be written from this output.** Where a joint distribution
*cannot* be computed the honest output is the two marginals stated as marginals
— here it can be, so it is.

---

## 10. The suite, and the close divergence

Five numbers that sum, at both ends, each with its tree named. See the PR body
for the authoritative figures; **the sealed close-history entry cannot describe
the tree it produces**, because `close ticket` seals the entry and deletes the
workspace in one operation. **This file and the PR body are authoritative for the
post-close tree; the sealed summary describes the pre-close one.**

**The first base run was CONTAMINATED and is preserved rather than deleted**:
`pytest-BASE-CONTAMINATED-edits-landed-mid-run.txt`. I started it in the ticket
worktree and then edited `score_tools.py` and `instruments.toml` while it ran —
the exact rule §8 of the charter states, broken by the ticket agent this time.
The base figure quoted anywhere in this ticket comes from a **clean clone of
`8dd0442`** with nothing else running in it.

---

## 11. What I could not do

- **`run tlc` does not exist.** `scripts/tla_spec_dev.py run` accepts only
  `spec-unit-tests` and `effect-conformance`. Reported as `N/A`, not substituted.
- **The partitive `one of the N` false positive is not repaired**, §8.
- **`ONE OF THOSE 25 IS A CARD` is one wrong COUNT-MOVED of 39**, §5.
- **The charter is not a clean held-out document.** The assignment requires
  reading it before touching git, so it was read before the recogniser was
  written. `CUT-THE-APPARATUS-EPIC.md` and the baselines were genuinely unopened.
- **`n:m` and `n/m` are 2,236 of the 2,463 misses and both are declared.**
  Reaching them means deciding that `7 / 1462` is a count rather than a ratio,
  which is a judgement about the sentence, not about the numbers.
