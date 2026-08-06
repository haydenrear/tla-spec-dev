# Scorecard — ab_quota_ledger, artifact `W`, judge pass 2

`run_id`: `20260806-v1-W-p2` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:85-95`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:117-124`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:36-43`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:64-70`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:111-120`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2 is met: test_ledger_file_on_disk_matches_ledger_lines (85-95) asserts the raw bytes on disk exactly -- 'COMMIT acme 5 5\nCLOSE acme 5\n' -- read through an independently opened path rather than through the object's own query, so it is content and not shape and it is not self-confirming. Anchor 3 is met on the narrowest margin of the three artifacts, and I want the margin on the record. The class the whole-view corpus structurally misses is refusal (guard_relaxation 0 of 3 for corpus-whole, EVIDENCE.md:111-120), and W catches one there through durable content: test_r3_close_is_singular_second_close_line_never_written (117-124) closes, closes again into a rejection, and asserts the CLOSE lines are still exactly one -- a relaxed tenant_closed guard writes a second line and dies. 36-43 additionally pins a rejection-ORDER tie that only a correctly ordered guard chain produces, and 64-70 pins the numeric id ordering past r9. What holds W here rather than higher-by-breadth is that this is an 11-case file which delegates R4 inertness wholesale to the shared suite by its own account (NOTES.md:140-146), so most of its refusal checks assert a reason string and only the one above checks that nothing moved. I nearly scored 2 on that breadth and did not, because the anchor asks for at least one fault in the class and not for coverage of it -- recorded rather than split. Anchor 4 refused: hand-written, and the model-derived corpus is the shared instrument, identical across artifacts (EVIDENCE.md:53-56). Control caveat applied: positive control red with no deciding instrument for its polarity (EVIDENCE.md:260), so corpus-port's SURVIVED cells are floors and were used as evidence for nothing.

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
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:69-115`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119-121`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:327-328`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

Anchor 2, no higher, and the descriptor is where the disagreement worth recording lives. W is the mechanical minimum on every raw figure -- 78 code lines against 151 and 202, 11 callables, 2 classes, 11 public surface -- and simultaneously carries 10 branch points and 7 instance-state fields inside its single effectful module (EVIDENCE.md:327-328), a figure on which it is joint worst. Smallest and least isolated at the same time; per rule 7 I converted neither ranking into a score and record that they point opposite ways. On the design itself: state is declared once (31-42) and each field has exactly one writing command (69-115) -- `_available` in reserve and release, `_committed` in commit, `_closed` in close_tenant -- so there is no god-state and nothing written from everywhere, and the smallness is not paid for in behaviour, since the shared contract passes 28 of 28 and all ten seeded faults die somewhere. One place where W is arguably simpler than the behaviour requires, recorded rather than scored: R4's clause that a rejection reason is always one of the six named is represented by nothing -- the reasons are literal strings at seven construction sites (71, 73, 75, 77, 87, 98, 107, 109, 111), where both other artifacts collect the vocabulary and assert membership. That is an absent guard rather than accidental structure, so it does not move the anchor. Anchor 3 refused: no before/after figures exist for W, and MF-020 forbids reading its low absolute counts as a measured simplification.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:39-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:60-65`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119-121`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:158-170`

**Refuses to claim** (required and non-null for a score of 4):

_(not required: this score is below 4)_

**Rationale:**

There is no port, no injection and no declared boundary. The ledger path is stored on the rules object and truncated in the rules' constructor (39-42), `_append_line` opens the file inline (119-121), and `ledger_lines` reads the file directly (60-65) -- so the durable side is touched from three of W's own methods and even the single write funnel is not a boundary, because the read path goes around it. Nothing in the code or the notes declares a boundary for the code to follow or fail to follow. The measurement agrees: `declared_interfaces` 0, and corpus-port-swap:fake is verdict-for-verdict identical to :real across all eleven mutants (EVIDENCE.md:158-170) because there was no second implementation to bind and the runner re-ran the real one (EVIDENCE.md:49-51). Neither anchor fits exactly and I am saying so rather than rounding. Anchor 0 requires that no boundary is discernible AND state is written from everywhere; the second half is plainly false, since every field has exactly one writing command (69-115). Anchor 1 requires boundaries named in prose or a declaration that the code then does not follow; W names none, so it does not even reach the failure anchor 1 describes. I scored 1 as the closest fit and refused 2 outright, because 2 requires cross-boundary calls to go through something identifiable as a port and there is nothing here that a second implementation could be substituted for.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:59-62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:178-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:69-81`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:25-153`

**Refuses to claim** (required and non-null for a score of 4):

That its blank-line filter has ever done anything. W records that `_append_line` cannot emit a blank line, that the filter in `ledger_lines` is therefore unreachable in normal operation, and that 'I did not run a case that exercises this filter; I am not claiming to have observed it doing anything, only that it is there' (NOTES.md:179-189). It equally refuses to claim its reading of `reservation_id` on commit and release is verified, naming it 'unverified by any assertion, only a reading I committed to' (NOTES.md:157-167).

**Rationale:**

Anchor 2 is met more literally by W than by either other artifact: NOTES.md:25-153 is a clause-by-clause account that, for every clause of the feature, names where it lives and the concrete input that would have caught its absence, and 28 of 28 pass on the unedited shared contract (EVIDENCE.md:59-62). I checked a sample of those claims against the code rather than crediting the enumeration -- the rejection order at quota_ledger.py:70-77 is the feature's order, and the boundary case it names (amount equal to available accepts) follows from the `>` at line 76. Anchor 3: a model-derived check ran against this artifact and passed unmutated, 3734 executed cases, 0 failures, with the executability column beside it (EVIDENCE.md:178-187). Anchor 4: ten deliberate behaviour-breaking changes were applied one at a time to a copy of W, proved to revert byte-identically, and each is KILLED by at least one instrument (EVIDENCE.md:69-81), with the negative control N01 surviving everywhere as required -- so the check is demonstrated capable of failing rather than asserted to be. Limits applied: the positive control is red with no deciding instrument for its polarity (EVIDENCE.md:260), so this rests on the instruments that decided M07 correctly and not on corpus-port or the port-binding columns; and I seeded and ran nothing myself, which the rubric records as the practice that moved this dimension two points on unchanged input.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:102-113`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:157-167`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179-189`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190-210`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:108-115`

**Refuses to claim** (required and non-null for a score of 4):

That close_tenant's rejection order between unknown_tenant and outstanding_reservations was ever verified. W records that no input exists which makes both apply, that it could not produce evidence for an ordering claim with no distinguishing input, and that it therefore wrote that down rather than asserting the order was checked (NOTES.md:102-113, 190-210) -- the one place in any of the three records where a passing test is explicitly denied the weight its name would carry.

**Rationale:**

Anchor 2 is met inside the artifact and not only in a report: test_extra.py:108-115 is a test whose own docstring calls its assertion 'trivially true since an unknown tenant can hold no reservations', and quota_ledger.py:56-58 and 61-63 state why the id sort is numeric and why ledger_lines re-reads the file. Anchor 3 is met three separate times, and each is a refusal to emit a verdict the basis does not support rather than a hedge: the close_tenant rejection ORDER is not written up as checked, because no input distinguishes unknown_tenant from outstanding_reservations and W says so instead (NOTES.md:102-113 and 190-210); the reservation_id reading is marked 'unverified by any assertion, only a reading I committed to' (157-167); and the blank-line filter is marked present but never observed doing anything (179-189). Anchor 4 is met: the record carries results unflattering to W itself -- a test of its own that it admits does not distinguish what its name suggests, a branch of its own it admits is unreachable and unexercised, and a decision of its own it admits no assertion covers. Those are findings against interest, in W's own record, and they are the class of thing this dimension exists to reward. Prose was explicitly not an input and I checked the temptation: W's notes are the longest and most self-critical of the three, so I verified each refusal against the code rather than crediting the writing -- reserve cannot register a reservation for a tenant absent from `_quota` (quota_ledger.py:70-71 and 82), which is why the close-order claim is genuinely undecidable, and `_append_line` (119-121) genuinely never emits a blank, which is why the filter at line 65 is genuinely dead. The refusals are true of the code, not just well phrased.

## Verdict

W is the smallest artifact and keeps the most honest record of the three -- its notes withhold precisely the claims its inputs cannot support -- but it has no boundary at all: three of its own methods touch the ledger path directly, so nothing about the durable side can be swapped, faked or tested apart from the rules.

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

- **D1 = 2.** This artifact's own case file is 11 tests and it delegates R4 inertness wholesale to the shared suite by its own account, so I very nearly took the anchor down on breadth. The anchor asks for at least ONE fault in a class the whole-view corpus cannot reach, and `test_r3_close_is_singular_second_close_line_never_written` is one, caught through durable content rather than a reason string. I scored the anchor as written and put the margin in the rationale instead of quietly pricing it into the number.
- **D3 = 0.** Anchor 0 has two clauses and the second — "state is written from everywhere" — is plainly false here: every field has exactly one writing command. Neither 0 nor 1 fits this artifact, and rather than take the harsher one silently I scored 1 as the closest fit and wrote out why neither anchor describes it. That is the one place on these three cards where the anchor set itself did not have a slot for what I was looking at.
- **D2 = 1.** I considered it on the grounds that R4's clause "a rejection reason is always one of the six named above" is represented by nothing here: the reasons are literal strings at seven construction sites, where both other artifacts collect the vocabulary once and assert membership. Rejected because that is an ABSENT GUARD, not accidental structure, and D2 asks about structure. It is recorded in the D2 rationale anyway, because it is a real difference between the three artifacts that no summary in this fixture states.
- **Prose, and the reason this card's D5 = 4 is not a reward for candour.** This artifact's notes are the longest and most self-critical of the three, which is precisely the shape that could buy an undeserved honesty score. I verified all three of its refusals against the code before awarding the anchor: `reserve` genuinely cannot register a holder for a tenant absent from `_quota`, so the close-order claim genuinely has no distinguishing input; and `_append_line` genuinely never emits a blank line, so the filter it declines to claim credit for is genuinely dead code. The 4 is for refusals that are true of the code. Had any one of them been merely well phrased, this would be a 3.
