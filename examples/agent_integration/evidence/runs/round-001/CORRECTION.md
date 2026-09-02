# round-001: the epic seat's `done_check=FAIL` is the harness's error, not a result

`RESULT.json` in this directory records `failed_roles: ["epic"]`. **Do not read
that as the epic agent failing.** It is kept unedited because the record of a
run is not something to rewrite, and this file is the correction that travels
with it.

## What actually happened

The epic agent produced, in 1848s of a 2400s budget, for $16.26:

* `specs/program_model` with 13 Internal and 13 mirrored External actions,
  including `Release` — the transition-only property the fixture exists to
  test, which cannot be seen in any single state;
* TLC green on both configs, 111 distinct states each;
* 112 generated spec-unit cases, green against the real `Shortener`;
* 112 exported Test Graph traces, channel gate passed;
* a scaffolded `test_graph/` project with the `shortlinkExternal` graph composed;
* and on `epic/shortlink-spec`, in its own worktree, a validating
  `ticket_plan.yaml` with three scheduled tickets and a rendered issue body for
  the first one.

The fixture's own four tests were untouched and green afterwards.

## Why the check said FAIL

It looked in the working directory. `git-epic-workflow` tells an epic agent to
work on `epic/<slug>` in its own worktree, and that is exactly what this one
did. The plan was three commits away on another ref:

```
$ git show epic/shortlink-spec:specs/desired_program_model/ticket_plan.yaml
# Canonical plan for epic shortlink-spec (git-epic-workflow) ...
```

**A measurement taken on the wrong fixture is not a refutation; it is a void
run.** Round 2 of this project reached the same conclusion about `T1` and
withdrew its headline number rather than reporting it. The same applies here,
and the harness owns the error.

Filed as `H-01`. Both `done_check`s now scan `refs/heads` as well as the
worktree and report **where** they found what they found; the ticket worktree
branches from whichever ref carries the plan. Pinned in
`tests/test_agent_integration_harness.py`, using this run's own workspace as
the demonstrated failing input. Re-run against the corrected predicate, this
workspace returns:

```
plan found at: epic/shortlink-spec
exit 0
```

## The ticket seat, which the harness got right

`done_check=PASS`, 806s of a 3000s budget, $8.65, **zero toolchain refusals**,
fixture still green. It branched its own worktree onto the epic tip, opened
SL-1, implemented a CLI channel, closed the ticket through the equality gate,
and promoted into `specs/current`.

`T2` predicted this seat was the most expensive operation in the toolchain —
*"EXPENSIVE, 4+ round trips ... three sequential ledger refusals plus F-02's
plan-status refusal"*. **Measured: zero.** See the matrix for what that does and
does not license.
