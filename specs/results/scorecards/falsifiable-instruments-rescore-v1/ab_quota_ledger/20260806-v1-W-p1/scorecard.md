# Scorecard — ab_quota_ledger, artifact `W`, judge pass 1

`run_id`: `20260806-v1-W-p1` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

**You are scoring artifact `W`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:196-214`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:268-302`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:180-187`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met on a measured cell: M04-durable-stale-total SURVIVED `map-silent` and was KILLED by `map-checking` (EVIDENCE.md:74), the two differing only in whether the effect provider asserts durable content or shape. Anchor 3 is met by the refusal class: `guard_relaxation` is 0 of 3 for `corpus-whole` and 3 of 3 for `corpus-neg` (EVIDENCE.md:111-119). Anchor 4 withheld, rule 5 applied. The positive polarity has no deciding control on this artifact: M07 is NOT_DECIDABLE on `corpus-neg` and `corpus-slice-led` and WRONG on `corpus-port` (EVIDENCE.md:196-214), and all three port-binding columns SURVIVED that deliberate break after each executed 294 accepting `Reserve` cases (EVIDENCE.md:268-302). And this artifact's own 11-case suite never appears in the table -- the `suite` column is the shared behavioral file. Two further facts I record rather than convert: this artifact's kill table is byte-identical to another artifact's in this packet, and it has the smallest own-suite of the three (11 cases against 32 and 53), a difference the instrument is structurally unable to see. Executability cited (EVIDENCE.md:180-187) so the kills are read beside 3734 executed cases and 0 failures on unmutated code.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:31-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:79-83`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:100-101`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:310-328`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179-188`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met. Seven fields, all established in one constructor (quota_ledger.py:31-42); `module_state` 0, `max_depth` 1, `max_branch_points_in_callable` 4, and the smallest figures in the block on every size axis (EVIDENCE.md:310-328). No god-state, and no variable written from everywhere: `_available` is written by `reserve` (quota_ledger.py:79-83) and `release` (quota_ledger.py:100-101) and nowhere else. Like its middle neighbour it stores `_available` although it is derivable, so R1 is maintained by hand at two sites; two lines of redundancy, not a defect at this anchor. The one structure the behavior does not require is disclosed by the artifact itself: the blank-line filter in `ledger_lines` is unreachable given its own writer (NOTES.md:179-188), which is defensive code the artifact says it never exercised -- too small to move an anchor and recorded because it is the only 'simpler than required' candidate I found. Anchor 3 refused: no before/after figures are recorded for any simplification. Explicit statement of what I did NOT do, because it is the obvious wrong move here: I did not convert this artifact's low `code_lines` (78, against 151 and 202) into a higher D2. Rule 7 and MF-020 forbid it, and I score the 202-line artifact at the same anchor.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** 1

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119-121`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:60-65`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:39-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:169-177`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:50-52`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
There is no port here and none is claimed. Filesystem access appears in three separate places inside the class that holds the rules: the truncate at construction (quota_ledger.py:39-42), the inline `read_text()` in the `ledger_lines` query (quota_ledger.py:60-65), and the `open(...)` in `_append_line` (quota_ledger.py:119-121). Anchor 2 is therefore not fully satisfied: writes funnel through a private helper, but reads and truncation bypass even that, and a private write helper whose sibling reads go direct is a formatting convenience rather than something identifiable as a port. The runtime evidence agrees rather than the imports: shipping no second implementation, this artifact's `corpus-port-swap:fake` column IS its real one and the runner says so (EVIDENCE.md:50-52). I rejected 0: 'state is written from everywhere' is false -- this is a small, tidy class with one writer per field -- and 0 would misdescribe it. I rejected 2 for the reason above. The ladder has no exact rung for this artifact, because anchor 1 presumes a boundary NAMED in prose that the code fails to honour and this artifact names none; 1 is where an artifact with no boundary and no false claim about one lands between an anchor that overstates the disorder and one that requires a port. Torn 1/2, took the lower and said why. Note in the artifact's favour, which did not move the score: NOTES.md:169-177 argues the direct read is deliberate -- a cache would mask a broken write path -- which is a real design argument, and it is an argument for LESS indirection, so it cannot raise a modularity anchor.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:180-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:25-153`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:85-95`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:268-302`

**Refuses to claim** (required and non-null for a score of 4):

_n/a — this score is not a 4._

**Rationale:**
Anchor 2 is met more explicitly here than by either neighbour: NOTES.md:25-153 is a clause-by-clause account that takes each clause of the feature in turn, says where it lives in the code, and names the concrete input that would have caught it being absent -- and marks the cases it could not execute instead of quietly listing them with the rest. test_extra.py:85-95 additionally checks the durable side against raw file bytes read independently of the object under test, so the enumeration is not entirely self-reported. Anchor 3 is met by the shared model-derived corpus: 3734 executed, 0 failures on unmutated code (EVIDENCE.md:180-187), 28 shared cases passed (EVIDENCE.md:62). I nearly scored 2 rather than 3, which is the unusual direction of doubt here: most of this enumeration points at the shared suite rather than at this artifact's own 11 cases, so the fullest account of the three rests on the thinnest own-suite of the three. I settled on 3 because anchor 3 asks that the CHECK be model-derived, and the corpus supplies that independently of who wrote the cases. Anchor 4 withheld on the same grounds as its neighbours: this artifact's own cases were never mutated, and the shared instrument's demonstration is partial -- M07 SURVIVED all three port-binding columns after each executed 294 accepting `Reserve` cases (EVIDENCE.md:268-302).

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:108-114`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:157-167`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179-188`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190-210`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:15-19`

**Refuses to claim** (required and non-null for a score of 4):

That its `close_tenant` rejection ORDER between `unknown_tenant` and `outstanding_reservations` was ever tested. specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190-210 records that no input exists which makes the two checks collide, so the test that carries the ordering in its name covers only the reason, and specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:108-114 says so in the docstring of that very test. It separately refuses to claim the blank-line filter in `ledger_lines` has ever been exercised -- specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179-188: 'I did not run a case that exercises this filter; I am not claiming to have observed it doing anything, only that it is there' -- and refuses to claim its reading of `reservation_id` on `commit`/`release` is verified by anything at all (specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:157-167).

**Rationale:**
Anchor 2 is met inside the artifact rather than only in a report: test_extra.py:108-114 places the limitation in the docstring of the test it weakens, saying the ordering claim is 'trivially true since an unknown tenant can hold no reservations'; quota_ledger.py:15-19 flags on the shipped `Result` type that the commit/release `reservation_id` reading is a decision to be read about rather than a settled fact. Anchor 3 is met three separate times, each naming the SPECIFIC claim being withheld rather than hedging in general: NOTES.md:190-210 ('I could not produce evidence for an ordering claim that has no distinguishing input, so NOTES.md says exactly that ... instead of asserting the order was verified'), NOTES.md:157-167 ('this is unverified by any assertion, only a reading I committed to'), NOTES.md:179-188 (a shipped branch declared never executed). Anchor 4 is met by results unflattering to this artifact specifically: one of its eleven tests is disclosed as vacuous with respect to the property its own name asserts, and one shipped branch is disclosed as never having run. That is the only place in these three artifacts where the record volunteers a fact that makes its own coverage look worse, and it is volunteered at the site of the weakness rather than in a footnote. Rule 4, stated because it bit in the opposite direction: this is the most repetitive and most hedged writing of the three, and the hedging IS the evidence here -- I scored the disclosures, which are specific and checkable against the code, not the sentences carrying them. I tested anchor 4 against the objection that 'I did not run this' is an omission rather than a result; I rejected the objection because a stated, located gap in one's own coverage is a finding about the artifact that a reader can act on, which is what the anchor is for.

## Verdict

The most honest record of the three -- it discloses one of its own tests as vacuous and one of its own branches as never executed, at the sites of both -- attached to the least modular code, where the class holding the rules opens the ledger file in three separate places and there is no port to swap.

**Total: 13 / 20** (D1 3, D2 2, D3 1, D4 3, D5 4).

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

**What most nearly changed my mind on this artifact.** D3, in the direction of 0. Reads and truncation bypass even the one private write helper, which is as close to 'no boundary is discernible' as anything in this round. I held at 1 because the rest of anchor 0 -- 'state is written from everywhere' -- is simply false of this code: every field has exactly one writing command and the class is 78 lines. The second pull was D4 downward to 2, since the fullest clause-by-clause enumeration of the three delegates most of its evidence to the shared suite while shipping the thinnest own-suite of the three.

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

