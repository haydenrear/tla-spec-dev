# round-001: the epic seat's `done_check=FAIL` is the harness's error, not a result

`RESULT.json` in this directory records `failed_roles: ["epic"]`. **Do not read
that as the epic agent failing.** It is kept unedited because the record of a
run is not something to rewrite, and this file is the correction that travels
with it.

## A second correction, from the review of PR #317

Three claims in the first version of this file were wrong, and they are left
above/below as written with the corrections here — a record that is edited to
look right afterwards is not a record.

**1. The fixture's docstring lied, and it steered this run.** `shortlink.py`
opened *"A link shortener with expiry and a reservation window … a reservation
must be claimed before it expires."* **There is no expiry in that file.** The
epic agent read it and built its epic around implementing "the reservation
window the module docstring promises" — a logical clock, per-slug deadlines,
`Tick`, `ClaimRefusedExpired`. So the three-ticket plan below is partly a plan
to specify behaviour the program does not have, and **this round did not measure
what the example says it measures**: whether an agent finds the trace-only
`release` property without being told where to look. It was told to look
somewhere else. The docstring is fixed and pinned; the epic seat should be
re-run before its result is cited again.

**2. "0 toolchain refusals" was wrong. It is 1.** The classifier matched
`skill-manager` and `test_graph` as substrings anywhere in a command, so three
of the epic seat's four "toolchain" errors were a failed `cat` of a skill's own
files. Re-classified by the executable, this run is **2 toolchain / 5 shell**,
and of the two, one is a genuine refusal — `new-uv-node.py` rejecting
`shortlink.external_cases` with *"node id must be dotted lowercase segments"*,
which it is (filed as `G-08`) — and one is the agent running a real script from
a drifted working directory. The corrected reading is pinned by
`test_the_committed_evidence_reclassifies_the_way_the_record_says`.

**3. The numbers below came from the agent's closing message**, which
`dispatch()`'s own docstring says is the one thing this harness must not trust.
They are now read off the workspace instead, and they hold:

| claim | harness-side source | reads |
|---|---|---|
| 13 Internal + 13 mirrored External actions | `grep -c` on `specs/program_model/actions.yml` | **26** |
| 112 spec-unit cases | `grep -c 'StateGraphCase('` | **112** (and 112 external) |
| 112 exported traces | `find … -path '*traces/*.json' \| wc -l` | **113** = 112 + `manifest.json` |
| TLC green, 111 distinct states | `specs/results/program_model/tlc-internal.txt` | **111 distinct, 0 left on queue** |
| spec-unit cases green | same directory, `spec-unit.txt` | *"spec-unit validation passed for 1 target(s)"* |

`workspace_state()` now captures all five on every run, so the next write-up has
a source that is not the transcript.

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
