# CA-03 — repository suite, measured end to end

**Command — this one, not `README.md:35`, which omits `--with pyyaml` and yields
12 phantom reds:**

```bash
uv run --with pytest --with pyyaml -m pytest tests -q
```

**Measured at `f221496`** (the tree with the work, the spec close and all
evidence except this file), in the CA-03 worktree. Raw output: `suite-raw.txt`.

```
6 failed, 1525 passed in 1250.46s (0:20:50)
```

**Baseline is 6.** The epic-base figure of 7 in
`GOAL-four-results-stand/baseline.md` includes
`test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer`,
which **CA-02 deleted with its subject** — `tests/test_price_removal.py` no
longer exists at this tree. `denominator_rule`: **the numerator fell because the
assertion left the suite, not because the tree changed to satisfy it.**

## Item for item, no more and no less

| red | cause | verdict |
|---|---|---|
| `test_architecture_tags.py::test_the_same_tag_control_holds` | `RM-06-DF-01` | **DELIBERATE**, not repaired |
| `test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` | inherited, not repaired |
| `test_source_citations.py::…[specs/current/spec_manifest.yaml]` | inherited, undeclared | not repaired |
| `test_source_citations.py::…[specs/desired_program_model/spec_manifest.yaml]` | inherited, undeclared | not repaired |
| `test_source_citations.py::…[specs/program_model/spec_manifest.yaml]` | inherited, undeclared | not repaired |
| `test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts` | inherited, undeclared | not repaired |

**ZERO reds attributable to CA-03. Zero baseline reds repaired, silently or
otherwise.**

## A measurement the run itself produced

**`examples/validation/scorecards/subjects.toml` is byte-unchanged after the
full suite:**

```
$ git status --porcelain
?? specs/results/scorecards/cut-the-apparatus/CA-03/suite-raw.txt
```

That matters because CA-03's repair makes `scaffold` **write** to that file, and
`tests/test_architecture_tags.py:548` and several tests in
`tests/test_score_tools.py` scaffold with `--subject` into temporary
directories. The scorecard-root guard is what stops 1,525 passing tests from
appending junk into the declaration file for every sealed card. **Measured over
the whole suite rather than argued from the code.**

## Spec unit

```bash
python3 -m scripts.tla_spec_dev --spec-root specs run spec-unit-tests
```

```
1 failed, 68 passed in 18.78s
FAILED specs/current/tests/test_current_ticket_workflow.py::test_current_ticket_workflow_scaffold_points_to_desired_plan
  AssertionError: current manifest active_ticket 'PA-01' is not present in the desired ticket plan
```

**Inherited `CA-01-DF-02`, and the identical figure CA-05 reported.** Proven
inherited rather than asserted: `git show 4302082:specs/current/spec_manifest.yaml`
already reads `active_ticket: PA-01`, byte-identical to this tree.

**Read the validator's output, not its exit code** — exit 1 is this inherited
red, not CA-03's.

`--ticket CA-03` is not runnable after close: `close ticket` promotes
`specs/tickets/CA-03/desired` into `specs/current` and moves the ticket into
`specs/.history/cut-the-apparatus-epic/ticket-002-CA-03`, so the ticket-local
target no longer exists. The repository-level run above covers the same tests.

## TLC

**N/A.** `model_delta_expectation: none expected`, and none occurred: the
ticket's `current` and `desired` were byte-identical at close (`diff -rq`
clean), and the complexity ledger recorded `delta: direction=zero (vs CA-02)`.

## Home close-out

```
✓ …/wt-epic-cut-the-apparatus-CA-03/.skill-manager holds nothing that removing
  it would destroy
```

Exit 0. The run also prints six `! reconcile` warnings about missing `slm-agent`
and `tracer-agent` projections in the **operator's global** home, each advising
`skill-manager sync`. **Pre-existing, not this worktree's, and NOT run** — the
charter forbids it and the epic deliberately holds 11 units stale for its
duration.
