# Scorecard — ab_quota_ledger, artifact `T`, judge pass 2

`run_id`: `20260806-v1-T-p2` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:161-199`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:108-114`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:117-131`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:100-105`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:111-120`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2 is met by content, not shape: test_ledger.py:117-131 pins four interleaved ledger lines as literal strings including each tenant's running total, and every such case runs against both wirings, so a wrong-content fault cannot hide behind a length or type check. Anchor 3 is met twice over. (a) Refusals: test_ledger.py:161-199 parametrises nine rejections, snapshots all five observable queries INCLUDING the durable lines before and after, and asserts at line 199 that the snapshot was non-empty -- so it would catch a relaxed guard by the state it moved, not only by the reason string. The evidence packet shows this is the class the whole-view corpus structurally misses: guard_relaxation is 0 of 3 for corpus-whole (EVIDENCE.md:111-120). (b) Cross-aspect before-state: test_ledger.py:108-114 asserts available('acme')==7 AFTER a commit of 3, which is exactly the M08 fault. Anchor 4 is refused: T's cases are hand-written. The only model-derived cases in this eval are the shared corpus, which EVIDENCE.md:53-56 records as byte-identical across all three artifacts with one sha1, so it is the instrument, not T's case set, and it cannot be credited to any artifact. Prose was not an input; T's NOTES.md is the most confident of the three and I scored only the test file. Control caveat, applied: the positive control M07 is RED with no deciding instrument for its polarity (EVIDENCE.md:263), and the port-binding block records M07 SURVIVED on corpus-port-swap after 294 accepting Reserve cases, so I read every SURVIVED in the corpus-port column as a floor and used none of them as evidence about T.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:118-120`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:151-160`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:172-182`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:341-342`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:78`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2, no higher. Read the descriptor first: T is the LARGEST artifact on every raw figure (4 modules, 202 code lines, 6 classes, 25 public surface -- EVIDENCE.md:325-330) and the SMALLEST on the two figures that describe how much decision-making sits next to an effect (branch_points_in_effectful_modules 1 vs 10 and 10; instance_state_in_effectful_modules 1 vs 8 and 7 -- EVIDENCE.md:341-342). Those two rankings point in opposite directions; per rule 7 I converted neither into a score and record the disagreement as the finding. Judging the design rather than the figures: there is no god-state and no variable written from everywhere. `available` is not stored at all (domain.py:118-120), so R1 is true by construction rather than maintained by three call sites; `_committed` has exactly one writer (domain.py:158), `_closed` exactly one (domain.py:180). A measured consequence, which I nearly took as anchor 3 and did not: two of the ten faults could not be seeded into T by changing an existing statement and had to be inserted as new ones (`seeded_by: addition` at EVIDENCE.md:78 and :80), because the code sites those faults live in do not exist in T. That is a real, per-artifact effect of the simplification -- but it is not what anchor 3 asks for. Anchor 3 asks for before AND after FIGURES, and no before figure for T exists in the packet, in NOTES.md, or anywhere I am permitted to read. Refused, on rule 5.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:13-16`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:22-43`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/__init__.py:37-39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:26-36`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/memory_journal.py:14-22`

**Refuses to claim** (required and non-null for a score of 4):

That the fake covers the file adapter's own behaviour. T keeps its two file-specific cases outside the shared list precisely because they are about the file and not the rules (NOTES.md:93-100; tests/test_ledger.py:241-254), and the measured columns bear the limit out: a fault seeded in the real adapter is invisible through the fake (M09 SURVIVED under corpus-port-swap:fake, KILLED under :real, EVIDENCE.md:168). T also declines to indirect anything else -- no port over the arithmetic, no repository interface over the reservations dict (NOTES.md:53-55) -- so nothing but the durable side is swappable.

**Rationale:**

Anchor 3 first, then 4. The domain does not import its I/O: domain.py:13-16 imports __future__, dataclasses and typing and nothing else, and the driven port is declared in the domain's own vocabulary with a written contract (domain.py:22-43). The specific swap, named: quota_ledger/__init__.py:39 constructs `Ledger(quotas, FileJournal(ledger_path))`; replacing `FileJournal(ledger_path)` with `InMemoryJournal()` on that one line changes the durable side and touches no domain file, because __init__.py is the only module importing both. The rubric's caveat is the reason this is a 4 and not a 3 by assertion: import topology is not modularity, so I looked for what CALLS what at runtime. Two independent pieces of runtime evidence. (a) tests/test_ledger.py:26-36 is a parametrised fixture that builds the rules over FileJournal and over InMemoryJournal and runs the same case list against both, and each case asserts a literal expected value rather than that the two wirings agree -- the file's own docstring at lines 5-9 names that trap and avoids it. (b) The measured port-binding columns: on T alone of the three, corpus-port-swap:fake diverges from corpus-port-swap:real (M09 SURVIVED against the fake, KILLED against the real -- EVIDENCE.md:168), which is only possible if the binding actually changed the object being called at runtime. On U and W those two columns are identical because the runner re-ran the real implementation (EVIDENCE.md:49-51). So T's second implementation is a fact the instrument can see, not a claim in a comment.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:59-62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:178-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:69-81`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:202-226`

**Refuses to claim** (required and non-null for a score of 4):

That R2 holds if the durable append fails. T states plainly that commit and close_tenant move memory and then append, that a raising append would leave memory ahead of the ledger, and that this is 'the one place I can name where R2 is not enforced by construction' (NOTES.md:136-141). It also refuses to claim any behaviour for a non-integer amount, naming that 2.5 would flow into a ledger line unchallenged (NOTES.md:142-145).

**Rationale:**

Anchor 2: the behaviours are enumerated and each is shown to hold -- tests/test_ledger.py:202-226 reads R1, R2, R3 and R5 off one concrete expected transcript rather than off five separate weak assertions, and the shared behavioural contract passes 28 of 28 unedited (EVIDENCE.md:59-62). Anchor 3: the check is model-derived and was run against THIS artifact -- corpus-whole executed 3734 generated cases with 0 failures on unmutated code, and map-checking and map-silent the same (EVIDENCE.md:178-187); the executability column is what makes that a claim rather than a zero from an instrument that ran nothing. Anchor 4: the check is demonstrated capable of failing. Ten seeded faults were applied one at a time to a copy of T, proved to revert byte-identically, and every one of M01..M10 is KILLED by at least one instrument (EVIDENCE.md:69-81) while the negative control N01 SURVIVED everywhere as it must. I did not seed or run anything myself; the rubric's own instability note records that judges who ran their own faults moved this dimension by two points on byte-identical trees, and the packet exists so that this 4 rests on recorded measurement instead. One limit I applied rather than ignored: the positive control is red (EVIDENCE.md:263), so I rested the anchor only on the instruments that DID decide M07 correctly -- corpus-whole, corpus-slice-res, map-checking, map-silent and suite -- and not on corpus-port or any port-binding column, where M07 survived 294 accepting Reserve cases.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136-141`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:125-147`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/file_journal.py:14-23`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:88-92`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2 is met in the artifact and not only in a report: the limits are written into the code as well as the notes -- file_journal.py:14-23 states in the adapter itself that constructing one truncates an existing file and that the trailing newline is framing the contract does not carry, and domain.py:96-104 names which command writes which piece of state. NOTES.md:125-147 names four unspecified interpretations unprompted. Anchor 3 is met: T declines to certify what its basis does not support, saying of a failed durable write that this is the one place R2 is not enforced by construction (NOTES.md:136-141) rather than asserting R2 holds throughout, and at NOTES.md:88-92 it names the single place it leaned on a language guarantee (dict insertion order) instead of restating the requirement, and then converts that exposure into a test past r10. Anchor 4 refused, and this was close. It asks for a RESULT in the record that is unflattering to the thing being scored; T's record contains no such result. Every limitation it names is a defended design choice, and every number it reports about itself is clean (53 of 53, 28 of 28) with no admitted gap and no case that came out badly. Rule 5: torn between 3 and 4, take the lower and say why.

## Verdict

The only artifact of the three that is ports-and-adapters in fact -- a declared port, two working implementations, and a swap demonstrated at runtime rather than by import topology -- so take T when the boundary is what you need; do not read its D2 as a simplification result, because no before/after figure exists anywhere for it.

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

- **D2 = 3.** The `seeded_by: addition` result for M08 and M10 is a genuine, measured, per-artifact consequence of this artifact's central simplification: two of the ten faults have no one-token form in this design because the code sites they live in do not exist. I nearly counted that as "a simplification was made and its effect measured". It is not a before/after pair of FIGURES, which is what the anchor says, and stretching it to fit would have forked the rubric silently in the one file that exists to stop that. Refused, and recorded in the D2 rationale so the finding survives the score.
- **D5 = 4.** This artifact names its limits precisely and converts one of them into a test. But anchor 4 asks for a RESULT in the record that is unflattering to the thing being scored, and there is none — every number it reports about itself is clean and every limitation is a defended choice. Rule 5, took the lower.
- **Reading `M09 SURVIVED` under `corpus-port-swap:fake` as a defect in the fake.** It is a fault seeded in the real adapter, which the fake by construction does not contain. I used the divergence as positive runtime evidence that the binding changes the callee — the only such evidence in the whole packet — and put its cost in `refuses_to_claim` rather than in the score.
- **Prose.** This artifact's `NOTES.md` is the most self-assured of the three and its "the swap, in one sentence" framing is the most quotable claim in the fixture. Prose is never an input: the D3 = 4 rests on `tests/test_ledger.py:26-36` and on the measured port-binding columns, not on that sentence. Had the parametrised fixture been absent, the same sentence would have bought a 3.
