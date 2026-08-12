# SV-06 — evidence for the goal-score wiring design

**The design itself is `references/goal_score_wiring.md`.** This page is its
evidence: what was run, over which tree, and what came out.

**SV-06 is a RESEARCH ticket. It ships no production code and edited no skill.**
Every skill file named below was read from `$SKILL_MANAGER_HOME` and none was
written. `skill-manager sync` was never run.

---

## 1. Tree

Branch `feature/SV-06`, branched from `epic/score-drives-validation` at
**`a527305`** — verified with `git rev-parse --short HEAD`, not taken on trust.
`a527305` is *Open the score-drives-validation epic*, one commit above the epic
base `eab2883` that the charter's baselines were measured at.

---

## 2. The survey — one script, every figure

```
uv run --with pyyaml python3 \
  specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-06/analysis/goal_score_survey.py
```

Output sealed at `survey.txt`. **Every figure is about this repository's plans
and record at `a527305` and about no wider population.**

| figure | value |
|---|---|
| distinct epic goals across every `ticket_plan.yaml` on disk, live and sealed | **27** |
| … that name a scorecard dimension (`D1`–`D5`) in statement/metric/harness/target | **12** |
| … whose `baseline.evidence` points at a sealed `scorecard.json` | **0** |
| distinct `baseline.evidence` values | 25 |
| sealed `scorecard.json` files under `specs/results/scorecards/` | 87 |
| files in the three surveyed skills matching `/scorecard\|score_tools\|rubric/` | **6** |

Two of these correct figures the epic sealed at `eab2883`: the "no goal has ever
been keyed to a dimension" baseline (`SV-06-DF-01`) and the "four files" surface
(`SV-06-DF-03`).

The skill-surface count excludes each skill's own installed dependencies by
name — without that exclusion it is 7 and the seventh is a `pygments` lexer
inside `git-issue-workflow/.venv`. The exclusion is in the script, not applied
by hand.

---

## 3. `spec-double-compiler` — confirmed, not assumed

The charter says its ~990 matches are a bundled copy of this repository's
record. Checked at `$SKILL_MANAGER_HOME/skills/spec-double-compiler/`:

- 979 files carry the string `scorecard`, about 20,000 occurrences;
- by directory: `specs/results` 468 files, `specs/.history` 433,
  `examples/validation` 52 — the sealed record;
- the unit carries `.git`;
- its top-level listing is this repository's listing;
- **`references/eval_scorecard.md` is byte-identical (`cmp`) to this
  repository's copy at `a527305`.**

**Confirmed, with one correction.** It is not a bundled copy of the *record* —
it is the **whole repository shipped as a skill unit**, live card and tooling
included. It is correctly out of scope as an integration point, and the
correction matters for §6 of the design: the card already reaches an adopter
through a skill install today.

While confirming this, `SKILL.md:1337` was found to describe the card as *"Five
judged dimensions"* at a tree where it serves two and refuses three.
`SV-06-DF-04`.

---

## 4. The validator experiment — reported because it argues AGAINST the field

An invented `scored_by:` block (rubric / rubric_version / dimension / subject /
baseline_card) was added to one goal of a scratch copy of this epic's plan,
plus a `score_signal:` on one ticket-goal link.

```
uv run --with pyyaml python3 \
  $SKILL_MANAGER_HOME/skills/git-epic-workflow/scripts/validate_epic_plan.py <plan>
```

| plan | exit | output |
|---|---|---|
| `specs/desired_program_model/ticket_plan.yaml`, unmodified | 0 | `OK: … 7 tickets across 4 waves, 4 goals` |
| the same plan + `scored_by:` + `score_signal:` | 0 | same message |

Sealed under `validator-experiment/`. The plan schema reads named fields and
ignores unknown ones — **an optional scoring block costs zero lines of Python
today.** The design rejects it anyway (`goal_score_wiring.md` §8): every field
is already sayable in `harness`, `metric` and `baseline.evidence`, and
`dimension:` would export a project-local key into a schema three skills share.
**Cheap to add is not a reason to add.**

The experiment's other half is the one that matters for absence: **a plan with
no scoring block validates today, unchanged, and will validate identically
after SV-07** — because SV-07 adds no field at all.

One incidental: `score_signal: N/A: <reason>` unquoted is invalid YAML in a
plan. Not filed — the skills' own examples quote it
(`local_signal: "N/A: this ticket is the measurement"`), so the documented form
is correct.

---

## 5. `serve` — the surface metric, unmoved

```
python3 examples/validation/scorecards/score_tools.py serve | wc -c
```

**6,281 bytes, 9 rungs** at `a527305` — D2's four rungs 0–3 plus D3's five rungs
0–4. **No proposal in the design touches `references/eval_scorecard.md`, so the
byte cost of the entire SV-07 hand-off is 0 and no anchor is created.** The
carriers are prose in three skill files and a free-text convention in a plan;
per the epic's costing rule, a prompt is free and an anchor is permanent, and
this design creates none of the permanent kind.

---

## 6. `scope` — R3 over the design page

```
uv run --python 3.12 python3 examples/validation/scorecards/score_tools.py scope
```

**Every row names its tree.**

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `a527305` + SV-06 | 93 | 68 | 0 | 5 | 20 |
| `a527305`, `goal_score_wiring.md` moved aside | 93 | 68 | 0 | 5 | 20 |

**SV-06's delta is zero on every column**, and `scope --path
references/goal_score_wiring.md` reports 0 counted figures. **That is bound 1
(`RD-02-DF-01`), not a clean result**: `scope` re-derives figures of the form
`D<n> = k on N of M cards`, and SV-06's figures count goals, files and evidence
values rather than cards, so they are invisible to the checker rather than
checked by it. The design page says so in its own §10 and the discipline is
owed by hand instead.

`scope`'s exit 1 is this repository's inherited state — its demonstrated failing
input, per `score_tools.py`'s own docstring — and not a defect introduced here.
Sealed at `scope-with-sv06.txt` and `scope-without-sv06.txt`.

---

## 7. Suite — and a THIRD inherited red the epic does not list

```
uv run --with pytest --with pyyaml python -m pytest tests -q
```

**Tree `a527305` + SV-06 (`references/`, `specs/results/`, `specs/tickets/SV-06/`
and the five findings): `3 failed, 1495 passed` in 1204s.**

`denominator_rule`: **1,498 collected**, which is the figure `close-the-loop`
closed on (`2 failed, 1496 passed` = 1,498). **Zero movement in the
denominator.** SV-06 adds no test, deletes none, skips none and weakens none —
its whole product is two documents, a survey script and five findings.

The runtime is inflated: `SV-01` and `SV-02` were running the same suite
concurrently in their own worktrees. Their processes were left alone. Runtime is
not a reported figure here.

### Naming the three

| test | status |
|---|---|
| `tests/test_architecture_tags.py::test_the_same_tag_control_holds` | inherited, deliberate — the same-tag control |
| `tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer` | inherited, deliberate — the pricer grep, which at this tree names `CLOSE-THE-LOOP-EPIC.md` and `NEXT-EPIC.md` |
| `tests/test_card_has_one_home.py::test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule` | **inherited, and NOT on the epic's list of two** |

**The third is not SV-06's and it is not new work — it arrived with the commit
that opened this epic.** Its four offender lines are:

```
SCORE-DRIVES-VALIDATION-EPIC.md:40   states dimension D2
SCORE-DRIVES-VALIDATION-EPIC.md:41   states dimension D3
specs/desired_program_model/ticket_plan.yaml:8   states dimension D2
specs/desired_program_model/ticket_plan.yaml:8   states dimension D3
```

`git show --stat a527305` touched **exactly two files**, and they are those two.
`SCORE-DRIVES-VALIDATION-EPIC.md` does not exist at `eab2883`. So the
epic-opening commit turned this test red, in the same document that says *"Two
reds are inherited deliberately."* **There are three.**

Demonstrated to be inherited rather than caused: with
`references/goal_score_wiring.md`, the whole `specs/results/scorecards/score-drives-validation/`
tree and the five findings all removed, the test fails with the identical four
lines. **SV-06's own design page appears nowhere in the offender list** — it
points at the card and never restates it, which is the property this test
exists to enforce and a useful independent check on the page.

**Not filed: the finding budget of 5 is spent and none of the five is blocking.**
Escalated here and in the ticket report instead, following `RM-02`'s precedent
for a spent budget. It is reproducible in under three seconds:
`uv run --with pytest --with pyyaml python -m pytest tests/test_card_has_one_home.py -q`.

**The fix is the test's own prescribed one and it is a POINTER, not a corrected
copy** — the charter and the plan should link `references/eval_scorecard.md`
instead of restating which dimensions it scores. **Not done here**: both files
are outside SV-06's `implementation_scope`, `ticket_plan.yaml` is the canonical
plan, and repairing an inherited red silently is exactly what the epic's rules
forbid.

---

## 8. Findings filed

Budget 5, spent 5, **none blocking**.

| id | what |
|---|---|
| `SV-06-DF-01` | the epic's own baseline is false in its loudest clause — 12 of 27 goals are dimension-keyed; the true gap is 0 of 27 scored baselines |
| `SV-06-DF-02` | `goals-and-evaluation.md`'s judged-baseline rule has a compliance rate of 0 of 27 here, and the file has no branch that would produce compliance |
| `SV-06-DF-03` | the surveyed surface is six files, not four; the missed `discovery.md` is the earliest seam in the lifecycle |
| `SV-06-DF-04` | `SKILL.md:1337` ships a description of a five-dimension card that the checker refuses |
| `SV-06-DF-05` | `portable_scorecard.md` §2 item 1 was settled by the next epic and still ships as current |

Nothing was fixed inline. `SV-06-DF-04` and `SV-06-DF-05` are outside this
ticket's `implementation_scope`; `SV-06-DF-01` and `SV-06-DF-03` sit inside
sealed baselines that the epic's own discipline forbids editing mid-epic
(`PA-01-DF-01` precedent); `SV-06-DF-02` is a skill file, which this ticket may
not touch and which SV-07 owns.

---

## 9. What SV-05 should test

The design's absence guarantee is stated in advance so it cannot be adjusted
afterwards. In `CL-04`'s shape: hand a blind agent the six surveyed files after
SV-07 lands, plus the plan of an epic declaring no judged harness, and ask it to
run the goal process end to end. **If it asks what rubric to use, the design
failed.** A pass is that it never notices the added sentences.
