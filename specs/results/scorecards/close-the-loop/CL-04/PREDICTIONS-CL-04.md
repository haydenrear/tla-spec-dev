# CL-04 — predictions, sealed before measuring

**Sealed at `2026-08-11T21:00:12Z`**, in the commit that carries this file and
**before a single command in Part 1, Part 2 or Part 3 was run** — before any
suite, any `serve`, any `--digest-only`, any re-price, any finding count and
before any blind agent was dispatched.

What had been read at sealing time, and nothing else: `gh issue view 224`,
`CLOSE-THE-LOOP-EPIC.md`, `specs/desired_program_model/ticket_plan.yaml`,
`RESULT-CL-02.md`, `CL-03/RESULT.md`, `HARVEST-CL-03.md`, the `### Version
history` table in `references/eval_scorecard.md`, `cmd_serve` in
`score_tools.py`, and the head of `deferred_findings.yaml`. Every prediction
below is therefore a prediction about **whether the predecessors' reports
reproduce**, not a guess in the dark — which is the only thing an evaluation is
entitled to predict and is also why a clean sweep would be uninformative.

**ALARM CONDITION, DECLARED IN ADVANCE.** If **all eleven** hold, this
evaluation reports an **ALARM against itself**: it will mean CL-04 asked only
questions whose answers it already had, and measured nothing.

---

## GOAL-change-rule-runnable

**P1 — the base surface is 6,319, not 6,409.** `score_tools.py serve | wc -c` in
a clean checkout of the epic base `a662675` is **6,319** bytes with **9** rungs.
The `6,409` in the plan, the issue and the epic doc is 90 bytes of the command's
own stderr (`CL-01-DF-01`).

**P2 — the served surface fell.** At the epic tip `0adfb79`, `serve | wc -c` is
**6,281** bytes, **9** rungs. Net **−38 bytes, −0.6%**, no rung added, deleted
or reworded. It did not grow.

**P3 — five versions, five distinct served digests, two anchors digests.**
`serve --card-version N --digest-only` for N = 1..5 returns **five distinct**
values; v4 returns `sha256:a213a36770ccab09` and v5 returns
`sha256:2d7d4a0506d9b259`, **byte-identical to what the version-history table
declares and to what the sealed CL-03 cards record**, so no sealed card is
silently re-based.

**P4 — a stranger's bump costs no source edit and now breaks nothing.** In a
scratch copy outside this tree, editing **only** `references/eval_scorecard.md`
(the version line, one history row, one caveat) makes `serve` report card
version **6** with `score_tools.py` untouched, and the full `tests` suite adds
**zero** failures beyond the two inherited reds. CL-03 reported that four of
CL-01's tests went red on the v5 bump and that it made them relative to what the
file declares; the claim is that the repair generalises to the *next* bump, not
just to the one that exposed it.

**P5 — an unsupported version is still refused loudly.** `serve --card-version 7`
against the unmodified card exits **2** with `REFUSED:` on stderr and names the
edits that would make it legal. Nothing is stamped.

## GOAL-price-means-something

**P6 — the price reproduces, and it is still zero.** At the tip:
`repriced_history.py` prints **0 priced results** and exits 0; `entail` against
the sealed RM-03 before-table at `--head 6298eee` prints **EXTINCT** for
`RM03-GM-RUNNER` and **CONTROL-EXCLUDED** for `RM03-GM-CTRL-C`, with the control
still **printed**; `--head deadbeefdeadbeef` exits **2**; `RM-01-RF-1` still
reads **PRICED** and is still the only price this project has.

## GOAL-loop-closes-once

**P7 — the closure reproduces from the sealed bytes alone, with no judge re-run.**
The four CL-03 cards carry `D3` = **4, 4, 3, 3**; **one judge model id** across
all four; **one artifact** and one architecture tag; the two v4 cards record
served digest `a213a36770ccab09` and the two v5 cards `2d7d4a0506d9b259`. The
card version is the only mover.

## Cost, channels and the toolchain

**P8 — the suite at the tip is 2 failed, and they are the inherited two.** A
clean **real** checkout of `0adfb79` — not a `git archive` — gives exactly
**2 failed**, being `test_the_same_tag_control_holds` (`RM-06-DF-01`) and
`test_nothing_in_the_repository_invokes_the_pricer` (the narrative-document
grep). Neither was repaired by anyone.

**P9 — the numerator was NOT budget-capped this epic; it was budget-EXCEEDED.**
`deferment_policy.budget` is 5 with `blocking: escalate`. I predict CL-01 + CL-02
+ CL-03 filed **11 to 14** findings in `deferred_findings.yaml` — over budget,
with the overflow escalated rather than dropped. (Last epic the numerator was
capped at 30 claims against the same budget of 5; this is the opposite failure
mode, and it is the better one.)

**P10 — the shipped toolchain took zero of this epic's findings, and `scripts/`
is byte-identical.** **Zero** of this epic's findings name `scripts/` or
`spec_double_compiler/` in their `surface`, and `git diff --stat a662675..0adfb79
-- scripts/ spec_double_compiler/` is **empty**. The entire epic happened inside
the eval harness, exactly as `portable-substrate` did.

**P11 — there is no token basis anywhere in the record.** No file under
`specs/results/` records a token, character or cost figure for a *round's own
production*. The 800,181 characters in `HARVEST-CL-03.md` are a measure of the
**corpus swept**, not of what any round spent. So the per-token ratio cannot be
read off the record and must be constructed from a proxy that CL-04 names, and
**it will not be comparable to any prior round, because no prior round has one** —
which is the same defect the repair filed two epics ago was supposed to end.

---

## What would make this evaluation worth having

A falsification. **P4, P9 and P11 are the three with a real mechanism that could
go the other way**, and P4 is the one the epic's headline rests on: "a stranger
can run it" is only demonstrated if the *next* bump is clean, not merely if the
bump we made was survivable after we repaired what it broke.
