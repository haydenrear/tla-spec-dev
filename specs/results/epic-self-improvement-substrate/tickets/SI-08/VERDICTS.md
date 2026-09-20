# SI-08 — Evaluation A: the frozen reading

**Base `2131cdad`, measured 2026-09-20, worktree `../wt-341-evaluation`,
branch `feature/341-evaluation`.**

**This ticket owns FOUR goals and measured exactly those four.**
`GOAL-epic-owns-the-model`, `GOAL-no-new-gates`, `GOAL-progressive-disclosure`
and `GOAL-evals-one-command` moved to SI-23 at schedule revision 4 and were
**not measured here** — an evaluation ticket cannot honestly decide a goal that
later tickets keep changing.

**This is Evaluation A: a frozen reading.** SI-23 re-reads these four beside its
six so each delta can be attributed. These numbers are the counterfactual half
of every clause in that comparison.

## One verdict per clause

| goal | clause | baseline | measured | verdict |
|---|---|---|---|---|
| **one-unit** | 1 — one unit, zero standalone copies in root **or** project | 6 units across 6 repos in every home | project: **0** dup dirs, **0** dup records, plugin installed. root: **8** dup dirs, **8** dup records, **no** plugin | **NOT MET** (project met; root unchanged from baseline) |
| **one-unit** | 2 — every listed graph and eval case green | — | graphs **3/3 green**; eval half names a population that no longer exists (61 cases, 6 undecidable by construction, 0 scored before today) | **SPLIT**: graphs **MET**; eval cases **UNDECIDED** |
| **one-unit** | 3 — change-managed unit | — | git source, `errors: []`, no `NEEDS_GIT_MIGRATION`, `skt check` offers the update | **MET** (sync verified by detection, not execution) |
| **findings-become-changes** | 0 `recorded-local` at close | 13 | **0** (and 0 under both the partial and full read) | **MET** |
| **findings-become-changes** | every finding carries a `skill_change` | 0 in backlogs; 39 rows without | **19 of 121** parseable; **94 absent**, **8 malformed** — and the 121 is itself short by **16**, because the ledger never reads the per-ticket partition the epic told its tickets to file into (`SI-08-DF-11`) | **NOT MET** |
| **findings-become-changes** | applied / declined-with-reason / not-a-skill | — | **9 terminal** (5 applied, 4 declined); 10 `proposed`; **45 `pending`** | **NOT MET** |
| **blockers-propose** | the card runs | no instrument exists | 4 blind judges, 2 subjects, 4 usable cards, 0 failures | **MET** |
| **blockers-propose** | two judges agree within 1 | — | max spread **1** (1 of 10 pairs), **0** elsewhere | **MET** |
| **blockers-propose** | discriminates proposer vs non-proposer | — | **I2 = 2 on all four cards**; only I1 moves (+0.5) | **NOT MET** |
| **pinned-eval-toolchain** | ref pinned in the repo, not the home | 0 pinned; `main` moving | 2 units pinned by 40-hex commit, `verified_head == pinned`; ambient home already diverged (`0f380781` vs pinned `286a3694`) | **MET** |
| **pinned-eval-toolchain** | runner asks, refuses to guess | nothing asks | refusal **exercised** (exit 1); override **exercised** and recorded as an override | **MET** (tty branch read, not executed) |
| **pinned-eval-toolchain** | every full-suite run records the ref | 0 of N; `evals/results/` absent | **1 of 1** — this ticket ran the suite's first scored case | **MET for the one run**, with three limits |

Full workings, with the instrument the plan names for each goal, are in
`../../goals/<GOAL>/SI-08-EVALUATION-A.md`.

## Regression baseline — by NAME, not by count

`uv run --python 3.12 --with pytest --with pyyaml --with jinja2 --with hypothesis python -m pytest tests -q --ignore=tests/test_score_tools.py`
→ **10 failed, 1690 passed, 7 skipped in 364.68s.**

The ten failures are **exactly** the ten the work order names as known, matched
1:1 by name. **No failure was added and none was fixed:**

```
test_architecture_tags::test_the_same_tag_control_holds
test_corpus_diagnostics::test_cli_passes_on_the_committed_example_corpus
test_example_drivers_write_inside_spec_tree::test_a_validation_run_does_not_generate_over_a_committed_corpus
test_instrument_demonstrations::test_every_fast_demonstration_reproduces
test_negative_corpus_adapter_conformance::test_the_negative_corpus_names_its_arguments_as_the_committed_corpus_does
test_source_citations::test_every_line_citation_resolves_to_the_line_it_cites   [3 params]
test_ticket_retirement::test_repository_canonical_delivered_plan_has_matching_close_receipts
test_verdict_schema::test_the_corpus_gate_states_its_verdict_as_data
```

Full output: `baseline-pytest.txt`.

Running the graphs dirtied four committed `case_coverage.json` files under
`examples/effect_providers/` — which is the behaviour
`test_example_drivers_write_inside_spec_tree` exists to catch. They were
reverted, not committed; this ticket adds no behavioural delta.

## Test graphs — via the skill runner

`python3 skills/test-graph/scripts/run.py <graph>`, which **does** run (the bare
`cd test_graph && ./gradlew` path is the one that fails, and it was not used):

| graph | result |
|---|---|
| `specWorkflow` | **BUILD SUCCESSFUL**, rc 0, 1m20s |
| `cliWorkflow` | **BUILD SUCCESSFUL**, rc 0, 10s, 2/2 steps |
| `effectProviderExamples` | **BUILD SUCCESSFUL**, rc 0, 1m11s |

## The front door: which case was I in

**The `skt` front door resolved and then FAILED**, so the by-hand fallback was
reached and this says which case that was. `skt ticket new SI-08 --base 2131cdad
--path ../wt-341-evaluation` printed *"error: bootstrap-home.sh not found in this
home; worktree rolled back"* and created nothing — **tested by PATH, not by exit
code**, which through a pipe was 0.

Root-caused to one line: `skt/src/skt/ticket.py:150` resolves
`<home>/skills/git-issue-workflow/scripts/bootstrap-home.sh` and never looks in
`<home>/plugins/*/skills/`. The project home HAS the script — inside the
`tla-spec-dev` plugin. **The migration this epic performed is what broke the
front door.** Filed as `SI-08-DF-03`; fallback `git worktree add -b
feature/341-evaluation ../wt-341-evaluation 2131cdad` succeeded.

Consequence: **this worktree has no per-checkout Skill Manager home**, because
the command that creates one is the command that failed. `skill-manager home
close-out --home <worktree>/.skill-manager` has **no home to close out** and was
not run. Nothing in this PR touches any home.

## Traps checked

| trap | result |
|---|---|
| a case declaring `plugins:` silently loses hooks while both arms score 1.00 | **clean** — all 61 cases declare **0** `plugins:` blocks |
| `skt sync` exits 11 on two malformed eval fixtures — not a broken home | **honoured** — no reinstall attempted; `skt check` used instead of `skt sync` |
| the test graphs DO run via the skill runner | **confirmed** — 3/3 green |

## What I could NOT verify — stated as unverified

1. **`skt sync` actually applying an update.** Verified by *detection* only
   (`skt check` names the newer version and the command). Executing it would
   mutate the project home mid-measurement, which the work order forbids.
2. **The interactive ask in `evals/run.sh`.** Gated on `[ -t 0 ]`; every run here
   was non-interactive. The no-tty, override and refusal branches were executed;
   the tty branch was read.
3. **That a pinned ref MOVES a score.** One run at one ref. Two refs would cost
   ~$1.08 and were not run.
4. **60 of the 61 eval cases.** One case was scored. The suite's "0% pass rate"
   is a sample of one and should not be quoted.
5. **Whether the improvement card discriminates on a genuine non-reporter.** The
   negative-control subject turned out to report its blockers outside the
   designated section, so the pair does not settle it. The card's own
   redaction-pair non-vacuity check was **not** run.
6. **The judges' cost.** `claude --safe-mode -p` prints no cost line; no figure
   is available and none is invented.
7. **Citation resolvability inside the judge cells.** By construction the cells
   cannot open the subjects' paths, so citations were checked as present and
   well-formed, not as resolving.
8. **`tests/test_score_tools.py`** — see the note below.

## Bug attribution

Every defect this ticket recorded happened outside any modelled action of this
repository's program model. Anchors, per `references/bug_attribution.md`:

- `SI-08-DF-03` (front door) — **`UNMODELED/skt-cli`**. The model does not cover
  the skt plugin's home resolution; what it would have to gain is an action for
  "resolve a unit's script from a home", which today has no representation.
- `SI-08-DF-01`, `SI-08-DF-05`, `SI-08-DF-06`, `SI-08-DF-08`, `SI-08-DF-11` —
  **`UNMODELED/evals-harness`**. The eval harness and the ledger are
  instruments, not modelled program behaviour.
- `SI-08-DF-02`, `SI-08-DF-04`, `SI-08-DF-07`, `SI-08-DF-09` —
  **`UNMODELED/plan`**. Plan, target and operator-home facts; no action covers
  them and it is not obvious the model should.
- `SI-08-DF-10` — **`UNMODELED/docs`**.

Nothing gates on this section.
