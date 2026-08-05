# Scorecard — ab_quota_ledger, artifact `T`, judge pass 1

`run_id`: `20260805-T-p1` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

**You are scoring artifact `T`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:101-109`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:100-105`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:67-71`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136-141`
**Refuses to claim** (required and non-null for a score of 4): That R2 survives a durable write that fails -- NOTES.md:136-141 states that commit updates memory then appends, so a raising append would leave memory ahead of the ledger, and names this as the one place R2 is not enforced by construction. It also refuses to claim non-integer amounts are handled (NOTES.md:142-145), which I confirmed: `reserve("acme", 2.5)` is accepted and writes `COMMIT acme 2.5 2.5`.

**Rationale:** Anchor 2 is met by measurement, not claim: map-checking kills durable_content 2 of 2 where map-silent kills 1 of 2 (EVIDENCE.md:101-109), so content is asserted, not shape. Anchor 3 is met because corpus-neg kills guard_relaxation 3 of 3 while corpus-whole kills 0 of 3 (EVIDENCE.md:111-119) -- a refusal class the whole-view corpus structurally cannot reach. Anchor 4's "derived rather than hand-written" is carried by corpus-neg, and the record names an unreachable class; independently, T's own hand-written cases killed all eight faults I seeded, including three the shared suite misses. I score 4 rather than 3 because both halves of the top anchor are separately satisfied and I could not find a hard class its own cases left open.

## D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:118-120`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:87-114`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:146-181`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2: no god-state and no variable written from everywhere -- `_outstanding` is written by reserve/commit/release, `_committed` by commit alone (domain.py:158), `_closed` by close_tenant alone (domain.py:180), and `available` is derived (domain.py:120) so R1 cannot drift. Anchor 3 requires a simplification whose effect was measured with before and after figures both recorded; T argues its derivation of `available` in prose (NOTES.md:73-84) but records no before/after figures for it, so 3 is not satisfied. I deliberately did not convert the complexity table into a score. Note the four-module shape costs the largest public surface of the three, and I judged it proportional only because the extra module buys the demonstrated swap scored under D3.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:22-43`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:13-16`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/__init__.py:37-39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/memory_journal.py:14-22`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:26-36`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:168`
**Refuses to claim** (required and non-null for a score of 4): That anything else is indirected. NOTES.md:53-56: "There is no port in front of the arithmetic, no repository interface over the reservations dict, no service layer." It claims one port and demonstrates exactly one.

**Rationale:** I did not take the swap on trust -- I edited __init__.py:39 in a scratch copy to return `InMemoryJournal()`, changed no domain file, and all 28 shared behavioral tests plus all 53 of T's still pass, with no file created on disk at all. That is runtime evidence about what calls what, which is what anchor 3 demands over import topology. Anchor 4 is met by test_ledger.py:26-36, where one parametrized fixture drives every behavioral case against both `FileJournal` and `InMemoryJournal`, each asserting literal expected values rather than that the two wirings agree. Corroborated mechanically: T is the only artifact whose `corpus-port-swap:fake` column diverges from `:real` (EVIDENCE.md:168), which is measured proof that the fake column ran a genuinely different implementation.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:180-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:71-81`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:202-225`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:108-114`
**Refuses to claim** (required and non-null for a score of 4): Atomicity and crash-recovery. NOTES.md:136-141 refuses to claim any ordering or rollback guarantee on a failed durable write, and NOTES.md:129-135 refuses to invent reopen-and-resume behavior.

**Rationale:** Anchor 2 is met by an enumerated transcript check (test_ledger.py:202-225 reads R1/R2/R3/R5 off one concrete expected ledger) plus the feature's trickiest sentence pinned by name at test_ledger.py:108-114. Anchor 3 is met because the model-derived corpus decides against this code -- 3734 executed cases, 0 failures on unmutated code (EVIDENCE.md:180-187). Anchor 4 is met because behavior-breaking changes are demonstrated to be caught (EVIDENCE.md:71-81), and I reproduced this independently: eight faults I wrote, eight kills by T's own suite. The strongest single fact is that behavior survived a structural change I made myself -- the whole durable side replaced, 28 of 28 baseline behaviors intact.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136-141`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:102-123`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260-270`
**Refuses to claim** (required and non-null for a score of 4): That its structure was free of cost -- NOTES.md:102-123 records that the feature file and the structural ask actually conflicted, that `QuotaLedger` is therefore a factory function wearing a class's name, and that this is "the only place where the shape of the code is driven by a name the feature fixed."

**Rationale:** Anchor 2: blind spots are named unprompted and specifically (four interpretations at NOTES.md:125-147, each naming what was not built). Anchor 3 exists in the code, not only the prose: `Result.rejected` asserts membership of the six-reason vocabulary at domain.py:74, so the program refuses to emit an undeclared reason rather than pass one through; and test_ledger.py:260-270 parses the domain's imports because "does not import" is a claim about the file rather than about intent -- it refuses to let the boundary claim stand on prose. Anchor 4: the R2 gap under a failing append is a genuinely unflattering result about the artifact, and I verified the non-integer defect it admits is real. The prose is polished and did tempt me; I discounted it and scored the assert, the AST test, and the executed defect.

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

---

## Verdict

The only artifact of the three with a real port -- I replaced the entire durable side by editing one line outside the domain and all 28 baseline behaviors held with no file touched; treat its four-module shape as bought, not spent.

## Total

**18 of 20.** Contested dimensions (spread > 1 between the two blind passes): **none**.

## What this judge REJECTED

**I rejected scoring D1 and D4 from the packet's kill tables alone, and it changed a score.** W's and U's evidence packets are **byte-identical apart from the artifact label** -- I diffed them and the diff returned nothing but the two header lines. Eleven mutants across eleven instruments, the per-class block, the port-binding columns, the executability counts: not one cell differs between an artifact with a seam and a 400-command model oracle, and an artifact with `open()` inline in the domain and eleven tests. T differs from them in only three measured cells. Had I scored from the tables, U and W would have been indistinguishable on D1 and D4. That is why I wrote my own seven faults and ran them against each author's own suite -- which separated them immediately (W survived F4 and F5). If I had not done that, this round would have produced identical D1/D4 numbers for two artifacts that are not equivalent.

**I nearly gave W a D3 of 0 and backed away.** Anchor 0's text is "no boundary is discernible; state is written from everywhere." The first clause fits W exactly; the second does not -- its writes are localized per command and each dict has a small writer set. I took 1 and said why, rather than letting half an anchor's text drive a floor score.

**I nearly gave U a D3 of 3 and backed away after running the swap.** Rebinding `quota_ledger._LedgerFile` to a memory implementation *works* -- I ran it, the ledger produced its lines and no file was created. For about a minute that looked like "an adapter could be replaced without touching the domain." I rejected it: the name I rebound lives in the domain module, is private by convention, and the constructor at line 110 chooses the implementation itself. A swap that requires monkeypatching a module's private global is not a port, and counting it would have made D3 a test of Python's mutability rather than of the design.

**I rejected the reading that would have given all three artifacts a D4 of 4.** Every artifact is measured by the same model-derived corpus, so if the harness's demonstration counts as the artifact's, anchor 4 is free for everyone and the dimension carries no information. I adopted a stated crediting rule instead -- an artifact gets credit for a catch when either its own cases catch it or the shared corpus catches it against its code -- and then used rule 5's tie-break where only the second half held.

**I rejected the D2 reading that would have capped all three at 1.** D2's anchors 0 and 1 are about whether complexity was measured and related to the design, and *no artifact measured its own complexity* -- the mechanical block was produced by the harness. A literal reading puts all three at 0 or 1. I rejected it because the card explicitly instructs the judge to read the measured descriptor and then judge the structure, which makes anchor 2 a judgement about the design rather than about whether the author ran a tool. All three landed at 2 and none reached 3, because not one of them recorded a before/after figure for any simplification. That is the flattest result on this card and I think it is a real finding: **the "simplification with measured effect" anchor was reachable by any of them for the cost of two tool runs, and none did it.**

**A check I started and abandoned.** I began re-running `scripts/code_complexity.py` myself to sanity-check the mechanical block, and stopped -- the block is recorded and never scored, so a second copy of an unscoreable figure could only tempt me to use it. I did not run it.

**Evidence I decided not to count.** T's `corpus-port-swap:fake` cell for M09 (SURVIVED where `:real` KILLED) reads at first like an instrument miss. I decline to count it against T and count it *for* T instead: it is the signature of a fake that genuinely differs from the real adapter, which is the thing D3 anchor 4 asks for. For U and W the same column ran the real implementation, so it could not have differed.

## Disclosures

**Nothing on the must-not-open list was opened.** I did not open `arm_a/`, `arm_b/`, `arm_c/`, `examples/validation/ab/README.md`, `seeded_faults.toml`, `check_catalogue.py`, either `PREDICTIONS` file, `reference/`, `reference_ports/`, `UNBLINDING.md`, `measure/`, `arms/`, any `*EPIC*.md`, `specs/desired_program_model/`, or anything under `specs/.history/`. `ls` of the repository root returned several `*EPIC*.md` filenames in the listing; I read none of them. I read only `references/eval_scorecard.md`, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` trees.

**I did compare the artifacts, and I should say exactly how.** I scored each tree sequentially -- T fully, then U, then W -- and did not open a later artifact's source while an earlier one was open. But two cross-artifact facts entered my reasoning after all three were read: (1) the U/W evidence-packet diff, which is what drove me to write my own mutants, and (2) the observation that U's write-before-memory ordering (168 before 170) eliminates the exact gap T admits at NOTES.md:136-141. Fact (1) affected W's D1 and D4 scores. Fact (2) affected nothing -- I did not reward U or penalise T for it, since neither artifact's anchors turn on it. The seven faults I ran were designed once and applied in semantically matched form to all three, so no artifact faced an easier or harder set.

**What I inferred about arms, and whether I let it matter.** T is unmistakably the product of a prompt that asked for ports and adapters: its NOTES has a section titled "Where the feature file and the architecture ask conflicted" and refers to "Section 1" of an instruction it was given, which the shared FEATURE.md does not contain. W's NOTES likewise refers to "Section 1's instructions" and "Section 6's forbidden list", and U refers to no sections at all. So T and W were given some structured prompt and U apparently a different one. I could not tell which arm is which treatment, and more importantly the inference does not survive contact with the scores: T and W sit at opposite ends of D3 (4 and 1) despite both citing "Section 1", which is itself worth recording -- **whatever structural instruction T and W shared, only one of them produced a port.** I did not adjust any score for arm.

**Ways this round may be fooling itself.**

1. *The instrument cannot see the thing the epic is named after.* U and W score 2 and 1 on D3 for reasons visible in three lines of code each, and their measured evidence packets are byte-identical. Every port-related instrument -- `corpus-port`, `corpus-action-bound`, `corpus-port-swap:real`, `corpus-port-swap:fake` -- returned the same eleven verdicts for both. The only cell anywhere in the round that distinguished a real port from no port was T's M09 fake/real divergence, one cell out of ninety-nine.

2. *The positive control is RED in all three packets and the port columns are where it fails.* M07 SURVIVED on `corpus-action-bound`, `corpus-port-swap:real` and `corpus-port-swap:fake` for every artifact, each having executed 294 accepting `Reserve` cases -- so this is a demonstrated insensitivity, not an execution gap. `corpus-port` also got M07 wrong on all three. The instrument that the epic most needs to trust is the one whose deciding control is not green, and the packets say so plainly, to their credit.

3. *D1 and D4 risk becoming free points.* Both dimensions' upper anchors lean on model-derived cases that no artifact authored and that are identical across artifacts. If future rounds do not require judges to seed their own faults against each author's own suite, these two dimensions will report the harness's competence and call it the artifact's.

4. *My own faults are hand-written by one judge in one sitting*, and F4/F5 happening to be the two W missed could be luck. Seven faults is a small sample; I would not defend the W-versus-U gap on a wider set without re-running it.
