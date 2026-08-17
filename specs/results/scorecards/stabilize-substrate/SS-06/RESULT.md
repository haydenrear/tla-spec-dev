# `SS-06` — the tree, not the count

**Every figure below names the tree it was measured on and which side of the
ticket close it was taken on.** Nothing here is quoted from the charter, the
plan, or a sibling ticket's report; where a published figure and my measurement
disagree, both are printed and the disagreement is reported as the result.

---

## 0A. Review round of PR #286 — what I got wrong

**An independent reviewer instructed to REFUTE returned CHANGES with nine
findings, two high. Every one was re-derived here by execution before being
accepted, and every one held.** Nothing was rejected.

**The reviewer's summary of me is the finding, and it is the sentence to keep:
every figure I produced by RUNNING re-derived exactly — two of them better than I
claimed — and every figure I produced by READING rather than running is wrong.**

| # | what | where it is corrected |
|---|---|---|
| **F1** high | **My headline diagnosis is refuted by executing the check I said could not see it.** The escalated clause is **withdrawn**; the cause is register coverage, which `SS-07-DF-08` had already diagnosed | §5A, `SS-06-DF-05` |
| **F2** high | My new check **could not tell a declaration from a quotation of one** — a time bomb that fires when the next ticket disposes `CA-10-DF-15` | §7.0, `SS-06-DF-06` |
| **F3** | I inflated the `or True` population **2 → 3**, in the ticket about population inflation | §3.5, `SS-06-DF-01` |
| **F4** | **My repair for `SS-06-DF-05` committed `SS-06-DF-05`'s mechanism** | §7.0, `SS-06-DF-07` |
| **F5** | The wall-clock figure was a cold run against a warm one. **Deleted; nothing moved at all** | §3.3 |
| **F6** | The battery's table **did not support the sentence it sat under** for 1 of 6 nodes. Seventh case added | §3.3 |
| **F7** | The widened guard still missed `stage.from`, `stage.to`, `remove` — and `SS-02-DF-09` named `stage.from` | §5.2 |
| **F8** | "three of the six shipped states" — there are **nine** states; 6 was the link-entry count | §5.2, §5.3 |
| **F9** | Two `close ticket` products in this PR are outside my keys and were not disclosed | §8.8 |

**What held, and where I under-claimed.** The uncollected-node list is
**byte-identical** to the reviewer's independently derived one. The six-site
vacuous population is **not inflation** — `CA-10-DF-14`'s own reproduction grep
returns all six at its own `found_at_commit`, so **the finding under-counted by
its own method**. The deletion battery reproduced verbatim; `CA-10-DF-15` at three
confirmed and the new check **genuinely refuses pre-repair, verified by running**;
`SS-02-DF-09`'s widen confirmed in both directions; the suite
`7/1596/0/1/1604` confirmed independently with an identical seven-name FAILED set.

**And three of the nine are not mine.** The owner has ruled that **13 was wrong at
`436c78c` too** (1491 → 1503 scaffold → 1504 ledger move; the 13th node is
`test_spec_yaml_parses[deferred_findings.yaml]`, from the owner's own ledger
relocation — so my 12 is right at both trees); that my plan entry's
`schedule_revision: 1` against the plan's 2 is theirs; and that `SF-309` is real
and its resolution is theirs.

**The figures in §1 are unchanged by this round** except for the new tip, because
none of the nine findings was about a number I measured by running.

---

## 0. Headline

- **The five numbers sum at every tree this ticket stood in — five of them.**
  BASE `8dd0442`, workspace not open: **7 / 1550 / 0 / 1 / 1558**.
  REVIEW TIP `5c06db8`, the authoritative one: **7 / 1598 / 0 / 1 / 1606**.
  **`failed` did not move at any of the five**, and every unit of the +48 in
  `collected` is attributed by node.
- **Clause (d) is verified BY EXPERIMENT and the published number is wrong.**
  The "13 uncollected nodes" population is **12 at this tree**, measured by
  deleting `specs/current/` and `specs/desired_program_model/` in a throwaway
  clone and diffing the `--collect-only` node lists. All 12 are collected at my
  base and at my tip. None is a defect.
- **Clause (c): the skip population is 0 at the base and 0 at the tip**, and the
  plan's stated mechanism for the last four was false — which is a separate fact
  from their being gone.
- **Clause (e): the vacuous-pass population is SIX, not three.** `CA-10-DF-14`
  names three; the identical guard is at six sites in the same module. All six
  are repaired. **None of them turned red**, and the deletion battery says
  exactly why: they discriminate on CONTENT and were blind only to ABSENCE.
- **The sweep found a second sub-shape the finding does not name** — the
  tautological assertion `X or True`, at **two** sites: one repaired here, one
  filed. A **third, weaker** non-falsifiable assertion of a different shape is
  filed beside it. The class is **not** closed at six. (This bullet said "three
  sites" until review; see §3.5.)
- **`CA-10-DF-15` decided: CONFIRMED, and its population is three, not two.**
- **`SS-02-DF-09` decided: WIDEN.** Both guards widened, and the reviewer's own
  hypothetical evasion executed to prove the widening discriminates.
- **The +2 `test_source_citations` reds are not the scaffold's defect.** All
  three failing manifests carry the **identical 15 stale citations**: one defect
  counted three times.

---

## 1. The five numbers, at both ends, at a named tree

Command, exactly as the assignment declares it, exit code read **unpiped**:

```
uv run --with pytest --with pyyaml -m pytest tests -q
uv run --with pytest --with pyyaml -m pytest tests -q --collect-only
```

| | failed | passed | skipped | xfailed | collected | sums? |
|---|---:|---:|---:|---:|---:|---|
| **BASE `8dd0442`**, workspace **not open**, before `SS-04` | **7** | **1550** | **0** | **1** | **1558** | `7+1550+0+1=1558` ✓ |
| **TIP `8fa4626`**, workspace **OPEN**, before reconciling | **7** | **1563** | **0** | **1** | **1571** | `7+1563+0+1=1571` ✓ |
| **TIP `6ee1532`**, workspace **OPEN**, `SS-04` reconciled | **7** | **1600** | **0** | **1** | **1608** | `7+1600+0+1=1608` ✓ |
| **TIP `64c2f91`**, workspace **CLOSED** (post-close) | **7** | **1596** | **0** | **1** | **1604** | `7+1596+0+1=1604` ✓ |
| **TIP `5c06db8`**, workspace CLOSED, **review round — authoritative** | **7** | **1598** | **0** | **1** | **1606** | `7+1598+0+1=1606` ✓ |

**Five rows, because a figure is a joint property of the artifact AND the tree,
and this ticket stood in five different trees.** The middle two are both real
measurements and neither is discarded: `8fa4626` is this ticket's work before its
promotion predecessor landed, `6ee1532` is the same work with `SS-04` merged in.

**THE AUTHORITATIVE FIGURE FOR A READER STANDING IN THE MERGED TREE IS THE LAST
ROW: `7 / 1598 / 0 / 1 / 1606` at `5c06db8`**, the review round.
**`failed` did not move at any of the five trees** — the same seven nodes by name
throughout. The review round's `+2` is the two directions of the `SS-06-DF-06`
withdrawal marker, both passing, attributed by node in
`evidence/collection-attribution.txt` §D→E.

**And the divergence the plan told every ticket to expect is here, disclosed
rather than discovered.** `close ticket` seals the history summary and deletes
the workspace in ONE operation, so the sealed entry at
`specs/.history/stabilize-substrate-epic/ticket-005-SS-06/summary.md` carries
`7 / 1600 / 0 / 1 / 1608` — the **pre-close** tree — while this document carries
`7 / 1596 / 0 / 1 / 1604`. **`R-H4` forbids editing the sealed entry, and this
one at least SAYS which tree its figure is of**, which `SS-01`'s did not. The
difference is exactly `-4` and it is the machinery, not a movement: `close
ticket` deletes `specs/tickets/SS-06/` and `test_spec_yaml_valid`'s six suffixed
ids collapse back to two un-suffixed ones. **Attributed by node in
`evidence/collection-attribution.txt` §C→D, and predicted before it happened.**
Filed as `SF-308` in `specs/results/skill_feedback.md` — five tickets have now
written this same sentence by hand, which makes it a defect in `close ticket`
rather than a fact of life.

Sealed raw output: `evidence/pytest-base-8dd0442.txt`,
`evidence/collect-base-8dd0442.txt`, `evidence/pytest-preclose-8fa4626.txt`,
`evidence/collect-preclose-8fa4626.txt`, `evidence/pytest-preclose-6ee1532.txt`,
`evidence/collect-preclose-6ee1532.txt`,
`evidence/pytest-postclose-64c2f91.txt`,
`evidence/collect-postclose-64c2f91.txt`.

### 1.0 Every movement, attributed, with the direction named

**failed: 7 → 7 → 7 → 7. No movement in either direction, at any of the four trees.**
The same seven nodes, by name, at the base and at both tips. **This ticket
produced no new red**, and the only reds it removed are `SS-04`'s three, which
arrived through the reconcile and were repaired in the same commit that brought
them in — so they are never counted as a red here and never counted as a repair
that moved this ticket's number. §3.4 explains why the vacuous-pass repair could
not produce a red at this tree, and §6 attributes all seven.

**skipped: 0 → 0**, **xfailed: 1 → 1** (`SS-01`'s strict xfail, untouched).

**passed: 1550 → 1563, +13. Numerator movement, all of it new nodes**, none of it
a red turning green: `+9 mine`, `+4 machinery`.

**collected: 1558 → 1608, +50**, attributed **by node**, not inferred
(`evidence/collection-attribution.txt`):

| | nodes | cause |
|---|---:|---|
| **mine** | **+9** | 8 in the new `tests/test_declared_reds_cite_an_open_finding.py` (the `CA-10-DF-15` check) and 1 in `test_absent_input_demonstrations.py` (the `SS-02-DF-09` path-reader demonstration). All 9 pass. |
| **`SS-04`, not mine** | **+37** | `tests/test_counted_figure_recogniser.py`, `SS-04`'s new module, arriving through the reconcile. Not attributable to this ticket in either direction. |
| **machinery, not mine** | **+4** | 6 added − 2 removed in `test_spec_yaml_valid`'s parametrisation: `open ticket` scaffolds `specs/tickets/SS-06/`, and the un-suffixed ids `complexity_ledger.yaml` and `ticket.yaml` become suffixed `0`/`1` pairs. **This is the documented +4 that `close ticket` removes again**, and it is why the last row of the table exists. |

**passed 1550 → 1600, +50**: the same three groups, none of it a red turning
green — **except three that are exactly that, and they are declared**: `SS-04`'s
three `test_score_tools.py` reds (`SS-04-DF-06`) arrive red through the reconcile
and are repaired by this ticket in the same commit, so they never appear as reds
in any figure published here. **§5B is where they are accounted for**, and
`SS-08` should read them as three attributed reds repaired, not as an unexplained
+3.

The six guards I repaired moved **nothing** in any of the five buckets. That is
the correct outcome and it is stated as such rather than dressed up: the repair
changes what the suite says when an input is ABSENT, and no input is absent here.

### 1.1 The base I branched from, re-derived rather than quoted

The assignment predicted "roughly `7 / 1550 / 0 / 1 / 1558`". Measured here:
exactly that, at `8dd0442`, in this worktree. **It is not the plan's
`8 / 1509 / 0 / 1 / 1518` at `50046b2` and not the charter's
`17 / 1483 / 4 / 0 / 1504` at `436c78c`.** Both of those are earlier trees;
neither is quoted anywhere below.

### 1.2 I contaminated my first base run, and I am keeping it

`evidence/pytest-base-8dd0442-CONTAMINATED-edited-mid-run.txt` is a complete run
of the base command that I **edited three of the test files underneath**
(`test_analyze_complexity.py`, `test_score_tools.py`,
`test_absent_input_demonstrations.py`) while it was executing. That is the exact
rule `planning_rules.operational_rules_this_project_has_paid_for` states, broken
by the person who had just read it — **the seventh party in this epic to do it.**

It is kept, not deleted, and it is not the figure in §1. I re-ran the base from
a `git stash`-clean tree afterwards and that clean run is the base figure.

**And the two runs are byte-identical except for the `uv` cache path and the
duration** (`1698.52s` clean vs `1761.00s` contaminated). The reason is worth
recording rather than treating as luck: `pytest` imports every test module
during collection, at t=0, so the code that executed was the base code in both
runs and my edits reached only the tracebacks. **The contamination was harmless
HERE for a reason that will not hold next time** — an edit that lands before
collection, or a change to a data file a test reads at run time (the ledger, a
manifest, a scorecard) would have changed the report silently.

---

## 2. The two populations the kickoff said were already resolved

### 2.1 Clause (d): the uncollected nodes are **12**, not 13, and they are workflow state

**Measured, not explained.** In a throwaway clone at `8dd0442` I deleted
`specs/current/` and `specs/desired_program_model/` — which is precisely what a
workflow close does — and diffed the `--collect-only` node lists.

```
collection with the epic workflow SCAFFOLDED : 1558
collection with the workflow CLOSED          : 1546
difference                                   : 12 nodes
```

Every one of the 12 is a parametrisation over a path that exists only while a
spec workflow is open: 8 in `test_source_citations.py` (over
`specs/{current,desired_program_model}/{spec_manifest.yaml,TlaSpecDevCli.tla}`)
and 4 in `test_spec_yaml_valid.py`. **No node is collected only in the closed
state.** Full list: `evidence/uncollected-nodes-measured.txt`.

**The charter, the plan and the issue all say 13.** At the tree I branched from
it is 12. I did not chase the difference into `436c78c` — the number that
matters for clause (d) is the one at the tree the clause is decided on — but
**`SS-08` should not re-publish 13 without re-deriving it**, and the direction of
the movement is denominator: the population of nodes-that-depend-on-an-open-
workflow, not a count of defects.

> **RESOLVED BY THE EPIC OWNER after review, and 13 was wrong at `436c78c` too.**
> The owner measured it: **1491 → 1503 (the scaffold, +12) → 1504 (the ledger
> relocation, +1)**. The 13th node is
> `test_spec_yaml_parses[deferred_findings.yaml]`, and it appeared because the
> owner **moved the ledger**, not because the workflow was scaffolded. So the
> scaffold restored **12** at `436c78c` as well, the two causes had been summed
> into one number, and the owner is correcting it in five places. **My 12 is
> right at both trees; the difference was never mine to chase, and the reviewer
> confirmed my node list is byte-identical to theirs.**

Clause (d) is satisfied at my base and my tip **by collection, not by
explanation**: all 12 are collected in both.

### 2.2 Clause (c): the skips are 0, and the prediction that cleared them was false

`0 skipped` at the base and `0` at the tip. There is no skip to explain or
retain.

**The plan and the charter both predicted the last four (`test_workflow_close_
keeps_the_ledger.py:92`) would "unskip when `SS-01` repoints".** That prediction
is **false as a mechanism**, and the `SS-01` reviewer demonstrated it: repointing
`LIVE_LEDGER` alone converts them to **four reds** on `cannot close ticket
workflow: - ticket SS-01 is not closed: status=planned`, because the skip was
covering a second, unfiled reason — the subject was the live spec tree, which
refuses its own close while a workflow is open. They are gone because `SS-01`
moved the subject to the sealed `cut-the-apparatus` snapshot.

**A prediction that comes true by a different mechanism is not a confirmed
prediction.** The population is 0 and the plan's account of why is wrong; both
belong in `SS-08`'s reading.

**My repair adds no skip at this tree.** Three of the six guards I repaired now
answer `pytest.skip(...)` instead of returning silently — but they only fire
when `specs/current/` is absent, and it is present at base and tip. The skip
count is unchanged at 0 in both directions, and the deletion battery is where
the three skips are actually observed.

---

## 3. The vacuous passes: the population, the repair, and what the deletion method found

### 3.1 The population is six, and `CA-10-DF-14` names three of them

`CA-10-DF-14` names `test_repository_own_model_reproduces_the_recorded_state_
space_bound`, `test_cm01df02_the_repository_own_cfg_is_unchanged_by_the_fix` and
`test_repository_own_model_has_landed_the_setup_phase_collapse`. The guard it
describes — `if not path.is_file(): return` — is at **six** sites in
`tests/test_analyze_complexity.py`. The three the finding names guard
`specs/current/**`; the three it does not guard
`examples/distributed_history/specs/program_model/**`.

The three unnamed ones were invisible to the finding because the CA-10 pass was
taken in a **closed-workflow** tree, where only the `specs/current` guards fired.
The example files are committed, so their guards have never fired — **and a
guard that has never fired is exactly the one nobody notices.**

### 3.2 The repair: two different answers, because there are two different questions

| sites | subject | absent state is | answer shipped |
|---|---|---|---|
| 3 | `specs/current/{TlaSpecDevCli.tla,MC.cfg}` | LEGITIMATE — the workflow can be closed | `pytest.skip(...)` naming the path: **UNDECIDED, announced** |
| 3 | `examples/distributed_history/**` | A DEFECT — the files are committed | `assert path.is_file(), ...`: **a REFUSAL** |

Neither answer is PASS, which is
`planning_rules.r1_now_requires_an_absent_input` applied to a test instead of an
instrument. A blanket `pytest.skip` — the fix `CA-10-DF-14` suggests — would have
been wrong on the second three: it would convert a deleted committed fixture into
an announced non-answer.

Two of the six guards also tested ONE file while the body read TWO (`tla` checked,
`cfg` read). Both are named now.

### 3.3 What the deletion method found — and the honest answer is "less than the ticket hoped"

`vacuity_probe.py` runs the method as a **named, repeatable battery** rather than
a one-off grep: it mutates a throwaway clone, runs a named node list, reverts, and
prints `NOTICED` or `PASSES-UNCHANGED`. Six cases, sealed at
`evidence/deletion-battery-BEFORE.txt` and `evidence/deletion-battery-AFTER.txt`.

| case | what is taken away | BEFORE (`8dd0442`) | AFTER |
|---|---|---|---|
| `input-absent-specs-current` | the whole of `specs/current/` | `3 passed` → `3 passed` — **PASSES-UNCHANGED** | `3 passed` → `3 skipped` — NOTICED |
| `input-absent-example-model` | the committed `External.tla` and `.cfg` | `3 passed` → `3 passed` — **PASSES-UNCHANGED** | `3 passed` → `3 failed` — NOTICED |
| `code-deleted-state-space-bound` | the multiplication in `state_space_bound()` | `6 passed` → `3 failed, 3 passed` — NOTICED | same |
| `code-deleted-parse-cfg-invariants` | the body of `parse_cfg_invariants()` | `6 passed` → `3 failed, 3 passed` — NOTICED | same |
| `subject-changed-setup-phase` | the `setup_phase` declaration in the live model | `3 passed` → `2 failed, 1 passed` — NOTICED | same |
| `subject-changed-mc-cfg` | the `INVARIANT` name in the live `MC.cfg` | `3 passed` → `1 failed, 2 passed` — NOTICED | same |

| `subject-changed-example-next-relation` **(added in review)** | one disjunct removed from the example's `ExternalNext` | — | `3 passed` → `1 failed, 2 passed` — NOTICED, and it is the **only** case that reaches `test_cd06` |

**The finding this produces is more precise than the one it was aimed at, and
less alarming.** `CA-07-DF-05` established that *nothing in that suite would ever
have gone red in either direction*. **That is not true here.** What these nodes
could not notice was the input **not being there at all**.

> **CORRECTED in review, twice, and both corrections are against me.**
>
> **The wall-clock figure is deleted.** This section said *"moved nothing in the
> report but the wall clock, 5.48s to 1.28s"*. Under controlled repetition
> (`evidence/f5-timing.txt`) the module runs **1.28s present vs 1.27s deleted**
> warm, and the three-node list **0.03s vs 0.02s**. `5.48s` was a **cold-cache
> first run** compared against a warm one. **Nothing moved at all — not the
> counts and not the clock — and the vacuity claim is STRONGER without the
> figure**, which is why the figure is gone rather than adjusted.
>
> **And the sentence "these six notice every change to the code and the model
> they cover" was not supported by the table it sat under.** Measured node by
> node, `test_cd06_real_distributed_history_external_matrix_lists_the_next_
> disjuncts` **PASSES under both code mutations** (it asserts an action list, not
> a bound or a cfg invariant) and appears in neither subject-change node list.
> **Five of six were established by execution and the sixth was asserted** — in a
> ticket whose subject is checks that assert more than they establish. A seventh
> case now reaches it (row above), so all six are established.

So the honest reading of clause (e): **the six were real tests with one blind
spot, not six tests that could never fail.** Reporting them as "six passes that
assert nothing" would overstate it, and this ticket exists partly because
overstatement is the recurring failure of this record.

### 3.4 Did any of them go red when made real? **No — and that is the result**

The ticket says a repaired vacuous pass that goes red is the substrate reporting
truthfully for the first time. **None of the six did**, because the inputs are
present at this tree. **They go red only under deletion**, which is where the
battery observes them, and that is the whole content of the repair: the answer to
an absent input moved from PASS to SKIP or FAIL without any figure in the suite
moving.

**Numerator/denominator, stated plainly:** the vacuous-pass population moved
**6 → 0 within `tests/test_analyze_complexity.py`**, with no movement in failed,
passed, skipped, xfailed or collected attributable to it. The class as a whole is
**not** at zero — see §4.

### 3.5 A second sub-shape, found by sweeping for the class instead of the instances

> **CORRECTED in review: I inflated a named sub-shape 2 → 3, in the ticket whose
> subject is population inflation.** This section said the `or True` population
> was **three**. My own stated command at the tree I named returns **two**
> (`grep -rn "or True" tests/` at `8dd0442`). The third row —
> `tests/test_code_complexity.py:856`, `assert value >= 0` — is a **different
> shape**, and my own ledger row said so honestly while this narrative did not.
> **Folding it in was exactly the error `CA-10-DF-14` made in the other
> direction**, and it is worse here because I had the correct statement written
> down one document away.

`grep -rn "or True" tests/` at `8dd0442` returns **two** sites. `X or True` is
`True` for every `X`: **the assertion cannot fail.**

| site | shape | disposition |
|---|---|---|
| `tests/test_score_tools.py:2204` | `assert "R-H6" in … or True` — a **tautology** | **REPAIRED HERE** |
| `tests/test_falsifiable_controls.py:524` | `assert shutil.which("python3") or True` — a **tautology** | **FILED** (`SS-06-DF-01`) |
| `tests/test_code_complexity.py:856` | `assert value >= 0` over counts — **a different, weaker shape**: non-falsifiable by any input the test can produce, but not a tautology | **FILED** (`SS-06-DF-01`), and counted separately |

**The honest statement: `or True` = 2 (one repaired, one filed). Non-falsifiable
assertions across both shapes = 3.** Two numbers, because they are two
populations.

After the six guards and this one line, `tests/` contains **no bare-return guard
and no `or True` assertion** other than the one filed row.

---

## 4. `CA-10-DF-15` — DECIDED: confirmed, and the population is three

Measured at `8dd0442`, unmodified, in a throwaway clone
(`evidence/declared-reds-were-green-8dd0442.txt`):

- Four tests in `tests/` declare themselves red. **Three of the four were
  GREEN**: `test_the_repo_ledger_passes_its_own_audit`, `..._with_rh6`, and —
  **not named by the finding** — `test_the_shipped_rh5_demonstration_still_goes_
  red`. `3 passed in 293.06s`.
- All three cite `RM-06-DF-02`, whose ledger disposition is **`settled`**.
- The fourth, `test_architecture_tags::test_the_same_tag_control_holds`, cites
  `RM-06-DF-01`, which is **`open`**, and it **is** red at base and tip.
- `audit` over this repository: **`0 violation(s)`, exit 0**
  (`evidence/audit-0-violations-8dd0442.txt`).
- The subject row in `specs/results/scorecards/INSTRUMENT-LOG.toml` carries
  `settled_by = "RM-04"`: the stale `ranges`/`tiers_measured` fields were
  **withdrawn** in favour of prose naming the 49-card population they were true
  of, plus an executed assertion. **It was not edited into agreement with the
  record**, which is the objection `RM-06` reverted for.

**Decision, in two halves.**

1. **The three docstrings now say when the violation was settled and by what**,
   which is `CA-10-DF-15`'s own `suggested_fix`. The assertions are untouched;
   only the declarations and their failure messages changed.
2. **The relation is now COMPUTED**, not described:
   `tests/test_declared_reds_cite_an_open_finding.py` requires every test that
   declares itself red to cite at least one finding that is still `open` or
   `carried` in the ledger, using `scripts/disposition.py`'s own vocabulary so it
   cannot drift into a second opinion. It **refuses the three stale declarations
   before the repair and accepts the live one throughout** — a demonstrated
   failing input on a real subject, not a fixture.

**Why the second half, and not just the docstring edit.** The mechanism —
*a declaration of deliberate redness that outlives the red* — survived from
`RM-06` to `CA-10` to here because **nothing computed it**. That is
`planning_rules.consumption_is_changing_what_the_substrate_checks` on a live
example: the finding was routed twice and consumed zero times.

**Stated limit.** The check catches *the finding this declaration rests on was
settled*. It does **not** catch *this test is green for some other reason*.
Establishing that costs a subprocess run of every declared-red test — the `rh5`
one alone is five minutes — and a check nobody can afford to run is a check
nobody runs. The limit is in the module docstring, not discovered later.

Filed as `SS-06-DF-03`.

### 4.1 `CA-10-DF-13` — DECIDED: gone, and not by me

The plan's acceptance asks for `CA-10-DF-13` to be decided on the record and the
issue warns not to chase it as written. **It is not red at my base.**
`tests/test_goal_baseline_is_a_card.py` is collected (29 nodes) and does not
appear in the failure list at `8dd0442`, at the pre-close tip, or post-close.

`SS-03` repaired it, and the repair matches the docstring's own remedy — *"move
the demonstration to another failing goal and say which; do not delete it"* — by
a better route than the one suggested: the demonstration now reads the whole
record keyed by `(workflow, id)` rather than by live-plan lookup, so the subject
is pinned where it actually lives instead of where the live plan happens to point.
The general defect is filed as `SS-03-DF-01`. **Nothing for `SS-06` to do; the
decision is that it was decided elsewhere, and this is stated so `SS-08` does not
find an unexplained absence.**

---

## 5. `SS-02-DF-09` — DECIDED: widen, and the widening is demonstrated

The finding, from an independent reviewer of PR #284 instructed to refute, says
SS-02's two doctrine-boundary guards are **narrower than the claims the PR cited
them for**. My remit was to widen them or to file that they cannot be widened
honestly. **They can, and the evidence is the reviewer's own hypothetical
executed** (`evidence/ss02-df09-seeded-evasion.txt`).

### 5.1 `test_the_check_gates_nothing`

Seeding `scripts/_probe_gate_caller.py` containing
`from score_tools import cmd_absent_input` — the exact evasion the finding names:

```
the guard AS SHIPPED : callers == []           -> PASSES. The evasion is invisible to it.
the guard AS WIDENED : FAILED ... ['scripts/_probe_gate_caller.py']
with the seed removed: 3 passed
```

Widened from one directory and one spelling to **five program surfaces**
(`scripts`, `skill-scripts`, `templates`, `test_graph`, `spec_double_compiler`)
and **three spellings** (`absent-input`, `absent_input`, `cmd_absent_input`).
**Zero hits at this tree**, so the clause now passes for a reason rather than by
construction. `tests/` and `examples/validation/scorecards/` are excluded and the
exclusion is stated in the file: a test referencing the check is the check being
tested, and the second is where it is defined.

It also carries its own absent-input guard: if the walk reads fewer than 50 files
it **refuses** rather than reporting clean, because "swept nothing" and "found
nothing" are different answers.

### 5.2 `test_the_register_is_the_only_thing_the_check_reads`

Widened from `argv` alone to **every path-bearing field `score_tools._absent_stage`
actually reads**: `argv`, `cwd`, every `env` value, `stage.from`, `stage.to`,
`link.from`, `link.to`, `write.file` and every `remove` entry.

> **CORRECTED TWICE in review, and both against me.**
>
> **F7.** The first widening **still missed `stage.from`, `stage.to` and
> `remove`** — all three read by `_absent_stage` (`score_tools.py:4686`,
> `:4721`), and **`SS-02-DF-09` named `stage.from` explicitly.** I widened the
> guard from one field to five while the reviewer's own worked example stayed
> outside it. The field list is now derived from that function's own
> `spec.get(...)` calls, which is the only source that cannot drift from the code.
>
> **F8.** I wrote *"`link.from` … is `.` in three of the six shipped states"*.
> There are **nine** shipped states (three contracted instruments × three), and
> **6 was the link-ENTRY count**: 3 of 6 link entries carry `from = "."`, in 3 of
> the 9 states. Verified by counting the register.

Because a green guard over clean data is exactly the state the narrow version was
in, the discriminating power is **demonstrated rather than assumed**:
`test_the_path_reader_sees_every_field_and_not_only_argv` builds a spec whose
`argv` is impeccable and whose `link.from` is `/Users/someone/their-app`, and
asserts the reader sees it.

### 5.3 What could NOT be widened honestly, stated rather than implied

- A text search cannot see a call assembled at runtime, dispatched through a
  registry, or spelled by a shell fragment. **A clean result is a floor, never a
  proof.**
- `link.from = "."` is legitimately the whole repository in **3 of the register's
  6 link entries** (occurring in 3 of its 9 declared states), so the widened guard
  bounds **absolute and escaping** paths and **cannot bound reach within the
  repository**.
- The clause (NO NEW GATE OVER SUBJECT-PROGRAM CONTENT) therefore still holds
  partly **by inspection**. The reviewer's core point — *it holds, but not
  because these tests establish it* — is now less true, not untrue.

Filed as `SS-06-DF-04`.

---

## 5A. `SS-06-DF-05` — WITHDRAWN AND RESTATED. My diagnosis was refuted by running the check I said could not see it.

> **CORRECTION, review round of PR #286, and it is the most important thing in
> this document.** What follows replaces the section that stood here. The
> DEFECT was real and is repaired; **the CAUSE I published was wrong, and the
> clause I escalated to the epic owner is withdrawn.**
>
> **The sealed `specs/.history/…/ticket-005-SS-06/summary.md` still carries the
> refuted sentence.** `R-H4` forbids editing it, so it is not edited. **A reader
> who trusts that sealed summary over this document will be reading a claim this
> section refutes**, and there is no mechanism in this repository that would tell
> them so — which is itself the shape of `SF-308`.

### What I found, and it stands

`vacuity_probe.py` guarded `--root` with `(root / "tests").is_dir()`, and
`Path.is_dir()` returns `False` on a `PermissionError`. A directory the process
may not READ therefore answered in the EMPTY state's exact words —
*"root is not a checkout of this repository (no tests/ or scripts/)"*. The verdict
was already correct (a refusal, exit 2); the stated **cause** was a fabrication.
A second, smaller one: a case whose subject was absent before mutation exited 1,
the code a *failing* battery uses. **Both repaired, the first pinned by a seeded
mutant** (`evidence/selftest-mutants.txt`, mutant C).

### What I claimed about it, and it is false

I wrote that `SS-02`'s absent-input clause **cannot** see this class "because the
clause is stated on the verdict", that "the mechanism exists and the rule does not
require it", and that "nothing in this repository's doctrine separates them". I
then escalated a proposed doctrine clause to the epic owner.

**All of it is refuted by execution** (`evidence/f1-my-diagnosis-refuted.txt`).
Build a throwaway register entry for the probe and run the **shipped** check:

```
--only vacuity-probe-pre    absent ok   unread ok   empty ok    REFUSED   exit 1
    vacuity-probe-pre ['unreadable','empty'] are INDISTINGUISHABLE … UNDECLARED
--only vacuity-probe-post   absent ok   unread ok   empty ok    SATISFIED exit 0
```

**All three states report `ok` on the verdict and the check refuses anyway, on the
message.** `absent_measure` calls `absent_indistinguishable` unconditionally
(`score_tools.py:4818`, `:4938-4946`); an undeclared collapse becomes a problem and
sets `verdict = REFUSED`. **The substrate already computes exactly the property I
said it could not see.**

And "one sentence in the plan would have caught all three" is refuted by this
epic's own `planning_rules.consumption_is_changing_what_the_substrate_checks`:
**a doctrine line with no instrument is a preference.** I proposed a doctrine line
for a property that already has an instrument — the same error the rule names,
committed by the ticket citing the rule.

### The real cause: REGISTER COVERAGE — and my own cited precedent says so

**`SS-07-DF-08`, the row I cited as my precedent, opens with it:** *"`stranded_
loaders.py` is NOT registered in `instruments.toml`, so `score_tools.py
absent-input` does not sweep it."* Its `suggested_fix` already names the clause the
class needs: *"a NEW instrument shipped by a ticket should be run through
`absent-input` BEFORE it is published … because registration is manual and nothing
notices an unregistered instrument."*

**I read that row, cited it, and then proposed a different clause for a cause it
had already diagnosed correctly.**

And the three-instrument table I published is wrong in the direction that
flattered my claim:

| | instrument | registered? | what the substrate did |
|---|---|---|---|
| `SS-01-DF-04` | the ledger reader inside `scorecard-audit` | **yes** | **The substrate REQUIRED a declaration and got one** — the contract carries an `[[instrument.absent_input.indistinguishable]]` block with a reason. |
| `SS-07-DF-08` | `stranded_loaders.py` | **no** | never swept |
| `SS-06-DF-05` | `vacuity_probe.py` | **no** | never swept |

**One mechanism, yes — but the substrate handled the one instrument it could see,
and the other two were simply never shown to it.** "Nothing in this repository's
doctrine separates them" was a claim about two files nobody had pointed the check
at.

### What is withdrawn, and what replaces it

- **WITHDRAWN:** the proposed clause "declared absent-input states must be
  pairwise distinguishable in their output, or carry an `indistinguishable`
  block". The shipped check already enforces precisely that.
- **RESTATED:** the finding is **register coverage**. An instrument that is not in
  `examples/validation/instruments/instruments.toml` is never swept, registration
  is manual, and nothing notices an unregistered instrument. **The proposal to
  adopt is `SS-07-DF-08`'s existing one**, not a new one of mine.
- **The registration question is the epic owner's**, who has said they will rule
  on it. I did not register `vacuity_probe.py` and I did not touch
  `instruments.toml`.

**Why I got it wrong, stated plainly:** I read `absent_measure`'s clause text and
reasoned about it instead of running it, in a ticket whose entire subject is that
reading a check is not the same as executing it. Every figure in this document that
came from running reproduced; **this one came from reading.**

## 5B. `SS-04-DF-06` — the three reds `SS-04` shipped into a file that is now mine

`schedule_revision 2` moved `tests/test_score_tools.py` into my conflict keys,
because it was assigned to `SS-01`, which is closed, so **no open ticket could
claim it** while `SS-04` was turning three of its tests red. **`SS-04`'s PR #285
was still OPEN when I measured this**, so the three reds are not in my tree and
the edits cannot land in this PR.

**Decided by simulation rather than deferred**: a throwaway clone with
`feature/SS-04` merged into `feature/SS-06` by hand
(`evidence/ss04-df06-three-reds-decided.txt`, patch at
`evidence/ss04-df06-three-edits.patch`).

**Reproduced:** `3 failed, 113 deselected`, exactly the three `SS-04-DF-06`
names. **Every characterisation re-derived from data rather than accepted:**

- 39 lines reach `COUNT-MOVED`; **all 39 are form `P` and all 39 carry
  `dim is None`**; dimension-bound `COUNT-MOVED` lines: **0**.
- The `UNREACHABLE` reason set gained exactly two: `no counted noun` and
  `numerator has no predicate`.
- The failing row in the third is **line 2 of the test's own two-line fixture**
  (`worst 1, 2 of 6 moved in each arm`). Line 1, the movement notation the test
  is *about*, yields nothing before and after. **The fixture asserted more than
  the docstring claimed.**

**Decision: apply all three, none deleted, and one of them strengthened.**

| red | decision |
|---|---|
| (1) census | Apply the minimal edit **plus an assertion that justifies it**. Scoping to non-P is right — `RM-06-DF-03` is about a dimension-bound claim and form P cannot carry a dimension — but narrowing a control to a form label **on trust** is the move `RM-06-DF-01` refuses. The exclusion is now guarded: every `COUNT-MOVED` row is asserted `dim is None` on every run, so a dimension-bound one can never hide behind it. |
| (2) reasons | Apply as written. The requirement is that every reach limit be **named**, the assertion is `<=` over a named set, so **extending** it satisfies the requirement more fully. Shrinking the reason list would be the wrong move and the docstring now says so. |
| (3) fixture | Apply the **stronger** of `SS-04`'s two options: assert the right **answer**, not an absence. The movement line still yields nothing; the counted line is asserted `UNREACHABLE` with its reason named. A test that asserts a whole file yields nothing goes red whenever the recogniser learns anything, correctly or not. |

**Verified:** `3 passed` on the three, and **`116 passed`** over the whole module
in the simulated merge — the same node count as before `SS-04`, so nothing was
deleted to reach green.

**Held rather than applied**, and the reason is not caution: edit (3)
**cannot** land before `SS-04` merges, because without form `P` line 2 of that
fixture yields nothing and asserting it `UNREACHABLE` would go red. Edits (1) and
(2) are harmless without `SS-04` and would land silently. **Applying two of three
would leave the file in a state neither ticket ever measured**, so all three are
held together. Applying them is one commit the moment #285 lands.

---

## 6. Every red, attributed, with the direction named

Seven at the base. Numerator/denominator direction is stated for each.

| red | attribution | mine? |
|---|---|---|
| `test_architecture_tags::test_the_same_tag_control_holds` | **DELIBERATE**, `RM-06-DF-01`, disposition `open`. The control reports a real, unflattering result. **Not repaired**, and the new declared-red check accepts it precisely because its finding is live. | no |
| `test_instrument_demonstrations::test_every_declared_path_exists` | **DECLARED**, `CA-04-DF-04`. Not repaired. In my conflict keys and deliberately left alone. | no |
| `test_instrument_demonstrations::test_every_fast_demonstration_reproduces` | **DECLARED**, `CA-04-DF-04`. Same. | no |
| `test_source_citations[specs/program_model/spec_manifest.yaml]` | inherited: 15 stale line citations in the promoted manifest. | no |
| `test_source_citations[specs/current/spec_manifest.yaml]` | **THE SAME 15 CITATIONS, COPIED.** See §6.1. | see §6.1 |
| `test_source_citations[specs/desired_program_model/spec_manifest.yaml]` | **THE SAME 15 CITATIONS, COPIED.** | see §6.1 |
| `test_ticket_retirement::…matching_close_receipts` | **expected and self-clearing** — planned tickets have no close receipt. Goes green as the epic's tickets close. Not a defect. | no |

### 6.1 The two "scaffold" citation reds are one defect counted three times

The charter attributes these two to *"the scaffold created a manifest whose
citations do not all resolve"*. **Measured:** all three failing manifests report
the **identical 15 stale citations**, byte-for-byte once the path prefix is
stripped (`evidence/source-citations-one-defect-counted-thrice.txt`).

`specs/current/spec_manifest.yaml` and
`specs/desired_program_model/spec_manifest.yaml` are **copies of
`specs/program_model/spec_manifest.yaml`**, which was already red for the same
15. The scaffold did not create a defect; **it replicated one, and the red count
rose by 2 with no new defect behind it.** That is denominator movement — the same
defect became reachable through two more parametrisations — and reading it as
"+2 new reds" is the error `denominator_rule` exists to prevent.

**Not repaired.** The root is `specs/program_model/spec_manifest.yaml`, which is
outside my `implementation_scope` (`tests/`, `examples/validation/`, `scripts/`,
`specs/results/scorecards/stabilize-substrate/`) and outside my conflict keys.
Repairing the two copies without the root would leave the record with one red and
two green rows for one unfixed defect, which is worse than three honest reds.
**The substrate already checks this** — `test_source_citations` is doing exactly
its job — so there is no class to consume, only an unfixed defect to name.

---

## 7. Findings filed

Five rows appended to `specs/deferred_findings.yaml`; the ledger goes 334 → 339
rows and nothing was rewritten, reordered or removed.

| id | what | disposition |
|---|---|---|
| `SS-06-DF-01` | a SECOND sub-shape of `CA-10-DF-14`: the tautological assertion `X or True`, two instances outside my keys | `carried` → `SS-05` |
| `SS-06-DF-02` | **my own instrument read its subject's prose as its subject's result** — `summarise` grepped the whole pytest report and published `3 failed, 3 passed` for a three-node run | `repaired`, mutant-demonstrated |
| `SS-06-DF-03` | `CA-10-DF-15` confirmed; population is three, not two; cause is `RM-06-DF-02` settled by `RM-04` with the declarations left standing | `repaired` |
| `SS-06-DF-04` | `SS-02-DF-09` adjudicated: both guards widened, evasion executed, residual limit stated | `repaired` |
| `SS-06-DF-05` | **"I was not allowed to look" reported as "there is nothing there"**, in this ticket's own instrument. **Defect real; my stated CAUSE refuted in review** — the shipped check DOES compute it and the real cause is register coverage, which `SS-07-DF-08` had already diagnosed. §5A | `repaired`; **the escalated clause is WITHDRAWN** |
| `SS-06-DF-06` | **the declared-red check could not tell a declaration from a QUOTATION of one** — a time bomb that went red exactly when the next ticket disposed `CA-10-DF-15`. Third instance of `SS-06-DF-02`'s class, in the check written to police the class | `repaired`, structurally, pinned both ways |
| `SS-06-DF-07` | **my repair for `SS-06-DF-05` committed `SS-06-DF-05`'s mechanism** — deleting only `specs/current/MC.cfg` turned `2 failed, 1 passed` into `3 skipped` saying *"no spec workflow is open"* while one was. Fourth instance in this ticket | `repaired` |

`scripts/disposition.py --ledger specs/deferred_findings.yaml --ticket SS-06` →
`DISPOSED ticket SS-06: 5 findings, all three clauses hold`, exit 0.

### 7.0 Four instances of ONE mechanism, all in this ticket's own work

The reviewer's summary of me is the finding: **every figure I produced by running
re-derived exactly, and every figure I produced by reading rather than running is
wrong.** The same split runs through the findings:

| # | where | what it read as what |
|---:|---|---|
| `DF-02` | my census | `pytest`'s echoed source read as `pytest`'s result |
| `DF-05` | my instrument | `PermissionError` read as "nothing there" |
| `DF-06` | my new check | a **quotation** of a declaration read as a declaration |
| `DF-07` | my repair for `DF-05` | one missing file read as "no workflow is open" |

**Four recognisers, four times reading a subject's surface as the subject's state,
in the ticket whose whole subject is that.** `DF-06` and `DF-07` were found by the
reviewer, not by me — and `DF-07` in particular only surfaced because they deleted
a *different file* than the one I tested with.

### 7.1 `SS-06-DF-02` is the one worth reading

I wrote an instrument whose whole purpose is to find checks that cannot fail, and
**within the hour it shipped a recogniser that read a figure out of the text it
was quoting.** `pytest` echoes the source of a failing assertion; the helper I had
just repaired contains the string `` `3 passed` either way `` in its docstring;
the census printed `3 failed, 3 passed` for a run of **three** nodes.

**The only reason it was caught is that the wrong answer was arithmetically
impossible.** A plausible wrong number would have shipped, and it is the same
class as `CA-08-DF-01` — a recogniser bound by the form of the text it sweeps —
seen from the other side.

---

## 8. What I could not do, and what I chose not to do

1. **Conflict keys, stated at BOTH schedule revisions rather than only the
   convenient one.** I edited `tests/test_score_tools.py` (`CA-10-DF-15`, routed
   to me to decide) while it was **outside** my keys — it was assigned to `SS-01`,
   which is closed, so no open ticket could claim it. **`schedule_revision 2`
   moved it INTO my keys**, after the `SS-04` review found the same gap. The edit
   was out-of-key when made and is in-key now; both are true and both are
   recorded. It is docstrings, failure messages and one `or True`; **the
   assertions are untouched.**
   `tests/test_absent_input_demonstrations.py` (`SS-02-DF-09`, also routed to me)
   is `SS-02`'s key and is **still outside mine at revision 2**; `SS-02`'s PR #284
   is merged, so no concurrent owner holds it.
   `tests/test_declared_reds_cite_an_open_finding.py` is new and collides with
   nobody. **`examples/validation/scorecards/score_tools.py` was not touched**:
   `SS-04` owns it and its defects are deferred, not fixed. **I did not touch
   `examples/validation/instruments/instruments.toml`**, so revision 2's new
   shared-append rule does not apply to this PR.
2. **I did not repair the `test_source_citations` reds** (§6.1), the deliberate
   reds, the declared `CA-04-DF-04` demonstrations, or anything in
   `score_tools.py`.
3. **I did not repair the two remaining `or True` sites**, though each is a
   one-line edit. The reason is the deferment policy, not difficulty, and
   `SS-06-DF-01` says so.
4. **`run tlc` does not exist.** `run` accepts only `spec-unit-tests` and
   `effect-conformance` — verified at this tree. Reported `N/A`, not substituted.
5. **`python3 examples/validation/scorecards/score_tools.py audit` cannot run
   under the system interpreter here** — Python 3.10, and `score_tools.py`
   imports `tomllib` (3.11+). The declared local signal was run as
   `uv run --with pyyaml python examples/validation/scorecards/score_tools.py
   audit`, which is the same program on a 3.14 interpreter; the substitution is
   in the interpreter, not the command, and it is disclosed rather than silently
   made.
6. **The vacuous-pass class is not closed at six.** §3.5 and `SS-06-DF-01`.
7. **`score_tools.py index` was never invoked** by this ticket. `SS-07-DF-01`
   says it mutates `INDEX.md` in 16 of 18 sealed trees; `git status` is clean of
   any `INDEX.md` in this branch.
8. **Two files in this PR are `close ticket` PRODUCTS, not edits of mine, and
   both are outside my conflict keys** (disclosed after review, F9):
   `specs/results/complexity_ledger.json` (written by the close) and
   `specs/results/skill_feedback.md` (the close appends the entry; I filled in
   its `feedback_status` and added `SF-308`/`SF-309`). Every ticket in this epic
   writes both, and neither is in any ticket's keys — the same unpartitioned-
   surface shape `schedule_revision 2` recorded for `instruments.toml`.
9. **I did not register `vacuity_probe.py`** in
   `examples/validation/instruments/instruments.toml` and did not touch that
   file. §5A: the registration question is the epic owner's and they have said
   they will rule on it.
10. **The sealed `summary.md` carries a claim §5A refutes**, and `R-H4` forbids
    editing it. Stated here because nothing in the substrate would tell a reader
    otherwise.
