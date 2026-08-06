# Scorecard — ab_quota_ledger, artifact `U`, judge pass 2

`run_id`: `20260806-v1-U-p2` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

**You are scoring artifact `U`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The rules, in the file where the score is written

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

## D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:85-88`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:114-131`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279-312`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111-120`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2 is met by assertions that read the durable artefact rather than the accessor that reports on it: file_lines() at test_quota_ledger.py:37-39 opens the path independently, and test_commit_lines_reach_the_file_itself (85-88) pins the exact two lines with their running totals. Anchor 3 is met by the refusal class, which the whole-view corpus structurally misses (guard_relaxation 0 of 3 for corpus-whole, EVIDENCE.md:111-120): test_a_rejected_command_writes_nothing_durably (114-131) parametrises six rejections and compares the file's bytes across each, and 255-273 pins both declared rejection orders. The strongest instrument here is check_rules (279-312) recomputing R1, R2 and R3 from the file after EVERY command of a 400-step randomised sequence (315-362), with an anti-vacuity guard at 360-362 asserting the sweep actually reached acceptances rather than only rejections -- that is the artifact's own control on its own oracle and it is unusual. I did check the sweep against the code rather than taking it on trust, and it has one hole worth recording: line 336 validates an ACCEPTED reserve only for known-tenant, not-closed and amount>=1, and U maintains R1 incrementally, so an over-quota acceptance would drive `available` negative while R1 still balanced -- the sweep would not catch a relaxed quota guard. That does not cost the anchor, which asks for at least one fault in a hard class, but it is why I did not read the sweep as blanket coverage. Anchor 4 refused: U's oracle is an independently hand-written model in its own test file (315-324), not derived from a model, and the model-derived corpus is the eval's shared instrument, byte-identical across artifacts (EVIDENCE.md:53-56). Control caveat applied: the positive control is red with no deciding instrument for its polarity (EVIDENCE.md:260), so corpus-port's SURVIVED cells were read as floors and used as evidence for nothing.

## D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

**Score:** 2

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:103-110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:138-152`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:174-182`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:28-37`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:327-328`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2, no higher. The descriptor puts U in the middle on every raw figure (1 module, 151 code lines, 17 callables) and at the top on branch_points_in_effectful_modules (10) and instance_state_in_effectful_modules (8) (EVIDENCE.md:327-328) -- because there is one module and it holds both the rules and the file. Per rule 7 that figure is recorded, not scored; what it describes is the D3 problem, not disproportionate complexity. Judging the design: five pieces of state declared in one constructor (103-110), and each has few and named writers -- `_available` written only by reserve (150) and release (180), `_committed` only by commit (170), `_closed` only by close_tenant (194). No god-state, nothing written from everywhere, and the rejection vocabulary is collected once and enforced at the single construction site rather than restated at each call (28-37, 57-59), which is behaviour R4 requires made structural. The cost against T, recorded but not penalised: `available` is stored and maintained rather than derived, so R1 is an invariant two call sites must keep rather than an arithmetic identity -- proportional to the behaviour, but not free. Anchor 3 refused: no before/after complexity figures exist for U anywhere in the packet or its notes, and the cross-artifact table is not a before/after.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** 2

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72-92`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:132-134`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:10`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:158-170`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2 is fully met and anchor 3 is not. `_LedgerFile` (72-92) is an identifiable seam that declares itself the durable side, and the code follows it without leaks: every durable write goes through `self._ledger.append(...)` (168 and 193) and every read through `self._ledger.lines()` (134), so no path, encoding or file mode appears anywhere in the rules. That is what anchor 2 asks for. Anchor 3 asks whether the domain imports its I/O and whether an adapter could be replaced without touching the domain, and on both counts the answer is no: pathlib is imported into the same module as the rules (10), and `QuotaLedger.__init__` takes a path and constructs the concrete `_LedgerFile` itself (110), so the rules own the choice of adapter and no caller can substitute another without editing the class. The measurement agrees rather than contradicts: `declared_interfaces` is 0 for U, and corpus-port-swap:fake is byte-for-byte the same verdict column as :real on all eleven mutants (EVIDENCE.md:158-170) because the runner had no second implementation to bind and re-ran the real one (EVIDENCE.md:49-51). I scored the code as built, not as intended; U's notes say plainly it chose not to abstract over the file beyond that class (NOTES.md:114-118), which is a coherent choice and still a 2.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:59-62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:178-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:69-81`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315-362`

**Refuses to claim** (required and non-null for a score of 4):

That the write-before-mutate ordering in commit and close_tenant buys crash safety. U states that nothing in the feature requires it, that 'it is not a crash-safety feature and I did not build one (no fsync, no journaling, no recovery; that is out of scope)' (NOTES.md:59-63), and separately refuses to claim any behaviour for a non-integer amount, naming that 1.5 would be held, committed and printed into a COMMIT line, and that the six-reason vocabulary has no way to reject it (NOTES.md:96-103).

**Rationale:**

Anchor 2: the behaviours are enumerated and each shown to hold -- 28 of 28 on the unedited shared contract (EVIDENCE.md:59-62), plus U's own construction, durability, id-allocation and rejection-order groups, plus check_rules recomputing R1, R2 and R3 after every command of a 400-step sequence (test_quota_ledger.py:315-362). Anchor 3: a model-derived check was run against this artifact and passed on unmutated code -- corpus-whole 3734 executed, 0 failed, with the executability column beside it so the zero is distinguishable from an instrument that ran nothing (EVIDENCE.md:178-187). Anchor 4: the check is shown capable of failing -- ten deliberate behaviour-breaking changes were applied one at a time and reverted byte-identically, and every one of M01..M10 dies on at least one instrument (EVIDENCE.md:69-81), while the negative control N01 survives everywhere as required. Two limits I applied rather than papered over: the positive control M07 is red and has no deciding instrument for its polarity (EVIDENCE.md:260), so I rested this on corpus-whole, corpus-slice-res, map-checking, map-silent and suite, which decided it correctly, and not on corpus-port or the port-binding columns; and I ran nothing myself, because the rubric records that judge-run faults are exactly what made this dimension move on unchanged input.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:87-103`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:59-63`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:74-77`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:163-166`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:1-13`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2 is met in the artifact rather than only in a report: quota_ledger.py:163-166 states the ordering decision and its reason in the commit method itself, quota_ledger.py:74-77 states why reads come from the file rather than a mirror, and the test file's own docstring (1-13) declares what it is covering that the shared suite does not. NOTES.md:87-103 names its blind spots unprompted, including one that is a hole in its own implementation: a non-integer amount would be held, committed and printed into a ledger line, and it says so instead of leaving it unmentioned. Anchor 3 is met: U refuses to let a passing suite stand as a verdict its basis cannot support -- it records that the shared suite never gets past r3 and therefore cannot decide its reading of 'ascending', and pins the reading with its own case instead of claiming the shared suite confirmed it (NOTES.md:74-77) -- and it declines to call its write ordering crash safety (59-63). Anchor 4 refused, and this was the closest call on any of the three cards. U's record does contain something against its own interest -- it volunteers that it ran `ls` on the fixture directory and saw the names of files it was told not to open (NOTES.md:125-129). I decided that is a disclosure about the author's conduct, not a RESULT about the artifact being scored, and the anchor asks for a result. Rule 5: torn, took the lower.

## Verdict

Take U for detection, not for the boundary: it has the strongest oracle of the three -- a 400-step randomised sweep that recomputes R1, R2 and R3 against the file on disk after every single command -- but the rules construct their own file adapter from a path, so nothing about the durable side can be replaced or faked without editing the class that holds the rules.

## Disclosures

**Anything I saw that I was not meant to see.** Nothing on the forbidden list was opened. I read `references/eval_scorecard.md`, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, every file under the three permitted `specs/results/scorecards/ports-as-adapters/blind/artifact_*/` directories, `examples/validation/scorecards/score_tools.py` (the checker, to learn exactly what `check` enforces — the `file:line` regex and the `refuses_to_claim` rule), and my own three card directories. I opened no arm prompt, no `examples/validation/ab/README.md`, no `seeded_faults.toml`, `check_catalogue.py`, `reference/` or `reference_ports/`, nothing named `PREDICTIONS*`, nothing else under `specs/results/scorecards/` (no `UNBLINDING.md`, `RESULTS.md`, `INDEX.md`, `SELF-IMPROVEMENT.md`, `INSTRUMENT-LOG.toml`, `HISTORY-*`, `measure/`, `arms/`, `channels/`, no other round's cards), nothing under `specs/.history/`, no `*EPIC*.md`, nothing under `specs/desired_program_model/`, and no directory ending `-p1`. One incidental exposure to record: I ran `ls` at the repository root before starting and therefore saw the FILENAMES of the `*EPIC*.md` files and of `PORTS-AS-ADAPTERS-STARTER-PROMPT.md`, one of which names the epic these artifacts came from. I opened none of them and read no contents of any of them.

**De-blinding.** I did not look for the mapping and I do not know which arm any label denotes. I should still say that these artifacts partly de-blind themselves to anyone who reads them: one ships a declared port with two working implementations and a composition module, one ships a single module with an internal file class, and one ships a single module with inline file calls. If this eval's arms are an architecture prompt against a control, the likely ordering is legible from the code alone. That is a property of the fixture rather than a leak from anything I read, and I record it because a judge who noticed it should say so.

**Anything I ran, and whether it changed anything on disk.** `ls`, `grep -n`, one `diff` between two permitted `EVIDENCE.md` files, `cat` of the scaffolded cards and `mechanical.json`, two small Python scripts of my own (kept outside the repository, in the session scratchpad) that patched my three `scorecard.json` and three `scorecard.md` files, and `python3 examples/validation/scorecards/score_tools.py check ... --require-filled`, which reported `0 problem(s)`. I executed no artifact code, ran no pytest, seeded no fault, and copied nothing to a scratch directory for execution. Nothing on disk changed outside my three card directories. `mechanical.json` is untouched in all three, because I measured nothing and it is recorded rather than scored.

**REJECTED — the four that apply to all three cards.**

1. **The size ranking as a D2 tiebreak.** I nearly ranked D2 by `code_lines` (78 / 151 / 202). Rejected under rule 7 and MF-020: the smallest artifact here is simultaneously joint-worst on branch points and instance state inside its effectful module, so the two rankings point in opposite directions. Converting either into a score would have been arithmetic wearing judgement's clothes. All three sit at D2 = 2 and the disagreement is written into the rationales as a finding instead.
2. **Every `SURVIVED` in the `corpus-port` column and in all three port-binding columns, as evidence about any artifact.** The positive control M07 is red, its polarity has NO deciding control at all (`"positive": {"deciding": []}`), and the port-binding block records M07 `SURVIVED` on an instrument that executed 294 accepting `Reserve` cases. Under a red positive control those zeros are a floor, not a measurement. This cuts against the artifact I scored highest as much as for it: I did not use the port corpus as credit on D3 either.
3. **D1 = 4 for anybody.** The only model-derived cases in this eval are the shared corpus, recorded as byte-identical across all three artifacts under a single `cases.py` sha1. It is the eval's instrument and belongs to no artifact; crediting it would have handed all three the same 4 for something none of them did, and would have made D1 stop discriminating at exactly the point it was supposed to.
4. **Seeding my own fault to settle D4.** The rubric's own instability note records that judges who did this moved D4 and D5 by four dimension-points across byte-identical trees. Three D4s of 4 is a lot of 4s and I want the reason on the record: they rest entirely on the packet's kill table, executability counts and control status. If they are wrong, they are wrong for a reason a reader can check in the table rather than in something I did off the record.

**REJECTED — specific to this card.**

- **D5 = 4. This was the closest call on any of the three cards.** This artifact volunteers, unprompted, that it ran `ls` on the fixture directory and saw the names of files it had been told not to open — a finding against its own interest, in its own record, which is exactly the shape anchor 4 rewards. I decided it is a disclosure about the author's CONDUCT rather than a result about the ARTIFACT, and the anchor asks for a result. Rule 5, took the lower. A second judge reading it the other way would not be unreasonable and this is the dimension most likely to come back contested.
- **D3 = 3.** `_LedgerFile` is a real seam, every durable read and write goes through it, and nothing about files leaks into the rules — it is tempting to call it a port and award the swap. Refused: the rules import `pathlib` and construct the concrete adapter from a path in their own constructor, so there is nothing a caller could substitute without editing the class that holds the rules. The measurement agrees, and I checked that it agreed rather than assuming it: the fake and real port-swap columns are identical on all eleven mutants because there was no second implementation to bind.
- **Crediting the randomised sweep as "model-derived" for D1 = 4.** It is a hand-written oracle living in the test file. It is the best oracle in this fixture and it is still hand-written.
- **A claim I nearly made IN THIS ARTIFACT'S FAVOUR, and checked instead.** I was about to write that the 400-step sweep covers the guard relaxations. It does not: its acceptance check validates known-tenant, not-closed and `amount >= 1` only, and this design maintains R1 incrementally, so an over-quota acceptance drives `available` negative while R1 still balances. A relaxed quota guard walks straight through the sweep. That is in the D1 rationale, and it is the one place where reading the code changed what I was going to say about the tests.
