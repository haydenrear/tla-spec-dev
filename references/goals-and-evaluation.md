# Goals and evaluation

An epic exists to move something measurable. Tickets that only reference their
own slice optimize local correctness and leave the epic's actual outcome
unmeasured — every ticket passes, the epic ships, and nobody can say whether the
thing got faster, more accurate, or more reliable.

The fix is one primitive: an epic declares **goals**, one or more terminal
**evaluation tickets** own the harness that decides them, and **every ticket
declares how it relates to at least one goal**. That relation is load-bearing
context: it tells the ticket agent what result its change is supposed to
produce, which cheap local signal predicts it, and which final measurement it
will be judged by.

Goals are agreed with the user at epic creation, alongside the deferment policy
(`deferment.md`). Do not infer them from the codebase and do not default them.

## What counts as a goal

A goal is a specific, falsifiable claim about the program after the epic, with
a command that decides it. Write goals as outcomes, not as work.

| Not a goal | Goal |
| --- | --- |
| "Refactor the ingest path" | "p99 ingest latency ≤ 250ms at 5k rps, throughput not regressed" |
| "Improve retrieval" | "Answer-match eval ≥ 0.82 on `evals/retrieval_v3.jsonl`, from 0.71" |
| "Add integration tests" | "The `epicIntegration` graph passes end to end with no skipped nodes" |

Goal kinds:

- **`perf`** — latency, throughput, memory, cost; needs a baseline run and a
  target expressed against it.
- **`eval`** — accuracy/quality on a fixed dataset with a scoring harness; needs
  a pinned dataset and scorer version.
- **`integration`** — a named end-to-end Test Graph or system path passing under
  realistic composition, not per-ticket units.
- **`quality`** — an invariant/coverage/robustness property with a deciding
  command (TLC model, fuzz budget, conformance suite).

Every goal names one deciding command. A goal nobody can run is a slogan; either
find the harness, schedule a wave-1 ticket that builds it, or drop the goal.

## Ask the user at epic creation

Ask before scaffolding the workflow, and ask concretely:

> What should be measurably better when this epic is done? For each outcome I
> need: the metric, the command that measures it, its value today, and the
> threshold that counts as success. If a harness does not exist yet, I will
> schedule a wave-1 ticket to build it and measure the baseline before the
> tickets that change behavior.
>
> I will add a final evaluation ticket that runs those measurements on the
> integrated epic branch, and every other ticket will declare how it moves each
> metric so its agent knows what result it is aiming at.

Push back on unmeasurable answers once, offering the nearest measurable form.
If the user genuinely has no measurable outcome (pure refactor, docs, plumbing),
record that decision explicitly rather than inventing a metric:

```yaml
epic_goals: []
goals_waived: "<user's reason: no behavioral delta; correctness held by existing suites>"
```

The validator warns on a waived or missing goal set; it does not block. A waived
epic still runs its normal ticket validation matrices.

## Baselines

A target without a baseline cannot be evaluated — "p99 ≤ 250ms" is unfalsifiable
if nobody knows today's number.

- **Harness exists** — measure at epic kickoff on the freshly created epic
  branch, before any ticket lands. Commit the measurement under the epic
  evidence root and record its value and commit SHA in the goal.
- **Harness does not exist** — schedule a wave-1 ticket whose slice is the
  harness plus the baseline run. Every behavior-changing ticket depends on it.
  Until it merges, the goal's `baseline.value` stays `unmeasured` and the
  validator warns.

Never take the baseline after the first behavioral ticket has merged; that
measures the epic against itself.

## Plan schema

`epic_goals` sits at the root of
`specs/desired_program_model/ticket_plan.yaml`, next to `deferment_policy`:

```yaml
epic_goals:
  - id: GOAL-ingest-p99            # stable, never reused, never renamed
    kind: perf                     # perf | eval | integration | quality
    statement: "Batched ingest cuts tail latency without losing throughput."
    metric: "p99 ingest latency (ms) at 5k rps; throughput (events/s)"
    harness: "uv run scripts/bench_ingest.py --profile epic --out <evidence>"
    baseline:
      value: "p99 412ms, 5.1k events/s"     # or: unmeasured
      measured_at: "<commit sha the baseline ran on>"
      evidence: "results/epic-<slug>/baseline/ingest.json"
    target: "p99 <= 250ms and throughput >= 5.0k events/s"
    evaluation_ticket: "EPIC-9"     # ticket with role: evaluation that decides it
    evidence_root: "results/epic-<slug>/goals/GOAL-ingest-p99"
```

Each ticket gains a `goals` list, and evaluation tickets gain `role` and
`owns_goals`:

```yaml
tickets:
  - id: EPIC-3
    # ...existing scheduling fields...
    goals:
      - goal: GOAL-ingest-p99
        contribution: direct            # direct | enabling | guard
        expected_effect: "-120ms p99 from write batching; throughput unchanged"
        local_signal: "uv run scripts/bench_ingest.py --profile ticket --quick"

  - id: EPIC-9
    role: evaluation                    # omit or use `implementation` elsewhere
    owns_goals: ["GOAL-ingest-p99"]
    goals:
      - goal: GOAL-ingest-p99
        contribution: guard
        expected_effect: "decides the goal; adds no behavioral delta"
        local_signal: "N/A: this ticket is the measurement"
```

Contribution kinds:

- **`direct`** — this ticket's change is expected to move the metric. Requires a
  numeric or directional `expected_effect` and, wherever possible, a
  `local_signal` the agent can run inside its own worktree.
- **`enabling`** — no expected movement on its own; it unblocks a `direct`
  ticket (harness, refactor, plumbing, fixture). `expected_effect` states
  `none — enabling only` plus what it unblocks.
- **`guard`** — the ticket must not regress this metric even though it targets
  another goal. `local_signal` is the regression check.

## Scheduling rules the validator enforces

When `epic_goals` is non-empty:

- every goal is referenced by at least one non-evaluation ticket — a goal no
  ticket contributes to is a goal nobody is working on;
- every ticket declares at least one goal entry;
- each goal's `evaluation_ticket` exists and carries `role: evaluation`;
- every contributing ticket **reaches its goal's evaluation ticket** through
  `depends_on`, so the evaluation cannot start before the work it evaluates;
- every contributing ticket promotes **before** that evaluation ticket in the
  promotion lane.

Mirror those `depends_on` edges into GitHub with `--add-blocked-by` like any
other dependency, so the tracker shows the evaluation ticket blocked by its
contributors.

Missing goals, a missing evaluation ticket, an `unmeasured` baseline, and a
`direct` contribution with no local signal are **warnings**: the plan still
validates, and the epic owner decides. Inconsistencies inside a declared goal
set (unknown goal IDs, an evaluation ticket that promotes before its
contributors, a goal with no contributor) are **errors**.

## What the ticket agent does with it

The assignment block carries the goal context, and the ticket agent:

1. reads its goal entries **before** implementing, and treats
   `expected_effect` as the result it is aiming at, not decoration;
2. runs `local_signal` before close and records the number under the ticket
   evidence root — this is a signal, not a gate: a missed local signal is
   reported, not hidden, and never justifies weakening the REQUIRED matrix;
3. reports the measured local signal against `expected_effect` in the PR body's
   `## Goal contribution` section, including "no measurable movement" outcomes;
4. files a deferred finding (`deferment.md`) when it discovers the goal is
   unreachable by the planned slice, rather than expanding scope to chase the
   metric.

A ticket whose local signal moves the wrong way is not automatically a failed
ticket — the integrated evaluation decides. It is, however, always reported.

## What the evaluation ticket does

An evaluation ticket is a real ticket: it has a slice, a spec ticket, and a
close record. Its slice is the measurement, not the behavior. It:

- promotes last among the contributors to the goals it owns;
- runs each owned goal's `harness` on the integrated epic tip, from a fresh
  start, and writes results under the goal's `evidence_root`;
- reports **baseline → measured → target** and a verdict per goal;
- files deferred findings for regressions it uncovers instead of fixing them;
- never edits the target to match the result, and never re-runs selectively
  until a number passes. Report the run that happened.

An evaluation ticket that finds a goal missed does not fail the epic on its own.
It hands the epic owner a decision: add a ticket, accept the shortfall with a
recorded reason, or re-scope the goal — all at finalization.

## Finalization

The epic PR reports every goal as a row:

| Goal | Kind | Baseline | Measured | Target | Verdict |
| --- | --- | --- | --- | --- | --- |

Verdicts are `met`, `missed`, or `unmeasured` (with a reason). An epic may close
with a missed goal only when the user has explicitly accepted it and the reason
is recorded in the PR body. Never close with a silently unmeasured goal: run it,
or say why it could not run.
