# RD-04 — the evidence behind `references/architecture_tags.md`

**A research result. No production code ships from this ticket.** The design is
`references/architecture_tags.md`; this file is the measurement behind it and the
record of what it could not settle.

- **Tree:** `/Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-04`, a
  ticket worktree, at `7514df0` (`feature/RD-04`, branched from
  `epic/reading-discipline`).
- **Analysis:** `analysis/derive_and_test.py`, output preserved verbatim as
  `analysis/run.txt`, machine record as `analysis/result.json`.
- **Instruments used:** `scripts/code_complexity.py` (shipped, report v1) and
  `examples/validation/scorecards/score_tools.py scope` (RD-01, shipped).
  Nothing new was built and nothing was measured that the repository could not
  already measure.
- **Corpus:** the 49 sealed cards under `specs/results/scorecards/`, seven
  examples. `specs/.history/**` is deliberately out — those are snapshots of the
  same cards and counting them would be a denominator about the archive.

---

## 1. What was measured

### 1.1 Derivation over the trees the cards were scored over

Eleven declared scopes. The predicate is in `analysis/derive_and_test.py::derive`
and it reads only figures `scripts/code_complexity.py` already prints.

| scope | iface | eff mods / code mods | state co-location | derived | declared | |
|---|---|---|---|---|---|---|
| `blind/artifact_T` (`arm_b`) | 1 | 1 / 4 | 0.125 | `ports-and-adapters` | `ports-and-adapters` | agree |
| `blind/artifact_U` (`arm_a`) | 0 | 1 / 1 | 1.0 | `effectful` | `effectful` | agree |
| `blind/artifact_W` (`arm_c`) | 0 | 1 / 1 | 1.0 | `effectful` | `effectful` | agree |
| `scripts/` | 0 | 28 / 31 | 1.0 | `effectful` | `effectful` | agree |
| `examples/validation/ab/reference_ports/` | 1 | 1 / 5 | 0.111 | `ports-and-adapters` | `ports-and-adapters` | agree |
| `examples/validation/ex1_scaffold_only` | 0 | 1 / 1 | — | `effectful` | `effectful` | agree |
| `examples/validation/ex4_pipeline_coherent` | 1 | 1 / 21 | 0.100 | `ports-and-adapters` | `ports-and-adapters` | agree |
| `examples/validation/ex3_over_complex` | 0 | 0 / 1 | — | `UNDERIVABLE:no-effect-surface` | `effectful` | **disagree** |
| `examples/validation/ex5_pipeline_divergent` | 1 | 0 / 16 | 0.0 | `UNDERIVABLE:no-effect-surface` | `ports-and-adapters` | **disagree** |
| `examples/validation/ex6_jenga` | 0 | 0 / 6 | — | `UNDERIVABLE:no-effect-surface` | `effectful` | **disagree** |
| `spec_double_compiler/` | 2 | 0 / 3 | — | `UNDERIVABLE:no-effect-surface` | — | — |

**7 decided, 4 refused. Every refusal is the same reason.** Reported as a
refusal, never as `effectful`.

### 1.2 The earn-its-place test

Within the example `ab_quota_ledger`, 34 of its 35 cards map to a scoped subject,
across **eight rounds and all three card versions**. `effectful` = `arm_a` +
`arm_c` (24 cards), `ports-and-adapters` = `arm_b` (10).

| dimension | `effectful` n=24 | `ports-and-adapters` n=10 | verdict |
|---|---|---|---|
| D1 | 2–4 | 3–4 | overlaps |
| D2 | 2–2 | 2–2 | overlaps — **NULL-ENTAILED**, §1.6 |
| **D3** | **1–2** | **4–4** | **SEPARATES** |
| D4 | 2–4 | 2–4 | overlaps |
| D5 | 2–4 | 3–4 | overlaps |

**One dimension of five.** The axis earns its place on D3 and on nothing else —
and **only three of the four `overlaps` cells are measurements**; see §1.6.

### 1.3 The same-tag control

`arm_a` (18 cards) against `arm_c` (6), same example, **same** derived value. If
the D3 separation were about something other than the tag, an arbitrary pair
should reproduce it.

| dimension | `arm_a` | `arm_c` | |
|---|---|---|---|
| D1 | 2–4 | 3–3 | overlaps — control holds |
| D2 | 2–2 | 2–2 | overlaps — control holds |
| D3 | 1–2 | 1–1 | overlaps — control holds |
| D4 | 2–4 | 3–4 | overlaps — control holds |
| D5 | 2–4 | 4–4 | overlaps — control holds |

**The control holds on all five.** It is a control this ticket added; the
earn-its-place test as proposed does not require one, and without it any two
artifacts would pass.

### 1.4 Tier check on the one separation found

| tier | `effectful` | `ports-and-adapters` | verdict |
|---|---|---|---|
| `opus` | 22 cards, 1–2 | 10 cards, 4–4 | SEPARATES |
| `sonnet` | 2 cards, 1–2 | **0 cards** | **NOT MEASURED** |

**No `sonnet` judge has ever scored a `ports-and-adapters` subject on this
example.** Recorded as absent, not as agreement — `absent` and `checked, none
found` are different claims.

### 1.5 The contested spread, decomposed

`toolchain_removal` D3 = 2, 2, 3, 4 is the only contested group in 49 cards and
the only D3 tier split. Each card was attributed to a scope by counting path
references **in its own sealed D3 citations** — no re-judging, no card edited.

| card | tier | D3 | citation counts (`scripts/` / `spec_double_compiler/` / `reference_ports/`) | scope | derived tag |
|---|---|---|---|---|---|
| `K-p1` | opus | 2 | 2 / 1 / 1 | `scripts/` | `effectful` |
| `K-p2` | opus | 2 | 4 / 0 / 1 | `scripts/` | `effectful` |
| `K-p4` | sonnet | 3 | 3 / 4 / 1 | `spec_double_compiler/` | `UNDERIVABLE:no-effect-surface` |
| `K-p3` | sonnet | 4 | 0 / 0 / 1 | `reference_ports/` | `ports-and-adapters` |

**Within each scope the spread is zero.** The four judges scored three subjects.

The cards say so in their own words. `K-p1`'s sixth D3 citation is
`reference_ports/quota_ledger_fake.py` labelled *"Cited as the anchor-4 evidence
I REJECTED, because this is a fixture, not the toolchain."* `K-p2`'s fifth reads
*"WHY NOT 3: declared_interfaces 0, declared_interface_methods 0,
modules_with_effectful_calls 30 of modules 33. No domain inside scripts/ that
does not import its I/O"* — the same three figures this design derives on.
`K-p3`'s five citations are all to the fixture and its tests.

**Limit, stated rather than sold.** Scope choice and judge tier are perfectly
confounded across these four cards. This shows the spread is *explained by*
scope. It does not show tier is not also a factor, and RD-01's other two tier
splits (greenfield D4, greenfield D5) are untouched by it.

### 1.6 Null-entailment — is an `overlaps` verdict a measurement?

**RD-02 measured that a gap mutant can price a removal only if every detector
that killed it is one the removal deletes — 0 of 9 over the sealed table — so its
zero-price results were entailed by the setup rather than measured.** The
earn-its-place test has the same failure mode, and RD-04's first draft did not
state it. Added on reconcile at the epic owner's direction.

A dimension that took **one value** across the whole population cannot separate,
so an `overlaps` verdict there reports the example rather than the tag:

| dimension | values the population took | the verdict is |
|---|---|---|
| D1 | 2, 3, 4 | a measurement |
| **D2** | **2** | **NULL-ENTAILED — no separation was possible** |
| D4 | 2, 3, 4 | a measurement |
| D5 | 2, 3, 4 | a measurement |

**Three of four are measurements; one is not.** The design is unchanged — D2 gets
no refusal authority either way — but it gets none for a *weaker* reason than the
other three, and that must be said rather than folded into a single "overlaps".

### 1.7 The converse — does the derivation entail the score it separates on?

Derivation clause (c) asks for a second implementation behind the seam; D3's
anchor 4 asks for a driven port exercised by a real adapter *and* a fake. Close
enough that the separation could be the predicate encoding the anchor.

**Refuted by the record: `ex4_pipeline_coherent` derives `ports-and-adapters`
under all three clauses and was scored D3 = 3 by both blind judges.** The
predicate does not force a 4.

*Not an R-H2 violation:* this is a claim about the **predicate**, not a
comparison of scores across examples. One counterexample anywhere refutes it, and
no `ex4` number is compared with any `ab_quota_ledger` number.

The clauses remain **correlated** with the anchor. That is a confound the
demonstration table row carries forward; it is not an entailment.

---

## 2. What this would have caught, and what it would not

| the record's cost | would the design have caught it |
|---|---|
| D3 contested 2/2/3/4, both judges saying no new evidence could settle it | **Yes.** A declared scope per card makes the four cards three groups with zero spread. |
| One judge refusing a D3 = 4 its own execution supported "because the port lives in a fixture" | **Yes.** That is a scope statement, and it becomes a field instead of a paragraph. |
| The D3 tier split | **Partly.** It is fully explained by scope here, and the explanation is confounded with tier. |
| `D2 = 2` on greenfield against 3/4 on a before/after — the class that cost an epic | **No.** It is not architecture, it is subject shape, and §9.4 of the design shows it fails the earn-its-place test on the record as it stands. Putting it on the architecture axis would have been the first suppression key. |
| `arm_a` D3 = 2 against `arm_c` D3 = 1 | **No.** Same derived value, one point apart. The design explains none of it and does not grow a value to cover it. |
| Three of five `architectural-coherence` fixtures | **No.** They touch no outside world; they derive `UNDERIVABLE` and stay comparable to everything. |

---

## 3. R3 applied to this ticket's own output

`score_tools.py scope --path references/architecture_tags.md` was run before
sealing, as the work order required.

- **First run: 1 UNREACHABLE.** The figure at line 267 read *"D2 is 2 on 39 of
  39 `ab_quota_ledger` cards"*, and the checker could not resolve the population.
- **The figure was also wrong.** `ab_quota_ledger` has **35** cards, not 39. The
  number was corrected against the cards on disk, not against the sentence.
- **Final run: 3 HOLDS, 0 REFUTED, 0 COUNT-MOVED, 1 UNREACHABLE** — the one
  unreachable figure is a demonstrated failing input left in place deliberately
  and documented where it sits.

**RD-01's instrument caught a false figure in the document that was written to
argue for it, on its first run.** That is the demonstrated value of R3 in this
ticket, and it is recorded here rather than quietly fixed.

### 3.1 And the instrument can manufacture a refutation

`scope` resolves a population from a named *example*. Every figure worth writing
about a tag is scoped by a *subject*, which is neither an example nor an arm.
Take the true figure *"D3 = 4 on 10 of 10 `ports-and-adapters` cards of
`ab_quota_ledger`"* — all 10 cards of `arm_b` carry D3 = 4 and no other
`ports-and-adapters` subject of that example has a card.

| probe | verdict |
|---|---|
| `same_line.md` — qualifier immediately after the count | `UNREACHABLE` |
| `wrapped.md` — the same, wrapped after `10 of 10` | **`REFUTED`**, population 35, *"25 card(s) … do not carry D3 = 4"*, twelve named |
| `qualifier_after_noun.md` — `…10 of 10 cards of the \`ports-and-adapters\` subject of \`ab_quota_ledger\`` | **`REFUTED`**, one line |
| `qualifier_in_aside.md` — `…10 of 10 cards, on the example \`ab_quota_ledger\`, of arm_b's subject` | **`REFUTED`**, one line |

**Every one of those 25 counterexamples is a card about a different subject. The
claim is true and the refutation is manufactured.** All four probes preserved at
`analysis/wrap_probe/`.

**The mechanism is placement, not wrapping**, and the narrower first statement is
corrected here. `scope` inspects a window of at most three words immediately
after the count: a narrowing word inside it is seen (`UNREACHABLE`); the same
word after the card noun, in an aside, or on the next line is invisible, and the
figure is refuted at example scope. *The epic owner could not reproduce the
wrapping instance with different probe text and identified the broader class; the
last two probes were added to confirm it.*

**And a second blind spot compounds it, measured by RD-02.** `scope` is keyed on
a `D[1-5]` token. A four-line probe (`no_dimension_token.md`) carrying four
counted figures — three naming their dimension in words, one naming `D3` —
reports **"1 counted figure(s)"**.

Together: **RD-01's own headline is a scoped claim whose scope nobody stated.**
Its denominator is *figures carrying a dimension token*, not *counted figures*;
its numerator can include refutations that are artifacts of placement rather than
false claims. `REFUTED` is the verdict `GOAL-scope-loss-catchable` counts as its
**headline**, with no target and a high count declared the honest outcome — so a
checker that can both miss figures and manufacture refutations can move that
headline in either direction. Filed as `RD-04-DF-01`.

### 3.2 What this ticket did to the sweep's own counts

At the reconciled tip (`5b3ba21` merged in) the repository-wide sweep reports
**58 counted figures: 26 REFUTED · 11 COUNT-MOVED · 9 HOLDS · 12 UNREACHABLE.**

**Attributed, per the denominator rule:**

| | RD-04's files | everything else |
|---|---|---|
| REFUTED | **4 — every one a probe under `analysis/wrap_probe/`** | 22 |
| HOLDS | 3 | 6 |
| UNREACHABLE | 3 | 9 |
| COUNT-MOVED | 0 | 11 |

**RD-04 discovered no new false claim in the historical record.** Every REFUTED
it adds is a deliberate failing input carrying a README that says so. The
historical sweep is RD-03's job.

**And the denominator itself is not what it looks like** — §3.1: `scope` counts
only figures carrying a `D[1-5]` token, so "58 counted figures" is a statement
about that subset and not about counted figures in this repository.

---

## 4. Cards not mapped, counted rather than omitted

**1 of 49.** `hexagonal-prompting/ab_quota_ledger/20260804-owner-pre`, arm
`A-control-reference` — the owner's non-blind pre-treatment pass, `pass: 0`,
which its own `UNBLINDING.md` records as deciding nothing. It is excluded from
the 34-card comparison in §1.2 and counted here.

---

## 5. Predictions, and how they came out

Committed before the analysis was run, in the order they were formed.

| # | prediction | outcome |
|---|---|---|
| P1 | Architecture separates D3 within `ab_quota_ledger` | **held** — disjoint, 1–2 against 4–4 |
| P2 | It separates at least one other dimension | **FAILED** — D1, D2, D4 and D5 all overlap. This is the finding that shaped the design: authority is per-dimension because the evidence is per-dimension. |
| P3 | The derivation agrees with a hand declaration on every subject | **FAILED** — 3 of 11 disagree, all `no-effect-surface`. This is why `UNDERIVABLE` exists as a first-class outcome rather than a fallback to `effectful`. |
| P4 | The `toolchain_removal` spread decomposes by scope | **held** — three scopes, zero within-scope spread |
| P5 | The same-tag control holds | **held** on all five dimensions |

**Two of five predictions failed, and both failures changed the design.** Per the
standing rule, if every prediction had passed that would have been reported as an
alarm.

---

## 6. Findings filed

Filed, not fixed — this ticket is a measurement.

| id | what |
|---|---|
| `RD-04-DF-01` | `score_tools.py scope` cannot resolve a subject-scoped figure, so every claim the tag design enables lands in `UNREACHABLE`. |
| `RD-04-DF-02` | `ex5_pipeline_divergent` is declared ports-and-adapters by its own prose and derives `UNDERIVABLE:no-effect-surface`: it has 16 code modules and **zero** effectful calls. A fixture built to demonstrate architectural divergence has no outside world to diverge about. |
| `RD-04-DF-03` | No `sonnet` judge has ever scored a `ports-and-adapters` subject on `ab_quota_ledger` (n = 0). The one demonstrated separation the design rests on is single-tier. |
| `RD-04-DF-04` | The `state_colocation < 0.5` threshold is unvalidated: observed values are 0.100–0.125 against 1.000 and no artifact has ever been measured near the boundary. |
| `RD-04-DF-05` | The `toolchain_removal` D3 tier split reported by RD-01 is fully explained by scope choice, and scope and tier are perfectly confounded across its four cards. The split may be a scope artifact; the record cannot separate them. |

---

## 7. Suite

**Run, and the number names its tree, and it is not evidence for anything.**

```
uv run --with pytest --with pyyaml python -m pytest tests -q
2 failed, 1428 passed in 704.99s
```

**In the ticket worktree `/Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-04`.**
The two failures are `RD-01-DF-02`'s known class exactly:
`test_card_has_one_home.py` and `test_code_complexity.py` walk the gitignored
per-checkout homes that `wt new` itself creates. **This tree has four of them** —
`.claude/`, `.codex/`, `.gemini/` and `.skill-manager/` — each holding a full
copy of the card, the instrument and the sealed scorecards, so the same
violation is reported four times over.

**The first run of those two tripwires flagged two files of RD-04's own**, and
those were real:

- `references/architecture_tags.md` restated D3's anchor 3 verbatim in a table
  cell, and again in §2.1;
- `analysis/derive_and_test.py` restated it in a comment — and `.py` files under
  `specs/results/` are deliberately **in** scope for that check, because they are
  generators rather than records.

Both were rewritten to *refer* to the anchor by id rather than repeat its text.
**Zero RD-04 files are flagged now**; every remaining line in both failures comes
from a gitignored home. This ticket adds no production code and no test, so the
suite decides nothing about it either way — but it did catch RD-04 doing the
thing it exists to catch, which is worth recording.
