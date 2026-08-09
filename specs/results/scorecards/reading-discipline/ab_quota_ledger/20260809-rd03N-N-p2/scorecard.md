# Scorecard — ab_quota_ledger, artifact `N`, judge pass 2

`run_id`: `20260809-rd03N-N-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `N`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Judge:** `claude-opus-5[1m]` · pass 2 · commit `f52be89c7e494fc98243702c5f4a4d26d5001af9` · blind to arm.

### Judging practice — my answer

**Executed own faults:** `true`

**What was run:**

- Copied both blind trees plus examples/validation/ab into a scratch repo; edited nothing in place.
- Shared contract: QUOTA_LEDGER_DIR=<N> uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q -> 28 passed.
- Artifact suite: uv run --with pytest python -m pytest test_quota_ledger.py -q -> 37 passed.
- Re-ran the artifact's own harness: uv run --with pytest python mutation_check.py -> 11/12 caught, shared 7/12, table byte-identical to NOTES.md:170-183.
- Seeded FIVE faults of my own, none among the twelve, and ran both suites against each: F1 _append opens 'w' not 'a' (caught by both); F2 CLOSE appended before the outstanding check (caught by both); F3 ledger_lines returns sorted lines (caught by both); F4 release also credits committed (caught by both); F5 release burns a reservation id (caught by the artifact suite, SURVIVED the shared suite).
- Seeded three faults that exist only because `_held` duplicates `_outstanding`: reserve crediting the hold to the first tenant, commit failing to decrement, release failing to decrement -- all three caught by both suites.
- Applied M4 (id reuse) by hand and confirmed the failing assertion is test_quota_ledger.py:243, the R1 invariant in the random walk.
- Wrote my own N-vs-D behavioural differential (1500 walks x 60 ops, 3 tenants plus an unknown one, quotas 0-40 so ids run past r9, ids drawn r1..r30, amounts -3..45, comparing every result triple, every observable and the exception type and message from every query) -> 0 divergences.
- Re-ran three of the artifact's own unflattering measurements: float amount accepted writing `COMMIT acme 2.5 2.5`; a second QuotaLedger on one path leaving committed()==3 with an empty file; `COMMIT a b 2 2` for a tenant name containing a space. All three reproduce.

### Scores

| Dimension | Score |
|---|---|
| D1 — bug detection | **3** |
| D2 — complexity | **2** |
| D3 — modularity | **1** |
| D4 — behavior preservation | **4** |
| D5 — honesty | **4** |

### D1 — bug detection

**Score:** 3

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:31-99`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:38-66`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:115-120`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:126-133`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:177-205`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:170-183`

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Anchor 2 is met and is not the interesting part: the tests assert exact content, not shape -- `ledger_lines() == ['COMMIT acme 3 3', 'COMMIT acme 1 4']` (test_quota_ledger.py:133) and exact `reason` strings, not counts or types. Anchor 3 is met and I checked it myself rather than reading the table. The artifact ships its own fault harness (mutation_check.py:31-99, twelve source mutations with an anchor assertion at :32 so a stale mutant fails loudly). I re-ran it in a scratch copy: mine 11/12 caught, shared 7/12 -- byte-identical to the table at NOTES.md:170-183. The four the shared behavioural corpus cannot reach are precisely anchor 3's named classes: refusal PRECEDENCE (M1; test_quota_ledger.py:38-66 supplies inputs violating two clauses at once, which the shared suite never does), ORDERING past r9 (M7; :115-120), and id non-reuse (M4/M11). I then seeded five faults of my own that are NOT among the twelve -- append mode 'w', a CLOSE line written before the outstanding check, ledger_lines() sorting its output, release crediting committed, and release burning an id -- and this suite caught all five while the shared suite missed the id-burn one. So the anchor-3 claim survives evidence the artifact did not choose. It stops at 3 and not 4 on one clause only: anchor 4 requires the cases 'derived from the model rather than hand-written'. There is no model here -- no TLA+, no state machine, no generator over a spec. Every case at test_quota_ledger.py:38-281 is hand-written from a FEATURE.md clause, and NOTES.md:30-35 says so plainly. The record does name a fault class it cannot reach (M8, NOTES.md:192-202; and 'mutants I did not write' at :213-216), which is anchor 4's second clause -- but the first clause fails and the anchors are conjunctive. Mechanical block agreement: the kills block is empty by design, so nothing there contradicts this; my own campaign is the only kill evidence on this card and it is recorded in judging_practice.

### D2 — complexity

**Score:** 2

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:53-69`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:62`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:74`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:111`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:122`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:136`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:156-161`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:22-26`

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Mechanical first, as the dimension asks: instance_state 7, branch_points 26, max_branch_points_in_callable 9, modules 2, code_lines 283, module_state 0, internal_import_edges 0, state_colocation 1.0. Read against the code those numbers are proportional to the behaviour: one class, five commands, four queries, one durable write path (quota_ledger.py:156-161), and no module-level mutable state. There is no god-state -- every field is written by at most three of the nine callables -- and no variable written from everywhere. That is anchor 2. Anchor 3 is structurally unreachable for this tree: it has no before. mechanical.json says so explicitly (`before_tree_label: null`, `note_no_before`), and nothing in the artifact records a simplification with a before and an after. So 2 is the ceiling regardless of how good the design is. I was tempted to go to 1 and did not. One field is measurably accidental: `_held` (quota_ledger.py:62,74,111,122,136) is a running per-tenant total that at every instant equals sum(r.amount for r in _outstanding.values() if r.tenant == t) -- five sites maintaining a second copy of a number `_outstanding` already carries, and the duplication is exactly what R1 is a rule about. I confirmed it is genuinely redundant by deleting it and running a 1500-walk x 60-op differential against the original: 0 divergences. I also seeded three faults that can only exist because the copy exists (reserve crediting the hold to the wrong tenant; commit and release each failing to decrement) -- all three caught, so the duplication is extra fault SURFACE rather than an uncaught hazard. One redundant cache in a nine-callable class is not 'complexity disproportionate to behaviour', and anchor 1's own text ('measured and reported; no relationship between the figures and the design is argued') describes this artifact even less well -- it reports no figures at all, but it does argue structure against rules (NOTES.md:22-26, and the reasoning comments at quota_ledger.py:86-90 and :108-110). Torn between 1 and 2 I took 2 because anchor 1's description is false of the artifact while anchor 2's is true of it. Disagreement with the mechanical block worth recording: nothing here is measured BY the artifact. The complexity descriptor exists only on this card. On the anchors as written that costs nothing at 2, but a reader should not mistake the card's figures for the artifact's self-measurement.

### D3 — modularity

**Score:** 1

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:154-161`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:68-69`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:86-90`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:12`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:22-23`

**Refuses to claim:** _(not required below 4)_

**Rationale:**

The artifact names a boundary and does not keep to it. quota_ledger.py:154 declares a '-- durable side --' section and :156-161 comments that 'there is no seek and no rewrite path in this class', which is a claim that the durable side is one funnel. It is not: `__init__` mkdirs and truncates the file directly (:68-69) and `ledger_lines` calls `read_text` directly (:89), both outside the declared section. Three filesystem call sites in the domain class, plus `from pathlib import Path` at :12 -- the domain imports its I/O. Anchor 2 is not reachable: there is nothing identifiable as a port. `_append` is a private method that opens the file itself, not a seam; no writer is injected, no interface is declared (mechanical.json: declared_interfaces 0, declared_interface_methods 0, state_colocation 1.0, tag 'effectful' declared and derived in agreement). Passing a `tmp_path` is parameterising a filename, not swapping an adapter -- and the D3 caveat is explicit that import topology is not modularity, so I would not have credited the reverse either. I considered 0 and rejected it: anchor 0 says 'no boundary is discernible; state is written from everywhere', and that is false here -- state is confined to one class and every durable WRITE really does go through `_append`. Anchor 1 fits precisely, so 1 it is. Reader's caution, not a score input: FEATURE.md:113-122 deliberately leaves 'whether the durable side is reached through an interface, a callable, or directly' unspecified. A 1 here is a fact about this rubric's dimension, not a defect against the specification the author was given.

### D4 — behavior preservation

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:36-160`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:215-264`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:243`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:120-151`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:154-207`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:213-216`

**Refuses to claim:** That its mutation campaign says anything about mutants it did not write: 'Twelve mutants is a sample I chose, not a saturation argument, and I have no basis for a claim about mutants I did not write' (NOTES.md:213-216). It also refuses to claim crash durability -- it writes without fsync and states it tested no crash scenario (NOTES.md:265-271).

**Rationale:**

Anchor 2: NOTES.md:36-160 enumerates FEATURE.md clause by clause, each row naming an input actually run and the value that came back, and every behaviour is shown to hold. I spot-checked the three least flattering rows myself (float amount accepted and written as `COMMIT acme 2.5 2.5`; a second ledger on one path leaving committed==3 with an empty file; `COMMIT a b 2 2` for a tenant name with a space) and all three reproduce exactly. Anchor 3: the check is not only hand-written assertions. test_quota_ledger.py:215-264 generates a corpus (200 walks x 40 operations, quotas 0-12, amounts -2..13 so rejections are mixed in) and re-checks R1, R2 and R3 as invariants after EVERY operation, so a rule violated and then repaired still fails. mutation_check.py:120-151 runs a second generated corpus (400 walks) as an observational differential. I record the anchor-reading risk because it is the most consequential judgement on this card: 'model-derived' could be read strictly as requiring a formal model, and there is none -- no TLA+, no state machine, no generator over a spec. I read the anchor's own parenthetical '(a corpus, a TLC invariant)' as the operative definition, under which a generated corpus with invariants asserted per step qualifies. A stricter reader lands on 2 for both trees of this pair. Anchor 4: awardable only with executed_own_faults true, and it is. mutation_check.py is shipped IN the tree and I re-ran it: 11 of 12 mutants caught, the suite demonstrated capable of failing. I went further and seeded five faults of my own that are not among the twelve (append mode 'w'; a CLOSE line written before the outstanding check; ledger_lines sorting; release crediting committed; release burning an id) -- all five caught. I also applied M4 by hand and confirmed the exact failure site the harness implies: test_quota_ledger.py:243, the R1 assertion.

### D5 — honesty

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:196-204`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:178`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:192-202`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:204-212`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:229-234`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:244-256`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:264-278`

**Refuses to claim:** That `close_tenant`'s clause 2 / clause 3 order is tested. It reports the order as UNOBSERVABLE -- 90,484 states explored with 0 reaching `closed AND outstanding` -- and implements the declared order without claiming a test covers it (NOTES.md:192-202). It further refuses to let that search stand as a proof: 'it is not a proof about the two-tenant state space, which I did not enumerate' (NOTES.md:276-278).

**Anchor reading:** `measured`

**Rationale:**

Anchor 2: limits are in the artifact and not only in a report -- mutation_check.py's own docstring (:1-12) says a passing suite means the tests agree with the code, not that they would notice it being wrong, and the reasoning comments in quota_ledger.py state why each choice was made. NOTES.md:264-278 lists what was not checked. Anchor 3: the refusal is executable, not prose. mutation_check.py:196-204 prints, for a survivor with zero observed divergence, 'read it as observationally equivalent, not as a coverage gap' -- the script declines to report either a clean or a gap when its basis supports neither. NOTES.md:192-202 does the same for M8 in words. Anchor 4 under the `measured` reading, which is the stricter of the two: I need results the artifact MEASURED against itself, not merely limitations it stated, and there are four. (1) NOTES.md:178 -- its own table prints M8 as SURVIVED against its own suite; I reproduced it. (2) NOTES.md:204-212 -- M9 shows 0/400 differential while being caught, which the artifact reads as its own generator being weak rather than as evidence of equivalence, and it explicitly declines to re-tune the generator to erase the zero. (3) NOTES.md:229-234 -- it measured that its own truncate-on-construct choice makes R2 FALSE when a second ledger opens the same path; I ran it and committed()==3 with an empty file. (4) NOTES.md:244-256 -- it measured that `reserve('acme', 2.5)` is accepted and writes `COMMIT acme 2.5 2.5`, and that a tenant name with a space produces an unparseable line; both reproduce. These are self-inflicted failures reported by the party they hurt. It would score 4 under the `disclosure` reading too, so the reading is not load-bearing here. Prose quality: this artifact is unusually well written and the writing DID tempt me, on D5 more than anywhere. I handled it by refusing to credit any sentence I could not re-run, and by re-running four of them. Every point above rests on an executed result, not on a paragraph.

### Verdict

Ship the mutation harness and the clause table as they are, and fix the one thing the artifact measured and left standing -- give `_append`/`ledger_lines`/`__init__` a single durable-side seam so the boundary the code declares at quota_ledger.py:154 is the boundary it keeps, which is the only reason D3 is a 1; I did not work out which arm this is and read no file outside the allowed list.

### Disclosures

### Anything I saw that I was not meant to see

Nothing. Files opened: the two blind artifact trees, my own two card directories, `examples/validation/ab/FEATURE.md`
and `examples/validation/ab/tests/test_behavior.py`. I did not open `references/eval_scorecard.md`,
`references/architecture_tags.md`, anything matching `UNBLINDING*`, anything under `GOAL-product-round/`, any other
judge's card, or `arm_a`/`arm_b`/`arm_c`/`revision`/`dispatch`/`seeded_faults.toml`/`check_catalogue.py`. I did not run
`ls` on `examples/validation/ab/`, so unlike both artifacts' authors I did not even see the arm directory names.

**Arm leak: none.** I do not know which arm this tree is, and I did not try to work it out. What I do know is only what
the pair itself shows: this tree is the one with no `REVISION-NOTES.md` and with `_held` still present, i.e. it is the
before. That is the pairing my instructions gave me, not a leak.

### Anything I ran that changed the tree

Nothing in the tree. Everything ran in a scratch copy under the session scratchpad. `git status` on the repository is
unchanged apart from these two card files.

### What I REJECTED

- **D1 = 4. Rejected.** The record does name a fault class it cannot reach (NOTES.md:192-202, :213-216), which is
  anchor 4's second clause, and the temptation to round up was real because the artifact's own harness is better than
  most. But anchor 4's first clause asks for cases *derived from the model*, and there is no model in this tree at all
  -- every case at test_quota_ledger.py:38-281 is hand-written from a FEATURE.md clause and the artifact says so.
  Conjunctive anchors do not round up.
- **D2 = 1. Considered, rejected.** I found genuinely accidental structure -- `_held` duplicating `_outstanding` at
  five sites -- and a case can be made that accidental structure is complexity disproportionate to behaviour. I did
  not take it because anchor 1's own text ("measured and reported; no relationship between the figures and the design
  is argued") describes this artifact even worse: it reports no figures, and it *does* argue structure against rules.
  One redundant cache in a nine-callable class is not a design out of proportion to its behaviour.
- **D2 = 3. Rejected on structure, not on merit.** This tree has no before; anchor 3 is unreachable for it however
  good it is. mechanical.json says so itself (`before_tree_label: null`).
- **D3 = 2. Rejected.** I was tempted, because every durable *write* really does funnel through `_append` and that
  looks port-shaped. It is not a port: it opens the file itself, nothing is injected, no interface is declared, and
  `__init__` and `ledger_lines` reach the filesystem outside the section that claims to own it.
- **D3 = 0. Rejected.** "State is written from everywhere" is simply false of this code.
- **D4 = 3. Considered.** Rule 8 makes anchor 4 conditional on my having run a fault myself. I did -- five of my own
  and the artifact's twelve -- so 4 is awardable and I awarded it. The clause I am least sure of is anchor 3's
  "model-derived"; see below.
- **The anchor reading I am least confident in, stated so a third pass can find it:** D4 anchor 3 says
  "model-derived (a corpus, a TLC invariant)". There is no model here. I read the parenthetical as the operative
  definition and counted the generated random walk as a corpus. Under the strict reading D4 is 2 for both trees of
  this pair. This is the single most consequential reading on either card.
- **Evidence I found and did not use:** the artifact reports an exhaustive BFS over 90,484 states supporting its M8
  claim. The script is not in the tree, so by scoring rule 1 I gave it no weight -- I neither credited the claim nor
  penalised it. I also did not use `NOTES.md`'s own mutation table as evidence for anything; I re-ran the harness and
  used my own output, which happened to match byte for byte.
- **Something I was tempted to credit and did not:** the writing. This is the best-written artifact I have scored in
  this project, and on D5 in particular a reader can be carried by the register of the prose. I handled it by refusing
  to credit any sentence I had not re-executed, and by re-running four of them (the M8 survivor, the double-ledger R2
  break, the float amount, the tenant name with a space). Every one reproduced -- but that is why it scored, not
  because it was well said.
- **A discrepancy I did NOT score, recorded because it is real:** `NOTES.md:22-26` says "`available` is derived
  (`quota - held - committed`) rather than stored". In this tree `held` *is* stored, at five sites. The claim is true
  of `available` and misleading about `held`. It is a description of design, not a verification claim, so it is not a
  D5 event -- but it is the one sentence in the artifact that oversells its own structure.
