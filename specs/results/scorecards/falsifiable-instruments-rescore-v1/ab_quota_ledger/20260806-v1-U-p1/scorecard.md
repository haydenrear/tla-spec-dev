# Scorecard — ab_quota_ledger, artifact `U`, judge pass 1

`run_id`: `20260806-v1-U-p1` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:196-214`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:268-302`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180-187`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met on a measured cell: M04-durable-stale-total SURVIVED `map-silent` and was KILLED by `map-checking` (EVIDENCE.md:74) -- the same corpus over the same code, separated only by an effect provider that asserts durable content rather than shape. Anchor 3 is met by the refusal class: `guard_relaxation` is 0 of 3 for `corpus-whole` and 3 of 3 for `corpus-neg` (EVIDENCE.md:111-119). Anchor 4 withheld, rule 5 applied. The instrument that carries anchor 3 is undecided by the positive control on this artifact -- M07 is NOT_DECIDABLE on `corpus-neg` and on `corpus-slice-led` and WRONG on `corpus-port` (EVIDENCE.md:196-214) -- and all three port-binding columns SURVIVED that deliberate break after each executed 294 accepting `Reserve` cases (EVIDENCE.md:268-302), so the positive polarity has no deciding control at all. And this artifact's own 32-case suite is absent from the kill table entirely: the `suite` column is the shared behavioral file, identical for every artifact. Nothing measured here is about this artifact's own detection capability. Recorded disagreement: the table read literally would support a 4; I decline it because its SURVIVED cells are floors, which the packet says in its own words.

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
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:146-152`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:180-182`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:310-328`
- `examples/validation/ab/FEATURE.md:113-122`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met. One module, six fields, all established in one place (quota_ledger.py:103-110); `module_state` 0, `max_depth` 1, `max_branch_points_in_callable` 4 (EVIDENCE.md:310-328). There is no god-state and no variable written from everywhere: `_available` is written by exactly two commands, `reserve` (quota_ledger.py:146-152) and `release` (quota_ledger.py:180-182), and each is a command whose whole job is to move it. The one piece of accidental structure I can name is that `_available` is STORED although it is derivable from quota, holds and committed, so R1 is maintained by hand at two sites rather than being true by construction; that is a redundancy of two lines, not a god variable, and it does not move the anchor. Anchor 3 refused: no simplification with a recorded before and after exists anywhere in this artifact -- neither its NOTES nor its tests mention a complexity figure at all -- and the mechanical block is a cross-artifact comparison, not this artifact's before and after. Recorded disagreement with the block: the block ranks this artifact in the middle on every size figure and I score it at the same anchor as both neighbours, because rule 7 forbids converting the figures and FEATURE.md:113-122 removes the interface-vs-direct difference from the judgeable set.

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
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:193`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:115-118`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:50-52`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met in fact. Every filesystem touch in the program lives inside `_LedgerFile` -- the truncate at construction, the append, and the read (quota_ledger.py:72-92) -- and the rules class never opens a file: its durable calls are `self._ledger.append(...)` at quota_ledger.py:168 and :193, and `self._ledger.lines()` behind `ledger_lines`. A two-method surface reached only through those calls is identifiable as a port even though the artifact declines to call it one (NOTES.md:115-118 lists 'an abstraction over the file beyond the one small class that writes it' among the things it did not add). Anchor 3 fails on both of its clauses. The module that holds the rules imports `pathlib.Path`, so the domain is not separated from its I/O by any boundary a swap could cross; and there is no swap that does not touch the domain, because `QuotaLedger.__init__` CONSTRUCTS the adapter itself at quota_ledger.py:110 -- there is no parameter, no factory, no injection point, and I cannot name a specific swap that leaves the class unedited, which the anchor requires me to do. The runtime evidence agrees rather than merely the imports: this artifact ships no second implementation, so its `corpus-port-swap:fake` column IS its real implementation and the runner says so on every run (EVIDENCE.md:50-52) -- the fake and real columns are identical in all eleven rows. I considered 3 on the strength of how clean the seam is and rejected it: a seam you cannot pass a different object through is a tidying, not a port.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279-312`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:268-302`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met, and by the strongest self-written check of the three: `check_rules` (test_quota_ledger.py:279-312) recomputes R1, R2 and R3 from scratch -- reading the ledger file from disk, not through the object's own accessor -- against a model maintained independently of the implementation, and it is invoked after EVERY one of 400 randomized commands (test_quota_ledger.py:315-362), with an anti-vacuity assertion at the end that the sweep actually committed and closed something. The rules the feature enumerates are therefore enumerated and each shown to hold. Anchor 3 is met by the shared model-derived corpus: 3734 cases executed with 0 failures on unmutated code (EVIDENCE.md:180-187) and 28 shared cases passed (EVIDENCE.md:62). Anchor 4 withheld, torn 3/4 and taking the lower: nothing ever mutated this artifact's own suite, so its demonstrated capability to fail is untested, and the shared instrument's demonstration is partial -- the deliberate break M07 SURVIVED all three port-binding columns after each executed 294 accepting `Reserve` cases (EVIDENCE.md:268-302). I note that the randomized sweep is hand-written; the anchor-3 credit comes from the corpus, not from the sweep, which is why the sweep's quality raised the rationale and not the score.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:358-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96-103`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:57-61`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:164-166`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:125-129`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met inside the artifact and not only in the report: test_quota_ledger.py:358-362 names the blind spot its own randomized sweep would otherwise have had -- 'a sequence that only ever rejected would prove nothing' -- and asserts against it rather than trusting it. Anchor 3 is met twice. NOTES.md:57-61 refuses to let the write-before-memory ordering be read as crash safety ('it is not a crash-safety feature and I did not build one'), and NOTES.md:96-103 refuses to claim integrality is enforced, states plainly that `reserve(t, 1.5)` would be held and printed into a COMMIT line, and names why it cannot be fixed inside the fixed six-reason vocabulary. Anchor 4 withheld. The unflattering material in this record is about the SPECIFICATION (a missing seventh reason) and about the author's process (NOTES.md:125-129 volunteers that an `ls` revealed forbidden filenames) rather than a result unflattering to the artifact. And rule 1 bites here in the artifact's disfavour: the shipped comment at quota_ledger.py:164-166 asserts the write ordering means 'a write that fails leaves the two sides agreeing (R2)', which is a stronger claim than the one its own NOTES concedes -- the code overstates where the report is careful, and the code is what I score. Torn 3/4, took the lower.

## Verdict

A clean single-module implementation with a real filesystem boundary that is hard-wired rather than swappable -- `_LedgerFile` is constructed by the class that uses it at quota_ledger.py:110, so no adapter can be replaced without editing the domain -- carried by the strongest self-written check of the three, a 400-step randomized sweep rechecking R1/R2/R3 against an independent model after every command.

**Total: 13 / 20** (D1 3, D2 2, D3 2, D4 3, D5 3).

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

**What most nearly changed my mind on this artifact.** D3. `_LedgerFile` is a genuine, complete concentration of I/O: the rules class in this artifact opens no file anywhere, which is more than one of its neighbours manages, and the temptation to award 3 for that was real. What stopped it is that the anchor requires me to NAME a specific swap, and I could not write one down that does not edit quota_ledger.py:110. The second-strongest pull was D4: the randomized model sweep is the best test-writing in the round, and it is still hand-written assertions, which is exactly what anchor 3 distinguishes itself from.

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

