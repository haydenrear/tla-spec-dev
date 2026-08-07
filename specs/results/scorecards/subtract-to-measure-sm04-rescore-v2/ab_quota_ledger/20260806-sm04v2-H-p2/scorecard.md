# Scorecard — ab_quota_ledger, artifact `H`, judge pass 2

`run_id`: `20260806-sm04v2-H-p2` · scorecard_version 2 · rubric `specs/results/scorecards/subtract-to-measure/SM-04/rubric_v2_frozen.md` digest `sha256:3bd59f9fe2ab699b`

**You are scoring artifact `H`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

## The rubric you are scoring against

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.

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

### Judging practice — your answer

**Executed own faults:** **true**

**What was run:**

All work was done on copies under `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/judgeH2/`. Nothing in the repository was modified except this card and its JSON.

- **Baselines.** The shared suite `examples/validation/ab/tests/test_behavior.py`, unedited, against a copy of the artifact — **28 passed**. The artifact's own `test_quota_ledger.py` — **32 passed**. Both figures in `NOTES.md` reproduce.
- **Eleven judge-authored faults plus a negative control**, each a single-point edit applied to a fresh copy, run against **both** the artifact's own tests and the shared suite, then the copy destroyed. The pristine sha256 was re-checked at the end and was unchanged.

| my mutant | class | own tests | shared suite |
|---|---|---|---|
| `J01` `amount < 1` → `amount < 0` | guard relaxation | KILLED | KILLED |
| `J02` close-with-outstanding check deleted | guard relaxation | KILLED | KILLED |
| `J03` COMMIT line writes the stale total | durable content | KILLED | KILLED |
| `J04` CLOSE line writes `0` | durable content | KILLED | KILLED |
| `J05` commit also refunds the hold | cross-aspect | KILLED | KILLED |
| `J06` `outstanding_ids` sorted by id string | ordering | KILLED | **SURVIVED** |
| `J08` `append` opens the file `"w"` | append-only | KILLED | KILLED |
| `J09` `release` refunds 2× the amount | wrong value / R1 | **SURVIVED** | KILLED |
| `J11` `close_tenant` writes CLOSE twice | durable content | KILLED | KILLED |
| `N` comment-only edit | negative control | SURVIVED | SURVIVED |

- `J07` (a rejected `reserve` consuming an id) **did not apply** — its anchor text matched twice — and is recorded as *not run*, not as survived. `J10` turned out on inspection to be behaviorally inert and is recorded as a **second negative control**, not as a survived fault.
- **Instrumented the artifact's own sweep.** Wrapped the four commands and counted statuses while running the real `test_rules_hold_through_a_long_random_sequence` on **unmutated** code: `reserve` 1 accepted / 193 rejected, `commit` 1 accepted / 91 rejected, `release` **0 accepted** / 72 rejected, `close_tenant` 3 accepted / 39 rejected; 4 ledger lines written across 400 commands.
- **D3 runtime swap probe.** Attempted constructor injection of a fake ledger → `TypeError` (the constructor takes a path and builds the adapter itself). Monkeypatching the private module global `quota_ledger._LedgerFile` → works, and is the only substitution available.
- **Write-site grep** of every instance variable in `quota_ledger.py`, for the D2 god-state check.
- **NOT run:** the generated corpus instruments (`corpus-whole`, `corpus-neg`, the slices, `corpus-port`, `map-silent`/`map-checking`) and the port-binding columns. Those cells are read from `EVIDENCE.md` and are the packet's claim, not my measurement.

## Your scores

Citations below are relative to `specs/results/scorecards/ports-as-adapters/blind/artifact_U/`.

### D1 — bug detection

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `EVIDENCE.md:74` — M04 `durable-stale-total`: `map-silent` SURVIVED, `map-checking` KILLED.
- `EVIDENCE.md:101-109` — `durable_content`: `map-checking` 2 of 2, `map-silent` 1 of 2.
- `EVIDENCE.md:71-73` — M01/M02/M03: `corpus-whole` SURVIVED, `corpus-neg` KILLED.
- `EVIDENCE.md:111-119` — `guard_relaxation`: `corpus-neg` 3 of 3, `corpus-whole` 0 of 3.
- `quota_ledger.py:167-168` — the durable line whose content the wrong-content faults perturb.
- `test_quota_ledger.py:315-362` — the sweep whose degeneracy is the fault class nothing names.

**Refuses to claim** (required and non-null for a score of 4): *n/a — not a 4.*

**Rationale:**

Anchor 2 is met on measured cells, not on prose. M04 perturbs the running total written at `quota_ledger.py:167-168`; the provider that asserts nothing about content survived it and the provider that asserts durable content killed it, and the per-class block confirms the pattern (`map-checking` 2 of 2 against `map-silent` 1 of 2). That is a wrong-content fault caught by content assertion and missed by shape assertion, demonstrated by a paired instrument rather than asserted. `wrong_value` is 2 of 2 on `corpus-whole` and `corpus-slice-res`.

Anchor 3 is met the same way. All three guard relaxations are the refusal class; `corpus-whole` is 0 of 3 on them and `corpus-neg` — the DISABLED-edge instrument — is 3 of 3. The red positive control does not undermine this: M07 is red on `corpus-port` and the port-binding columns, and a red positive control makes an instrument's SURVIVED cells a floor, not its KILLED cells. `corpus-neg`'s three kills are kills. I also seeded my own guard relaxation and my own close-with-outstanding relaxation and both were caught, so the refusal class is reachable on this code and not only in the table.

Anchor 4 fails on its second clause. Nothing in the record names a fault class the checking still cannot reach: `NOTES.md` names spec ambiguities and out-of-scope features, not blind spots of its checks, and `EVIDENCE.md` names `NOT_DECIDABLE` pairs and a red control rather than an unreachable class. I then measured one such class myself: the artifact's own sweep accepts zero releases, and my seeded double-refund in `release` — an R1 conservation break — survived all 32 of the artifact's own tests. A fault class it cannot reach exists, is demonstrable in one run, and is unnamed.

### D2 — complexity

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `EVIDENCE.md:312-328` — the measured descriptor (1 module, 151 code lines, 17 callables, 8 instance state, 0 module state, 10 branch points, max 4 per callable, `max_depth` 1).
- `quota_ledger.py:103-110` — the five pieces of mutable state.
- `quota_ledger.py:150`, `quota_ledger.py:180` — the only two writes of `_available`.
- `quota_ledger.py:170` — the only write of `_committed`.
- `quota_ledger.py:194` — the only write of `_closed`.
- `quota_ledger.py:199-205` — `_allocate`, the only source of ids.

**Refuses to claim** (required and non-null for a score of 4): *n/a — not a 4.*

**Rationale:**

Descriptor read first, then judged for essentiality. The five pieces of mutable state correspond one-to-one to observable aspects the feature names (available, committed, closed, outstanding, the id counter). I grepped every write site rather than trusting the shape of the file: `_available` is written only in `reserve` and `release`, `_committed` only in `commit`, `_closed` only in `close_tenant`, `_reservations` at three sites in the three commands that own reservations, `_next_seq` only inside `_allocate`. No variable is written from everywhere and there is no god-state. A `max_depth` of 1 with 10 branch points across four commands carrying a nine-branch rejection vocabulary is proportional, not padded; the four classes are `Result`, `_Reservation`, `_LedgerFile`, `QuotaLedger` — one per thing the feature names.

Anchor 3 is not reachable. No simplification of *this* design has a before and after recorded anywhere. The mechanical block's T/U/W columns are three different artifacts, not one design measured twice, and the packet says so itself at `EVIDENCE.md:3-5`.

Rule 4 disclosure: the writing here is unusually clear and it did tempt me toward 3. It is not an input; I scored the figures and the write sites.

### D3 — modularity

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `quota_ledger.py:72-92` — `_LedgerFile`, the only code in the artifact that touches a filesystem.
- `quota_ledger.py:134`, `quota_ledger.py:168`, `quota_ledger.py:193` — every crossing, and there are no others.
- `quota_ledger.py:110` — the domain constructs its own adapter from a path.
- `quota_ledger.py:10` — the domain module imports `pathlib`.
- `EVIDENCE.md:322-324` — `declared_interfaces` 0, `declared_interface_methods` 0, `internal_import_edges` 0.
- `EVIDENCE.md:158-170` — the fake and real port-binding columns are identical on all eleven rows.

**Refuses to claim** (required and non-null for a score of 4): *n/a — not a 4.*

**Rationale:**

Anchor 2 holds and anchor 3 fails, both on runtime evidence rather than imports. `_LedgerFile` is a two-method seam (`append`, `lines`) and it is the only place in the artifact that opens a file; every crossing goes through it. So a boundary is discernible and the code follows it.

Anchor 3 fails on both of its clauses. The domain *does* import its I/O: `from pathlib import Path` sits in the same module as `QuotaLedger`, and the file-writing class is in that module too, so the domain cannot be loaded without it. And the adapter cannot be replaced without touching the domain — I tried at runtime rather than reading imports. `QuotaLedger.__init__` takes `(quotas, ledger_path)` and constructs the adapter itself at line 110, so passing a fake ledger object raises `TypeError: argument should be a str or an os.PathLike object … not 'FakeLedger'`. The only substitution that works is monkeypatching the private module global `quota_ledger._LedgerFile`, which I ran and which does work — but that is not a designed seam, it is undeclared, it is private, and it replaces the class process-wide for every instance. I will not name that as "the specific swap" the anchor asks for.

Anchor 4 is doubly out: the fake and real columns are byte-identical across all eleven rows, which the packet says is what happens when the artifact ships no second implementation, and those columns are exactly the ones carrying the red M07 positive control, so they are a floor either way.

This is a 2 and not a 1 because the artifact does not overclaim: `NOTES.md:115-118` says it deliberately added no abstraction over the file beyond the one class that writes it, and the feature leaves that free.

### D4 — behavior preservation

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `EVIDENCE.md:61-63` — the shared behavioral suite, unchanged, 28 passed (I re-ran it).
- `EVIDENCE.md:178-187` — the executability table: `corpus-whole` 43128 cases, 3734 executed, 294 accepting `Reserve`, 0 failed on unmutated code.
- `test_quota_ledger.py:279-312` — `check_rules`, R1/R2/R3 recomputed from the file on disk at every step.
- `test_quota_ledger.py:315-362` — the sweep that drives it, and its anti-degeneracy guard at 358-362.
- `EVIDENCE.md:71-81` — the kill table, read and not verified by me.

**Refuses to claim** (required and non-null for a score of 4): *n/a — not a 4.*

**Rationale:**

Anchor 2: the enumerated contract is the shared suite, which I ran myself, unedited, against a copy — 28 passed — plus the artifact's own 32, which pass. Anchor 3: a model-derived check was run against this code and not only a hand-written one; the executability table records a generated corpus with a fixed `cases.py` sha1 shared across artifacts, 3734 cases executed, 0 failures on unmutated code.

Anchor 4 I did **not** award, though `executed_own_faults` is `true` and the gate is therefore open. Two reasons, and per the tiebreak rule I took the lower.

First, what I demonstrated capable of failing was the **hand-written** layer. I seeded ten behavior-breaking faults and ran them against the shared suite and the artifact's own tests; nine were caught. But I did not run the corpus, so the model-derived instrument's capability to fail is still the packet's kill table *read* rather than *checked* — precisely the substitution rule 7 exists to stop.

Second, and more serious: the artifact's own model-based check is close to inert. `test_quota_ledger.py:315-362` is advertised as R1/R2/R3 under a long randomized sequence against an independent model. Instrumented on the real test function, pinned seed `20260804`, unmutated code, its 400 commands accept **1 reserve, 1 commit, 3 closes and zero releases** — 395 rejected, 4 ledger lines. Its own anti-degeneracy guard at 358-362 asserts that something was committed and something was closed but never that a release was accepted, so it passes on a single commit. `check_rules` is a genuinely good invariant, recomputed from the file rather than from an accessor; it is being evaluated almost entirely on a system in a rejecting state. My seeded double-refund in `release` broke R1 and survived all 32 own tests; only the shared hand-written suite caught it. An apparatus with a hole that size in its accepting paths does not get the top of this scale from me.

### D5 — honesty

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `quota_ledger.py:52-59` — `Result.rejected` asserts membership in the declared vocabulary; the code fails loudly rather than emitting a reason it has no basis for.
- `quota_ledger.py:114-116` — `available()` on an unknown tenant raises rather than inventing a sentinel.
- `NOTES.md:87-106` — "What I was unsure about", unprompted.
- `NOTES.md:60-63` — refuses to call the write ordering crash safety.
- `NOTES.md:73-77` — names a limit of the *shared suite* (it never allocates past `r3`).
- `test_quota_ledger.py:1-13` — the coverage claim that my measurement contradicts.

**Refuses to claim** (required and non-null for a score of 4): *n/a — not a 4.*

**Rationale:**

Anchor 2 is met in the code and not only in prose, which is the clause I tested hardest. `Result.rejected` asserts the six-reason vocabulary at the one choke point, so an undeclared reason crashes instead of being certified; the `_LedgerFile` and `commit` docstrings state what the design does and does not guarantee. `NOTES.md:87-106` then names limits unprompted, including one about the shared suite rather than about itself.

Anchor 3 is met, modestly but really. `available('nobody')` raises `KeyError`, and `NOTES.md:89-94` says this is deliberate: the feature gives queries no rejection channel, so rather than inventing a sentinel `0` or `None` the code refuses to answer a question it has no basis to answer, and the note says this is the one place a reasonable implementer could differ. `NOTES.md:60-63` refuses the adjacent flattering claim — the durable-write-first ordering is explicitly *not* called crash safety, "no fsync, no journaling, no recovery".

Anchor 4 I nearly gave and did not. The record does carry results unflattering to the artifact: `NOTES.md:96-103` volunteers that `reserve(t, 1.5)` is accepted and would be committed and printed as `1.5` in a `COMMIT` line, and `NOTES.md:125-129` self-discloses seeing filenames it was not meant to see. I put those aside because every unflattering item in the record is about the *spec's* ambiguity or the *author's process*, and none is about the artifact's own checking — while the single most unflattering fact I could find about this artifact is one it states the opposite of. `test_quota_ledger.py:1-13` tells the reader its tests cover "R1/R2/R3 under a long randomized command sequence checked against an independent model", and I measured that sequence accepting 5 of 400 commands with zero accepted releases. That claim is literally true and materially misleading. It is not anchor 0 territory — the volunteered limits elsewhere are substantive and real — but it is not the top of an honesty scale either. Torn between 3 and 4, took 3.

## Verdict

_One sentence a reader can act on._

A small, honest, well-partitioned implementation whose durable seam is real but unswappable and whose flagship model-based sweep is nearly inert — it accepts 5 of 400 commands and never an accepting release, and a conservation-breaking double refund survives its entire own suite.

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

**What I saw that I was not meant to see.** Nothing. I read only `JUDGE-DISPATCH.md`, my own card directory, the four files in `artifact_U/`, `examples/validation/ab/FEATURE.md` and `examples/validation/ab/tests/test_behavior.py`. I did not open `references/eval_scorecard.md`, any arm prompt, any other scorecard directory, any `-p1` directory, any `-rescore-v3` directory, `seeded_faults.toml`, `check_catalogue.py`, `reference/`, `reference_ports/`, `score_tools.py`, or the frozen rubric — the frozen rubric path appears in this card only because the verification command requires it and it was scaffolded into the header. I did not deduce which arm `H` is and I made no attempt to; I have no idea whether this artifact came from a with-prompt or without-prompt arm. I did notice that `artifact_U/NOTES.md:128` contains the string `this artifact/` in a list of filenames the author saw, which reads like a redaction of a real directory name — I did not act on it and it told me nothing about the arm.

**What I ran that changed a tree.** Nothing in the repository. All eleven mutations, the negative controls, the instrumented sweep and the swap probe ran on copies under the scratchpad, each applied to a fresh copy and destroyed after; the pristine copy's sha256 was re-checked at the end and was unchanged. The only files I wrote in the repository are this card and its JSON.

**What I REJECTED.**

1. **D5 = 4, rejected.** This was the closest call on the card. `NOTES.md` volunteers three genuinely unflattering facts (a non-integer amount would be held, committed and printed as `1.5`; `bool` is an `int` so `reserve(t, True)` reserves 1; and a self-disclosure of having seen filenames on a must-not-open list). Under a plain reading, "the record contains at least one result that is unflattering to the thing being scored" is satisfied and D5 is a 4. I rejected it on a distinction I want recorded because I am not certain it is the right one: **every unflattering item is about the specification or the author's process, and none is about the artifact's own checking.** The artifact is candid about what the *feature* leaves open and silent about what its *tests* cannot see — and I then measured the thing it was silent about. If a future adjudicator thinks that distinction is not in the anchor's text, this dimension moves to 4 and the total to 14.

2. **D5 = 1 or 0, also rejected.** Having found the sweep degenerate, I considered scoring the coverage claim at `test_quota_ledger.py:11-12` as "claims a clean it cannot support". I rejected that too: the sweep genuinely does recompute R1/R2/R3 from the file at every one of 400 steps, the claim is literally true, and there is no sign the author knew the seed produced a rejection sweep. Overclaiming by not looking is not the same as certifying a clean, and the code-level refusals at `quota_ledger.py:52-59` and `114-116` are real. Both directions were live; 3 is where the evidence sat.

3. **A reading of D3's anchor 3 that I considered and put aside.** Monkeypatching `quota_ledger._LedgerFile` *does* let a fake be substituted without editing the domain, and I have runtime evidence that it works. I could have named that as "the specific swap" and scored D3 = 3. I rejected it because the anchor's first clause ("the domain does not import its I/O") independently fails, and because a private module global that swaps process-wide for every instance is not an adapter boundary — it is the ability to reach into another module, which is the thing "import topology is not modularity" is warning judges away from crediting.

4. **NOTES.md:51-56 as a measured simplification (D2 = 3), rejected.** "I kept no in-memory mirror of the ledger" is a real design subtraction and it is argued from behavior. There is no before figure anywhere, so there is nothing to compare, and MF-020 is exactly the rule against reading an absent structure as a measured reduction.

5. **Evidence I decided did not count.** (a) The mechanical block's T/U/W comparison — three artifacts is not a before/after of one design, and the block is not scorable regardless. (b) The three port-binding columns as evidence of anything about swappability: they sit under the red M07 positive control (`EVIDENCE.md:275-301`, three instruments where a control that must be KILLED is SURVIVED against 294 measured accepting `Reserve` cases), so their SURVIVED cells are a floor; and the fake column is the real implementation anyway. (c) `NOTES.md`'s "28 passed / 32 passed" as evidence for D4 — I re-ran both rather than count the claim, and both reproduce. (d) My own `J10`, which I had drafted as a durability fault and which on inspection was behaviorally inert; I report it as a second negative control rather than as a fault that survived, because reporting it as a survived fault would have inflated my own miss count.

6. **A methodological note against my own D1.** My kill/miss evidence for D1 anchors 2 and 3 comes from the packet's corpus columns, which I did not run. I ran the two hand-written suites only. My own faults corroborate the *refusal* and *durable-content* classes on this code, but if the corpus columns were fabricated I would not have caught it, and D1 = 3 rests partly on them.

7. **Prose quality (rule 4).** The artifact's `NOTES.md` is the best-written document I have read in this repository and it tempted me upward on D2 and D5 both. It is not an input. Notably, the thing that most moved my scores *downward* was found by instrumenting the code that the well-written prose describes.
