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
| whole-record counted figures | **103** | **3,004** |
| — REFUTED | **81** | **81** |
| — COUNT-MOVED | **0** | **39** |
| — HOLDS | **2** | **2** |
| — UNREACHABLE | **20** | **2,882** |
| files swept | 367 | 369 |
| files carrying a figure | **37** | **258** |
| `scope` process exit code | **1** | **1** |
| counted figures over the 10 named work-directing documents | **3** | **271** |
| documents in that list reading ZERO | **9 of 10** | **0 of 10** |

**REFUTED did not move and HOLDS did not move.** That is the point, not an
aside: `FORM P` **cannot produce either verdict**, so nothing that had an answer
before has a different one, and no exit code anywhere changed.

**The 3,004 − 103 = 2,901 new figures are all FORM P's, and 61 of them are
mine.** This ticket's own documents are inside `DEFAULT_SWEEP` —
`specs/results/scorecards/**/*.md` matches `PROSE-FORM-SPEC.md` and this file,
and `specs/deferred_findings.yaml` matches the five findings I appended — so a
write-up about counted figures adds counted figures to the corpus it is
measuring. **All 61 are UNREACHABLE. Excluding them, the record's own figure is
2,943 over 256 files**, and `files swept` rises 367 → 369 for the two documents
this ticket added.

**AND THREE OF MY OWN SENTENCES BRIEFLY BECAME REFUTED CLAIMS ABOUT THIS
PROJECT.** A finding I filed spelled out a dimension-bound figure over `49 rows`
as a HYPOTHETICAL, and another quoted a real one about an abolished dimension;
the sweep read all three as claims, re-derived them against the 95-card corpus,
and REFUTED went 81 → 84. **This paragraph does the same thing if the literals
are written out, which is why they are not** — and it took four passes to stop
reintroducing them, once in this very sentence.
**An invented figure written into a swept file is indistinguishable from a claim
somebody made.** All three were rewritten as placeholders — the shape is stated,
the literal is not — and the first draft of §5 of this file transcribed 39 real
card figures verbatim, which double-counted every one of them and took
COUNT-MOVED from 39 to 55. **Both were caught by running the instrument on the
ticket's own output, which is the only reason they are in this paragraph rather
than in the epic's figures.**

### The figure in that table is measured at a named commit, and it has to be

**This document is inside the corpus it measures.** `DEFAULT_SWEEP` matches
`specs/results/scorecards/**/*.md`, so every counted figure in this write-up is
read by the next `scope` run — and editing this paragraph changes the number in
the table above it. That is not a defect to be engineered away; it is
`SS-01-DF-03` pointed at itself. **A figure is a joint property of the artifact
and the tree it was measured in**, and this one is measured at the commit named
in `FINAL-FIGURES.txt`, which is a `.txt` and therefore **not swept** — the one
place in this evidence root where a figure can be written down without changing
itself.

Anyone re-deriving the whole-record number will get a different total from the
one in the table if they run it at a different commit, and **the difference will
be this file.** The record's own figure — everything outside
`specs/results/scorecards/stabilize-substrate/SS-04/` and outside the five
ledger rows this ticket appended — is the stable one to quote.

---

## 1. What moved, with numerator and denominator named

- **Whole-record figures 103 → 3,004, of which 2,943 are the record's and 61 are
  this ticket's own documents.** *Numerator and denominator both, and they are
  the same movement*: the recogniser reads a form it could not read before, so
  figures that were always in those files are now counted. **No pattern was added
  to `DEFAULT_SWEEP`** and `sweep_paths` is untouched.
- **Files carrying a figure 37 → 258** over a swept population of 367 → 369.
  The **denominator** rose by 2 (this ticket's two new documents). The
  **numerator** rose by 221, of which 219 are the record's.
- **REFUTED 81 → 81, HOLDS 2 → 2, exit code 1 → 1.** Flat by construction and
  asserted by `test_no_bound_figure_changed_its_verdict` and
  `test_the_exit_code_is_unchanged_for_an_input_that_resolves`.
- **COUNT-MOVED 0 → 39.** All 39 are FORM P's, all name cards, all in documents
  this ticket did not write, and **none is a refutation**: the finding is that
  the card population moved under a figure, not that the figure is false. §5.
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
verdict set over all 2,901 FORM P rows in this tree and asserts it against
`PROSE_VERDICTS`.

- **`REFUTED` is unavailable** because a prose figure binds no value to a
  dimension, so there is no proposition to contradict. **A false REFUTED is worse
  than an UNREACHABLE.**
- **`HOLDS` is unavailable too**, and that asymmetry is deliberate. A card-noun
  figure whose denominator re-derives *exactly* is still `UNREACHABLE`, reason
  **`numerator has no predicate`** — the denominator was checked and the
  numerator was not, and calling that HOLDS would be the instrument claiming to
  have checked a claim it only half-read.

FORM P's 2,862 UNREACHABLE rows, by named reason:

| reason | count | share |
|---|---:|---:|
| `non-card noun` | 1,883 | 65.8% |
| `no counted noun` | 952 | 33.3% |
| `unresolved qualifier` | 19 | 0.7% |
| `numerator has no predicate` | 5 | 0.2% |
| `anaphoric scope` | 3 | 0.1% |

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

The 39 are listed in full, with file and line, in the sealed sweep at
`scope-whole-record-TIP.txt` under `## COUNT-MOVED`. **They are deliberately not
transcribed here.** Copying 39 real `<n> of <m> cards` figures into a file that
`DEFAULT_SWEEP` reads would report every one of them TWICE for every future
reader — this write-up did exactly that in its first draft and inflated
COUNT-MOVED from 39 to 55 with its own prose. **The instrument's own output is
the citation.**

**One of those 39 is wrong and it is named rather than patched.**
`specs/deferred_findings.yaml:6700` is a sentence of the shape *"one of those 25
… is a card"* — a membership statement whose predicate the noun heuristic read
as a noun phrase, giving a numerator of 1 over a denominator of 25 with `cards`
as the counted noun. **1 of 39 = 2.6%.** Special-casing it
would be a rule written around a single known sentence. (Quoted by path rather
than verbatim, for the reason in the paragraph above.)

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
| P1 | FORM P finds >20 and <400 figures over the default sweep | **FAILED** — 2,901. I was wrong by an order of magnitude about how much counted prose this record carries. |
| P2 | >85% of them are `non-card noun` | **FAILED** — 65.8%. The bucket I did not anticipate is `no counted noun`, a third of the rows: the figure ends a line, or its noun sits outside the three-token window. `SS-04-DF-03`. |
| P3 | FORM P produces zero REFUTED | passed |
| P4 | the charter moves off 0 and reads >10 | passed — 15 |
| P5 | `CUT-THE-APPARATUS-EPIC.md` moves off 0 | passed — 7 |
| P6 | whole-record REFUTED and the exit code are unchanged | passed — 81 and 1 |
| P7 | the superset finds ≥15% more shapes than FORM P takes | passed — 76% more (5,800 vs 3,299) |
| P8 | ≥2 of the five named figures do not parse | passed — 3 |

**6 of 8. Not an ALARM** (`measurement_rule`: an ALARM is every prediction
passing). The two that failed are the two about the record's own density, and
they failed in the direction that says the blindness was worse than I estimated.

---

## 8. WHAT IT MISSES — the product

Measured by `recall_audit.py` against a separate over-broad scanner. **A superset
hit is not necessarily a counted figure**; the denominator is "shapes a reader
might have to check" and the numerator is "shapes the recogniser reaches".

**Over the whole default sweep: 3,299 of 5,800 = 56.9%. It misses 2,501, and
every one of them is in a declared category — the exact per-shape split is in
`recall-whole-record.txt`, which is regenerated by the script and does not go
stale the way a table transcribed into this file does.**

The order of the six declared categories does not move: `n/m` ratio-or-movement
notation is the largest by a wide margin (roughly 56% of the misses), then the
`n:m` colon form (roughly 34%), then figures **split across a line break**, then
the distributive `every one of the N` this recogniser **deliberately refuses**,
then `n in m`, then spelled-out numbers above twenty. **Unclassified: zero.**

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

### Three defects in my own recogniser, all found by measurement

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
3. **A `REFUTED` figure naming an abolished dimension killed the whole command.**
   `c['dimensions'][r['dim']]` is a subscript, card version 5 abolished D1, D4
   and D5, and one such sentence in any swept file produced `KeyError: 'D5'` —
   **a traceback on exit 1, taking every other figure's answer with it**, and
   indistinguishable from the ordinary "something is REFUTED" exit 1 to anyone
   reading only the code. **The defect predates this ticket by five card
   versions**; I met it because a finding I filed quoted such a figure into the
   ledger. Repaired inside the conflict key, demonstrated before and after in
   `d5-keyerror-demo.txt`, pinned by a test, and the semantic question it opens
   is filed as `SS-04-DF-05`.

---

## 9. The two findings routed to this ticket, consumed rather than cited

**`SS-01-DF-03` — a `scope` verdict is a joint property of the file and the tree
it is swept in, and the output recorded nothing about the tree.** Every run now
prints, in text and JSON:

```
The tree this was swept in — SS-01-DF-03
  root            /Users/hayde/IdeaProjects/wt-epic-stabilize-substrate-SS-04
  root HEAD       <the commit, and WORKING TREE DIRTY when it is>
  scorecard root  …/specs/results/scorecards
  cards           95
  files swept     <n>  (DEFAULT_SWEEP)
```

(Shape only — the live values move with the tree, which is the point. A real
capture is in `scope-whole-record-TIP.txt` and in `FINAL-FIGURES.txt`.)

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

## 10. The suite — five numbers that sum, at both ends, each with its tree

**The authoritative table is `FINAL-FIGURES.txt`** — a `.txt`, which
`DEFAULT_SWEEP` does not read, so writing a figure there does not change it.

| tree | failed | passed | skipped | xfailed | collection |
|---|---:|---:|---:|---:|---:|
| base `8dd0442`, **clean clone**, workflow closed | 7 | 1550 | 0 | 1 | 1558 |
| tip `97d70ed`, ticket workspace OPEN | — | — | — | — | 1598 |
| tip `97d70ed`, workspace CLOSED — **the tree this PR leaves** | 10 | 1583 | 0 | 1 | 1594 |

`7 + 1550 + 0 + 1 = 1558`. `10 + 1583 + 0 + 1 = 1594`.

**Every unit attributed; nothing is unexplained.**

- **collection +36 — denominator**: the 36 nodes of
  `tests/test_counted_figure_recogniser.py`. The 1598 row is the same tree with
  the workspace open: `open ticket` widens `test_spec_yaml_valid` over
  `specs/tickets/SS-04/` by **+4**, and `close ticket` removed those 4 again.
- **failed +3 — numerator, and all three are MINE.** The three in
  `tests/test_score_tools.py` that pin the OLD recogniser's exhaustive answer.
  **Declared, not discovered**; filed as `SS-04-DF-06`; **not repaired, because
  that file is `SS-06`'s conflict key and not this ticket's.** In all three the
  test's stated purpose still holds — what went stale is a closed enumeration
  written when one sentence form was the only one.
- **passed +33**: 36 new nodes minus those 3.
- **skipped 0 → 0. xfailed 1 → 1.**
- **Zero inherited reds repaired, zero inherited reds changed their reason.** The
  tip FAILED list is the base FAILED list plus exactly those three, verified by
  diffing the two, and both `test_instrument_demonstrations` assertions are
  byte-identical at either end despite this ticket adding a register row.

### The close divergence, disclosed rather than discovered

**`close ticket` seals the history entry and deletes the workspace in ONE
operation, so the sealed entry can never describe the tree it produces.** The
sealed summary describes the pre-close, workspace-open tree. **The row marked
*"the tree this PR leaves"* is authoritative.**

### And the first base run was CONTAMINATED — by me

I started it inside the ticket worktree and then edited `score_tools.py` and
`instruments.toml` while it ran. **That is the rule §8 of the charter states,
broken by a ticket agent this time rather than by the owner.** It is preserved,
labelled, and is not the baseline:
`pytest-BASE-CONTAMINATED-edits-landed-mid-run.txt`. Every base figure here comes
from a **clean clone of `8dd0442`** with nothing else running in it.

---

## 10a. Findings filed — ledger 334 → 340, append-only

| id | what | routed to |
|---|---|---|
| `SS-04-DF-01` | `_CARD_NOUN` counts `rows` and `judges` as cards. FORM P's half repaired; **the BOUND forms' half is latent and those forms CAN return REFUTED** | `SS-08` |
| `SS-04-DF-02` | the partitive `one of the two highest` — a membership claim read as a count. Its distributive cousin **is** repaired and pinned | `SS-08` |
| `SS-04-DF-03` | 949 of FORM P's 2,848 UNREACHABLE rows say `no counted noun`, a fact about a three-token window and **not** about the record. Where sealed prediction P2 failed | `SS-08` |
| `SS-04-DF-04` | every documented `python3 …score_tools.py …` dies with a **traceback** under a `python3` below 3.11, and **this ticket's own document sweep reported ten zeroes before it was caught** | `SS-08` |
| `SS-04-DF-05` | a `REFUTED` figure naming an **abolished dimension** killed the whole command with `KeyError: 'D5'`. **Repaired here**; the semantic question is carried | `SS-08` |
| `SS-04-DF-06` | the three declared reds above, with the minimal edit for each and the reason none was applied | `SS-06` |

---

## 11. What I could not do

- **`run tlc` does not exist.** `scripts/tla_spec_dev.py run` accepts only
  `spec-unit-tests` and `effect-conformance`. Reported as `N/A`, not substituted.
- **The partitive `one of the N` false positive is not repaired**, §8.
- **One wrong COUNT-MOVED of 39**, `specs/deferred_findings.yaml:6700`, §5.
- **The charter is not a clean held-out document.** The assignment requires
  reading it before touching git, so it was read before the recogniser was
  written. `CUT-THE-APPARATUS-EPIC.md` and the baselines were genuinely unopened.
- **`n:m` and `n/m` together are about nine tenths of the misses, and both are declared.**
  Reaching them means deciding that `7 / 1462` is a count rather than a ratio,
  which is a judgement about the sentence, not about the numbers.
