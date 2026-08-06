# Scorecard — ab_quota_ledger, artifact `T`, judge pass 1

`run_id`: `20260806-v1-T-p1` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:196-217`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:283-293`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:180-187`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met on a measured cell rather than an assertion: M04-durable-stale-total SURVIVED `map-silent` and was KILLED by `map-checking` (EVIDENCE.md:74) -- same corpus, same artifact, the only difference being an effect provider that asserts durable content rather than shape. Anchor 3 is met by the refusal class: `guard_relaxation` is 0 of 3 for `corpus-whole` and 3 of 3 for `corpus-neg` (EVIDENCE.md:111-119), which is exactly the anchor's 'class the whole-view corpus structurally cannot reach on its own'. Anchor 4 withheld on two grounds and rule 5 applied. First, the instrument that carries anchor 3 has no green positive control here: M07 must be KILLED, and `corpus-neg` is recorded as insensitive -- it killed the control 'while executing none of the cases its own declared limitation says it needs' (EVIDENCE.md:196-217) -- while all three port-binding columns SURVIVED that same deliberate break after each executed 294 accepting `Reserve` cases (EVIDENCE.md:283-293). Second, this artifact's own 53-case suite never appears in the kill table; the `suite` column is the shared behavioral file, identical for every artifact, so no cell in the table is about this artifact's own detection. Disagreement with the mechanical evidence, recorded rather than split: the table read literally would support a 4, and I decline it because the control that would let a zero be told from a broken instrument is red. Executability is cited (EVIDENCE.md:180-187) so the kills above are read beside 3734 executed cases and 0 failures on unmutated code, not beside a blank.

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
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:88-104`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:324-342`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:78`
- `examples/validation/ab/FEATURE.md:113-122`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met on the design. `available` has no writers at all -- it is `quota - held - committed`, computed on each call (domain.py:118-120) -- so R1 has no maintenance sites that can drift, and the three fields that are written have one writing command apiece (domain.py:88-104): `_outstanding` by reserve/commit/release, `_committed` by commit alone, `_closed` by close_tenant alone. There is no god-state and no variable written from everywhere. The block corroborates the shape rather than the size: `module_state` 0, `max_depth` 1, and 1 branch point and 1 instance-state item in the effectful module against 10 and 8 for the next artifact (EVIDENCE.md:324-342). One measured corroboration that the structure is essential rather than decorative: two of the eleven seeded faults had to be seeded by `addition` on this artifact rather than `perturbation` because 'the fault has no one-token form in this design' (EVIDENCE.md:78) -- a design that does not store `available` has no statement in which 'commit refunds the hold' can be written. Anchor 3 refused: a simplification was made but no before figure for it exists anywhere in the record, and the mechanical block is a three-way comparison of different artifacts, not this artifact's before and after. Recorded disagreement with the block: on raw size this is the LARGEST of the three (202 code lines, 4 modules, public_surface 25, against 78/1/11) and I score it at the same anchor as the smallest, because FEATURE.md:113-122 declares the interface-vs-direct choice unspecified and instructs a judge not to read a difference there as a defect. Prose: this NOTES is the most persuasive of the three and it tempted me toward a 3; the anchor asks for recorded before and after figures and there are none, so the argument did not buy the point.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:22-43`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/__init__.py:37-39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:26-36`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260-270`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:168`

**Refuses to claim** (required and non-null for a score of 4):

That every one of its cases runs against both implementations: specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:96-100 records two file-specific tests that sit OUTSIDE the two-wiring case list because they are about the file rather than the rules. It separately refuses to claim R2 survives a failed durable write -- specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136-141 states that commit updates memory before appending, that there is no rollback and no write-ahead ordering, and names this as the one place where R2 is not enforced by construction.

**Rationale:**
Anchor 3 is met in code, not by declaration. The domain names its one outside need as a Protocol in its own vocabulary and never constructs one (domain.py:22-43); the swap is a single expression in the only module allowed to know both sides -- replace `FileJournal(ledger_path)` with `InMemoryJournal()` at __init__.py:39 -- and no domain file changes. The rubric's caveat that import topology is not modularity is answered by RUNTIME evidence, not by the AST check at test_ledger.py:260-270: in the port-binding table `corpus-port-swap:fake` and `corpus-port-swap:real` return DIFFERENT verdicts on M09 (EVIDENCE.md:168), which is only possible if the fake binding actually called a different implementation at run time. That single cell is also the only place in any of the three packets where a fake column differs from its real column, and the packet states that an artifact shipping no second implementation has its fake column run the real one. Anchor 4 is met at test_ledger.py:26-36: one parametrized fixture wires the same case list to FileJournal and to InMemoryJournal, and every case asserts a literal expected transcript rather than that the two wirings agree with each other -- the trap the file's own docstring names. I nearly held at 3 on the ground that the fake was written by the same author as the port and could have been shaped to fit it; I rejected that because what must survive the swap is the CASE list, and it does, unchanged and asserting values.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:180-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:74-79`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:108-114`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:283-293`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2: the behavior most at risk from this artifact's one simplification -- 'committing does not give the hold back' -- is enumerated and asserted BY VALUE on both wirings (tests/test_ledger.py:108-114), and NOTES.md:74-79 makes the MF-020 argument explicitly, calling the change a derivation rather than a deletion and naming the two cases that hold the behavior. The enumeration lives in the case list rather than in prose, which I accept as an enumeration. Anchor 3: the check is model-derived and not only hand-written -- the shared corpus executed 3734 of 43128 emitted cases with 0 failures on unmutated code (EVIDENCE.md:180-187) and the shared suite passed 28 (EVIDENCE.md:62). Anchor 4 withheld, torn 3/4 and taking the lower: the demonstration that a check can fail is carried entirely by the shared instrument -- this artifact's own 53 cases were never mutated -- and the demonstration is provably partial, since the deliberate break M07 SURVIVED all three port-binding columns after each executed 294 accepting `Reserve` cases (EVIDENCE.md:283-293). A break that a column fails to catch is not a demonstration that the column can fail.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/memory_journal.py:3-8`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/file_journal.py:19-23`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:5-9`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136-141`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:149-157`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met in the artifact itself and not only in the report. memory_journal.py:3-8 states, in a shipped module, that the fake exists so that 'the port is a port' is demonstrated by a second implementation 'rather than an assertion in a comment'; file_journal.py:19-23 names the framing the port contract does not carry and says whose job stripping it is; tests/test_ledger.py:5-9 names the vacuity trap -- two wirings of the same domain agree even when the domain is wrong -- and states the file is built to avoid it. Anchor 3: NOTES.md:136-141 declines to claim R2 holds under a failed durable write and names it as the one place R2 is not enforced by construction, rather than reporting R2 clean. Anchor 4 withheld: the record contains no RESULT unflattering to this artifact. Every limit it names arrives with a rationale that neutralises it, the only two figures reported are 28 passed and 53 passed, and NOTES.md:149-157 reports over-compliance with the reading restrictions (it declined a file that was not even on the list). Naming a limit and recording an unflattering result are different acts; this record performs the first thoroughly and the second not at all. Torn 3/4, took the lower.

## Verdict

The only artifact of the three where a driven port exists in fact -- the domain imports nothing that does I/O, the swap is one expression at quota_ledger/__init__.py:39, and one case list passes against a real and a fake adapter with a run-time cell to prove the fake was really bound -- but every bug-detection number it carries belongs to the shared harness under a red positive control, so read its D3 and ignore its D1 as a ranking.

**Total: 15 / 20** (D1 3, D2 2, D3 4, D4 3, D5 3).

## Disclosures

**Anything I saw that I was not meant to see.** Nothing on the forbidden list was
opened. I listed the directory tree of this run's own epic folder once and saw the
filename `UNBLINDING.md`; I did not open it, and I opened no `-p2` directory, no
`RESULTS.md`/`INDEX.md`/`INSTRUMENT-LOG.toml`, no `arm_*/`, no `seeded_faults.toml`,
no `reference/` or `reference_ports/`, no `PREDICTIONS*`, nothing under
`specs/.history/`, no `*EPIC*.md`, and no `specs/desired_program_model/`.

Two leaks reached me from inside the artifacts themselves, unsought.
`specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:106-109` quotes "Section 1" of its own prompt as requiring
that the domain hold "no file handle, no path"; `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:201-202`
refers to "Section 1's instructions ... (behavior vs. what-to-show)" and to
"Section 6's forbidden list". So from the artifacts alone I know at least two arms
received a numbered-section prompt and that T's contained an explicit
domain-holds-no-path instruction. I did not learn any arm label or the T/U/W
mapping and did not go looking. Recorded because a disclosed leak is recorded; my
D3 spread follows what the code does, and the same spread is readable off the code
with the NOTES files deleted.

**Anything I ran, and whether it changed anything on disk.** Read-only `find`,
`wc`, `grep` and `diff` over the three blind artifact directories and the two
permitted files under `examples/validation/ab/`; `diff` was used to compare the
three `EVIDENCE.md` packets against one another. I then ran
`python3 examples/validation/scorecards/score_tools.py check ... --require-filled`
over my own three card directories. I did **not** execute any of the three
implementations, did not seed a fault, did not re-run the shared suite, and did not
copy anything to a scratch directory for execution. Nothing outside my three card
directories was written. No `git` command that changes state was run.

**What most nearly changed my mind on this artifact.** D2. The mechanical block makes this the largest artifact of the three by every size figure (202 code lines against 78; public_surface 25 against 11) for behavior that is identical across all three -- 28 shared cases pass on each. For a dimension named 'complexity' that is close to a decisive argument for scoring it below the others. I did not, because FEATURE.md:113-122 removes the interface choice from the judgeable set and because D2's own anchor is about god-state and write-density, on which this artifact is the best of the three by the block's own figures (1 branch point in the effectful module against 10).

**What I REJECTED.**

1. *A D1 of 4 on all three artifacts.* Read literally the packet supports it: the
   cases that reach the refusal class are model-generated, and each record names
   limits. I rejected it because the instrument carrying that anchor has no green
   positive control — `control coverage` reports the positive polarity
   `"deciding": [], "green": false` — and because the artifacts' own suites (53,
   32 and 11 cases) never appear in the kill table at all, so no cell in it is
   about the artifact rather than the shared harness. Taking the lower cost every
   artifact a point and cost none of them a rank.

2. *Converting the mechanical block into D2.* The block ranks the artifacts
   202 / 151 / 78 `code_lines` and 25 / 20 / 11 `public_surface`. Turning that into
   a complexity score would have produced the exact ordering the block already
   states, which is rule 7's forbidden move and MF-020's warning; and
   `examples/validation/ab/FEATURE.md:113-122` declares the interface-vs-direct
   choice unspecified and instructs that a difference there is not a defect. All
   three sit at the same D2 anchor and the disagreement with the block is written
   into each rationale instead of averaged away.

3. *A D4 of 4 anywhere.* The kill table is a genuine demonstration that a check can
   fail, and PA-06's recorded failure mode was judges awarding this anchor after
   executing a break themselves. I did not execute one, and the executed breaks in
   the packet are the shared instrument's, not the artifact's. Withheld on all
   three rather than awarded to all three.

4. *Treating `seeded_by` as artifact quality, then partly un-rejecting it.* The
   packet says plainly that `perturbation` vs `addition` is a fact about the diff.
   I rejected it as a D1 input. I did let it into T's D2 rationale as corroboration
   only — that a fault has no one-token form is a measured statement about the
   shape of the code, and it is cited as corroboration of an anchor met on the
   source, never as the anchor's basis.

5. *A finding I decided to record rather than score: `artifact_U/EVIDENCE.md` and
   `artifact_W/EVIDENCE.md` are byte-identical apart from the artifact name.*
   `diff` returns exactly two differing lines, both the header. Not one measured
   cell — kill table, class block, port-binding table, executability, controls —
   separates those two artifacts. The whole measured difference between the three
   artifacts in this packet is four cells of T's kill table, one cell of T's
   port-binding table, and one rejected limitation. I did not read the identity as
   evidence that U and W are equivalent programs; they are not (see D3). I read it
   as a limit on what this packet can discriminate, and scored the source.

6. *An inconsistency in the control block I declined to let move a score.*
   `EVIDENCE.md:260-261` reports `"positive": {"deciding": [], ... "green": false}`
   and, on the very next line, `polarities with no deciding control: []`. Those two
   statements cannot both be true. It appears identically in all three packets. I
   used the first (positive polarity has no deciding control) because it is the
   conservative reading and because it agrees with the per-mutant cells; I did not
   penalise any artifact for an instrument defect.

7. *The prose.* T's NOTES is the most persuasive document of the three and U's is
   the most economical; W's is the most repetitive and the most hedged. The ranking
   my scores produce is not that ranking, and W's hedging is precisely what earned
   its D5. Rule 4 applied and stated in the rationales where it bit.

