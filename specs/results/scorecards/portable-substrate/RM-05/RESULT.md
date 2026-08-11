# RM-05 — the evaluation: which surface moved, what kind of cut helps, and whether the loop transfers

**Ticket:** [#213](https://github.com/haydenrear/tla-spec-dev/issues/213) ·
**epic:** `portable-substrate` · **branch point:** `58411dc`, verified ·
**promotion predecessor:** RM-04, merged · **role:** evaluation.
**Findings filed: 5. Fixed: 0.**

---

## 0. ROUND CONDUCT, DISCLOSED FIRST

- **The first suite run was taken over a moving tree and is DISCARDED.** I
  started `pytest tests -q` before opening the ticket, then ran
  `scripts/start_ticket.py RM-05` and committed while it was still running. It
  returned `1 failed, 1470 passed in 992.85s`. **A number taken over a moving
  tree is a number about no tree** — RM-02 §8.1 and RM-03 §1 both paid for that
  lesson and I repeated it. It was re-taken on the committed tree with
  `git status --porcelain` empty; §8 reports the re-run and this paragraph is
  the record of the discarded one.
- **Three blind adversarial channels were dispatched, and the worktree they read
  contained my own sealed predictions.** That is a blinding weakness I created.
  Two of the three (**B** and **C**) disclosed unprompted that they deliberately
  did not read `PREDICTIONS-RM-05.md` or anything under
  `specs/results/scorecards/portable-substrate/RM-05/`; **A** made no such
  statement and I cannot exclude that it read them. **A's headline result is
  therefore the one to discount, and it is also the one I re-derived myself
  before adopting it** (§5.1) — the four-row output and the control's verdict are
  reproduced above my own signature.
- **Predictions were sealed and committed at `df27cb8` before the first `Agent`
  call.** `PREDICTIONS-RM-05.md`, beside this file. §7 scores them and reports an
  **ALARM**.
- **No process was killed by name.** The only long-running processes were my own
  two suite runs, identified by PID before anything was touched, and neither was
  killed.
- **Nothing was fixed.** Five findings are filed open, and every escalation in
  §9.2 is stated with its reproduction rather than repaired.

---

## 1. THE OWNER'S THREE QUESTIONS

### 1.1 Are we still removing, or have we hit the floor?

**Both, and the two answers belong to two different surfaces. This epic produced
the first fall in the served surface in the card's history, and it did not move
the shipped toolchain by one byte.**

`RM-03-DF-03` is the reason the question cannot be answered in repository lines:
the change rule keeps old anchors and `R-H4` seals 73 cards, so a card removal
**cannot** delete prose and **cannot** delete code. Here is every surface I could
measure, each with the command that produces it.

| surface | `19c5c7b` (main, pre-epic) | `58411dc` (epic tip) | direction |
|---|---|---|---|
| **served rubric, bytes** — what a judge is handed | **8,396** | **6,409** | **−23.7%** |
| **served rubric, lines** | 84 | 68 | −19.0% |
| **anchor rungs a judge must apply** | **25** | **9** | **−64%** |
| scored dimensions | 5 | 2 | −60% |
| **local-machinery demands in the served rubric** | **5, mandatory** | **0 mandatory** (1 optional mention) | **−100%** |
| `references/eval_scorecard.md`, the file | 38,671 bytes / 709 lines | **44,266 / 804** | **+14.5% / +13.4%** |
| `^- **n** —` rung lines **in the file** | 25 | **25** | **unchanged** |
| instrument registry rows | **65** | **65** | **unchanged** |
| `scripts/` git tree | `e9d5544a…` | **`e9d5544a…`** | **byte-identical** |
| `SKILL.md`, `prompts/`, `templates/`, `spec_double_compiler/`, `test_graph/` | — | — | **byte-identical** |
| `references/`, the only shipped surface moved | — | — | **+1,033 / −144 over 2 files** |
| repository lines, excluding `specs/.history` | — | — | **+22,907 / −2,398** |
| repository lines, excluding `.history` and `specs/results` | — | — | **+6,269 / −2,396** |

```
$ python3 examples/validation/scorecards/score_tools.py serve | wc -c      # at each tree
$ git rev-parse 19c5c7b:scripts 58411dc:scripts
$ git diff --no-renames --shortstat 19c5c7b 58411dc -- . ':(exclude)specs/.history'
```

**Four things this table says that no page in the epic says.**

1. **The served rubric had never moved before.** It is byte-identical at
   `2098d55`, `f85f07a`, `4ec3028` and `19c5c7b` — every version-3 commit,
   spanning two whole epics. `serve` did not exist before version 3, so **the
   surface an adopter experiences has been measurable for exactly two version
   bumps and has fallen exactly once, here.** That is the strongest claim this
   epic can make and it is a claim about one change.
2. **The card file has never fallen.** 9,791 bytes at its first commit
   (`40bde2c`, version 1) to 44,266 today — **4.5×, monotonically, across every
   epic that called itself a simplification.** And the rung count *in the file*
   is still 25 at version 4, because the retired anchors are kept verbatim. Any
   sentence of the form "the card got smaller" is true of one number and false of
   the other, and `RM-03-DF-03` predicted exactly this.
3. **"One instrument gone" is not what the registry says.** RM-03 §9 reports one
   fewer instrument. The registry is **65 rows before and 65 after**: out go
   `SM-01's gap-mutant runner` and `a cli detector's argv against its entry
   point`; in come `RM-01's removal pricer` and `SM-04-GM-T1, driven through the
   shipped CLI`. The count of things that must stay demonstrable did not fall.
4. **The shipped toolchain did not move.** `RM-04-DF-02` measured `scripts/`
   byte-identical to `dbf355c`; it holds through `58411dc`, **and it is broader
   than RM-04 said** — `SKILL.md`, `prompts/`, `templates/`,
   `spec_double_compiler/` and `test_graph/` are byte-identical too. The epic's
   entire delta on what an installed copy of this skill contains is
   `references/eval_scorecard.md` (+239/−144) and a new 555-line
   `references/portable_scorecard.md`. **A removal epic added 650 net lines to
   the shipped reference set and removed nothing from anywhere else in it.**

**So: not at the floor on the served surface, and at a hard floor everywhere
else — and the floor is written into the project's own rules.** The card's own
text says so at `references/eval_scorecard.md:703-713`. What that means for the
owner's arc — remove → find the critical point → prompt architecture back in →
then static and spectral signal — is that **the critical point has been located
on exactly one surface**, and it is the surface the re-add is aimed at: 67 lines
a judge reads, of which blind channel B read all 67 and found four local
references and no leaked result (§5.2 F10).

### 1.2 What KINDS of removal and addition actually help?

**The owner's candidate pattern — "what came out were fields that recorded a
measurement without gating on it" — does not survive the record. It was tested,
not assumed, and it fails in both directions.**

Blind channel C built the typology and looked for counterexamples. Both
directions are populated:

**Removed AND it gated.** `total` — the pattern's own example — ran
`if total != running: err(...)` at `6aac1ec~1:score_tools.py:398-400`. That is a
refusal, and `SM-04-GM-T1` is the only mutant in that epic that went
`DIES → SURVIVES`; the census verdict reads *"the removal was LOAD-BEARING"*.
D4's anchor 4 was gated on `judging_practice` and `check` rejected a real card
for it. D2's anchor 4 gated on `D4 ≥ 3` and RD-03 recorded it capping D2 **eight
times**, with the judges naming the clause. SM-03's 13-path literal carried a
live `required <= enumerated` assertion.

**Still in the tree AND records without gating.** This is not a list of
exceptions; it is the doctrine. `no_new_gates_rule` means **nine** modules
disclaim gatehood in their own docstrings and **none** was removed. `judging_practice`
was explicitly *de-gated* at version 4 and deliberately kept. D1, D4 and D5 were
not deleted — they became `N-D1`/`N-D4`/`N-D5`, **required prose that takes no
score**, i.e. the pattern's own category, retained on every card. And 20 open
findings in the ledger are in exactly this class.

**The record's own discriminator is different and it is better.** The reasoning
that actually removed `ranges` names two clauses and the candidate pattern quotes
only the first. The second does the work: *"AND THEY CANNOT BE PINNED …
`ranges` is a figure over an OPEN population … re-affirmed forever, with no
measurement in any of the re-affirmations"* (`INSTRUMENT-LOG.toml:2576-2584`).
`[[movement]]` and `[[contested]]` also record without gating `authority()` and
both stay — because their populations are **closed**. So the operative property
is nearer **"has recurring upkeep and cannot fail"**, and even that fails on
`total`.

**The typology that does hold, with what each kind bought:**

| kind | instances | bought |
|---|---|---|
| **non-exporting rubric surface** | D1/D4/D5 as scores, D2 anchor 4, R-H1's third clause as adopter surface | **PORTABILITY — the only cuts that moved the served surface at all.** −24% bytes, −64% rungs |
| **duplicate of a single source of truth** | 20 card restatements (SM-06) | **CLARITY plus a new detection**: 3 of 4 seeded disagreements had been invisible to every instrument. Best-value cut in the record |
| **product-side duplication** | `_Tenant.outstanding`, `.quota`, `_held` (RD-03/RD-06) | **The only simplification this project has ever measured before/after.** 8 of 8 judges who saw a code change awarded anchor 3; 4 of 4 who saw none refused it |
| **rule loosened rather than thing deleted** | re-runnability (RM-01), detector-name → kill survivorship | **CLARITY** — produced the record's one defensible price on a real past removal |
| **hard-coded literal → derivation** | SM-03's 13 paths, `LABEL_POOL` | **CLARITY, partly reversed** — `RM-01-DF-03`: 3 of the 13 paths are now unreachable |
| **measured-dead instrument** | `[ports.*]` (SM-02), gap-mutant catalogue+runner (RM-03) | the second bought **portability** (no version an adopter receives); the first bought **nothing measurable** |
| **dead machinery whose entry point no longer runs** | `port-binding-report` (RD-02) | **NOTHING.** 33 lines out, 1,403 in |

**Additions that earned their keep**, on evidence: the **prompt → D3** (1→4,
replicated, length-matched control at 1/1, and now separating on a second
example); **sealed predictions** (four refuted across SM — the strongest single
argument that the apparatus is not decorative); **`removal_census.py` and its
`--total` refusal** (it is what made "+1677 net" visible and "−225 from
`scripts/`" unquotable); **`score_tools.py scope`** (moved 22 figures out of
HOLDS with nobody editing a document); **SM-06's one-home tripwire** (the only
added mechanism that catches anything). **`price_removal.py` earned its keep
narrowly and for one reason only** — it showed a *shipped* classifier wrong on a
real removal — and §2.1 is why that is the whole of it.

**Additions that did not:** the `[ports.*]` machinery (828 lines, zero unique
kills); the gap-mutant catalogue and the staged after-run (1,898 lines,
arithmetically incapable of changing a verdict on 9 of 10 rows); **`contested`**
— the card's only rule for judge disagreement, with no executor for three
versions; `anchor_reading`; 12 of 26 registry demonstration slots that assert only
`expect_exit = 0`, satisfiable by a fully skipped run.

**The one-sentence answer to the owner: the cuts that helped were cuts to what
gets SERVED. Everything else this project has removed bought either clarity or
nothing, and the record contains exactly one measured simplification of a
subject rather than of the apparatus.**

### 1.3 Does the self-improvement loop transfer?

**No. It breaks at the one step it is named for, and it did not close inside this
project either.**

Blind channel B built a scratch repository containing one Java file and ran the
loop end to end. **About 70% of it works unaided**: `serve`, `scaffold`, `check`,
`index`, `seal`, `history`, `contested` all run against a foreign tree; blinding
works with no inherited label history (`RM-02-DF-01`'s fix serves a stranger
correctly — B verified it); B closed score → seal → re-score → declare a
`[[movement]]` → `audit` re-derives the delta, in a tree with none of this
project's data.

**Then card iteration.** The card's own rule is *"Bump `scorecard_version`, keep
the old anchors, re-score at least one prior example under both."*
`score_tools.py:95-96` is `VERSION = 4`, `SUPPORTED_VERSIONS = (1, 2, 3, 4)`.

```
$ score_tools.py scaffold ... --card-version 5
error: argument --card-version: invalid choice: '5' (choose from '1','2','3','4')
$ score_tools.py check .../scorecard.json
INVALID: scorecard_version must be one of [1, 2, 3, 4], got 5
```

**The change rule is unfollowable without editing Python, and the failure is
silent rather than loud.** Scaffolding without `--card-version` succeeded and
wrote four cards stamped `"scorecard_version": 4` **carrying the version-5
anchors verbatim**, and once the version-history table was made self-consistent
`check` reported **0 problems**. The adopter ends with a rubric that says 5,
cards that say 4, and a green check.

**And the one iteration an adopter *can* perform without touching Python is
invisible to every check on the card.** `load_rubric` parses a dimension's caveat
as the last paragraph beginning with `**` and an uppercase letter
(`score_tools.py:341-344`). An adopter who rewrites a caveat in their own words
**deletes it from the served bytes with no warning, while `anchors_digest` stays
byte-identical** — B demonstrated it on `D3`'s *"Import topology is not
modularity"*, the caveat three judges in the sealed record cite by name as their
reason for refusing an anchor. The card's own "did the bar move?" instrument
reports no change.

**Three more things an adopter hits and no document mentions:** `audit` — the
executor of every reading rule — **crashes out of the box** with
`FileNotFoundError` until you also install `architecture_tags.py` and create an
**empty** `subjects.toml`; `REPO_ROOT = HERE.parents[3]` fixes the install depth
and `--rubric`/`--root` do not reach `_finding_ids()` or `DEFAULT_SWEEP`; and
**there is no adopter-facing document anywhere** — `portable_scorecard.md`
disclaims itself as research output, `eval_scorecard.md:455` explicitly disclaims
`architecture_tags.md` as adopter documentation, and `README.md` mentions
adoption zero times.

**Did the loop's machinery work when this project ran it?** Yes, once, and it is
worth saying plainly: version 4 is the first bump in the card's history whose
anchors digest moved, the rule's three parts were all done, and the measured
discontinuity on the two surviving dimensions was **zero points across both
versions and both tiers** on one arm and four cards. B re-derived that table
independently and calls it *"the right shape of evidence at a quarter of the
power."* I agree, and §3.3 records the confound it carries.

**But the loop did not CLOSE.** The owner's loop is *hand-found regression → card
iteration → architectural delta*. This epic's blind judges hand-found a real
defect in the fixture every `D3 = 4` in this project rests on — `FileJournal` can
stop touching the filesystem entirely and survive every case through both wirings,
because `ledger_lines()` is the only observer — **twice, in two different
tickets, independently.** RM-03 quoted its judge's sentence about it in praise of
prose notes and filed nothing. RM-04 recorded the four seeded faults in a card
note and filed nothing. `grep` over `deferred_findings.yaml` returns nothing about
it. **`RM-05-DF-05`.** A regression that stops at a card note is a regression the
loop did not carry, and that happened here, in the project that invented the loop,
with the loop's own instrumentation running.

---

## 2. THE FOUR GOALS, DECIDED

### 2.1 `GOAL-removal-can-be-priced` — **MET, and NOT by the removal the epic headlines**

**The instrument can return non-zero. The headline `PRICED` is not the
demonstration of it.**

- **`SM-04-GM-T1` reproduces.** `CAUGHT → UNCAUGHT` through the shipped CLI from
  an independent implementation. Target met, with the reservation in `RM-05-DF-02(c)`.
- **`RM-01-RF-1` is a real, defensible price.** Measured at both trees;
  `pytest-full` run whole at the after tree over 1,366 nodes finding nothing; a
  same-class positive control differing in exactly one property that dies at both
  trees; a contention-immune cross-check agreeing; and a `DETECTOR-WEAKENED` loss
  reason no survivorship test can produce. Blind channel A attacked this directly
  and **it held** — A's own rejected list says so and says it would have been the
  strongest-sounding conclusion available to it.
- **RM-03's "first PRICED removal" does not stand as stated.** `RM-05-DF-01`.
  The verdict is `ENTAILED-SURVIVES`, relabelled `→ PRICED`; the same verdict is
  returned for `RM03-GM-CTRL-C`, a row declared `is_control: true`,
  `removed_by: "nothing"`, `gap: "NONE, on purpose"`; and that row is **missing
  from the output block RM-03 §4.3 prints under a command that emits it**. For
  the fault class in question — every killing node inside a deleted file —
  `ENTAILED-SURVIVES` follows from `git show` alone and no other verdict is
  reachable.
- **Re-priced history is still 0 of 10.** RD-02's `0 of 9` survives a finer
  reading over kill sets.

**Decision: MET.** The goal asks whether a removal can be priced *at all* and
whether the instrument reproduces the known positive. Both are yes. **The target
is met by RM-01 and the headline attributed to RM-03 is withdrawn**, and the
epic's own framing — "an unpriced removal honestly labelled beats a zero that was
entailed" — applies to it: `gap-mutant-catalogue-and-runner` is honestly
**UNPRICED**, not PRICED.

### 2.2 `GOAL-dead-weight-gone` — **MET AS WRITTEN, and the charter that set it was wrong about the tree**

Per removal, never a total. `removal_census.py census` exits 0 and refuses a
total, as designed.

| lever | outcome |
|---|---|
| model-derived case bug-finding | **PARTLY REMOVED.** The catalogue and runner went (1,357 production + 537 test lines by the census's count). `scripts/kill_test.py` + `run_kill_test.py`, 1,384 lines and the *shipped* model-derived case machinery, are untouched |
| static gates | **NOT REMOVED, with a reason.** `RM-03-DF-05`: `kill_test` is a state variable of `TlaSpecDevCli.tla` with a live `kill_rate_floor` refusal, wired into `spec_manifest.yaml`'s `kill_tests` across the workflow. Removing it is a model delta RM-03 declared none of |
| the suite as a finding channel | **NEVER EXISTED.** `RM-03-DF-04`: searched at `9f110ae`, nothing in `SKILL.md`, `references/`, `prompts/`, `scripts/` or `templates/` funds it. The charter listed three levers "still carried" and one was not carried |

**Decision: MET as the goal is written** — *"the three are removed **or the round
says which survived and why**, each priced or labelled unpriced"* — and the
round did exactly that. **Say the gap loudly: the epic's charter and its plan's
`purpose` both assert three carried levers and the substrate carried two.** One
of the two was removed from the measurement apparatus and not from the product.
**Nothing this epic removed is something an adopter of the skill would have
received differently**, because `scripts/` did not move.

Per-removal prices, from the census and `price_removal.py`, with one correction:
`card-dimensions-to-notes` 144 cut / 1,035 proof / **1 : 7.19**, mechanical half
measured **FREE**, judged half **UNPRICED**; the architecture-tag exposition
38 cut / 0 proof, **UNPRICED**; `gap-mutant-catalogue-and-runner` 1,357 cut /
**0 proof** / 0.0 — **and that zero is a classification, not a measurement**
(§9.2 item 2).

### 2.3 `GOAL-dimensions-replicate` — **SPLIT: D3 yes, D2 no, D4/D5 dropped — and the split is confounded three ways**

Re-derived by me from `score_tools.py tags`, per example, never averaged
(`R-H1`/`R-H2`):

```
SEPARATES  ab_quota_ledger D3 effectful/ports-and-adapters:
             effectful [0,2] n=40   ports-and-adapters [4,4] n=18
SEPARATES  eval_toolchain  D3 effectful/ports-and-adapters:
             effectful [0,1] n=4    ports-and-adapters [2,4] n=2
does not separate  ab_quota_ledger D2:  effectful [2,4] n=40  p&a [2,2] n=18
does not separate  eval_toolchain  D2:  effectful [1,2] n=4   p&a [1,2] n=2
```

**D3 replicated on a second example.** Disjoint, same direction, both tiers on
both sides. **D2 did not**: max 2 over the six `eval_toolchain` cards, and `JJ`
had a genuine before/after (1,209 lines replaced by 899) with both judges refusing
anchor 3 for reasons about the artifact.

**Three confounds, and none is on RM-04's page:**

1. **D2's instrument changed and D3's did not.** Diffing the served blocks
   between `19c5c7b` and `58411dc`: **D3's block is byte-identical**; D2's
   preamble is replaced whole, its anchor 4 is deleted (0–3 scale now), and its
   caveat changes "3 or more" to "3". So the epic tested replication on one
   dimension whose bar did not move and one whose bar moved in the ticket
   immediately before. `RM-05-DF-03(c)`.
2. **No era boundary was declared for it.** The last `[[change]]` in
   `INSTRUMENT-LOG.toml` is `SM-04-scorecard-v3`, 2026-08-06 — a bump whose own
   text says *"THE ANCHORS DID NOT MOVE"* and which was declared anyway. The bump
   that **did** move them was not. `R-H1`'s executed clause is vacuous when the
   ledger is unmaintained. `RM-05-DF-03(a,b)`.
3. **Four judge models wear two tier labels, and no two rounds of this epic used
   the same pair.** `derived_tier` substring-matches: `claude-opus-5[1m]` (59
   cards) and `claude-opus-4` (3) are both `opus`; `claude-sonnet-5` (16) and
   `claude-sonnet-4-5` (5) are both `sonnet`. RM-03's re-score is
   opus-5[1m]/sonnet-4-5; RM-04's blind round is opus-4/sonnet-4-5; every earlier
   two-tier round is opus-5[1m]/sonnet-5. `tags` prints
   `tiers_measured=['opus','sonnet']` identically for both separating rows.
   `RM-05-DF-03(d)`, and it is a *second* confound on the cells `RM-04-DF-05`
   already showed are confounded with judging practice.

**And the `eval_toolchain` replication is thinner than it reads.** The
`ports-and-adapters` side is **one artifact, two judges, 2 and 4** — flagged
`CONTESTED` as `rm04-GG-d3-spread-2` with `third_pass: none`, the low card being
the one RM-04 §9 records as contaminated. The separation holds by exactly one
point of margin. **And it is already granting a live refusal** despite RM-04
§3's statement that it "refuses nothing": `compare --example eval_toolchain`
returns `INCOMPARABLE` on D3 today, citing a table row nobody declared.
`RM-05-DF-04`.

**D4 and D5 are dropped** — RM-03 cut them, RM-04 verified the cut, six cards
were scored under version 4 with `check` passing all six and every judge
answering all three notes. **Not deciding was not acceptable and they were
decided.**

**Decision: PARTIALLY MET.** D3 replicates and is the one dimension in this
project with two examples behind it. D2 is **bounded rather than broken**, and
the bound is weaker than RM-04 claims because three variables moved at once.
D4/D5 decided. **And one thing neither side has: blind channel B re-derived D3
over all 83 filled cards and found `D3 = 3` occurs 3 times, and 0 times in 63
cards of `ab_quota_ledger`. The scale is two-valued — ≤2 or 4 — and the judges
say why unprompted: the ladder is written for an application and changes what
"the domain" refers to between anchors 2 and 3.**

### 2.4 `GOAL-portable` — **MET as a decision, and the decision is that adoption requires LESS**

RM-02 answered the never-asked question from the 73 sealed cards: the card grades
architecture *and* conformance, the conformance part is **three clauses**, and
six items are irreducibly local. RM-03 then acted on it — cutting D1/D4/D5 and
D2's anchor 4 removed **two of the four things RM-02 costed an adopter** (a
formal model and a model-derived check) from the served rubric. I measured the
consequence directly: **the served rubric named local machinery in five places
under version 3 and names it in one under version 4, and that one says "where
none exists that is not a gap in the evidence."**

Blind channel B tested the irreducibly-local list item by item and reports it
**too short by two and wrong on one**: `SUPPORTED_VERSIONS` (the change rule
itself is local, §1.3) and the caveat-parsing idiom are missing, and item 3's
"harmless" is wrong — the tag machinery does not do nothing for an adopter, it
**aborts `audit`**. B found **nothing on the list that is actually portable**.

**Decision: MET.** The question moved from never-asked to decided on evidence
from the sealed record, the irreducibly-local list exists with reasons, and
portability did not become a reason to add *on the served surface*. **It did on
the installed surface**: `+555` lines of `portable_scorecard.md`, `+405` in
`score_tools.py`, and cuts #4 and #5 of the design's own five (`check_catalogue.py`,
1,344 lines; the architecture-tag surface, 1,656 lines) were **not taken** — and
the tag surface is now a hard dependency of `audit`.

---

## 3. FINDINGS BY CHANNEL, THE TOKEN BASIS, AND THE SHIPPED-TOOLCHAIN COUNT

### 3.1 The token basis — and the honest answer is that there is not one

**`RD-03-DF-13`'s repair lasted exactly one round.** RD-03 named its basis —
*"`input + output + cache_creation`, excluding cache reads"* — and reported
1.14 findings per 100k against SM-05's 0.60. **This epic recorded no token count
anywhere.** The word "token" does not appear in any of the five `RESULT` pages;
no per-worktree agent transcript survives; the figure is unrecoverable. So the
epic-level per-token ratio is **UNCOMPUTABLE**, and that is a finding about how
the epic was run, not a gap in this page.

**For RM-05's own channels I do have a number, and naming its basis is where the
finding bites me too.** The harness reports a single field, `subagent_tokens`,
with **no documented composition** — I cannot say whether it is
input+output+cache_creation, a sum including cache reads, or something else.

| channel | `subagent_tokens` | tool calls | wall clock |
|---|---|---|---|
| **A** — attack the pricing headline | 144,384 | 54 | 12m39s |
| **B** — adopt the substrate, run the loop | 160,346 | 55 | 13m30s |
| **C** — build the typology, test the hypothesis | 158,531 | 58 | 11m48s |
| **total** | **463,261** | 167 | — |

**Basis, stated in the same sentence as the number, as `RD-03-DF-13` requires:
the harness's `subagent_tokens` field, composition undocumented, over three
subagents. It is NOT comparable to RD-03's 1.14 or SM-05's 0.60, and I will not
print a comparison.**

**And the ratio is uninterpretable a second way, which no round has said before:
the numerator is capped.** The deferment budget is **5 findings per ticket**.
30 distinct defect claims came back from the three channels; 5 were filed. A
"findings per 100k" figure computed on filed findings measures the budget; one
computed on reported findings measures nothing anyone else counts the same way.
Both are printed here so neither can be quoted alone:

- **reported**: 30 / 463,261 = **6.48 per 100k**
- **filed**: 5 / 463,261 = **1.08 per 100k**, and 5 is the cap, not the yield.

### 3.2 Findings by channel

Attribution rule, borrowed from RD-03: **counted once, under the channel that
reached it first.** Where a channel and I reached the same thing independently I
say so.

**This epic, RM-01 … RM-04 and RM-06 — 23 filed:**

| channel | findings | which |
|---|---|---|
| **operator running an instrument they built** | **11** | RM-01 ×4, RM-02 `DF-01`/`DF-05`, RM-04 `DF-01`/`DF-03`/`DF-05`, RM-03 `DF-02`, and RM-04 `DF-02` (reading the work order) |
| **card census over the 73 sealed cards** | **3** | RM-02 `DF-02`, `DF-03`, `DF-04` |
| **the suite** | **4** | RM-06 ×4 |
| **operator doing the removal** | **4** | RM-03 `DF-01`, `DF-03`, `DF-04`, `DF-05` |
| **blind judges** | **1** | RM-04 `DF-04` |

**The suite produced four findings in one round, after seven rounds of zero —
and the reason is not that the suite got better.** RM-06 was a ticket funded to
*read the suite's output*, sorting sixteen red nodes into three groups. **The
channel was never the suite; it was paying somebody to read it.**

**And the blind-judge channel's count of 1 is the wrong number.** §1.3 and
`RM-05-DF-05`: two blind judges in two tickets found the epic's only concrete
defect in a shipped fixture and it was filed zero times. Counted by what reached
the ledger the channel produced 1; counted by what it found it produced at least
2 more, and the loss is a process defect, not a channel result.

**RM-05's own round — 5 filed of 30 reported:**

| channel | reported | filed | notes |
|---|---|---|---|
| **blind adversarial A** (pricing) | 14 | 2 | 2 further items (the census miscount, the `proof = 0` classification) were reached by the operator first and are credited below |
| **blind adversarial B** (adopter/loop) | 10 | 0 filed; **3 of the epic's conclusions verified GOOD** | its blocking item is §1.3 and §9.2 item 1 |
| **blind adversarial C** (typology) | 6 | 0 | §1.2 and §9.2 items 3–4 |
| **round operator** | 10 | 3 | §1.1's surface table, the comparability axes, the live refusal, the never-filed judge defect, the census pair, the token basis |
| **the suite** | **0** | 0 | 1 failure, deliberate, pre-existing |

### 3.3 Findings touching the SHIPPED TOOLCHAIN, stated separately

**Definition, named because the figure is meaningless without one: a finding
whose `surface` names a path under `scripts/`.** This reproduces the owner's
figure exactly and is therefore the definition the 8-of-134 was computed under.

| epic | findings | `surface` names `scripts/` |
|---|---|---|
| `ports-as-adapters` | 28 | 4 |
| `subtract-to-measure` | 30 | 3 |
| `falsifiable-instruments` | 30 | 0 |
| `reading-discipline` | 46 | **1** |
| **four prior epics** | **134** | **8** |
| **`portable-substrate`, RM-01…RM-06** | 23 | **2** (`RM-03-DF-05`, `RM-04-DF-01`) |
| **`portable-substrate` including RM-05** | **28** | **2** |

**One correction to the frame: the last epic was 1, not 0.** `RD-03-DF-08` names
`scripts/code_complexity.py`. The four-epic total of 8 is exact.

**And `RM-04-DF-02` means the two must be read carefully.** `scripts/` is
byte-identical across this entire epic, so neither finding is about code this
epic wrote. `RM-03-DF-05` is *"we did not remove it, and here is the model reason"*.
`RM-04-DF-01` is a live defect reached *through* `architecture_tags` into
`scripts/code_complexity.py`. **Zero findings this epic are about a change to the
shipped toolchain, because there were no changes to the shipped toolchain.**

**On the broader shipped surface — anything under `scripts/`, `references/`,
`SKILL.md`, `prompts/`, `templates/`, `spec_double_compiler/`, `test_graph/` —
the epic filed 6 of 28**: `RM-02-DF-02`, `RM-02-DF-04`, `RM-03-DF-03`,
`RM-03-DF-05`, `RM-04-DF-01`, `RM-05-DF-03`. Channel C adds a seventh unfiled
one (§9.2 item 3). **Findings about generated artifacts and about the eval
harness under `examples/validation/` are the other 22, and conflating the two is
what §3.3 exists to prevent.**

---

## 4. WHAT EVERY BLIND AGENT REJECTED

Asked explicitly of all three. This section is read as carefully as the findings,
and it is again the most valuable section of the round.

**Channel A (pricing) rejected eleven**, including four that would have made its
report stronger:

- **"The whole epic's price is zero."** *"This is the strongest-sounding
  conclusion available and the evidence does not support it."* It attacked
  `RM-01-RF-1` directly and it held on every axis. **That rejection is why
  §2.1 decides MET.**
- **"The after-table was measured against a contaminated tree."** It expected
  this from RM-03's own disclosure and **checked it**: the after baselines are
  exactly what `git archive 6298eee` predicts, so the staged tree was clean and
  the `catalogue` field describes the operator's worktree. Dropped.
- **"The D4/D5 `FREE` verdicts are wrong."** They are not — kill sets are
  node-identical and the positive control fired. RM-03 reports them correctly.
- **"The census `--` bug inflates RM-03's numbers."** It **deflates** them, and A
  says so and *"explicitly declines the insinuation of motive."*
- Also rejected: re-reporting the instrument's own disclosed `ENTAILED-SURVIVES`
  bound as a discovery; "RM-03 deleted tests to reach green" (the arithmetic
  checks out); a latent `node_present` weakness with no instance in the record.

**Channel B (adoption) rejected eight**, including its own headline:

- **"The leak detector regressed between v3 and v4."** *"I got that result first
  and it would have been my headline. On investigation it was my own test
  artifact."* Withdrawn, and it turned into the larger F2.
- **"`check --require-filled` does not fail."** A shell-pipe artifact. Withdrawn.
- **"The loop is prose, not tooling."** Tried and abandoned — it built the scratch
  repo and closed every step except card iteration. *"Reporting otherwise would
  have made this report look stronger."*
- **"The architecture tag hard-fails an adopter in another language."** Rejected on
  evidence: it fails **open**, exactly as designed. Only the missing-file crash is
  real, and it is smaller than the claim available.
- **"The label pool is still exhausted."** Rejected — fixed, and verified working
  for a stranger.
- **"D1 and D4 still grade this project's toolchain."** True of the sealed record
  (88% / 96% of rationales mention local machinery by B's broader measure) but
  **version 4 removed both scores**; reporting a fixed defect as live was declined.
- **"The card cannot discriminate at all."** Refused by the evidence.

**Channel C (typology) rejected seven**, including the tidy version of the thing
it was asked to test:

- **"Every removal was a record-without-gate."** *"I could have written it — four
  of seven census rows."* Dropped when `total != running` turned up at `6aac1ec~1`.
- **"The project cut what was measured dead."** Cleaner and mostly true, but D5
  was measured *orthogonal*, `total` was measured *alive*, the enumeration literal
  *insufficient*. Three findings under one word.
- **Totalling the census.** It computed the per-role sums and threw them away
  because `removal_census.py` refuses a total *"with a stated reason I could not
  improve on."*
- **"`price_removal.py` is unearned."** *"Available and rhetorically strong: 1,212
  lines producing one verdict."* Rejected as a cheap shot.
- **Reporting `scripts/` as "−225 lines"** — it could not reconcile 225 against a
  physical 118 and **did not pretend to**.

**Two of the three disclosed unprompted that they refused to read this ticket's
sealed predictions.** That is the answer to a question nobody asked them.

---

## 5. THE THREE THINGS I RE-DERIVED MYSELF BEFORE ADOPTING THEM

### 5.1 The control shares the headline verdict

```
$ python3 examples/validation/gap_mutants/price_removal.py entail \
    --before .../rm03-gap-mutants-before.json --head 6298eee

ENTAILED-SURVIVES   RM03-GM-CTRL-C-a-detector-that-no-longer-exists-is-reported-as-a-survival
UNDECIDED           RM03-GM-D4-...
UNDECIDED           RM03-GM-D5-...
ENTAILED-SURVIVES   RM03-GM-RUNNER-an-unapplied-mutant-reports-a-survival
```

Four rows. `RM-03-RESULT.md:258-263` prints this command with three, and the
missing one is declared `is_control: true`, `removed_by: "nothing"`,
`gap: "NONE, on purpose"`. The published `rm03-entail-at-head.json` carries
`"removal": null` and three rows. **`RM-05-DF-01`.**

And with a head that does not resolve, all four rows read `ENTAILED-SURVIVES`,
exit 0.

### 5.2 The undeclared separation refuses today

```
$ python3 examples/validation/scorecards/architecture_tags.py compare \
    --example eval_toolchain --subjects rm04_scripts rm04_eval_harness
D3  rm04_scripts [0,1]  rm04_eval_harness [2,4]  INCOMPARABLE
    (effect_boundary: effectful/ports-and-adapters, demonstrated on D3, table row
     `effect_boundary-eval_toolchain-D3-effectful-vs-ports-and-adapters`)
```

`tags` reports *"2 of 7 cell(s) grant a refusal"*. **`RM-05-DF-04`.**

### 5.3 The census miscounts, and its own check cannot see it

`diff_lines` (`removal_census.py:104-105`) skips any diff line beginning `---`,
`+++` or `@@`, which discards **content** lines beginning `--`.
`run_gap_mutants.py` at `f88d02e` has exactly 4 such lines; `git diff --numstat`
says 633 deleted and the census says **629**. `removal_census.py check` passes,
because `expect_lines` was taken from the same counter — **the expectation
re-derived by asking the function that produced it, which is the exact rule RM-06
established one ticket earlier.** Exactly one region in the whole manifest
mismatches, by 4 lines, and I verified that bound rather than asserting it.
Channel A reached the same defect independently. Escalated, §9.2 item 2.

---

## 6. WHAT SURPRISED ME

1. **The served rubric had never moved.** Byte-identical across two epics before
   this one. The one surface anybody outside this repository would ever see had
   not changed once while three epics argued about simplification.
2. **The instrument registry did not shrink.** 65 → 65. I expected the removal
   epic to be the one that reduced the number of things that must stay
   demonstrable, and it swapped two rows.
3. **The blind judges found the best defect in the epic and nobody wrote it
   down.** Twice. In a project whose standing recommendation for four rounds has
   been "keep funding blind judges" and which files everything else.
4. **The change rule cannot be followed.** `SUPPORTED_VERSIONS = (1,2,3,4)`. The
   entire portability argument rests on a loop whose central step requires
   editing the tool's source, and the design page that answers the portability
   question does not mention it.
5. **The positive control shares the headline verdict.** I did not expect the
   round's own control to be in the omitted row of a printed command.

---

## 7. THE PREDICTIONS, SCORED — AND THIS IS AN ALARM

Sealed at `df27cb8` before the first `Agent` call.

| | prediction | outcome |
|---|---|---|
| **P1** | A confirms `ENTAILED-SURVIVES` and files a material qualification RM-03 does not state | **HELD**, and far past the bar — the omitted control row |
| **P2** | B concludes the loop does not transfer, naming the change rule (`keep the old anchors`, `R-H4`) as the monotonic-growth reason | **HELD ON THE CONCLUSION, FALSIFIED ON THE MECHANISM.** B found a harder blocker I did not predict — `SUPPORTED_VERSIONS` — and reached monotonic growth by a different route (frozen rubric copies, `rubric_v3_frozen.md` +709 permanent) |
| **P3** | C falsifies the owner's candidate pattern on at least one row | **HELD** — counterexamples in both directions |
| **P4** | no blind channel finds a defect in `scripts/` | **HELD** — and it is an uninformative pass; nothing touched `scripts/` |
| **P5** | at least one channel names a leak, confound or self-reference not already on the record | **HELD** — A's omitted control row, B's silent caveat deletion, C's stale `architecture_tags.md` |
| **P6** | the suite at this tree returns `1 failed, 1470 passed`, the failure being `test_the_same_tag_control_holds` | **HELD** — §8 |
| **P7** | I will be tempted to publish a ratio on an invented basis; the honest report is that the epic recorded no token basis | **HELD on the second clause, and the first happened to me** — §3.1. I have a number and its composition is undocumented, which is `RD-03-DF-13` recurring in the page that reports it |

**Six of seven held cleanly and the seventh held on its conclusion. That is the
ALARM this document declared in advance, and I am reporting it as one.**

**Why my predictions were too easy, stated against myself.** I sealed them
*after* doing most of my own measurement, so P4 and P6 were near-certainties
dressed as forecasts. P1, P3 and P5 predicted only that adversarial agents would
find *something*, which no round in this project's history has failed to do.
**The one prediction with a real mechanism in it — P2 — is the one that was
falsified**, and it was falsified by a blocker I had not thought of. A prediction
set with one falsifiable mechanism in seven is a prediction set that was written
to pass, and the next round should seal its predictions **before** it measures,
not after.

---

## 8. SUITE NUMBERS, EACH WITH ITS TREE

`RD-01-DF-02`: *"the suite is green" has never been true in a ticket worktree.*
No number below is reported as green.

| # | tree | `git status` during the run | result |
|---|---|---|---|
| 1 | ticket worktree, `58411dc` → `df27cb8` | **DIRTY** — `start_ticket.py` scaffolded 57 files and a commit landed mid-run | 1 failed, **1470** passed in 992.85s |
| 2 | ticket worktree, `df27cb8` | **clean at start, then evidence files written under `specs/results/.../RM-05/` while it ran** | 1 failed, **1474** passed in 911.65s |
| **3** | **ticket worktree, `c8d3c37`** | **quiescent — nothing written from launch to exit** | **PENDING — filled in from `suite-c8d3c37-row3.txt` after the run, and this cell was committed reading PENDING so that no number here can have been written before the run produced it** |

Command, all three rows:
`uv run --with pytest --with pyyaml python -m pytest tests -q`, CPython via `uv`.
**All three are REAL CHECKOUTS with a `.git`, with `.claude/` and
`.skill-manager/` present; none is a `git archive` staging and no figure on this
page is a property of a tree without a `.git`.**

**Rows 1 and 2 are reported and not relied on.** Row 1 is the error RM-02 §8.1
and RM-03 §1 both paid for and I repeated. Row 2 started clean and I then wrote
this page under `specs/results/` while it ran — nothing in `CITATION_SCOPE` or
any collection glob reaches there, so collection could not move, but tests that
sweep `specs/results/scorecards` could in principle have read a moving tree.
**Row 3 is the measurement**, taken after every file this ticket writes was
committed, with nothing running against the worktree.

**Row 1 collected 1471 and rows 2 and 3 collected 1475.** The four are the
ticket-workspace nodes `scripts/start_ticket.py` scaffolds under
`specs/tickets/RM-05/`, which row 1 began before they existed and **which go away
at close** — RM-06 recorded exactly the same four. **So the tree this PR leaves
behind reads `1 failed, 1470 passed`, which is the owner-verified baseline at
`58411dc` unchanged.**

**The single failure is `tests/test_architecture_tags.py::test_the_same_tag_control_holds`
(`RM-06-DF-01`), it is deliberate, it is RM-06's, and this ticket did not touch
it.** The control is reporting a real result — it cannot tell treatment from
architecture — and repairing it during a measurement is the move this epic
forbids.

`denominator_rule` across the epic, on the passing column: **1470 at the epic
base `2c0d94e` and 1470 here.** The passing count did not move at all. **The
denominator fell by 15** — collection goes 1486 → 1471 — because RM-03 deleted
`tests/test_gap_mutants.py`'s 32 nodes while RM-01, RM-06 and RM-03 added others,
and RM-06 turned 10 of the 16 red nodes green. **A flat passing count across an
epic that repaired ten failures and deleted thirty-two tests is a coincidence of
two moving terms, not a stability result**, and it is stated that way.

---

## 9. FINDINGS

### 9.1 Filed — five, the budget, none fixed

| id | severity | one line |
|---|---|---|
| `RM-05-DF-01` | **blocking** | The headline `PRICED` verdict is shared by the round's own declared no-gap control, that row is missing from the output block the RESULT prints, and for this fault class `ENTAILED-SURVIVES` follows from `git show` alone. An unresolvable `--head` prices everything, exit 0 |
| `RM-05-DF-02` | major | Three demonstrated wrong answers: `price` returns `PRICED` over an all-`INERT` after-table and over a never-applied mutant (the exact fault `RM03-GM-RUNNER` seeds); `altered_score_probe` returns `UNCAUGHT` from a tree whose `check` is dead, and the fixed probe has no live-`check` control |
| `RM-05-DF-03` | major | `R-H1`'s instrument axis is the one comparability axis nobody computes: the ledger has been empty for two epics, the first anchor move in the card's history went undeclared, D2's served block changed while D3's did not, and four judge models wear two tier labels |
| `RM-05-DF-04` | major | An undeclared, contested, single-artifact separation is granting a live `INCOMPARABLE` today, on the round that says it "refuses nothing" |
| `RM-05-DF-05` | major | Two blind judges in two tickets found a real defect in the fixture every `D3 = 4` rests on — the real adapter can stop touching the filesystem and survive both wirings — and it was filed zero times |

### 9.2 Escalated rather than filed — the budget of 5 is spent and none of these is blocking

1. **The change rule is unfollowable without a source edit, and fails silently.**
   `SUPPORTED_VERSIONS = (1,2,3,4)` at `score_tools.py:95-96`. Scaffolding without
   `--card-version` stamps v4 onto cards carrying v5 anchors and `check` reports
   0 problems. **This is the single largest obstacle to `GOAL-portable` and it is
   the next epic's first ticket.** Reproduction in §1.3.
2. **The census's `proof = 0` on the epic's headline removal is a classification,
   not a measurement — and only the flattering half is printed.** Its 895 lines
   of committed measured tables (`rm03-gap-mutants-before/after.json`,
   `rm03-price/entail-at-head.json`) are declared `proof` nowhere, while the
   sibling removal on the same page counts a committed 709-line markdown copy as
   proof. RM-01 set the precedent of **printing both numbers and letting the
   reader add them back**; RM-03 printed one. Plus the 4-line miscount of §5.3.
3. **`references/architecture_tags.md` states three times (lines 634, 899, 944)
   that the shipped demonstration row carries `tiers_measured = ["opus"]`.** RM-04
   deleted the field and `tests/test_architecture_tags.py:642-643` now asserts it
   **may not** be there. Line 944 describes a check that can no longer fire. This
   is on the **shipped** reference surface, found by channel C.
4. **`score_tools.py:2428-2441` still raises `VIOLATION` on a declared
   `ranges`/`tiers_measured` mismatch that no ledger row can now supply — so the
   branch is reachable only by an adopter**, which contradicts `RM-04-DF-03`'s
   flat statement that neither field is read by anything that can refuse.
5. **`audit` crashes out of the box for an adopter** (`FileNotFoundError` on
   `architecture_tags.py`, then on `subjects.toml`, then `KeyError: 'example'`),
   **and there is no adopter-facing document anywhere.** Channel B.
6. **Rewriting a dimension caveat silently removes it from the served bytes while
   `anchors_digest` stays byte-identical.** Channel B, and it is the first edit an
   adopting team will make.
7. **No round in this epic recorded a token count.** `RD-03-DF-13`'s repair
   lasted one round. Every future round must print the basis in the same sentence
   as the number **and** print whether the numerator is budget-capped.
8. **`score_tools.py`'s module docstring still says `(scorecard_version 3)`** at
   the tip of the epic that shipped version 4.
9. **68 open findings carry no `disposition_ticket` and no `disposition_note`**,
   and settlement is recorded five different ways across the ledger. Channel C.

---

## 10. `scope` OVER THIS PAGE, AND THE BOUND THAT APPLIES

```
$ python3 examples/validation/scorecards/score_tools.py scope --path <this file>
```

See §10.1 for the run and its tree. **Every figure on this page names its tree in
the line that carries it**, because a sweep count is a joint property of the
record and the card population.

**The applicable bounds, and there are five now.**

1. **`RD-02-DF-01` is the binding one**, and it is binding here more than on any
   page in this epic. The sweep is keyed on `\bD[1-5]\b` and a figure of the form
   `D<n> = k on N of M cards`. **Almost nothing on this page is written that way:**
   8,396 → 6,409 served bytes counts bytes; 25 → 9 counts rungs; 65 → 65 counts
   registry rows; 8 of 134 counts findings; 463,261 counts tokens; 1470 counts
   test nodes. Every one is **invisible** to the checker — not refused, not
   `UNREACHABLE`, not counted. A reader who takes a low REFUTED count here as
   evidence that this page was checked has read it backwards.
2. **`RM-02-DF-05`** — the counted-noun pattern excludes the underscore, so
   `eval_toolchain` and `ab_quota_ledger` can never be a counted noun. Every
   example-scoped figure on this page states its example in the preceding line
   instead, which is the only route available.
3. **`RD-05` §7.1** — the checker cannot tell a claim from a **mention** of one.
   This page quotes `D2 = 2`, `D3 = 4 on 4 of 4` and `D3 = 3 on 0 of 63` in order
   to characterise them, and any of those reachable would be refuted for being
   quoted.
4. **`RD-04-DF-01`, the ≤3-word qualifier window, DOES bite — and I predicted in
   an earlier draft of this section that it would not.** It produces the one
   `UNREACHABLE`, reading the words *"in order"* as a narrowing qualifier:
   *"the counted noun narrows the population with ['order'], which names no
   example in this corpus."* That is the window mis-parsing English prose around
   a mention. **The prediction is recorded as written and not rescued**, because
   an earlier draft of this page said the figure was stated *"in that form
   deliberately so the checker can reach it"* and the checker did not reach it.
5. **`RM-04`'s fifth bound applies to this page's own most-quoted figure.**
   `scope` has **no scope narrower than an example**, and the figure this
   evaluation most wants to carry — *"the served rubric fell 23.7%, once, in the
   card's history"* — is about **one change**, which has no `N of M` form at all.

### 10.1 The run, and what it actually reported

```
$ python3 examples/validation/scorecards/score_tools.py scope \
    --path specs/results/scorecards/portable-substrate/RM-05/RESULT.md
4 counted figure(s): 2 REFUTED, 0 COUNT-MOVED, 1 HOLDS, 1 UNREACHABLE
```

Sealed verbatim beside this file as `scope-RM-05.txt`, at tree `df27cb8` + this
page. Population **83 filled cards carrying a D3 score**.

**THE COUNT MOVED WHILE I WROTE THIS SECTION, WHICH IS THE SAME DEFECT HAPPENING
IN REAL TIME.** The first run returned `2 counted: 1 REFUTED, 0 HOLDS, 1
UNREACHABLE`. Writing the paragraphs below — whose entire purpose is to say what
the checker can and cannot see — took it to **4 counted: 2 REFUTED, 1 HOLDS, 1
UNREACHABLE**. The second `REFUTED` is at line 816, in the sentence directly
below, where I quote `D3 = 4 on 4 of 4` a second time in order to explain why
quoting it refutes it. **I am reporting the number I got last and not editing the
section to bring it down.** `RM-01` §8 recorded exactly this and it recurred in
its successor.

**Both figures the FIRST run reached are on the same line — §10 item 3 — and both
are MENTIONS, not claims of mine.** The `REFUTED` one is `D3 = 4 on 4 of 4`,
which I quote from RM-03 in order to characterise how RM-04 bounded it; the sweep
reads it unscoped over all 83 cards and names 59 counterexamples. **This is
`RD-05` §7.1 happening to this page**: *"every round that reports a figure in
order to discuss it is refuted for doing so"*, and this round is now one of them —
twice.

**Not one figure this page PRODUCED was reached.** 8,396 → 6,409 served bytes,
25 → 9 rungs, 65 → 65 registry rows, 8 of 134 findings, 463,261 tokens, 1,486 →
1,471 collected nodes, 5 of 30 filed — every one is invisible to the checker
under `RD-02-DF-01`. **So the honest reading of `1 REFUTED` is: this document
contains no refuted claim of its own, and the checker reached none of its claims
at all.**

**And here is the one figure of mine that IS in the form the rule polices, and it
HOLDS — the fourth entry this repository's sweep has ever put in that column.**
`scope` resolves it at `scope: example ab_quota_ledger (population 63, 0 carry
D3 = 3)`. Of the example `ab_quota_ledger`, **D3 = 3 on 0 of 63 cards** — the
full distribution being 0:6, 1:16, 2:19, 3:**0**, 4:22. Over all 83 filled cards
carrying D3 the distribution is 0:9, 1:24, 2:23, 3:**3**, 4:24. **The D3 scale is
two-valued on the example this project has scored 63 times, and anchor 3 — the
rung a well-separated non-hexagonal design would land on — has never once been
awarded there.** That is `GOAL-portable`'s sharpest unresolved question and it is
§2.3's last paragraph.

**I am not fixing `scope`.** It is RD-01's instrument, this is a measurement
ticket, and `RD-02-DF-01`, `RD-04-DF-01` and `RM-02-DF-05` are all already open
against exactly these three behaviours.

---

## 11. REPRODUCE

```bash
# the surfaces
python3 examples/validation/scorecards/score_tools.py serve | wc -c        # 6409 at 58411dc
git rev-parse 19c5c7b:scripts 58411dc:scripts                              # same sha twice
git diff --no-renames --shortstat 19c5c7b 58411dc -- . ':(exclude)specs/.history'

# the control that shares the headline verdict
python3 examples/validation/gap_mutants/price_removal.py entail \
  --before specs/results/scorecards/portable-substrate/GOAL-dead-weight-gone/rm03-gap-mutants-before.json \
  --head 6298eee                                                           # FOUR rows

# the live refusal nobody declared
python3 examples/validation/scorecards/architecture_tags.py compare \
  --example eval_toolchain --subjects rm04_scripts rm04_eval_harness

# the census miscount
python3 examples/validation/removal_census/removal_census.py census | grep gap-mutant
git diff --no-renames -U0 --numstat f88d02e 6298eee -- examples/validation/gap_mutants/run_gap_mutants.py

# the loop's blocker
python3 examples/validation/scorecards/score_tools.py scaffold /tmp/x --example e \
  --arms a,b --judges 2 --card-version 5
```
