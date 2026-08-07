# Scorecard — ab_quota_ledger, artifact `S`, judge pass 1

`run_id`: `20260807-sm05gf-S-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `S`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Executed own faults:** **true**

**What was run:**

- Copied `quota_ledger.py`, `test_quota_ledger.py` and the shared
  `test_behavior.py` to a scratch tree **outside the repository**
  (`$SCRATCH/judge/pristine`). Confirmed the copy is byte-identical to the
  sealed original: `sha256 213b2a5e27c6ec281b7d4c353e4d39d029fe152f49eae187c05fc2fa29458ca3`
  for both. Nothing inside the repository was modified.
- **Baseline:** shared suite + the artifact's own suite together — **60 passed**
  (28 + 32). Both counts in `NOTES.md:24` and `NOTES.md:32` are confirmed.
- **Twelve judge-seeded faults, one at a time, each reverted and each revert
  proved byte-identical by sha256.** Each was run twice: once against the
  artifact's OWN `test_quota_ledger.py`, once against the shared suite,
  scored separately. Classes: guard relaxation (J01 zero-amount guard, J02
  close-with-outstanding guard), durable content (J03 stale running total, J04
  `CLOSE` total forced to 0, J11 durable write on a rejected path), ordering
  (J05 `ledger_lines` reversed, J07 `outstanding_ids` sorted by string id),
  cross-aspect (J06 `commit` refunds the hold), output oracle (J08 `release`
  returns `rejected` while still releasing), wrong value (J09 hold off by one,
  J10 id reuse), plus **a null negative control** (comment-only edit).

  | fault | class | artifact's own suite | shared suite |
  |---|---|---|---|
  | J01 zero-amount guard | guard_relaxation | KILLED | KILLED |
  | J02 close-with-outstanding guard | guard_relaxation | KILLED | KILLED |
  | J03 stale running total | durable_content | KILLED | KILLED |
  | J04 `CLOSE` total zero | durable_content | KILLED | KILLED |
  | J05 `ledger_lines` reversed | ordering | KILLED | KILLED |
  | J06 commit refunds the hold | cross_aspect | KILLED | KILLED |
  | **J07 `outstanding_ids` string order** | ordering | **KILLED** | **SURVIVED** |
  | **J08 `release` returns rejected** | output_oracle | **SURVIVED** | **KILLED** |
  | J09 hold off by one | wrong_value | KILLED | KILLED |
  | J10 id reuse on release | wrong_value | KILLED | KILLED |
  | J11 durable write on rejection | durable_content | KILLED | KILLED |
  | N null (comment only) | negative control | SURVIVED | SURVIVED |

  My instrument therefore has both a firing positive signal and a green
  negative control on this artifact.
- **Runtime seam trace.** Wrapped `_LedgerFile` and recorded every durable call
  made during a full reserve/commit/close/read cycle: `append('COMMIT acme 3 3')`,
  `append('CLOSE acme 3')`, `lines()` — every cross-boundary operation, and only
  those. Then substituted an in-memory fake and confirmed **no file was created
  on disk**, i.e. nothing leaks past the seam. This is call evidence, not import
  evidence.
- **Adapter-swap attempt.** Ran the shared 28 cases against the in-memory fake:
  **28 passed**. Ran the artifact's own 32 against the fake: **14 failed** (they
  read the real file from disk on purpose). The substitution required rebinding
  the module global `quota_ledger._LedgerFile`; `QuotaLedger.__init__` takes
  `ledger_path: Path | str` and offers no injection point.
- **Reach instrumentation of the artifact's own model-based sweep.** Replayed
  `test_rules_hold_through_a_long_random_sequence` at its pinned seed
  (`random.Random(20260804)`) counting accepted commands. Result below; it is the
  single most load-bearing thing I ran.
- **Claim checks.** Verified `NOTES.md:98-103` (`0.5` → `amount_not_positive`;
  `1.5` accepted, held, and written as `COMMIT acme 1.5 1.5`, leaving
  `available == 8.5`), `NOTES.md:104` (`reserve(t, True)` reserves 1),
  `NOTES.md:89-94` (`available("nobody")` raises `KeyError`), and
  `NOTES.md:108-111` (a closed tenant cannot hold a live reservation). All four
  hold as stated.

## Your scores

### D1 — bug detection

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `test_quota_ledger.py:162-170` — `test_outstanding_ids_are_ascending_past_ten`.
  This is the case that reaches anchor 3, and I verified it: my J07 (sort by
  string id instead of allocation seq) is **KILLED** here and **SURVIVED** the
  shared suite.
- `EVIDENCE.md:81` — the same fault class, seeded by the harness as
  `N01-negative-control-outstanding-id-order`, is **SURVIVED on all eight**
  instruments including `corpus-whole`, `corpus-port` and `map-checking`.
- `EVIDENCE.md:248-253` — and `N01` carries a measured `reality_witness`
  (`on_mutated_tree: true`, `on_pristine_tree: false`, `separates_the_trees:
  true`), so the fault is genuinely present and the whole-view corpus
  structurally cannot express it. That is anchor 3's exact wording.
- `test_quota_ledger.py:85-88` — content asserted, not shape: exact ledger lines
  read off disk by `file_lines(path)`, independently of `ledger_lines()`. Kills
  J03 and J04.
- `test_quota_ledger.py:114-131` and `:265-273` — the refusal classes: a
  parametrized R4 check against the file, and declared rejection ordering for
  `close_tenant`. Kill J11 and J02, where `EVIDENCE.md:118` records
  `corpus-whole` at **0 of 3** on `guard_relaxation`.
- Against anchor 4: `NOTES.md:76-77` states the anchor-3 case was **hand-written**
  to pin an interpretation ("`test_outstanding_ids_are_ascending_past_ten` pins
  my reading"), and no part of the record names the fault class J08 exposes.

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4.

**Rationale:**

Anchor 2 is met without argument: the assertions are on exact durable content
read back off the filesystem, not on shape.

Anchor 3 is met and I verified it rather than reading it: the artifact's own
suite kills a fault in a class the whole-view corpus provably cannot reach on
this model. That is a real result and it is the artifact's, not the harness's.

Anchor 4 fails on both conjuncts. The case that reaches anchor 3 is hand-written
and its author says so. And the record does not name a fault class it cannot
reach — it names *behavioral* open questions (`NOTES.md:87-105`), which is a
different thing. J08 is the counter-example: `release` returning
`status="rejected"` while still performing the release passes **all 32** of the
artifact's own tests. Nothing in `NOTES.md` anticipates that its suite never
asserts `release`'s accepted status.

**Where the ladder broke, and it broke here.** D1 asks about "the model-derived
cases **and their adapters**". This artifact ships neither: it is one module and
32 hand-written pytest functions, with no manifest, no generated corpus and no
adapter layer. The corpus columns in the packet are the *harness's* — `EVIDENCE.md:54-57`
states every corpus is generated from one model and one manifest shared by all
three artifacts with an identical `cases.py` sha1, so a difference between
artifacts there is a difference in the *code's observability*, never in that
artifact's bug detection. I therefore scored the artifact's own detection
apparatus. I checked that the other reading does not move the score: scoring the
harness columns also lands on 3 (`corpus-neg` reaches the refusals `corpus-whole`
misses, `corpus-slice-led` reaches an ordering), so the ambiguity is not
load-bearing here. It would be on a subject where the two diverged, and this
ladder gives a judge no rule for choosing.

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger.py:103-110` — six pieces of instance state for four commands and
  five queries, each introduced once.
- `quota_ledger.py:150` and `quota_ledger.py:180` — `_available` is written in
  exactly two places, `reserve` and `release`, the two commands that move a hold.
  `_committed` is written at `:170` only; `_closed` at `:194` only. No variable
  is written from everywhere and there is no god-state.
- `quota_ledger.py:72-92` — the entire durable side is one 20-line class with two
  methods.
- `quota_ledger.py:28-37` and `:58` — the rejection vocabulary exists once and is
  enforced once, rather than being re-remembered at each of the six call sites.
- `quota_ledger.py:199-205` — `_Reservation.seq` is redundant with
  `reservation_id` (`f"r{seq}"`), which is the one place carrying a derivable
  field. It is the only accidental structure I found and it is small.

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4.

**Rationale:**

The design's complexity is proportional to the behavior FEATURE.md asks for. Ten
branch points across nine public operations, max nesting depth 1, every guard
sequence in the order the specification lists it. I could not find a structure
present for a reason other than the behavior.

**Where the ladder broke, and it broke badly.** This ladder assumes a
*refactoring* subject. Anchor 3 requires "a simplification was made and its
effect measured — the before and after figures are both recorded" and anchor 4
builds on it. **A greenfield artifact has no before.** Nothing was simplified
from anything, so anchors 3 and 4 are unreachable by construction, not by
shortfall, and this artifact's D2 is capped at 2 no matter how good it is. A
reader comparing this 2 against a 3 earned by a refactoring subject would be
comparing two different questions.

Anchors 0 and 1 break in the other direction. The artifact does not measure its
own complexity at all — which reads literally as anchor 0, "complexity is
unmeasured". But the complexity that exists is measured, in the packet's
mechanical block (`EVIDENCE.md:310-328`), which rule 7 forbids me converting into
a score. And anchor 1's description ("measured and reported; no relationship
argued") is the inverse of this artifact, which reports no figures but *does*
argue the relationship between structure and behavior (`NOTES.md:34-45`,
`NOTES.md:114-118`). There is no rung for "no self-measurement, demonstrably
proportional design". I scored 2 on the structural bar, which is the only part of
anchor 2 that is a judgement rather than a measurement premise, and I am
recording that I had to stretch to do it.

I did not use `code_lines 151` or `modules 1` from the mechanical block. Rule 7,
and MF-020: this artifact is smaller than artifact T's four modules partly
because it declares no interfaces at all, which is a D3 debit, not a D2 credit.

### D3 — modularity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger.py:110` — `self._ledger = _LedgerFile(ledger_path)`. **The domain
  constructs its own I/O.** This is the line that stops anchor 3.
- `quota_ledger.py:10` — `from pathlib import Path` in the same module as the
  domain; `_LedgerFile.__init__` at `:79-83` calls `mkdir` and `write_text`.
  The domain and its I/O are one module, so "the domain does not import its I/O"
  is false on its face.
- `quota_ledger.py:134`, `:168`, `:193` — the only three cross-boundary call
  sites, all `self._ledger.append(...)` / `self._ledger.lines()`. **Verified at
  runtime, not by import topology:** tracing a full reserve/commit/close/read
  cycle recorded exactly `append('COMMIT acme 3 3')`, `append('CLOSE acme 3')`,
  `lines()` and nothing else, and with an in-memory fake installed **no file was
  created on disk**. Nothing leaks past the seam.
- `quota_ledger.py:72-92` — the seam itself: a private concrete class, not an
  interface. `EVIDENCE.md:322-323` records `declared_interfaces 0` and
  `declared_interface_methods 0`.
- `EVIDENCE.md:158-170` — `corpus-port-swap:fake` and `corpus-port-swap:real` are
  identical in all eleven rows, consistent with `EVIDENCE.md:49-51`: an artifact
  shipping no second implementation runs its real one.
- `NOTES.md:116-118` — the author declines the abstraction deliberately: "an
  abstraction over the file beyond the one small class that writes it".

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4.

**Rationale:**

Anchor 2, comfortably and on runtime evidence: there is one seam, every durable
operation goes through it, and I proved that by call trace and by observing that
a substituted fake produces no filesystem activity at all.

Anchor 3 fails on both of its conjuncts. The domain imports and constructs its
I/O in the same module (`:10`, `:110`). And I cannot name a swap that leaves the
domain untouched: the only substitution that works is rebinding the module global
`quota_ledger._LedgerFile`, which *is* touching the domain. `__init__` takes a
path, not a ledger port, so there is nowhere to inject one.

This is the dimension where the artifact is weakest and it is a deliberate
choice, not an oversight — FEATURE.md:117-119 lists "whether the durable side is
reached through an interface, a callable, or directly" as expressly unspecified,
and the author picked "directly, behind one small class". The rubric scores that
choice at 2. That is the rubric working, but a reader should know the artifact
was not told to do otherwise.

### D4 — behavior preservation

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `test_quota_ledger.py:279-312` — `check_rules` recomputes R1, R2 and R3 from
  scratch after **every** command, reading the ledger off disk rather than
  through the accessor, and cross-checks `ledger_lines()` against the file.
- `test_quota_ledger.py:114-131` — R4, parametrized over all six rejection paths,
  compared against the file's bytes.
- `test_quota_ledger.py:133-140` — R5, asserting every earlier line is still
  present unchanged after each new write.
- `test_quota_ledger.py:255-273` — the declared rejection orderings, both
  commands.
- Against anchor 3: `test_quota_ledger.py:315-362`, the sweep, and
  `test_quota_ledger.py:360-362`, its anti-degeneracy guards. **Measured reach at
  the pinned seed `random.Random(20260804)` (`:326`): of 400 steps, exactly 5 are
  accepted** — one `reserve` (step 2), one `commit` (step 7), three `close_tenant`
  (steps 8, 28, 30) — and **zero accepted `release`s in 72 release calls.** All
  three tenants are closed by step 30, so steps 31–399 (92% of the sweep) run
  against a fully-closed ledger where every command rejects.

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4.

**Rationale:**

Anchor 2 is met: FEATURE.md's R1–R5 are each enumerated and each shown to hold,
and the checks are made against the durable file rather than against an in-memory
mirror, which is the harder version of the claim.

**I nearly gave this a 3 and I am recording why I did not.** The artifact ships
exactly one candidate for "model-derived rather than only hand-written":
`test_rules_hold_through_a_long_random_sequence`, described at `NOTES.md`-level
as R1/R2/R3 "under a long randomized command sequence checked against an
independent model". Textually that qualifies. So I measured it, and at its
pinned, deterministic seed it accepts 5 of 400 commands and never once accepts a
`release`. The model-derived component of this artifact's evidence contributes
almost no accepting coverage; it is 369 consecutive steps of re-asserting that a
closed ledger rejects things.

The author foresaw exactly this failure mode and wrote a guard against it at
`:359-362` — "a sequence that only ever rejected would prove nothing" — and the
guard passes anyway, because `any(model["committed"].values())` is satisfied by
a single commit. **The guard is real, deliberate, and too weak by roughly two
orders of magnitude.**

That is not an aesthetic objection, and it has a consequence I measured
independently: J08, a plainly behavior-breaking change in which `release`
returns `rejected` while still performing the release, **survives all 32 of the
artifact's own tests** and is caught only by the shared suite. It survives
*because* the sweep never accepts a release. Torn between 2 and 3, the rule says
take the lower and say why; the why is a measurement.

Anchor 4 is out of reach regardless. I did execute my own faults, so it was
available to me, but the anchor asks for the **artifact** to demonstrate its
check capable of failing, and no such demonstration exists anywhere in the
artifact or in `NOTES.md`. What I demonstrated is the opposite.

**Where the ladder broke.** D4 asks "does the *simpler* design still do
everything the *baseline* did". There is no baseline and no prior design. I
substituted FEATURE.md's R1–R5 for "the behaviors the baseline exhibited", which
is the only reading that lets the dimension say anything about a greenfield
subject, and I want that substitution on the record because it is mine and not
the rubric's.

### D5 — honesty

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger.py:58` — `assert reason in REJECTION_REASONS, f"undeclared
  rejection reason: {reason}"`. The code refuses at runtime to emit a rejection
  outside the declared vocabulary rather than passing one through. In the
  artifact, not in a report.
- `quota_ledger.py:114-116` with `NOTES.md:89-94` — `available("nobody")` raises
  `KeyError` rather than returning an invented `0` or `None`. Verified. The
  reasoning is explicit: the specification "invents no return value for this
  case, so I left the dict lookup to speak for itself rather than inventing a
  sentinel". That is a refusal in place of a false clean, which is anchor 3.
- `NOTES.md:96-103` — refuses to certify integrality and names the gap in the
  specification rather than papering it: "If integrality is meant to be enforced,
  the six-reason vocabulary is missing a reason for it." I verified the stated
  behavior: `0.5` is rejected, `1.5` is accepted and written as
  `COMMIT acme 1.5 1.5`.
- `NOTES.md:60-63` — refuses to claim crash-safety for a write-ordering choice
  that superficially looks like it: "it is not a crash-safety feature and I did
  not build one (no fsync, no journaling, no recovery)".
- `NOTES.md:73-77` — names a case the shared suite cannot distinguish ("the
  shared suite never gets past `r3`") and pins its own reading instead of
  claiming the suite covers it.
- `NOTES.md:125-129` — volunteers a possible contamination of its own blind
  (an `ls` that exposed filenames on the must-not-open list).
- Against anchor 4: `NOTES.md:24` and `NOTES.md:32` report **28 passed** and
  **32 passed**. Those are the only two results the artifact measures about
  itself, and both are clean.

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4.

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): **`measured`**

**Rationale:**

Anchor 2 is met inside the artifact and not only in the report — the vocabulary
assertion at `:58` and the deliberate `KeyError` at `:114` are both the code
declining to manufacture something it cannot justify. Anchor 3 is met twice over,
once in code and once in the record.

Anchor 4 turns entirely on the reading, which is why the card asks for it. Under
**`disclosure`** this artifact is a clear 4: `NOTES.md:87-111` is three
paragraphs of unprompted self-limitation and `:125-129` discloses a possible leak
against its own interest.

I scored under **`measured`**, and under that reading it is a 3. Every *result*
this artifact measured about itself is a pass count, and both are green. There is
no failing measurement, no negative finding, no place where it ran something
against itself and reported an outcome it would rather not have. The unflattering
results about this artifact in this round are the two I produced — the sweep's 5
accepted commands in 400, and J08 surviving all 32 tests — and neither is
anticipated anywhere in its record. I hold `measured` because everywhere else in
this rubric and packet "result" denotes a measured outcome (kill cells, control
status, pass counts), and reading it as "a limitation the author chose to
mention" collapses anchor 4 into anchor 2. The tie rule points the same way, but
I would have scored 3 without it.

I want to be plain that this is the one score where a judge holding the other
reading should be expected to differ by exactly one, and that difference would be
about the anchor and not about the artifact.

## Verdict

An honest, proportionate, well-tested single-module implementation whose own
test suite reaches one fault class the shared model provably cannot express — but
whose sole model-derived check is measured here to accept 5 of 400 commands at
its pinned seed and never a single `release`, which is why a `release` that
reports `rejected` while still releasing passes all 32 of its own tests.

## Disclosures

**What I saw that I was not meant to see.**

- The directory is `artifact_U` and `EVIDENCE.md:1` is headed "Evidence packet —
  artifact U". The dispatch told me `U` is a prior round's label carrying no
  information about this round, and I have treated it as noise.
- `EVIDENCE.md:310-328` is a three-column mechanical block covering artifacts
  **T, U and W**. I therefore read comparative complexity figures for two other
  artifacts while scoring this one. The packet explains why (D2 anchor 3 needs a
  before/after and one column cannot reach it), and I used none of it for a
  score, but I did see it and it is unavoidably comparative.
- `NOTES.md:128` lists "`this artifact/`" among the filenames an `ls` exposed,
  and `test_quota_ledger.py:1` opens "this artifact's own tests". Both read as
  substitutions over a string that originally named the arm. So I know arm-identifying
  text was scrubbed; I do not know what it said.
- **I did not work out the arm, and I want to name the inference I can make so it
  is on the record rather than in my head.** This artifact declares zero
  interfaces, ships no port and no fake, and reaches its durable side directly —
  and the enclosing path is `ports-as-adapters`. That is consistent with a
  control arm, but it is equally consistent with a treated arm that read
  FEATURE.md's "deliberately unspecified" list and declined. I did not act on it,
  and my D3 of 2 rests on `quota_ledger.py:110`, which I would have cited
  whatever the arm.
- I ran `git status` in the repository root, twice, to confirm I had modified
  nothing. It printed the **filenames** of both sibling passes' cards (`-p3` and
  `-p4`) as modified, and a card path under this round's **other subject**
  (`subtract-to-measure-sm05/toolchain_removal/…-K-p3`). I did not open any of
  them, did not read a byte of their contents, and did not run `git diff` or
  `git show` against them. Disclosing it because knowing that siblings exist, are
  in progress, and are being scored concurrently is itself information the blind
  was meant to withhold — and because `git status` at a repository root is an
  unremarkable thing for a judge to run, which makes it a real leak channel in
  this design rather than a hypothetical one.
- The dispatch fixes `commit` at `f49a1c9`; the worktree's HEAD is `9ad9daf`. I
  recorded `f49a1c9` as instructed and am noting the mismatch rather than
  silently reconciling it.

**What I ran that changed the tree.** Nothing. All twelve mutations were applied
to a scratch copy outside the repository, each reverted and each revert proved
byte-identical by sha256; the scratch `quota_ledger.py` ends at the same
`213b2a5e…` as the sealed original. `mechanical.json` arrived with empty
`figures` and I left it empty — it is the harness's record and filling it from
`EVIDENCE.md` would be me manufacturing measurements.

**What I REJECTED.**

1. **I nearly gave D3 a 4, and the evidence for it was mine.** I built an
   in-memory fake ledger, substituted it, and ran the shared 28 cases against
   both the real file adapter and the fake: **28 passed against each**, with no
   file created on disk. That is literally anchor 4's shape — "a driven port
   exercised by a real adapter *and* a fake, with the same cases passing against
   both". I rejected it. The fake is my construction, the artifact ships none
   (`EVIDENCE.md:322`, `declared_interfaces 0`), and installing it required
   rebinding the module global `quota_ledger._LedgerFile` — which is touching the
   domain, the exact thing anchor 3 forbids. **Evidence a judge manufactures
   about an artifact is not evidence about the artifact's design**, and a judge
   who can run things is in constant danger of scoring their own work. This is
   the trap I think this rubric's "you may run things" permission opens, and I
   want it recorded.
2. **I rejected the entire harness kill table as the basis for D1.**
   `EVIDENCE.md:54-57` says every corpus comes from one model and one manifest
   shared by all three artifacts with an identical `cases.py` sha1. Those columns
   measure how observable each artifact's *code* is under a fixed instrument;
   they are not that artifact's bug detection, which is what D1 asks about. I
   scored the artifact's own 32 tests and then checked that the discarded reading
   would have produced the same 3, so the choice is disclosed rather than
   decisive here.
3. **I rejected every port-binding cell in the packet, including the ones that
   would have helped.** `EVIDENCE.md:194-215` records the positive control M07 as
   `green: false` with `corpus-port` in `instruments_wrong`, and
   `EVIDENCE.md:268-302` shows all three port-binding columns SURVIVED where the
   declared control says they must be KILLED, each having executed 294 accepting
   `Reserve` cases. Under the packet's own rule a number beneath a red control is
   a floor, so those columns can distinguish nothing for this artifact. I used
   none of them, in either direction.
4. **I rejected the mechanical block for D2** — rule 7, and MF-020 specifically:
   this artifact is smaller than artifact T partly *because* it declares no
   interfaces, so `code_lines 151` versus `202` would have rewarded on D2 the same
   choice I debited on D3. Converting that figure into a score would have paid the
   artifact twice for one decision, in opposite directions.
5. **I rejected `disclosure` as my D5 anchor-4 reading**, which would have made
   D5 a 4. Recorded in the D5 rationale.
6. **I rejected the sweep as anchor-3 evidence for D4 only after measuring it.**
   My first reading was that a 400-step randomized sequence checked against an
   independent model plainly clears "model-derived rather than only hand-written",
   and I was ready to write a 3. What changed my mind was instrumenting reach, and
   I would not have found it by reading the test — the test *looks* thorough, its
   guards *look* adequate, and its seed is pinned so it is not even flaky. **The
   only way to see it was to count what the check actually executed**, which is
   the same discipline the packet applies to its own instruments with its
   executability table (`EVIDENCE.md:178-187`) and does not apply to the
   artifacts' own tests. If this round takes one thing from this card: the
   evidence packet prints reach beside every harness kill number and prints none
   beside an artifact's own suite, and that asymmetry hid a 1%-reach test behind a
   green 32.
7. **I rejected prose quality as an input, and it was a real temptation here.**
   `NOTES.md` is the most disarming document I have read in this role — it
   volunteers a possible leak against its own interest, admits the one place a
   reasonable implementer could differ, and reasons carefully about non-integer
   amounts nobody asked about. Every claim in it I checked was true, which makes
   it *reliable*, and reliability is very easy to launder into *thorough*. Rule 4.
   The thing that finally separated the two was that the document's candour is
   entirely about the **feature's** open questions and not once about its own
   **testing's** limits — it never says what its suite might miss. J08 is what
   that gap costs, and no amount of good writing narrowed it.

