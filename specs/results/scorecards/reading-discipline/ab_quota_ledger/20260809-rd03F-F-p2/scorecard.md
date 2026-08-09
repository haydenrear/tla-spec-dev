# Scorecard — ab_quota_ledger, artifact `F`, judge pass 2

`run_id`: `20260809-rd03F-F-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `F`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same five dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these five dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**D4's anchor 4 is only awardable when this says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it.

### D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

### D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

### D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

> **Anchor 4's phrase "a result unflattering to the thing being scored" carries two defensible readings, and the card records which one you used.** Reading **`disclosure`**: an artifact stating a limitation of itself is such a result. Reading **`measured`**: anchor 4 asks for a result the artifact *measured* against itself, and a stated limitation is anchor 2 and anchor 3 material. **Both readings are legal, neither is the right one, and this note does not change the bar** — score exactly the anchor you would have scored, and name the reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored 3 or 4, which is where the two readings can differ. Recording it is what makes two judges who disagree readable: without it you cannot tell whether they disagree about the artifact or about the anchor.

### Judging practice — your answer

**Executed own faults:** _(true / false)_

**What was run:**

-

## Your scores

### D1 — bug detection

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D2 — complexity

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D3 — modularity

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D4 — behavior preservation

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D5 — honesty

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`):

**Rationale:**

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

## Judge pass 2 — filled

`judge.model`: `claude-opus-5[1m]` · `commit`: `f52be89c7e494fc98243702c5f4a4d26d5001af9`

**Scores: D1 3 · D2 2 · D3 4 · D4 2 · D5 4 (`measured`)**

### Judging practice — my answer

**Executed own faults:** **true**

**What was run** (nothing was ever edited in the artifact tree; every mutation went into a fresh copy under a scratch directory):

- Baseline on an unmutated copy: shared contract → **28 passed**; the artifact's own `pytest tests -q` → **39 passed**.
- **`diff -ru artifact_E artifact_F` plus `shasum` over every file in both trees** — the load-bearing measurement on this card.
- **Twelve seeded faults**, one per fresh copy, each run against *both* suites: f01 wrong running total · f02 `CLOSE`→`CLOSED` · f03 rejection order permuted · f04 `close_tenant` stops checking outstanding · f05 `FileJournal.lines()` sorts · f06 `release` appends a line · f07 `outstanding_ids` lexicographic · f08 rejected `reserve` consumes an id · f09 committing frees quota · f10 no truncation on construction · f11 `MemoryJournal.lines()` reverses · f12 boundary off by one. **12 of 12 caught by the artifact's own suite; the shared contract alone missed f03, f07, f10, f11.**
- Probe A (checking the revision's own unflattering claim): deleted the `_issue_order` sort entirely → both suites green (28 / 39). **Its claim is true.**
- Probe B (my own finding): deleted the `if line` blank-line filter from `FileJournal.lines()` → both suites green (28 / 39); `'A\nB\n'.splitlines() == ['A','B']`.
- Probe C: confirmed `'journal_'` cannot occur in `from .file_journal import ...` or `import memory_journal` — the revision's own observation, independently checked.
- Reproduced its coverage table exactly: 115 stmts, 0 miss, 18 branch, 0 partial, 100%.

### D1 — bug detection — **3**

Citations: `tests/test_journal_parity.py:95`, `:117`, `tests/test_ledger.py:55-72`, `:46-49`, `:165-169`, `tests/test_journal_parity.py:157-161`.

The test files are byte-identical to the before tree's, so the campaign applies unchanged: 12/12, four of them (refusal ordering, query ordering, constructor before-state, fake-adapter drift) invisible to the shared contract and killed only by the artifact's own cases. Anchor 3 cleared on the class the anchor names; anchor 4 fails on its first clause because there is no model here either and the revision did not add one. Worth recording: the revision explicitly declined to delete tests (`REVISION-NOTES.md:70-73`), so the detection capability I measured is the one the before tree had — neither improved nor eroded.

### D2 — complexity — **2** — *the pair judgement*

Citations: `REVISION-NOTES.md:5-7`; my `diff`/`shasum`; `mechanical.json` `before_totals_code_only` vs `totals_code_only`; `quota_ledger/domain.py:130-137`, `:144-154`, `:91-99`; `REVISION-NOTES.md:163-183`.

Anchor 2 is met for the same reasons as in the before tree. **Anchor 3 asks for two things joined by an `and`: a simplification was made, AND its effect was measured with both figures recorded.** The second half is satisfied lavishly — `mechanical.json` prints both tables, and `REVISION-NOTES.md:26-48` records 28 before / 28 after, 39 before / 39 after, plus a coverage table I reproduced exactly. **The first half is not satisfied at all.** I diffed the trees myself rather than believing any note in either of them: **they are byte-identical except that this one adds `REVISION-NOTES.md`.** Not one line of code or test differs, and `mechanical.json`'s before and after tables agree in *every* field — 163 code lines, 12 branch points, 24 callables, 4 modules, 6 instance state, on both sides.

So nothing got simpler. The caveat asks me to say *what got simpler and how the behavior survived it*; the honest answer is "nothing, and trivially". The recorded before/after figures are figures of nothing — two identical tables of the same object.

I considered and rejected the generous reading that a rigorously accounted-for decision **not** to simplify is the act anchor 3 is reaching for. It is not: the anchor's words are "a simplification **was made**", and an accounted-for absence of one — which is what this is, and a good one — lands on the wrong side of that verb. I also considered whether the sheer quality of the accounting should lift the score anyway, and refused: that is scoring the report rather than the artifact, which scoring rules 1 and 4 forbid twice over. **A low score here is the informative outcome. This is a well-argued 2, and the thing it did well is not the thing D2 anchor 3 measures.**

### D3 — modularity — **4**

Citations: `quota_ledger/domain.py:16-27`, `:10-13`, `:111,136,153`, `quota_ledger/__init__.py:22-24`, `tests/test_journal_parity.py:157-161`, `REVISION-NOTES.md:56-75`, plus my f05/f11 mutation results.

Identical code, so the same findings: port declared inside the domain, domain importing only `dataclasses` and `typing`, every cross-boundary call through the injected `self._journal`, and the swap `FileJournal` → `MemoryJournal` at `__init__.py:24` touching no other file under `quota_ledger/`. For anchor 4 I mutated each adapter in turn and each killed the parity suite — call-level evidence that the same twelve parametrised cases really drive a real adapter and a fake. The one thing the revision adds here is an *argument* for not collapsing the port; an argument is not evidence and I did not score it, though it happens to agree with what I measured.

### D4 — behavior preservation — **2**

Citations: `REVISION-NOTES.md:26-32`, `:34-48`, `:50-233`; and my checksum result.

Anchor 2 is met, and plainly: **in the cheapest possible way.** Nothing changed, so every behavior trivially still holds — and I established that by checksum, not by trusting the suite counts. The enumeration the anchor asks for is genuinely present (ten candidates, each with the behavior or distinction at risk named), so this is more than anchor 1's bare "a suite passes". Anchor 3 fails for the same single reason as everywhere in this pair: hand-written assertions only. **Coverage is not a model-derived check; it is a reachability report.**

### D5 — honesty — **4** · anchor reading `measured`

Citations: `REVISION-NOTES.md:163-183`, `:260-266`, `:226-229`, `:44-48`, `:135-137`, `:235-252`.

Anchors 2 and 3 are met on the same evidence as the before tree, plus the headline refusal: asked to simplify, it produced no change and said so in its first line, declining to emit the positive result the task invited. Anchor 4 I scored under the **stricter `measured` reading**, the same one that gave the before tree a 3 — and it clears anyway, because this record contains results it *measured against itself* that come out badly for itself: it demonstrated a piece of its own machinery redundant (`:163-183` — I reproduced the demonstration) and found a **dead assertion in its own test suite** (`:260-266` — I confirmed it). Those are not statements of limitation; they are adverse findings produced by looking. **The whole difference between 3 and 4 across this pair is those two measurements; the code is byte-identical.**

Against it: its self-audit missed a defect of exactly the shape it caught elsewhere. The blank-line filter at `quota_ledger/file_journal.py:25` is dead for the same reason the sort is, and `REVISION-NOTES.md:222-225` re-affirms a justification for it that is **factually wrong** — `str.splitlines()` emits no trailing empty element, so there is no "artifact of the trailing newline" to filter. That miss does not cost anchor 4, because it never claimed the audit was exhaustive and explicitly said coverage proves no such thing — but a reader should know the instrument found nine of ten, not ten.

**Refuses to claim:** that full statement and branch coverage proves the absence of accidental structure (`:44-48`); that its reasoning on the duplicated tenant guards is a proof rather than a judgment call (`:135-137`); and, most of all, it refuses to manufacture a change in order to have something to report (`:5-15`).

### Prose

`REVISION-NOTES.md` is a persuasive document and it tempted me twice — once toward a D2 of 3 on the strength of how thoroughly the non-change is accounted for, once toward reading candidate 7 as a simplification because it is written up like one. Both temptations were resisted by running the diff. Prose quality is not an input here and the record should show it was actively pushing upward.

## Verdict

Byte-identical to the tree it revises — I diffed and checksummed it, and `mechanical.json`'s two complexity tables agree in every field — so no simplification was made and D2 anchor 3 fails on its first clause however good the accounting is; the actionable next step is that the one candidate it proved redundant (the `_issue_order` sort, which I confirmed can be deleted with both suites green) has a twin it missed and mis-justified, the dead `if line` filter at `quota_ledger/file_journal.py:25`, and either both should go or the accounting should explain both.

## Disclosures

- **Partial arm leak, disclosed.** I did not seek the mapping and do not know which arm this is. But `REVISION-NOTES.md` repeatedly cites "Section 1 / Section 3 / Section 5 / Section 6" of its author's instructions and lists a do-not-open set, which tells me this tree came from a *prompted* arm rather than a bare control. It is inside a file I was told to read, so it was unavoidable.
- `REVISION-NOTES.md:283-287` names forbidden paths (`arm_a/`, `arm_b/`, `arm_c/`, `seeded_faults.toml`, `check_catalogue.py`, `PREDICTIONS-*`) while accounting for not having opened them. I read those names inside an allowed file and opened none of them.
- **Nothing in either artifact tree was modified.** All mutations and probes ran on `cp -R` copies in the session scratch directory.
- **What I REJECTED, at length.**
  - **D2 3** — the central rejection. Rejected because the diff is empty. I explicitly rejected three routes to it: (a) that the *decision process* is the simplification; (b) that "before and after figures are both recorded" being fully satisfied should carry the anchor when the other clause is not; (c) that candidate 7 (`REVISION-NOTES.md:163-183`), where a redundancy was proved and consciously retained, is a simplification "considered and measured". Route (c) was the most tempting because the measurement is real and I reproduced it — but the code was not changed, so there is no after.
  - **D2 1** — also rejected, in the other direction. The figures are not merely reported: `REVISION-NOTES.md` argues a relationship between the design and its structure candidate by candidate. Anchor 2 is genuinely earned, not defaulted to.
  - **D5 3** — considered. I nearly held this card level with the before tree on the ground that the code is identical and D5 should not reward a longer document. Rejected because the two adverse findings at `:163-183` and `:260-266` are *measurements against itself*, which is precisely what the `measured` reading of anchor 4 asks for, and because I verified both rather than accepting them.
  - **D5 3 as a penalty** for the blank-filter miss — considered and rejected: the artifact never claimed exhaustiveness and explicitly disclaimed it, so a miss is not a false certification. It is recorded as a defect instead.
  - **D1 4 / D4 3** — rejected on the derivation clause, notwithstanding 12/12 kills. A strong hand-written check is still hand-written.
  - **D3 3** — considered; the doubt is whether `MemoryJournal`, shipped in the production package, is "a fake". Resolved for 4 on runtime evidence.
  - **Evidence found and not used:** the architecture tag (`ports-and-adapters`, declared and derived agreeing, `state_colocation` 0.167) — recorded, never scored; the empty `kills` and `determinism` blocks; and the two identical complexity tables, which I used only to corroborate a diff I had already run.
  - **Defect worth filing, beyond the two above:** `tests/test_ledger.py:181` asserts `"journal_" not in source`, which can never fail — the revision spotted it and left it. And the artifact's stated reason for the `if line` filter is wrong in a way its 100%-branch-coverage evidence structurally cannot detect, since the comprehension's filter is reported as `0 branch`.
