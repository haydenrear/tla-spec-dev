# SV-05 — predictions, sealed BEFORE any measurement

**Sealed at `2026-08-12T22:4xZ`, in the commit that carries this file. The commit
timestamp is authoritative and supersedes any time written in this prose.**

Branch point **`71ce81a`**, verified with `git rev-parse --short HEAD` against
`epic/score-drives-validation` and against the SHA the work order gave. They
agreed.

---

## 0. What had already been run when this was sealed — disclosed, not hidden

Sealing after looking is the failure the round before `CL-04` declared an alarm
against itself for. So the list is exact. Before this file was written I had:

- run `git rev-parse`, `git log`, `git branch`, `ls`, `wc -l`;
- run `score_tools.py --help` (its usage text, no subcommand executed);
- **read** `SCORE-DRIVES-VALIDATION-EPIC.md`, the plan, all six ticket `RESULT`
  pages, `NEXT-EPIC.md` §0-AAAAAAAA, and the head of `HARVEST-CL-03.md`.

**Everything below is therefore a prediction about a number I have not computed,
or about an agent that has not been dispatched — never about a sentence I have
already read.** Where a ticket's own prose already states the answer, I predict
what I get by **re-deriving it from the cards and the scripts at MY tree**, which
is a different act from believing the page. Two things I had already OBSERVED and
therefore do not dress up as predictions:

- `RESULT-SV-04.md` §9 ships two **unfilled placeholders** — a suite row reading
  `SUITE_AFTER_REPAIR` at tree `REPAIR_SHA`. Observed on first read, not
  predicted.
- SV-03's four skill diffs were **escalated, not applied**. Stated in its RESULT.

---

## 1. The instrument and the served surface

| | prediction | mechanism |
|---|---|---|
| **P1** | `serve \| wc -c` is **6,281 bytes / 9 rungs** at `71ce81a`, and identical again with SV-05's own files present | no ticket in this epic edited `references/eval_scorecard.md`; `git diff eab2883 71ce81a -- references/eval_scorecard.md` will be empty |
| **P2** | **`--digest-only` is NOT a flag `score_tools.py serve` accepts.** The work order asks for output the tool cannot produce, and the per-version digest table has to be produced another way | `--help` lists `serve [--card-version N] [--rubric F] [--out FILE]` and nothing else |
| **P3** | rendering every card version 1–5 gives **five distinct served digests**, with v5 = `sha256:2d7d4a0506d9b259` and v4 = `sha256:a213a36770ccab09`; and **at least one earlier version serves MORE than 9 rungs** | D1 and D4 were scored dimensions before version 4 retired them to notes, and a retired dimension takes its rungs with it |
| **P4** | `check specs/results/scorecards` reports **95 cards, 95 filled** (87 at CL-03 + 4 from SV-01 + 4 from SV-04) and **330 problems**, the same 330 reported at 87 and at 91 | the problems are legacy drift on pre-v5 cards; cards written at the current bar add none |
| **P5** | `audit` reports **0 violations** and `contested` reports **no contested dimension introduced by this epic** | SV-01 and SV-04 both report unanimity on D2 and D3 within their rounds |

## 2. The suite, and the trees

| | prediction | mechanism |
|---|---|---|
| **P6** | the repository suite at `71ce81a` is **2 failed**, and the two are `test_architecture_tags.py::test_the_same_tag_control_holds` and `test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer` | the deliberate inherited pair; the third red the epic opened with was repaired by the owner at `2059500` |
| **P7** | collected is **1,530** at `71ce81a` (SV-07 closed on `2 failed, 1528 passed`) | SV-04's tail merges added cards and a `subjects.toml` entry, not tests |
| **P8** | SV-05's own documents move the suite by **0 collected** and add **no red** — including the pricer grep, which is **already** red on `NEXT-EPIC.md`, the file this ticket must edit | the grep's offender list already names `NEXT-EPIC.md`; adding text to an already-named file cannot widen the failing list |

## 3. The four goals

| | prediction | mechanism |
|---|---|---|
| **P9** | reading `scorecard.json` directly — not the RESULT prose — **all four SV-01 cards carry `D3 = 4`**, two at v4 and two at v5, and **both v5 rationales contain a sentence testing the caveat's condition and finding it false** | the cards are on disk and the RESULT quotes them; a mis-transcription is the thing being checked for |
| **P10** | **`GOAL-caveat-discriminates` is decided DISCRIMINATES, not a null** — and the verdict is discounted, not withdrawn, by `SV-01-DF-01`: one artifact, one judge model, and a prior `D3 = 4` one `ls` from every judge, a leak that cuts toward the predicted answer | §1 of SV-01's RESULT, re-derived from the cards |
| **P11** | **`GOAL-validation-is-scorable` is decided YES**, with the correction that the property was already in the card and that **the carrier claim SV-02 shipped is refuted by SV-07** | SV-07 executed the change rule against a card carrying the candidate prompt |
| **P12** | re-running SV-02's `scorability.py` at MY tree — **95 cards, not the 87 it was written against** — still reports the **diagram zero: `diagram`/`mermaid`/`UML`/`C4`/`.svg` in 0 sentences across 0 cards** | nothing in this epic scored a diagram; SV-04 explicitly rejected building one |
| **P13** | re-running SV-02's autopsy at 95 cards keeps D1 ≈ 37% and D4 ≈ 17% **within one percentage point**, because the eight added cards carry `N-D1` notes and no D1/D4 anchor decision at all | version 5 serves no D1 or D4 ladder |
| **P14** | **`GOAL-scored-at-goal-time` is decided NOT ACHIEVED at this tree.** Re-running SV-03's `baseline_is_a_card.py` gives **0 of 18** goals whose baseline the evaluation can open, and SV-06's survey gives **12 of 27** naming a dimension — both unchanged, because the four diffs were escalated and never applied | a design that is not installed changes no number |
| **P15** | the four proposed patches **apply cleanly** (`git apply --check` / `patch --dry-run`) against the installed skill files in `$SKILL_MANAGER_HOME` today | SV-03 recorded base hashes; the risk is that the home moved under them since |
| **P16** | **`GOAL-loop-reaches-the-program` is decided ACHIEVED, n = 1.** Re-running SV-04's `M1` at my tree reproduces **28 pass on the shared suite / ≥1 fail on the conformance suite**, and **`JF-5` (the domain bypassing the port) reproduces 70 of 70 GREEN** — the unflattering half | the mutants are described precisely enough to re-apply; if the unflattering half does not reproduce, the ticket's own best result is wrong |

## 4. The blind experiment — a 2×2, designed and sealed before dispatch

`GOAL-scored-at-goal-time`'s target says *"tested the way `CL-04` tested the loop,
BY AN AGENT WITH NONE OF OUR SOURCE"*. SV-06 §9 and SV-03 §10 both hand that test
to this ticket. **The design is fixed here, before any agent exists.**

Four agents, none given this repository, its `specs/`, its cards or its history.
Each gets a scratch copy of the surveyed skill text and one epic plan, and is
asked to run the goal process end to end.

| arm | skill text | the plan it is given |
|---|---|---|
| **A — CTL/judged** | pristine, as installed | an epic whose goal is decided by a **judged** instrument |
| **B — TRT/judged** | the same, **with SV-03's four diffs applied to the COPY** | the same judged plan |
| **C — CTL/no-card** | pristine | an epic with **no card anywhere**, decided by a shell bench |
| **D — TRT/no-card** | patched copy | the same no-card plan |

**Nothing is written to `$SKILL_MANAGER_HOME`. `skill-manager sync` is never
run.** The copy is hashed before and after.

| | prediction | mechanism |
|---|---|---|
| **P17** | **the absence guarantee holds: neither C nor D asks what rubric or card to use**, and D does not notice the added sentences | every added block opens with a conditional a no-card project fails, and SV-03's guard check fires on an unguarded one |
| **P18** | **THE COUNTERFACTUAL, and the prediction most likely to break: B names a specific sealed card as its judged baseline and A does not.** If A does it too, the diffs bought nothing and `GOAL-scored-at-goal-time` fails on its own evidence even if the diffs were installed | the third branch is the only text in any of the six files that asks for an openable card |
| **P19** | **at least one of the four reports something it REJECTED, and at least one discloses a contamination unprompted** | both are asked for by name, which is `CL-04`'s finding |
| **P20** | at least one agent reports a blocker in the *installed* text that no ticket in this epic named | four fresh readers on six files that three tickets only surveyed |

## 5. Cost, channel, and the counts that keep going wrong

| | prediction | mechanism |
|---|---|---|
| **P21** | **exactly ONE of the six tickets (SV-01) recorded a token count with a named basis; the other five recorded none** — a third consecutive epic of near-total lapse, cause unrepaired | `CL-04-DF-02`: nothing in the repository asks, and the only place it is demanded is the evaluation's dispatch, which arrives after the spend is gone |
| **P22** | this epic's tickets filed **between 25 and 32** findings, and **at least three** tickets report a spent budget of five with an escalation instead of a sixth filing | SV-02, SV-06 and SV-04 each describe the situation in their RESULT |
| **P23** | **findings touching the shipped toolchain under `CL-04`'s narrow definition (`scripts/`, `spec_double_compiler/`, `templates/`, `skill-scripts/`, root `SKILL.md`) = 0 for this epic** — the ledger stays near 10 of ~200 | every instrument finding this epic names `examples/validation/` or a skill file |
| **P24** | **and yet the two-epic zero on shipped BYTES is broken**: `git diff --stat eab2883..71ce81a -- scripts/ …` is **non-empty**, because SV-07 shipped `scripts/candidate_note_bar.py` | it is in SV-07's RESULT §1 as the thing it shipped instead |
| **P25** | **the consumption rate: exactly ONE harvested class was consumed into program validation (`A1`, by SV-04)**, so the programme moves from ~1 in 38 to **1 consumed / 38**, with a separate, larger count of classes newly FILED but still unconsumed | consumption means a class becoming validation in the program; filing is the cheaper act and SV-01-DF-05 did it three times |
| **P26** | `validate_epic_plan.py` from the CURRENT `git-epic-workflow` **exits non-zero on `close-the-loop`'s plan as it stands on `main`**, for a missing plan-level `schedule_revision`, while this epic's plan exits 0 | the skill was updated mid-epic at `4e6fcd7`; the epic plan was repaired at `4e6973d` and `main`'s was not |

## 6. The alarm

**P27 — at least 3 of P1–P26 are FALSIFIED.** `CL-04` got 3 of 11 wrong and said
that a round whose every prediction holds has learned nothing. **If every
prediction above passes, this document's own §6 is the ALARM and the report must
lead with it.**

## 7. What SV-05 REJECTS, decided before measuring

- **Running SV-07's both-wordings judging round.** SV-07 §6 leaves it to this
  ticket. **Refused, with a reason:** cards scaffolded against the candidate bar
  record a served digest for a **card version 6 that does not exist in the
  card**, which permanently adds drift rows to the record whose comparability is
  the thing the change rule protects. It answers a question about a **future
  carrier** and decides **none of the four goals**. Handed to `NEXT-EPIC.md`
  instead, with the hazard named.
- **Repairing anything.** Including the two inherited reds, the two unfilled
  placeholders in `RESULT-SV-04.md`, `main`'s invalid plan, and every blocker the
  blind agents return. This is a measurement.
- **Applying SV-03's four diffs to `$SKILL_MANAGER_HOME`.** They are applied to a
  **copy** so the counterfactual can be measured; the home is never written.
- **Averaging across examples or versions.** `R-H1`/`R-H2`. The v4 and v5 arms of
  SV-01 are two cells, never two rows of one mean; SV-04's `GL` and `LG` likewise.
- **Reporting a `git archive` figure as a tree property.**
- **Discarding any blind agent's output after reading its answer.**
