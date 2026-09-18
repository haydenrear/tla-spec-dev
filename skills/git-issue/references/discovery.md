# Discovery — scan before you write

An issue is only useful if it points the implementer at the right code. Do this
scan first; its output fills the `## References`, `## Goals & evaluation`,
`## Discovery notes`, the spec-workflow decision, and the regression scope.

## What to find

1. **Entry points and owners.** Where does the behavior live now? Grep for the
   feature's nouns/verbs, the public API surface, the config that toggles it.
2. **State machine surface.** Search for `*.tla` specs and the generated spec
   doubles. If the change alters observable or internal state-machine behavior,
   note the specific spec (`Internal.tla` / `External.tla`) — this decides the
   spec-workflow section. See `references/spec-workflow.md`.
3. **Tests and graphs.** Locate the `test_graph/` project, the graphs in
   `build.gradle.kts`, the unit tests, and any adapter conformance tests. What
   graph would catch a regression in this area? That list becomes close-out.
4. **Docs / prior art.** ADRs, READMEs, prior issues/PRs on the same surface.
5. **The measurement inventory.** What in this repo could *decide* whether the
   change worked? This is a separate sweep from step 3: a unit test says the code
   does what it says, a measurement says the program got better. Look for
   benchmark scripts and their profiles, eval datasets with their scorers and
   pinned versions, perf-marked or load-marked suites, end-to-end and integration
   Test Graph graphs, and any baseline numbers already recorded (committed result
   JSON, a README table, a prior PR body, an epic evidence root).

   Capture, for each: the exact command, what it reports, how long it takes, and
   whether a baseline value exists. Cheap-and-local versus slow-and-integrated
   matters — the cheap one becomes the issue's local signal, the integrated one
   becomes what decides the goal.

## The measurement inventory feeds the goal

Goals are cheapest to write when a harness already exists, and vaguest when none
does. The inventory is what turns "make ingest faster" into "p99 ingest latency
≤ 250ms at 5k rps, measured by `scripts/bench_ingest.py --profile epic`, from
412ms today". Use it to answer three things before writing the body:

- **Is there an instrument that decides this?** If yes, that is the
  `Metric / harness` bullet. If no, the honest options are to scope the issue to
  build the harness, route to `git-epic-workflow` so a wave-1 ticket builds it
  and measures the baseline, or record `N/A: <reason>` — not to write a goal
  nobody can decide. The instrument does not have to be a command: an artifact
  scored against a versioned rubric by judges who cite it is an instrument, and
  in some repositories it is the *better* one, because a number computed from an
  artifact can be improved by editing the artifact.
- **Is there a baseline?** A target with no baseline is unfalsifiable. Prefer a
  recorded number; otherwise say `unmeasured` and name how the implementer
  measures it before changing behavior.
- **Is there a cheaper proxy?** A quick local variant of the same harness — a
  `--quick` profile, a subset of the eval set, a single graph rather than the
  suite — becomes the `Local signal` the implementer can run in its own
  worktree. Its absence is recorded as `N/A: <reason>`, not left blank.

Useful sweeps for this step (adjust to the repo):

```bash
# benchmark / eval harnesses and their datasets
git ls-files 'bench*/**' '*bench*' 'evals/**' 'eval/**' 'datasets/**' 2>/dev/null
# perf- or load-marked tests
git grep -rln "pytest.mark.benchmark\|@Benchmark\|pytest.mark.perf\|jmh" 2>/dev/null
# end-to-end / integration graphs among the composed test_graph graphs
git grep -n "integration\|e2e\|endToEnd" -- build.gradle.kts 'test_graph/**' 2>/dev/null
# baselines someone already recorded
git ls-files 'results/**' 'baselines/**' '**/baseline*' 2>/dev/null
```

Record what you *didn't* find, too. "No benchmark exists for this path" is a
discovery result that changes the issue — it is the difference between a goal
with a deciding instrument and a goal that needs one built first.

## How to record it

For each relevant location capture `path:line` and a one-line reason. That pair
is exactly what the `## References` bullets need. Keep it a *starting point*,
not an exhaustive map — the implementer discovers the rest from these anchors.

Useful sweeps (adjust tools to the repo):

```bash
# state-machine specs and their doubles
git ls-files '*.tla' 'spec_double*/**' 2>/dev/null
# the test-graph project and composed graphs
git ls-files 'test_graph/**' 'build.gradle.kts'
# the feature's code by keyword
git grep -n "<feature-keyword>"
```

## Decisions to lock before writing

- **References list** — the files/symbols/specs above.
- **Goal and what decides it** — the metric, the deciding instrument, today's value,
  the success threshold, this issue's contribution kind, and the local signal.
  Discovery supplies the *candidates*; the user agrees the goal and target. If
  nothing here is measurable, lock that as `N/A: <reason>`.
- **Spec workflow: REQUIRED or NOT** — REQUIRED if any `Internal.tla` /
  `External.tla` behavior or invariant changes. When unsure, mark REQUIRED; a
  no-op spec pass is cheap, a missed one is not.
- **Regression scope** — the named test graphs (including the tla-spec-dev
  spec-graph integration graph) that must pass to close the issue.

Carry these four into the issue body template in `SKILL.md`. Regression scope and
goal are not the same list and neither substitutes for the other: the graphs say
nothing broke, the goal says something got better.
