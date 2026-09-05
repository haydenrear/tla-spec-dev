# agent_integration — the two roles, as real agents

Every other example here validates the toolchain by **calling** it. This one
validates it by **handing it to an agent and watching**, because there is one
defect class the others structurally cannot see.

`E-09` is that class. The whole bug-attribution apparatus — the doctrine, the
matrix, the channel vocabulary, the conservation rule — existed, was correct,
was tested, and was **invisible**, because nothing in the always-loaded entry
point referred to it. Every unit test was green. Every unit test would stay
green. The rule was written down and no agent would ever reach it.

No assertion over the repository can be red for that. An agent can.

## The two roles

They are not two runs of one thing. They are the two seats this workflow
actually has, and they have different privileges and different failure modes.

| | epic | ticket |
|---|---|---|
| tier | project | worktree |
| owns | the plan | one ticket out of a plan it did not write |
| may | dispatch, close the epic, **write the matrix** | implement, close its ticket |
| must not | implement | edit the matrix |
| predicted cost | cheap scaffold, uncertain plan discovery | expensive — `T2` measured four sequential refusals on a real close |

Each gets a **full Skill Manager home of its own**, cloned at its own tier, so
`tla-spec-dev`, `tlc2`, `pytest` and `jinja2` are that home's wrappers — the
ones with its absolute path baked into the body. An agent run against the
operator's PATH is running a different toolchain than the one under test
(`references/runtime_requirements.md`).

## Running it

```bash
python3 examples/agent_integration/run_agent_integration.py --fresh-evidence
```

Real agents, real money, up to ~90 minutes. Useful flags:

```bash
--role epic              # one seat only
--budget-seconds 150     # smoke the plumbing against a real agent, cheaply
--plumbing-only          # homes + workspace + done_checks, no agent at all
--workspace-root DIR     # default: a temp dir OUTSIDE this repository
--keep-homes             # keep the ~700MB home clones for debugging
```

`--plumbing-only` is the negative control and it is worth running first: both
`done_check`s must **FAIL**, because nothing has been done. A `done_check` that
passes with no agent is measuring nothing.

## What it measures, and what it refuses to measure

The agent's own summary is not evidence. An agent that hit four refusals and
recovered writes "done". So the harness reads four things it can see for itself:

- **`done_check`** — a shell predicate over the workspace, run by the harness,
  **never shown to the agent and never named in the ask**. An agent that knows
  the check can satisfy the check.
- **tool errors** — every `is_error` result in the transcript, paired back to
  the call that produced it. This is where refusals live.
- **the fixture's own tests** — green before, re-run after. An agent that
  modeled the program by breaking it has not modeled it.
- **the workspace's git state** — what landed, against what the agent said.

### The ask never names the answer

A role's `ask` names no flag, no file, and no verb. What the agent has to
discover *is* the measurement, and an ask that supplies it has measured
nothing. Same discipline as `examples/validation/agent_rounds/tasks.toml`.

### Errors are classified by the command, not the message

A failed call is `toolchain` only when the call itself **invoked** the thing
under test, and `shell` otherwise. Classified by the executable rather than by
the output text — a message-based rule reads whatever words happen to be there
and drifts toward matching the findings already known, which is `MF-020` with
extra steps. The `shell` errors are kept and visible. They are just not called
defects.

**By the executable, not by any substring**, and that distinction was learned
the expensive way. The first version matched `skill-manager` and `test_graph`
anywhere in the command, and on this repository's own committed evidence it was
**75% wrong**: three of four "toolchain" errors were
`E=.skill-manager/skills/…; cat $E/a; cat $E/b` — a failed `cat` whose *path*
carried the token. Its unit test passed because the negative input chosen for it
was a cat chain with no toolchain-shaped path in it, while the real failing
input sat in `evidence/runs/round-001/` unused. **False positives are how an
instrument gets switched off**, and an instrument that over-claims on its own
front page is the one thing this harness may not be.

### The checks look on every branch, because the workflow uses branches

Round 1 recorded the epic seat as `done_check=FAIL` while the agent had in fact
produced a complete, validating `ticket_plan.yaml` with three scheduled tickets
— on `epic/shortlink-spec`, in its own worktree, which is exactly what
`git-epic-workflow` tells an epic agent to do. The check looked at the working
directory and reported the absence of a file three commits away on another ref.

**A measurement taken on the wrong fixture is not a refutation; it is a void
run**, and the harness owned the error. Round 2 reached the same conclusion
about `T1` and withdrew its number rather than reporting it. So both predicates
now scan `refs/heads` as well as the worktree, and both **say where they found
it** — a bare exit 0 leaves a reader unable to tell a real pass from a check
that stopped looking.

The same fix has a second half: the ticket worktree branches from **whichever
ref carries the plan**, preferring `epic/*`. Round 1 branched it from `main`,
so any refusal the ticket agent hit while looking for a plan that was not there
would have been recorded against the toolchain. (It found the epic tip anyway,
moved its own branch onto it, and got on with the ticket — which is a fact about
that agent, not a reason to leave the harness wrong.)

### The attribution probe checks the shape, not the answer

`SKILL.md` step 13 tells a closing agent to name `<Module>.<Action>`, or
`UNMODELED/<bin>`. The probe asks only whether that **shape** appears anywhere
in what the agent produced. It does not check the naming is correct: fitting a
recogniser to a known answer is `MF-020`, and this project has refused it three
times. **A run with zero occurrences is `UNDECIDED`, not a failure**, and round 001 is
why that sentence is here. It read zero in both seats, and the obvious
conclusion — `E-09` recurring — does not survive reading step 13: every clause
is scoped to regressions and to cases the agent wrote, and the ticket agent hit
zero regressions. Producing no anchor was correct. Read the number against what
the agent actually hit, or this probe over-claims on exactly the axis the rest
of the harness is built to police.

## The fixture

`fixture/shortlink.py` is a link shortener with reservations, claims, releases
and resolution. It is deliberately small and deliberately not a CRUD toy: a
claimed slug can be released and re-reserved by a **different** owner, but never
while the first owner holds it. That property is false of any single state and
true only over a trace, so a spec that captures it has to model the transition
rather than the shape.

**The harness does not check whether `release` was modeled, and that is a
choice.** A recogniser for one expected action name is `MF-020` — fitting a
detector to a known answer — and this project has refused that three times.
Whether the agent found the property is read out of the workspace afterwards, by
a person, which is a `reading` channel and is recorded as one. The earlier
version of this sentence said the harness could see it; nothing in the harness
ever could.

## Known limitation: the launch is hand-bound

`references/runtime_requirements.md` says to launch through the home's
`bin/launch/claude` shim or `skill-manager exec`. **That path does not start a
session**, and this harness measured it:

```
$ skill-manager exec --home ~/.skill-manager -- claude -p "say OK"
Not logged in · Please run /login          (terminal_reason: api_error)
```

That is the **root** home, whose config dir resolves to the operator's own
`~/.claude`, so it is not the per-home config redirect. The same prompt without
`exec` completes; it completes again with `SKILL_MANAGER_HOME` and `PATH` bound
to the same home by hand. Measured on skill-manager 0.25.1 / claude 2.1.258 with
keychain OAuth; an `ANTHROPIC_API_KEY` launch passes its key through the
environment and would not see it.

So `dispatch()` binds the home explicitly, and does the one thing the docs warn
hand-exporting forgets: **every other home's `bin/` is removed from `PATH`**,
not merely this home's prepended. `CLAUDE_CONFIG_DIR` is left alone. The cost,
stated rather than glossed: the CLI wrappers come from the tier's home (the
isolation that reference actually argues for), while the skill and plugin bytes
come from the operator's agent config. `skt` loads, and its report is produced
by this home's `skt`.

Re-measure before removing this note. The finding is a fact about two versions,
not a permanent property.

## Evidence

`evidence/runs/<run-id>/` — never overwritten, which is why `--fresh-evidence`
is required:

```
RESULT.json          every phase, both roles, machine-readable
epic/ ticket/
  ask.txt            what the agent was actually given
  command.txt        the launch, and why it is shaped that way
  stream.jsonl       the full transcript, every tool call and result
  stderr.txt
  done_check.txt     the predicate, its exit code, its output
```
