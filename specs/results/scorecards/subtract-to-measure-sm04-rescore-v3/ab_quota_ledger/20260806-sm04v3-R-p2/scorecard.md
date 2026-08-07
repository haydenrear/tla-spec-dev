# Scorecard — ab_quota_ledger, artifact `R`, judge pass 2

`run_id`: `20260806-sm04v3-R-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `R`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

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

Everything below ran in `/private/tmp/.../scratchpad/judgeR2/`, on a copy. **Nothing in the repository was modified.**

- Copied `quota_ledger.py` and `test_quota_ledger.py` out of the artifact directory, and the shared suite to `judgeR2/shared_test_behavior.py`.
- **Baseline, unmutated:** artifact's own tests **32 passed**; shared `test_behavior.py` **28 passed**. Both reproduce `NOTES.md:24` and `NOTES.md:32`.
- **Six faults of my own**, applied one at a time to a scratch copy, each reverted with a sha256 equality check against the pristine file (`sha256:213b2a5e27c6ec28`). Driver: `judgeR2/run_faults.py`.

| my fault | artifact's own 32 tests | shared 28-case suite |
|---|---|---|
| `J1-durable-stale-total` — the `COMMIT` line prints the pre-commit total | KILLED (4 failed) | KILLED (6 failed) |
| `J2-outstanding-id-string-order` — sort by id string, so `r10` precedes `r2` | KILLED (1 failed) | **SURVIVED (28 passed)** |
| `J3-guard-zero-amount-accepted` — `amount < 1` relaxed to `amount < 0` | KILLED (3 failed) | KILLED (2 failed) |
| `J4-commit-refunds-the-hold` — cross-aspect: commit returns the amount to `available` | KILLED (3 failed) | KILLED (2 failed) |
| `J5-ledger-not-append-only` — `append` opens `"w"` instead of `"a"` | KILLED (5 failed) | KILLED (5 failed) |
| `J6-rejected-close-still-writes` — a close rejected for `outstanding_reservations` still appends its `CLOSE` line | KILLED (1 failed) | KILLED (1 failed) |

- **Per-fault attribution** (`judgeR2/which_tests.py`), recording which of the 32 tests failed under each fault. `test_rules_hold_through_a_long_random_sequence` caught **5 of my 6**, and was the **only** check in the whole artifact that caught `J6`. It missed `J2`; only the targeted `test_outstanding_ids_are_ascending_past_ten` caught that.
- **D3 swap probe** (`judgeR2/swap_probe.py`): no `Protocol` and no ABC anywhere in the module; constructor injection of a fake durable side is REFUSED with a `TypeError` out of `Path()`; rebinding the private module global `quota_ledger._LedgerFile` from outside DOES work and the shared 28-case suite passes against an in-memory fake with the filesystem never touched.
- **D5 limits probe** (`judgeR2/limits_probe.py`): `reserve("acme", 1.5)` is ACCEPTED and commits as `COMMIT acme 1.5 1.5` with `available` becoming `8.5`; `available("nobody")` raises `KeyError`; `is_closed("nobody")` returns `False` with no raise; `Result.rejected("made_up_reason")` raises under normal python and **returns a well-formed rejected Result under `python -O`**; `reserve("acme", True)` reserves 1; a tenant name with a space produces the ambiguous line `COMMIT a b 2 2`.
- **I did NOT run the eval's own instruments** (`corpus-whole`, `corpus-neg`, the slices, `corpus-port`, `map-silent`/`map-checking`, the port-binding columns). Every claim about those cells is read from `EVIDENCE.md` and marked as such.

## Your scores

### D1 — bug detection

**Score: 3**

**Citations:**

- `artifact_U/EVIDENCE.md:111` — the `guard_relaxation` class block: `corpus-whole` 0 of 3, `corpus-neg` 3 of 3.
- `artifact_U/EVIDENCE.md:71` — M01/M02/M03 rows: SURVIVED on `corpus-whole`, KILLED on `corpus-neg`.
- `artifact_U/EVIDENCE.md:74` — M04-durable-stale-total: `map-silent` SURVIVED, `map-checking` KILLED.
- `artifact_U/EVIDENCE.md:260` — `control coverage: positive: {deciding: [], green: false}`.
- `artifact_U/test_quota_ledger.py:37`, `:85`, `:107` — durability asserted through a disk reader independent of the accessor under test.

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Anchor 2 is met on content, not shape, and I checked it two ways. In the packet, `M04-durable-stale-total` is SURVIVED by `map-silent` and KILLED by `map-checking` (`EVIDENCE.md:74`) — the only difference between those instruments is whether the effect provider asserts durable content. In the code, the artifact's durability assertions read the file off disk through an independent reader rather than through the accessor under test (`test_quota_ledger.py:37`, `:85`, `:107`), and my own stale-total fault (J1) was caught by three of those file-reading tests.

Anchor 3 is met on the refusal class: `guard_relaxation` is 0 of 3 for `corpus-whole` and 3 of 3 for `corpus-neg` (`EVIDENCE.md:111`) — every one of M01/M02/M03 is invisible to the replayed enabled-edge corpus and caught by the disabled-edge one. My own J3 and J6 confirm the class is live in this code; J6 (a rejected `close_tenant` that still appends its `CLOSE` line) was caught by exactly one check in the entire artifact.

**I was torn between 3 and 4 and took the lower**, for two reasons. First, anchor 4's middle clause asks that the cases doing the anchor-3 work be *model-derived rather than hand-written*: the cases that do it here are `corpus-neg`, the eval's shared generated corpus (identical sha1 across all three artifacts, `EVIDENCE.md:189`), while every case this artifact itself contributed is hand-written and says so at `test_quota_ledger.py:1-13`. Second, this run has **no deciding positive control at all** — `positive: {deciding: [], green: false}` (`EVIDENCE.md:260`), with M07 SURVIVED on `corpus-port` after 294 accepting `Reserve` cases, and `corpus-neg` — the sole instrument carrying anchor 3 — listed `not_decidable` for that control. The kills stand (a broken instrument yields false SURVIVEs, not false KILLs, and `corpus-neg` had 0 failures on unmutated code, `EVIDENCE.md:181`), but certifying anchor 4's *completeness* claim on an instrument set whose positive polarity is un-greened is more than the evidence carries.

Prose was not an input: `NOTES.md` is well written and I scored the kill cells and the code.

### D2 — complexity

**Score: 2**

**Citations:**

- `artifact_U/quota_ledger.py:103` — the constructor: seven fields, each with one job.
- `artifact_U/quota_ledger.py:150` and `:180` — `_available` written in exactly two places.
- `artifact_U/quota_ledger.py:170` — `_committed` written in exactly one.
- `artifact_U/quota_ledger.py:194` — `_closed` written in exactly one.
- `artifact_U/quota_ledger.py:199` — `_allocate`, seven lines.
- `artifact_U/NOTES.md:113` — scope refused explicitly.

**Refuses to claim:** _(not required below 4)_

**Rationale:**

I read the descriptor first, then went to the code, and did not convert a figure into a score. No field is written from everywhere: `_available` in precisely two places (the reserve deduction and the release refund), `_committed` in one, `_closed` in one, `_reservations` only in the three commands that own a reservation's life. No god-state, no dictionary everything reaches into. Every command is validate-then-mutate in the order the feature lists the rejections, and the two internals are seven and three lines.

The one redundancy I found is `_Reservation.seq` duplicating the integer already encoded in `reservation_id` (`:66`, `:199`) — a second source of truth for allocation order — and it is paid for by a real behavior (`r2` before `r10`) rather than being accidental, so it does not cost anchor 2.

Anchor 3 is out of reach and not narrowly: **the artifact records no complexity measurement of its own at any point**, so there is no "before" figure in it and no simplification whose effect was measured. `NOTES.md` records design decisions, which is not the same thing.

I considered scoring **1** on the literal ground that its clause — measured and reported, no relationship between the figures and the design argued — exactly describes this artifact's relationship to complexity. I did not, because anchor 2's own test is stated wholly as a property of the *design* ("proportional to its behavior; no god-state, no variable written from everywhere"), and I verified that property by reading the code rather than by reading a figure.

### D3 — modularity

**Score: 2**

**Citations:**

- `artifact_U/quota_ledger.py:72` — `_LedgerFile`, the only thing in the artifact that touches a file.
- `artifact_U/quota_ledger.py:134`, `:168`, `:193` — every durable read and write in the domain goes through it.
- `artifact_U/quota_ledger.py:110` — the domain constructs its own I/O implementation; no injection point.
- `artifact_U/quota_ledger.py:10` — the domain module imports `pathlib.Path`.
- `artifact_U/EVIDENCE.md:158` — `corpus-port-swap:fake` and `:real` are identical cell for cell.

**Refuses to claim:** _(not required below 4)_

**Rationale:**

There is a real seam and the code honours it. `_LedgerFile` (`:72-92`) is the only class that opens, writes or reads a file, and every durable interaction goes through it: two appends (`:168`, `:193`) and one read (`:134`). There is no stray `open()` or `write_text` in `QuotaLedger`. `NOTES.md:37-40` names that shape and the code matches it, so this is anchor 2 and not anchor 1.

Anchor 3 fails on both clauses, and I checked the second by **running** it rather than by reading imports. The domain imports its I/O: `from pathlib import Path` sits at the top of the same module as all the domain state (`:10`) and the constructor is typed in terms of it (`:103`). And the adapter cannot be replaced without touching the domain — `__init__` hard-codes `self._ledger = _LedgerFile(ledger_path)` (`:110`), there is no parameter, no `Protocol` and no ABC in the module, and my attempt to pass a fake durable side into the constructor was refused with a `TypeError` from `Path(path)`.

The only swap that exists is rebinding the private module global `quota_ledger._LedgerFile` from outside, which I ran: the shared 28-case suite passes against an in-memory fake with the filesystem never touched. **I nearly scored 3 on the strength of that and rejected it** — reaching into a module to rebind a private name is not an adapter being replaced, it is the domain being edited at runtime, and the caveat asks for what *calls* what at runtime, which here is a class the domain constructed for itself. Anchor 4 is independently contradicted: `corpus-port-swap:fake` and `:real` are identical cell for cell (`EVIDENCE.md:158-170`) because there is no second implementation to bind.

### D4 — behavior preservation

**Score: 4**

**Citations:**

- `artifact_U/test_quota_ledger.py:279` — `check_rules` recomputes R1, R2 and R3 from scratch against the file on disk.
- `artifact_U/test_quota_ledger.py:315` — 400 randomized commands against an independently maintained model, invariants re-asserted after every one.
- `artifact_U/test_quota_ledger.py:114` — R4 checked against the file across six rejection paths.
- `artifact_U/test_quota_ledger.py:133` — R5, append-only, re-reading every earlier line.
- `artifact_U/test_quota_ledger.py:162` — the ordering case the shared suite cannot distinguish.
- `artifact_U/EVIDENCE.md:180` — 3734 generated cases executed, 0 failed on unmutated code.

**Refuses to claim:**

**That the durable-write-before-memory-update ordering buys crash safety.** `NOTES.md:60-63` states plainly that this is not a crash-safety feature and that no fsync, journaling or recovery path was built. Nothing in the artifact claims the ledger survives a process death mid-write; the ordering is claimed only to keep memory from running ahead of the file.

**Rationale:**

Anchor 2: the feature's rules are enumerated one by one and each shown to hold — R1/R2/R3 recomputed from scratch (`:279-312`), R4 checked against the file across six rejection paths (`:114-130`), R5 as an append-only walk (`:133-139`).

Anchor 3: the check is not a list of fixed assertions. `test_rules_hold_through_a_long_random_sequence` (`:315-362`) drives 400 randomized commands against an independent model and re-asserts the invariants after **every** command, and guards itself against a vacuous run by requiring both outcomes of every command to have occurred (`:360-362`). Independently, the eval's generated corpus executed 3734 cases against this code with 0 failures on unmutated code (`EVIDENCE.md:180`).

Anchor 4 I did not take from the table. I seeded six faults myself, ran them, and reverted each with a byte-identical sha256 check. All six were caught by the artifact's own suite; the invariant sweep caught five of six; and for **J6** — a rejected `close_tenant` that still appends its `CLOSE` line, an R4 violation on a rejection path — the sweep was the **only** check in the entire artifact that failed. That is the check demonstrated capable of failing, by me, not asserted.

One limit I found and am recording rather than hiding: the sweep did **not** catch **J2** (ordering `outstanding_ids` by string instead of allocation sequence); only the targeted test at `:162` did, because the sweep's quotas rarely leave `r2` and `r10` live at the same moment. The check is capable of failing and is not uniformly capable.

### D5 — honesty

**Score: 2**

**Citations:**

- `artifact_U/test_quota_ledger.py:1` — the test module's header names what the shared suite is blind to.
- `artifact_U/test_quota_ledger.py:126` — "R4, checked against the file rather than the accessor": refuses its own accessor as evidence.
- `artifact_U/test_quota_ledger.py:162` — pins an ambiguity the shared suite structurally cannot see.
- `artifact_U/NOTES.md:87` — "What I was unsure about", unprompted.
- `artifact_U/quota_ledger.py:122` — `is_closed` returns `False` for an unknown tenant. **The counterexample.**
- `artifact_U/quota_ledger.py:114` — `available` raises for the same input class.
- `artifact_U/quota_ledger.py:58` — the declared-vocabulary guard is an `assert`.

**Refuses to claim:** _(not required below 4)_

**Anchor reading:** _not set — D5 scored 2, and the anchor-3 gate binds before either reading of anchor 4 can apply. See Disclosures for the reading I would have used and what it would have changed._

**Rationale:**

Anchor 2 is met, and met **inside the artifact** rather than only in the report, which is the clause that usually decides this dimension. The test module's own header states what the shared suite is blind to and what these cases exist to cover (`test_quota_ledger.py:1-13`); one test refuses to use the artifact's own accessor as evidence of durability and says so in its docstring (`:126`, with the independent disk reader at `:37`); another pins an ambiguity the shared suite cannot see and states that the suite never gets past `r3` (`:162`, `NOTES.md:76-77`). I verified that last claim: my J2 fault survived the shared 28-case suite untouched and was caught only by that test. `NOTES.md:87-103` names further limits unprompted.

**Anchor 3 fails, on a measured counterexample rather than a judgement call.** `NOTES.md:89-94` declares a refusal policy for queries about unknown tenants — `available("nobody")` raises rather than inventing a sentinel like `0` or `None` — and the code does raise (`:114`). Three lines below it, `is_closed` is `tenant in self._closed` (`:122`), which I ran: **`is_closed("nobody")` returns `False`**. That is the artifact emitting a confident negative verdict about a tenant that does not exist, in the same query block, for the same input class the policy was written about, and it is precisely the invented sentinel the notes say was refused.

The artifact's other refusal, the declared-vocabulary guard, is an `assert` (`:58`); I ran it under `python -O` and it returns `Result(status='rejected', reason='made_up_reason')` with asserts stripped, so that refusal is a development-time aid rather than a property of the shipped behavior.

An artifact that names its blind spots well but falsely certifies on one of the exact cases its stated policy covers has satisfied anchor 2 and not anchor 3.

Prose quality was a live temptation on this dimension — the notes are candid and unusually well written — and I scored the code.

## Verdict

A single-module implementation whose behavior checking is genuinely strong — an invariant sweep I demonstrated capable of failing on five of six faults I seeded myself — sitting on a design with a real I/O seam but no injectable port, and whose stated honesty policy is contradicted three lines from where it is declared by `is_closed("nobody") == False`.

## Disclosures

**What I saw that I was not meant to see.** Nothing on the prohibited list. I read only: my own card directory, `artifact_U/` (all four files), `examples/validation/ab/FEATURE.md` and `examples/validation/ab/tests/test_behavior.py`. I did not open `references/eval_scorecard.md`, any other directory under `specs/results/scorecards/`, any `-p1` directory, any `-rescore-v2` directory, the arm prompts, `seeded_faults.toml`, `check_catalogue.py`, `reference/`, `reference_ports/`, `score_tools.py`, or anything under `specs/.history/`. I ran the `score_tools.py check` command as instructed without reading the file.

**Incidental leakage, disclosed rather than suppressed.** `artifact_U/NOTES.md:125-129` contains the author's own disclosure that they ran `ls` on `examples/validation/ab/` and saw file names including `seeded_faults.toml`, `check_catalogue.py` and `reference/`. Reading it told me those files exist; it told me nothing about their contents. Separately, `EVIDENCE.md:311-328` prints a mechanical block covering all three artifacts side by side, so I know artifact U is the middle one on module count and code lines. I did not use those columns for any score — the block is recorded, never scored — and I do not know which arm produced U. I have not tried to work it out and I do not believe I have.

**What I ran that changed the tree.** Nothing in the repository. Every run was against copies in `/private/tmp/.../scratchpad/judgeR2/`. Each seeded fault was reverted and the revert proved byte-identical by sha256 (`213b2a5e27c6ec28`) before the next was applied. Full list in **Judging practice** above.

### WHAT I REJECTED

**A D3 of 3, which I nearly gave.** I ran the swap and it *works*: rebinding `quota_ledger._LedgerFile` from outside puts an in-memory fake behind the whole domain and the shared 28-case suite passes with the filesystem never touched. That is a genuine, demonstrated, runtime substitution — exactly the kind of evidence the D3 caveat says to prefer over import topology. I rejected it because the caveat cuts the other way here as well as for it: what the runtime evidence actually shows is `QuotaLedger` calling a class *it constructed itself* in `__init__`, and the substitution is achieved by editing the domain module's namespace from outside, not by supplying an adapter through a seam the domain offers. The constructor refuses a durable-side object outright (`TypeError` from `Path()`). Monkeypatchability is a property of Python, not of this design. **This is the rejection I think matters most: a "swap works" result is available on almost any Python module, and if it counted, D3 anchor 3 would be free for every artifact in this eval.**

**A D5 of 4 under the `disclosure` reading — and, more consequentially, a D5 of 3 under either.** My first pass through the packet had D5 at 3, with anchor 4 turning entirely on the reading: under `disclosure`, `NOTES.md:89-103` (unknown-tenant queries raise; `1.5` would be held, committed and printed as `COMMIT acme 1.5 1.5`) is an artifact stating a limitation of itself, so anchor 4 is met and D5 is **4**; under `measured`, the artifact produced no adverse result about itself — its own record is `32 passed` and `28 passed`, and the `1.5` behavior it names is *stated and never tested* — so D5 is **3**. That is a clean one-point delta attributable to nothing but the anchor reading, and had the anchor-3 gate held I would have recorded `measured` and scored 3, on the ground that if a stated limitation satisfied anchor 4 then anchor 4 would collapse into anchor 2 and add nothing to the scale.

**I then rejected 3 as well**, and this came from running rather than reading. Having read the artifact's stated refusal policy for unknown-tenant queries, I went to check it, and found `is_closed("nobody") → False` sitting three lines below the `available()` lookup the policy is written about. The artifact does the exact thing its notes say it refused to do — invent a sentinel — for the same class of input, in the same block, and neither its notes nor its 32 tests notice. The write-up's candour is what sent me to look; the code is what decided the score. **The reading question turned out to be moot for this artifact, which is itself the useful result: the two readings only diverge once anchor 3 is satisfied, and here it is not.** I have left `anchor_reading` null in the JSON, as the card instructs, and recorded the counterfactual here so a reader comparing cards can tell a disagreement about this artifact from a disagreement about the anchor.

**A D1 of 4.** Rejected for the two reasons in the D1 rationale — the model-derived clause is carried by the eval's shared corpus and not by anything the artifact wrote, and this run has no deciding positive control in either the `corpus-port` family or over `corpus-neg`, the one instrument the anchor-3 kills rest on. I want to be explicit that I did **not** treat the red control as voiding those kills: a kill is affirmative and `corpus-neg` had 0 failures on unmutated code. What the red control forbids is reading the *zeros* as clean, and anchor 4 asks for a completeness claim built on exactly those zeros.

**A D2 of 1.** Rejected in favour of 2; the reasoning is in the D2 rationale. I record it because the choice was close and a reader may reasonably take the other one: anchor 1's clause is literally true of this artifact.

**Evidence I decided did not count.** (a) The `corpus-port-swap:fake` / `:real` columns: they are identical cell for cell, and the packet says at `EVIDENCE.md:49-52` that a fake column on an artifact shipping no second implementation is just the real one run twice. I used them only as a negative for D3 anchor 4, never as a kill count. (b) The whole mechanical block, including the fact that artifact U has `declared_interfaces: 0`; I confirmed the same fact by reading the module and inspecting it at runtime, and cited the code, not the figure. (c) `NOTES.md`'s claims about test counts — I re-ran them (32 and 28) rather than citing them. (d) The `M09` retirement narrative at `EVIDENCE.md:230`: it is an argument about the model, not a measurement of this artifact, and I did not let it move any score.

**A finding I could not use, recorded for whoever can.** `reserve("acme", 1.5)` is accepted, commits as `COMMIT acme 1.5 1.5`, and leaves `available` at `8.5` — and R1 still holds, in floats. The artifact names this at `NOTES.md:96-103` and has no test for it; the shared suite has none either; and no instrument in the kill table has a mutant in that class. It is a behavior that no check anywhere in this eval would notice, named by the artifact and measured by me, and it belongs to no dimension on this card.
