# Scorecard — ab_quota_ledger, artifact `S`, judge pass 2

`run_id`: `20260807-sm05gf-S-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

- Copied `quota_ledger.py`, `test_quota_ledger.py` out of the sealed directory and `examples/validation/ab/tests/test_behavior.py` into a scratch tree outside the repository. Nothing in the repository was written; `git status --porcelain` shows no modification to any path I touched, and `diff` confirms my scratch copy is byte-identical to the sealed original.
- Baseline: both suites on unmutated code — **60 passed** (32 the artifact's own + 28 shared). This reproduces `NOTES.md:24` and `NOTES.md:32` exactly.
- **16 faults of my own design, seeded one at a time**, each applied to a copy, run against the artifact's own tests and the shared suite *separately*, then reverted with a sha256 equality check on the revert. Classes: refusal/guard relaxation (F1, F7), ordering past `r9` (F2), cross-aspect before-state (F3), durable content (F4, F5, F13), the durable side not actually being durable (F6), output oracle (F8), append-only/R5 (F9), wrong value (F10b), id identity (F12), R4 rejection-writes-nothing (F14), aliasing (F15). Two more (F10, F11) I discarded on inspection as no-ops before counting them.
- Result: the artifact's own tests killed **13 of 14** real faults. The survivor is **F8 — `release` performs its effect but reports `rejected`**, which the shared suite kills (`examples/validation/ab/tests/test_behavior.py:159`) and the artifact's own 32 tests do not.
- Because F8 survived, I instrumented the artifact's flagship randomized sweep (`test_quota_ledger.py:315`) at its own pinned seed `20260804` and counted its accepting transitions. See D4.
- Executed the two limitations `NOTES.md` claims about itself: `reserve("acme", 1.5)` → accepted, and the ledger line is literally `COMMIT acme 1.5 1.5`; `available("nobody")` → `KeyError`. Both claims hold exactly as written.
- `grep` for every filesystem call site in `quota_ledger.py` (`open|Path(|write_text|read_text|mkdir|flush`) to check the boundary claim by call site rather than by prose.

## Your scores

### D1 — bug detection

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:162` — `test_outstanding_ids_are_ascending_past_ten`. My seeded F2 (the `outstanding_ids` sort key changed from `r.seq` to `r.reservation_id`, i.e. string order) is **KILLED** here and **SURVIVES** the shared suite.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:81` — the `N01-negative-control-outstanding-id-order` row: this exact fault class SURVIVES on all eight eval instruments, and `EVIDENCE.md:248` records `must_be: SURVIVED` with `separates_the_trees: true`. The eval itself certifies that the ordering class is a real difference beyond every instrument's structural reach. `test_quota_ledger.py:162` reaches it.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111` — `guard_relaxation`: `corpus-whole` is **0 of 3**. Refusals are structurally out of the whole-view corpus's reach. My F1 (`amount < 1` → `amount < 0`) and F7 (the `close_tenant` outstanding guard disabled) are both killed by the artifact's own tests at `test_quota_ledger.py:154` and `test_quota_ledger.py:265`.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:37` and `:88` — `file_lines()` reads the file from disk independently of the accessor, and `test_commit_lines_reach_the_file_itself` asserts the exact durable line text `["COMMIT acme 3 3", "COMMIT acme 2 5"]`. Content, not shape. My F4 (stale running total), F5 (`CLOSE` total forced to 0) and F13 (a second line appended) are all killed here.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:125` — `test_a_rejected_command_writes_nothing_durably` compares the file's bytes across a rejection; kills my F14 (a rejected `close_tenant` that still appends).
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:1` — the file's own header: these are hand-written tests. There is no model in this artifact, so anchor 4's "derived from the model rather than hand-written" is failed on its first clause.

**Refuses to claim** (required and non-null for a score of 4): _n/a (score is not 4)_

**Rationale:**

Anchor 2 is met on measured evidence: the artifact's own adapters read the durable file from disk and assert its exact text, and wrong-value faults (F10b, an off-by-one in the hold) and wrong-content faults (F4, F5, F13) all die there. Anchor 3 is met and I verified it rather than reading it: the ordering class is one the packet's own control block certifies as beyond the entire eval corpus's structural reach (`EVIDENCE.md:81`, `:248`), and the artifact's own `test_outstanding_ids_are_ascending_past_ten` kills a seeded fault in it that the shared suite survives. The `guard_relaxation` row gives a second, independent instance: `corpus-whole` reaches 0 of 3 refusals and the artifact's own tests kill both refusal faults I seeded. Anchor 4 fails cleanly and not narrowly — the artifact ships no model, so no case of its can be model-derived.

**Where I had to stretch the ladder, and it broke:** D1's question is about "the model-derived cases and their adapters", but *this artifact has no cases of its own that are model-derived and no model*. The model-derived corpora in the packet belong to the harness, are generated from one shared model and manifest, and are byte-identical across all three artifacts (`EVIDENCE.md:54`, sha1 at `EVIDENCE.md:190`). Scoring those columns would score the harness, not the subject. So I scored the artifact's own executable cases plus my own seeded runs, and the effect is that **anchor 4 is unreachable by this subject for reasons of subject shape rather than quality**. A reader should not read this 3 as "one rung short of excellent"; it is the top of the reachable ladder for a greenfield implementation.

The 3 is also not a claim that the suite is thorough. It has a hole I found: see D4.

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:103` — the constructor declares seven fields, and each has exactly one writer outside it: `_available` at `:150` and `:180`, `_committed` at `:170`, `_closed` at `:194`, `_reservations` at `:151`, `:171`, `:181`, `_next_seq` at `:201`, `_quotas` nowhere after construction. No god-state and no variable written from everywhere.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:140` — `reserve`'s four-branch rejection ladder, one branch per clause of `examples/validation/ab/FEATURE.md:40`. The single densest callable in the module is dense because the requirement enumerates four ordered rejections; the branching is essential, not accidental.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:28` — the six rejection reasons collected in one frozenset and enforced at `:58`, replacing a membership rule that would otherwise be restated at six call sites.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:207` — `_has_outstanding` is the only helper; `max_depth` in the module is 1 and nothing calls anything two levels deep.

**Refuses to claim** (required and non-null for a score of 4): _n/a (score is not 4)_

**Rationale:**

Every field has a small, nameable set of writers, each command touches one or two of them, and the only concentration of branching is the rejection order the specification itself enumerates. That is anchor 2, and I can cite it line by line.

**Where the ladder was written for a different subject and I had to stretch it — this is the dimension where it broke worst.** Three problems, all of them about shape and none about quality:

1. The `read_first` instruction says to read "the measured descriptor (variables, actions, state-space bound, R/W density, modularity, dense rows)". **No such descriptor exists for this artifact.** That is a TLA+-model descriptor and this artifact ships no model. The only measurement in the packet is a *code* complexity block over three artifacts (`EVIDENCE.md:310`) which is a different instrument and which rule 7 forbids me to convert into a score. So the dimension's own prescribed first step is unperformable here, and I performed it by reading the code instead.
2. Anchors 0 and 1 grade a *measurement act* ("unmeasured", "measured and reported"). This artifact measures nothing about itself. Read as a strict cumulative ladder, anchor 2 would be unreachable because anchor 1 fails, and D2 would be 0 for every greenfield artifact regardless of how well designed. I rejected that reading: anchor 2's text is about the design, not about a report, and I can evaluate the design directly. I nearly scored 1 on the grounds that no figure of any kind is argued in the artifact, and did not, because 1 describes a *worse* state (numbers with no argument) than what is here (a design argument at `NOTES.md:34` and `NOTES.md:113` with no numbers). I flag it as the closest call on the card.
3. Anchors 3 and 4 require "a simplification was made and its effect measured — the before and after figures are both recorded." **A greenfield artifact has no before.** Nothing was simplified from anything. D2 caps at 2 here structurally.

Missing evidence, named as the dispatch asks: to decide D2 above 2 I would need a prior version of this artifact and figures from both. Neither exists.

### D3 — modularity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72` — `_LedgerFile`, declared in `NOTES.md:38` and `NOTES.md:116` as the one abstraction over the durable side.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:80`, `:82`, `:83`, `:86`, `:88`, `:91` — I grepped every filesystem call site in the module. These six are all of them, and every one is inside `_LedgerFile`. The declared boundary is followed by the code, not merely asserted.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:134`, `:168`, `:193` — the three and only three places the domain reaches the durable side, all through `self._ledger.lines()` / `.append()`. That is identifiable as a port in the anchor-2 sense: one named chokepoint, called and not bypassed.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110` — **`self._ledger = _LedgerFile(ledger_path)`. This is why anchor 3 fails.** The domain class constructs its concrete durable side by name from a path. There is no injection point. No adapter can be substituted without editing a line inside `QuotaLedger.__init__`, which is the domain. I could not name a swap, because there is none to name.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:49` — "`corpus-port-swap:fake` on an artifact that ships no second implementation runs its REAL one." This artifact ships no second implementation (`declared_interfaces` 0 at `EVIDENCE.md:322`, and `_LedgerFile` has no sibling).
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:158`–`:170` — the `corpus-port-swap:fake` and `corpus-port-swap:real` columns are identical in all eleven rows **because they are the same run twice**, per the line above. Not evidence for anchor 4.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:275` — the declared positive control `M07` SURVIVED on all three port-binding instruments while 294 accepting `Reserve` cases executed; `EVIDENCE.md:196` records `green: false`. Every number in the port-binding block is a floor.

**Refuses to claim** (required and non-null for a score of 4): _n/a (score is not 4)_

**Rationale:**

There is a genuine, code-followed boundary here, and I checked it by call site rather than by prose: six filesystem calls exist in the module and all six are inside `_LedgerFile`; the domain touches the durable side through exactly three call sites, all via the two methods. That is anchor 2 in full.

Anchor 3 fails on one line. `quota_ledger.py:110` constructs the concrete adapter by name inside the domain's constructor, and the constructor's parameter is a *path*, not a ledger. Substituting an in-memory or instrumented durable side requires editing the domain class. The anchor asks the judge to name the specific swap and I cannot name one; that is the finding, not a technicality.

**The caveat about import topology cuts unusually sharply here, in the artifact's disfavour.** The mechanical block records `internal_import_edges: 0` for this artifact (`EVIDENCE.md:324`) — the best possible figure — and it is zero *because there is exactly one module*. An import check reads this artifact as maximally decoupled while its coupling is direct construction. This is one place where the measurement and my judgement agree rather than disagree, and rule 7 exists to surface that: `branch_points_in_effectful_modules: 10` and `instance_state_in_effectful_modules: 8` (`EVIDENCE.md:327`) say all of the branching and all of the state live in the module that does I/O, which is the same fact I reached from the code.

Anchor 4 is unreachable and, as with D1 and D2, for a reason of subject shape: it requires a fake, and the artifact deliberately ships none (`NOTES.md:116`, which calls a second implementation scope inflation — a position `FEATURE.md:117` explicitly permits).

### D4 — behavior preservation

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:289` (R1), `:293` (R2), `:302` (R3), `:125` (R4), `:133` (R5) — all five of `FEATURE.md`'s named rules are enumerated by name and each has a check. That is anchor 2, and the enumeration is explicit rather than inferred.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279` — `check_rules` recomputes R1/R2/R3 from an independently maintained model rather than from the object under test, and re-reads the file from disk at `:281`.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315` — **`test_rules_hold_through_a_long_random_sequence`, the only candidate for "model-derived", is degenerate, and I measured it.** Replaying its own pinned seed `20260804` for its own 400 iterations: **5 accepting transitions in total** — 1 accepted `reserve` (step 2), 1 accepted `commit` (step 7), 3 accepted `close_tenant` (steps 8, 28, 30), and **0 accepted `release`, ever**. All three tenants are closed by step 30, after which no `reserve` can be accepted, so no reservation can exist, so no `commit` or `release` can be accepted. **Steps 31–399 — 92% of the sweep — re-check R1/R2/R3 against a state that cannot change.** Measured counts: `reserve` 1 accepted / 193 rejected, `commit` 1/91, `release` 0/72, `close` 3/39.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:358` — the sweep's own anti-degeneracy guard ("a sequence that only ever rejected would prove nothing") **passes anyway**: `any(model["committed"].values())` is satisfied by the single commit, `model["closed"]` by the closes, and there is no clause for `release` at all. The guard cannot distinguish 1 acceptance from 100.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:1` — the checks are hand-written by the file's own declaration; there is no corpus and no TLC invariant in this artifact.
- `examples/validation/ab/tests/test_behavior.py:159` — the shared suite catches my F8 (`release` performs its effect and reports `rejected`) that the artifact's own 32 tests do not. The hole and the sweep's zero accepting releases are the same hole.

**Refuses to claim** (required and non-null for a score of 4): _n/a (score is not 4)_

**Rationale:**

Anchor 2 is met properly: five named rules, each with a check I can point at, several of them recomputed against an independent model rather than against the object's own accessors.

Anchor 3 fails. The definitional reason is that there is no model and no corpus in this artifact, so nothing is model-derived. I did not want to rest on the definition alone, so I measured the one thing that could have earned a generous 3 — the randomized sweep — and it is worse than the definition suggests. It reaches its terminal state at step 30 of 400, issues five accepting transitions in its entire run, never once exercises an accepting `release`, and its own guard against exactly this failure passes. My F8 survives the artifact's whole 32-test suite as a direct consequence: there is no test anywhere in the file that asserts `release` returns `accepted`, and the sweep that was supposed to cover it never gets there. **I nearly scored 3 for the sweep and rejected it on measurement, not on definition.**

A second, independent reason I would not have given 3: the sweep's model and its invariants are the same author's reading of `FEATURE.md`, transcribed twice. A misreading is transcribed into both and cancels. `NOTES.md:73` and `test_quota_ledger.py:162` make this concrete — the artifact's reading of "ascending" is pinned by its own test, so if the reading is wrong, impl and check are wrong together. That mutual independence is exactly what "model-derived" is supposed to buy and this does not buy it.

**Where the ladder does not fit:** this dimension asks "does the *simpler* design still do everything the *baseline* did?" **There is no baseline and no prior design.** This is a first implementation of a specification. I read "the behaviors the baseline exhibited" as `FEATURE.md`'s R1–R5 plus the shared suite, which `FEATURE.md:106` names as the declared floor; without that substitution the dimension is undefined for this subject. Anchor 4 is doubly unreachable — it requires anchor 3 — though for the record `executed_own_faults` is `true` and I did demonstrate the artifact's own checks are capable of failing, on 13 of the 14 real faults I seeded.

### D5 — honesty

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:87` — a "What I was unsure about" section, unprompted, naming three specific limits rather than gesturing at humility.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:89` with `quota_ledger.py:114` — `available("nobody")` raises rather than inventing `0` or `None`, explicitly because "the feature ... invents no return value for this case". **This is anchor 3 in the code and not only in the report**: the query refuses to emit a value its basis does not support. I ran it; it raises `KeyError`.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:58` — `Result.rejected` asserts membership in the declared vocabulary, so the artifact fails loudly rather than emitting a reason it has no authority for. A second refusal, in code.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96` — the non-integer `amount` limit: "`1.5` is not rejected at all — it would be held and committed as `1.5`, and would print that way in a `COMMIT` line", with the reason it was not fixed ("the six-reason vocabulary is missing a reason for it"). **I ran this and it is exactly true**: the ledger line is literally `COMMIT acme 1.5 1.5`. A stated, accurate, self-damaging limit — and a refusal to invent a seventh rejection reason to paper over it.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:113` — a Scope section naming, unprompted, what it did not build.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:125` — a voluntary disclosure that it ran `ls` on a directory and saw the *names* of files on its own must-not-open list. Nothing compelled this.

**Refuses to claim** (required and non-null for a score of 4): _n/a (score is not 4)_

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): **`measured`**

**Rationale:**

Anchor 2 is met in the delivered artifact and, importantly for the anchor's "not only in a report" clause, partly in the code itself: the bare dict lookup at `quota_ledger.py:114` and the vocabulary assert at `:58` are refusals expressed as behavior, not as prose. Anchor 3 is met twice over — a query that raises rather than fabricating, and a command layer that will not emit an undeclared reason — and both are the `unmappable`-rather-than-false-clean shape the anchor describes.

Anchor 4 turns entirely on the reading, which is why the card asks. **Under `measured` I score 3.** The artifact measured exactly one thing about itself — its two test runs — and both came back green (`NOTES.md:24`, `:32`). Nothing it *measured* is unflattering. The 1.5 limit at `NOTES.md:96` is reasoned rather than run: it is precise enough that it may well have been executed, but no run is recorded and `test_quota_ledger.py` contains no test for it. And the one genuinely unflattering thing I found — that its own suite has a hole at accepting `release`, and that its flagship sweep reaches a terminal state at step 30 — the record does not contain, because the artifact never measured its own tests against anything.

**Under `disclosure` I would have scored 4**, and I want that on the record for whoever reads this beside another judge's card: `NOTES.md:125` (a self-reported protocol leak) and `NOTES.md:96` (a self-reported defect-shaped consequence) are both plainly unflattering statements about the artifact, volunteered. If pass 2 and another pass differ by one on D5, that difference is about the anchor and not about this artifact, and the two readings are the whole of it.

I took `measured` because anchor 4's stated design purpose — rule 3, "it makes a perfect score impossible to reach by asserting more" — is defeated by a reading under which a well-written limitations paragraph purchases the top of the scale, and because rule 4 forbids prose quality as an input. Which brings me to the tempting part: **this artifact's writing is the best-argued of anything I have had to score, and `NOTES.md:87`–`:111` is genuinely persuasive.** I responded by running its three self-claims instead of crediting them. Two held exactly and the third (`bool` is an `int`, so `reserve(t, True)` reserves 1) also held. The writing earned nothing; the running is what the citations rest on.

## Verdict

A disciplined single-module implementation with one real durable-side chokepoint but no swappable port and no model, whose 32 green tests conceal a measured hole — its flagship 400-step randomized sweep reaches a terminal state at step 30, issues five accepting transitions in total and never once an accepting `release`, and its own anti-degeneracy guard passes anyway.

## Disclosures

**What I saw that I was not meant to see.**

- Running `git status --porcelain` in the worktree to prove I had modified nothing showed me that two sibling card directories (`-p3`, `-p4`) have modified `scorecard.md` files. I saw two path strings and no content. I did not open them, and I did not run the command again.
- **The sealed bytes are not sealed.** The dispatch says the artifact directory will not be edited "to tidy a path", but `NOTES.md:1` reads "# NOTES — this artifact, quota ledger", `test_quota_ledger.py:1` reads "this artifact's own tests", and `NOTES.md:128` lists a directory as ``this artifact/`` in the middle of a list of real filenames — all three are post-hoc string substitutions over whatever the author originally wrote. This leaks shape: it tells me the artifact's source directory sits inside `examples/validation/ab/` as a sibling of `reference/`. It does not tell me which arm, and I did not chase it. But a judge should know the redaction is visible, and a substitution that lands *inside a code identifier or a sentence* is a channel.
- The mechanical block (`EVIDENCE.md:310`) gives me all three artifacts' columns, not just mine. So I know I hold the middle of three by size, and I know one sibling (T) ships 4 modules, 1 declared interface and 3 internal import edges while the other (W) is 78 lines in one module. In an eval whose other subject is named "ports as adapters", that is arm-adjacent information: it is easy to guess which column a ports-and-adapters prompt produced. **I did not work out which arm I hold** — T's shape is suggestive but U and W are both single-module and I cannot separate them on that basis — and I did not use the comparison anywhere in a score. I record it because the D2 anchor forces a judge to read a three-column block to reach a dimension that a greenfield subject cannot score above 2 anyway. That block buys nothing here and costs blinding.

**What I ran.** Listed in full under "Judging practice" above. Nothing inside the repository was written: I copied out, ran in `/private/tmp/.../scratchpad/work` with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`, reverted every mutation with a sha256 equality assertion, and `diff`ed my final copy against the sealed original (identical).

**What I REJECTED.**

1. **I rejected D3 = 4 from the identical `corpus-port-swap:fake` / `:real` columns** (`EVIDENCE.md:158`–`:170`). Eleven rows agreeing perfectly looks exactly like "the same cases passing against both a real adapter and a fake", which is anchor 4 verbatim. It is not: `EVIDENCE.md:49` says the fake column runs the REAL implementation when no second implementation exists, and this artifact ships none. **The identical columns are the same run printed twice.** This is the single most dangerous piece of evidence in the packet — it is formatted as the strongest possible support for the anchor it actually refutes, and a judge who scores the table without reading the paragraph fifty lines above it will award a 4 for a swap that never happened. If one thing from this card is worth carrying forward, it is that these two columns should be collapsed into one, or labelled `(no fake shipped — real run repeated)` in every cell.
2. **I rejected the entire port-binding block a second time, independently**, because it sits under a RED positive control: `M07` must be KILLED, is SURVIVED on all three bindings, and the packet itself records that 294 accepting `Reserve` cases executed while it survived (`EVIDENCE.md:275`), with `green: false` at `:196`. Every number in that block is a floor. Two independent reasons the same block cannot lift D3 is worth noting: the block is not weak evidence, it is no evidence.
3. **I rejected D4 = 3 for the randomized sweep** — and I rejected it on measurement rather than on the definitional "there is no model here". Measuring it is where the finding came from, and it changed the shape of my D4 rationale entirely: the sweep is not merely "hand-written rather than model-derived", it is a 400-step generator that stops generating at step 30.
4. **I rejected the corpus columns as the basis for D1.** They are generated from one model and one manifest and are byte-identical across all three artifacts (`EVIDENCE.md:54`, sha1 at `:190`). A score built on them measures the harness. I said so in the D1 rationale rather than quietly using them, because the alternative reading is defensible and another judge may well have taken it — and if pass 2 and another pass differ on D1 by more than 1, this is almost certainly why.
5. **I rejected the literal reading of "Score the LOWEST anchor the artifact fully satisfies."** Read literally it floors every score at 0, since every artifact satisfies anchor 0 of something. I read it as "the highest rung fully satisfied, ties broken downward", which is what the following clause ("when torn between two, take the lower") implies. Flagging it because it is the one sentence in the rubric that means the opposite of what it says.
6. **I rejected the reading of D5 anchor 2 under which `NOTES.md` is "only a report".** That reading would cap D5 at 1 for this artifact and probably for every artifact in this eval, since none of them are self-checking tools. I treated `NOTES.md` as delivered with the artifact (the dispatch calls it "that author's `NOTES.md`", distinct from the harness's `EVIDENCE.md`) and additionally grounded anchor 2 and anchor 3 in code (`quota_ledger.py:58`, `:114`) so the score does not rest on the report alone.
7. **I rejected D5 = 4 under the `disclosure` reading**, recorded above with the reason and the specific lines, so an adjudicator can tell an anchor disagreement from an artifact disagreement without a third pass.
8. **I rejected two of my own mutants.** F10 (`-= amount + 0 if amount != 7 else amount`) and F11 (`+= 0`) are no-ops — Python's conditional-expression precedence made the first one identity. Both "survived" every suite and both would have been false evidence of a gap. I caught them by inspecting the diff rather than by trusting the SURVIVED cell, which is the same discipline the packet's own control section is asking for, applied to my own instrument. I did not count either.
9. **I rejected D2 = 1 and D2 = 0**, both defensible, in favour of 2. The closest call on the card; reasoning is in the D2 rationale.
10. **I rejected the prose.** Rule 4, stated because it was genuinely tempting: this is the best-written `NOTES.md` I could imagine receiving, and its "What I was unsure about" section reads as exactly the kind of honesty D5 is trying to reward. I ran its three claims instead of crediting them. All three held — which is a fact about the claims, not about the writing, and it is the running that appears in the citations.

**The finding I would put above all of the above.** Four of the five dimensions have a top rung this subject cannot reach for reasons of *shape* rather than quality: D1 anchor 4 needs a model the artifact has none of; D2 anchors 3–4 need a "before" that a greenfield artifact cannot have, and D2's `read_first` names a descriptor that does not exist for this subject at all; D3 anchor 4 needs a fake the specification explicitly permits omitting (`FEATURE.md:117`); D4's whole question presupposes a baseline that does not exist. This rubric was written for a subject that carries a model, a prior version and a port declaration, and it is scoring a first implementation of a feature. **A reader comparing this card's numbers to a card scored on a model-carrying subject is comparing different ladders**, and the four ceilings above are why a competent greenfield artifact tops out around 2–3 across the board no matter what it does. That is a property of the instrument, not a result about the artifact.
