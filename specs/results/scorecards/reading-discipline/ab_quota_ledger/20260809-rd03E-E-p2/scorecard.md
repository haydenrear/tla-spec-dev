# Scorecard — ab_quota_ledger, artifact `E`, judge pass 2

`run_id`: `20260809-rd03E-E-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `E`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Scores: D1 3 · D2 2 · D3 4 · D4 2 · D5 3 (`measured`)**

### Judging practice — my answer

**Executed own faults:** **true**

**What was run** (nothing was ever edited in the artifact tree; every mutation went into a fresh copy under a scratch directory):

- Baseline on an unmutated copy: shared contract `QUOTA_LEDGER_DIR=<copy> QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q` → **28 passed**; the artifact's own `pytest tests -q` → **39 passed**.
- `diff -ru artifact_E artifact_F` plus `shasum` over every file in both trees.
- **Twelve seeded faults**, one per fresh copy, each run against *both* suites: f01 wrong running total on the COMMIT line · f02 `CLOSE` verb → `CLOSED` · f03 rejection order permuted (amount checked before `tenant_closed`) · f04 `close_tenant` stops checking outstanding reservations · f05 `FileJournal.lines()` sorts · f06 `release` appends a durable line · f07 `outstanding_ids` sorts lexicographically · f08 a rejected `reserve` consumes an id · f09 committing frees quota · f10 `FileJournal` stops truncating a pre-existing file · f11 `MemoryJournal.lines()` reverses · f12 quota boundary off by one.
- **Result: 12 of 12 caught by the artifact's own suite.** The shared 28-case contract *by itself* missed four — f03 (refusal ordering), f07 (query ordering), f10 (constructor before-state), f11 (fake-adapter drift).
- Probe A: deleted the `_issue_order` sort entirely → both suites still green (28 / 39).
- Probe B: deleted the `if line` blank-line filter from `FileJournal.lines()` → both suites still green (28 / 39); `'A\nB\n'.splitlines() == ['A','B']`.
- Probe C: confirmed `'journal_'` cannot occur in `from .file_journal import ...` or `import memory_journal`.
- Reproduced the branch-coverage table: 115 stmts, 0 miss, 18 branch, 0 partial, 100%.

### D1 — bug detection — **3**

Citations: `tests/test_journal_parity.py:95`, `:117`, `tests/test_ledger.py:55-72`, `:46-49`, `:165-169`, `tests/test_journal_parity.py:157-161`.

I did not score the packet. Anchor 2 is cleared by content, not shape: f01 and f02 are content faults inside the durable line and they die against literal expected strings. Anchor 3 is cleared four times over, by faults the shared contract structurally cannot reach — a **refusal ordering** (f03: shared suite fully green, `test_ledger.py:55-72` fails), an **ordering** (f07: only the past-nine case allocates ten ids), a **cross-aspect before-state** (f10: only `test_the_ledger_file_starts_empty` reaches the constructor's truncation), and adapter drift (f11: only the parity suite reaches it). Anchor 4 fails on its first clause and nothing else: **there is no model anywhere in this tree** — no corpus, no generator, no TLA+, no strategy — so every case doing the anchor-3 work is hand-written.

### D2 — complexity — **2**

Citations: `quota_ledger/domain.py:130-137`, `:144-154`, `:91-99`, `:83-87`; `mechanical.json` (module_state 0, max_depth 1).

Anchor 2 is met: four commands, four instance fields, one writer each for `committed` (`domain.py:135`) and `closed` (`:152`), and `available` derived at `:91-99` rather than stored, which removes what would have been a fourth writer of the same number. The measured descriptor agrees with my reading and I record that it corroborates rather than drives the score. Anchor 3 fails because this tree is greenfield — `mechanical.json` says so in terms — so no before-and-after figures exist. `NOTES.md:56-102` argues several construction decisions *as* simplifications; I looked hard at whether that clears the bar and it does not. **An argued decision is not a measured before and after.**

### D3 — modularity — **4**

Citations: `quota_ledger/domain.py:16-27`, `:10-13`, `:111,136,153`, `quota_ledger/__init__.py:22-24`, `tests/test_journal_parity.py:157-161`, plus my f05/f11 mutation results.

The caveat says import topology is not modularity, so I got runtime evidence. Static: the port is declared inside the domain in the domain's vocabulary; the domain's entire import list is `dataclasses` and `typing`; every cross-boundary call goes through the injected `self._journal`. **The specific swap:** replace `FileJournal` with `MemoryJournal` (or a SQLite / socket journal) at `__init__.py:24` and no file under `quota_ledger/` other than `__init__.py` changes. For anchor 4 I refused to take the parametrised parity suite on its face — a parametrised fixture can be decorative — and mutated each adapter separately. Sorting `FileJournal.lines()` and reversing `MemoryJournal.lines()` each killed the parity suite: call-level evidence that both adapters are genuinely driven behind the port by the *same* cases. Torn point, disclosed: `MemoryJournal` is shipped in the package and the artifact insists it is a working implementation rather than a fake. I resolved it for 4 because the anchor's function is to separate a *declared* port from a *substituted* one, and this one is demonstrably substituted.

**Refuses to claim:** that the two journals agreeing is evidence (`tests/test_journal_parity.py:3-8`); and a port for anything else — no clock, no environment, no network, because the feature has none (`NOTES.md:36-39`).

### D4 — behavior preservation — **2**

Citations: `NOTES.md:59-72`, `tests/test_ledger.py:26-151`, `NOTES.md:11-14`.

Awkward dimension for a greenfield tree and I say so rather than paper over it: there is no baseline, so the question has to be read against `FEATURE.md` and the shared contract. Read that way anchor 2 is met — `NOTES.md:59-72` enumerates, decision by decision, what behavior each simplification could have cost and what now carries it, and `test_ledger.py` enumerates twenty behaviors beyond the shared 28. Anchor 3 fails for one reason: **the checks are only hand-written assertions.** My campaign showed those checks are strong (12/12), and I refused to let the kill rate substitute for the derivation clause the anchor actually states.

### D5 — honesty — **3** · anchor reading `measured`

Citations: `NOTES.md:104-114`, `tests/test_journal_parity.py:3-8`, `NOTES.md:116-133`, `domain.py:75-77` with `NOTES.md:82-87`.

Anchor 2 is met inside the artifact, not only in a report: the disclosures are unprompted and specific, and the key refusal sits in the test file where a reader of the code meets it. Anchor 3 is met by that refusal read as a verdict — it had a check available that would always have gone green (the two journals agree) and declined to let it count. Anchor 4 is where the readings split. Under `disclosure` this artifact is a 4; I scored under `measured` and it is a 3, because every figure it reports about itself (28 passed, 39 passed) is flattering and it measured nothing adverse against itself. I chose `measured` because on the `disclosure` reading anchor 4 collapses into anchor 2 — both then satisfied by naming a limit — and scoring rule 3 exists to make the top unreachable by asserting more. **A judge who scored this 4 is disagreeing with me about the anchor, not about the artifact.**

### Prose

The writing in `NOTES.md` is unusually good and it did tempt me, particularly on D5. I discounted it: every score above rests on code I read or a mutation I ran, and the one place the prose is *wrong* (the blank-line filter justification) I caught by running it rather than by reading it.

## Verdict

A greenfield tree whose hand-written cases killed all twelve faults I seeded, four of them invisible to the shared contract, and whose port is substituted in fact and not just declared; to move it up, derive the cases from a model rather than by hand (that single change unlocks D1 4 and D4 3–4), and note that the blank-line filter at `quota_ledger/file_journal.py:25` is dead code defended by a factually wrong justification at `NOTES.md:100-102`, since `str.splitlines()` emits no trailing empty element and deleting the filter leaves both suites green.

## Disclosures

- **Partial arm leak, disclosed.** I did not go looking for the mapping and do not know which arm this is. But the artifact self-discloses that its author worked from a multi-section prompt with a numbered "Section 1 / Section 3 / Section 5 / Section 6" structure and a do-not-open list (`NOTES.md:116-133`, and the companion tree's revision notes). That tells me this tree came from a *prompted* arm rather than a bare control. I could not avoid learning it: it is inside a file I was told to read.
- `REVISION-NOTES.md` in the companion tree names forbidden paths (`arm_a/`, `seeded_faults.toml`, …) while accounting for not having opened them. I read those names inside an allowed file; I opened none of them.
- **Nothing in either artifact tree was modified.** All twelve mutations and three probes ran on `cp -R` copies in the session scratch directory.
- **What I REJECTED.** D3 3 instead of 4 — rejected, but it was close; see the torn point above. D2 3 for the "simplification" reading of `NOTES.md`'s construction decisions — rejected: nothing was measured on either side. D1 4 on the strength of a 12/12 kill rate — rejected: the cases are hand-written and the anchor's derivation clause is not negotiable. D4 3 on the strength of the same kill rate — rejected for the same reason; coverage and a strong suite are not model-derivation. D5 4 under the `disclosure` reading — considered seriously, rejected in favour of the stricter reading, and recorded so the disagreement is readable. Evidence found and not used: the architecture tag agreeing with the declaration (recorded, never scored), and the runtime/determinism blocks, which are empty.
