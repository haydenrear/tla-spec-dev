# SV-03 — the goal process learns to name a card

**Branch point `5620c9a`, verified with `git rev-parse --short HEAD` rather
than taken on trust** — the epic charter records that `wt new` branches from
the local ref and has put tickets 4, 14 and 21 commits behind, and that a
handed-out SHA has failed to resolve once. Every measurement below was taken at
`5620c9a` plus this ticket's own untracked evidence, and every count names that
tree. The commit SHA this lands on is in the PR, not guessed at here.

---

## 1. What this ticket is, after the premise correction

The work order's original framing — *"no goal has ever been keyed to a
dimension"* — is false by a factor of twelve, and SV-06 proved it. **12 of 27
goals name a dimension in prose.** What none of them do is *be* a score.

This ticket ships the fix as SV-06 designed it: **four prose edits to three
skill files, no new field, no new gate, and zero bytes to `serve`.** Because
skills are READ from this repository and never edited from it, the edits are
**proposed as diffs and escalated**, and what lands here is the proposal, the
demonstration that it works, the demonstration that it costs a project with no
card nothing, and the tests that hold both.

---

## 2. The measurement, sharpened

SV-06 measured **0 of 27** by asking whether the string `scorecard.json` appears
in `baseline.evidence`. This ticket asks the question the evaluation ticket
actually has to answer — **given only the goal, can you open the card that
produced the baseline number?** — by resolving every value against the
filesystem.

`analysis/baseline_is_a_card.py`, at `5620c9a`, over **109 plans** on disk
(live and sealed):

| | |
|---|---|
| distinct epic goals | **27** |
| … naming a judged instrument | **18** |
| … whose baseline the evaluation ticket can OPEN | **0 of 18** |
| cite a **directory** | 8 |
| cite a **document** (`RESULT.md`, `SELF-IMPROVEMENT.md`, a reference page) | 8 |
| cite a path that **does not resolve at all** | 1 |
| are **pure prose**, no path | 1 |
| goals naming no judged instrument, out of scope and legal | **9** |
| sealed `scorecard.json` on disk, none cited by any goal | **87** |

**`denominator_rule`.** SV-06's *0 of 27* and this *0 of 18* are the same
numerator over two different populations. **18 is the right denominator** —
the other 9 goals are decided by mutants, benches and finding counts, and no
rule about cards applies to them. The correction makes the compliance rate
worse, not better, which is why it is worth making.

---

## 3. R1 — the demonstrated failing input, on a real epic plan

**`GOAL-loop-reaches-the-program`, in this epic's own live plan**, cites
`specs/results/scorecards/close-the-loop/` as its baseline evidence. **That
directory contains zero `scorecard.json` files.** The CL-03 cards are in two
sibling directories, `close-the-loop-cl03-v4/` and `-v5/`.

So the failure is worse than *"the evaluation has to pick a card out of a
folder"*: **there is no card in the folder to pick.** The baseline was sealed
at `eab2883` and is never edited, which makes it a stable subject rather than a
moving one. Pinned by
`tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened`,
whose docstring says to move the demonstration rather than delete it if the
plan is ever repaired.

**A second failing input, and it is aimed at the proposal itself.** SV-06's
verbatim wording for edit 2 — *"the path to the **single** sealed card that
produced the number"* — is unsatisfiable for `GOAL-D2-can-move`, whose baseline
is *"D2 = 2 on 27 of 27 cards"*, and for `GOAL-validation-is-scorable`, whose
baseline is *"D1 read 3 on 55 of 59 cards"*. `GOAL-D2-can-move` is the goal
SV-06 itself holds up as the best of its kind in this repository. The shipped
wording therefore asks for **enumerability, not singularity**: *"the sealed card
that produced the number, or — where the number is a figure over several cards
— the exact list of them."* Found by running the rule against the record, not
by reading it. Filed as `SV-03-DF-01`.

---

## 4. Proof a project with no card is unaffected — demonstrated, not asserted

`analysis/no_card_project_unaffected.py`, exit 0:

1. **A complete epic plan with no card anywhere** (`no_card_plan.yaml`: two
   goals, both decided by `bench/ingest.sh`, no rubric, no judge, no dimension)
   is run through `git-epic-workflow/scripts/validate_epic_plan.py` **from a
   pristine copy of the three skill units and from a copy with all four diffs
   applied**. Exit code and stdout are **identical**. So is the result for this
   repository's own live plan.
2. **Every added block opens with a conditional the no-card project fails** —
   *"Harness is judged and…"*, *"For a judged goal…"*, *"Where a goal's harness
   is a judged instrument…"*, *"Where the deciding instrument records notes…"*.
   **331 words added; 0 that a project with no card must obey.** The guard check
   is shown FAILING on an unguarded sentence
   (`test_the_guard_check_FAILS_on_an_unguarded_block`) so it cannot pass
   vacuously.
3. **The installed home is re-hashed before and after every run** and reported
   UNCHANGED. Nothing was applied; `skill-manager sync` was not run.

One honest wrinkle, recorded rather than hidden: the first version of that
script compared stdout+stderr and reported a **false difference**, because
`uv run --script` writes provisioning chatter to stderr on a cold cache. The
comparison is now exit code plus stdout, and the reason is in the function's
docstring. That was this instrument's own demonstrated failing input, observed
in flight.

---

## 5. The worked example

`example_goal.yaml` carries two goals and **the second one is as much of the
point as the first**: a command-harness goal with no card, written exactly as
it would be today and untouched by anything here.

The judged one cites **two real sealed cards**
(`close-the-loop-cl03-v4/…/p1` and `…/p2`), and the test opens them and checks
that the `D3 = 4 and 4` in the goal's prose, the rubric digest it names, and the
commit it names are the bytes on disk. **If the prose ever drifts from the card,
the suite goes red** — which is the entire property the third branch exists to
create.

It **adds no field**: every key is one the schema has today, and a test asserts
`dimension` is not among them. The dimension key lives in the free-text
`metric`, where 12 of 27 goals already put it.

Both files load **identically under `yaml.safe_load` and under
`scripts/extract_spec_manifest.parse_simple_yaml`**, asserted per file.

---

## 6. What landed in this repository, and why that is the right side of the line

| here | why not in a skill |
|---|---|
| `proposed-skill-diffs/*.patch` (4) | the change belongs in `SKILL_MANAGER_HOME`, which this repository may not write. A patch file is the escalation. |
| `ESCALATION.md` | the base hashes, the buys, the deviations from SV-06 with their evidence, and what was rejected |
| `example_goal.yaml`, `no_card_plan.yaml` | a skill may not carry this project's card paths; this project may. |
| `analysis/*.py` | measurement, sealed with the round |
| `tests/test_goal_baseline_is_a_card.py` | the only place that can hold the example to its cards |

**No `references/` page was added.** `references/goal_score_wiring.md` is the
design and `ESCALATION.md` is the proposal; a third page restating both is the
surface SV-06 spent its §8 refusing.

**Neither analysis script is registered in `instruments.toml`.** Its enumeration
scope is `roots = ["scripts", "examples/validation"]` and these are under
`specs/results/`, which that registry declares out as sealed measurement
archives. Stated here rather than left to be noticed.

---

## 7. Cost, in the units this epic measures in

| | before | after |
|---|---|---|
| `score_tools.py serve \| wc -c` | **6,281** | **6,281** |
| rungs | **9** | **9** |
| served digest | `sha256:2d7d4a0506d9b259` | `sha256:2d7d4a0506d9b259` |
| files this repository ships that were touched | — | **0** |
| new plan fields | — | **0** |
| new gates, checks or validator rules | — | **0** |

`references/eval_scorecard.md` is untouched. **The card does not learn about the
goal process; the goal process learns to name a card.**

---

## 8. Suite counts, with the tree for each

`uv run --with pytest --with pyyaml python -m pytest tests -q`

| tree | result |
|---|---|
| `5620c9a`, clean checkout, before this ticket | **2 failed**, the deliberate two |
| this branch, with the ticket workspace OPEN | see §8.1 |

**§8.1 — `denominator_rule`, and which side each move came from.**
`tests/test_spec_yaml_valid.py` is parametrised over every `*.y*ml` under
`specs/` outside `.history`, so the collected total is a joint property of the
tree *and* of whether a ticket workspace is open:

| source of the move | files |
|---|---|
| `specs/` yaml at `5620c9a`, clean | 23 |
| `tla-spec-dev open ticket SV-03` scaffolded a ticket workspace | **+4** |
| this ticket's evidence (`example_goal.yaml`, `no_card_plan.yaml`) | **+2** |
| total **while the workspace is open** | **29** |
| `tla-spec-dev close ticket SV-03` removed the workspace again | **−4** |
| total **on the committed tree** | **25** |

The +4 is transient and belongs to the workspace, not to the ticket: a run
taken between `open` and `close` collects four more parametrised cases than a
run taken on the committed tree, and it is the same code either way. The
committed move is **+2**, and both are this ticket's.

Plus **19 tests** from `tests/test_goal_baseline_is_a_card.py`. **The two reds
are inherited and were not touched**: `test_price_removal.py` (the pricer grep
tripped by narrative documents) and `RM-06-DF-01`. A third red existed at the
epic base, was the owner's, and was fixed at `b999d71` before this ticket
branched.

---

## 9. What was REJECTED

Fully in `ESCALATION.md`. The short list, and the first is the one that took
argument:

- **A checker that a judged goal has a card baseline.** The classifier is
  already written and `return 1` is one line. Refused: `no_new_gates_rule`,
  seven epics of static checking with zero bugs caught, and the thing it would
  gate is *the epic owner's prose about their own baseline*. The classifier has
  **no failing exit path at all**, and two tests assert that nothing in
  `scripts/` reads it.
- **A `dimension:` field**, a `scored_by:` block, a `score_signal:` field. SV-06
  built and validated the last two and rejected them; re-checked, not inherited.
- **A test asserting plans comply.** Same argument one layer down.
- **A card bump or any edit to `references/eval_scorecard.md`.** The blind
  adopter's blocker 2: a bump makes `[[movement]]` mandatory and undocumented.
- **A `--goal` flag on `score_tools.py`.** It inverts the dependency and makes
  the card a participant in the goal process instead of an instrument it names.
- **Retro-fitting this epic's own sealed baselines** to cite cards. That is
  editing a measurement to match a result, and it would destroy this ticket's
  R1 subject.

---

## 10. What this ticket could not settle

- **Whether an adopter ever reaches the third branch.** Everything here is
  designed and demonstrated against this repository, where we wrote both the
  card and the epics. `SV-05`'s blind test decides it, and SV-06 §6 already
  sealed the pass condition: *if the blind agent asks what rubric to use, the
  design failed.*
- **Whether a kickoff scoring round is affordable for an ordinary project.** The
  fail-open clause makes an unaffordable round legal; it does not make it cheap.
- **Whether `SV-07` still has a scope.** After this ticket, its placeholder
  objective is what SV-03 just did. Filed as `SV-03-DF-05` rather than acted on.
