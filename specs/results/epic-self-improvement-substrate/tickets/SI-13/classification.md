# SI-13 — which graphs run, which are opt-in, which are dead

Measured 2026-09-19. Every verdict below was read from a report or a CI job
record. No verdict here was inferred from an exit code, and no graph is called
green because a command returned 0.

## tla-spec-dev (this repository)

One command: `python3 test_graph/run-graphs.py` (`--list` classifies without
running). It materialises the managed provider bindings first and prints them,
then runs each graph and reads its verdict from that run's own `summary.json`.

| graph | class | verdict here | evidence |
|---|---|---|---|
| `specWorkflow` | RUN | PASSED (9/9 nodes) | `validation-reports/20260919-224128/summary.json` |
| `cliWorkflow` | RUN | PASSED | `validation-reports/20260919-224229/summary.json` |
| `effectProviderExamples` | RUN | PASSED | `validation-reports/20260919-224243/summary.json` |

Opt-in: **none** — no graph here reaches a third-party service.
Dead: **none**.

Run in the ticket worktree at base `07b9a97d`, from the plugin layout, using
`skills/test-graph/scripts/run.py` — this checkout's own contained copy of the
skill, not a Skill Manager home. That is the claim SI-13 was asked to
re-establish rather than inherit: green *from the plugin layout*, after SI-01,
SI-02 and SI-11 moved the paths underneath.

### The worktree blocker, and what it actually was

`SI-12-DF-05` reported that the three graphs cannot run in a ticket worktree.
Measured both ways in one throwaway checkout at the same base:

- `cd test_graph && ./gradlew specWorkflow` → **BUILD FAILED in 2s**,
  "Included build '.../build-logic' does not exist", no links created.
- `python3 skills/test-graph/scripts/run.py specWorkflow` → the three managed
  bindings are materialised and the graph runs to a green report in **1m42s**.

So what cannot run in a fresh worktree is *bare Gradle*, not the graphs. The
test-graph skill's runner already materialises the bindings —
`run_gradle()` calls `prepare_provider_bindings_or_warn` — and nothing in the
ticket front door said so. `SI-12-DF-05`'s suggested remedy ("track
build-logic") would reintroduce exactly what commit `175f5c7c` removed: tracked
symlinks whose blobs held one developer's absolute home path. Recorded as
`SI-13-DF-01`.

## skill-manager (separate repository, separate PR)

One command: `python3 test_graph/run-graphs.py` (`--list` classifies without
running). It imports `.github/scripts/select-graph-set.py` so CI and the laptop
share one exclusion list and one set of reasons, and reads verdicts from the
sweep ledger of that invocation.

**Registered: 30.** Established, not taken on trust: `grep -c 'testGraph('`
returns 32; two of those sit inside comments; `hyper-experiments` is also
registered a second way, through `tasks.register(...)` in the non-opt-in
branch, under the same name — so it is one graph, not two, and 30 is the count.

| class | count | graphs |
|---|---|---|
| RUN | 26 | smoke, onboard, sponsored, source-tracking, git-latest-source-tracking, plugin-smoke, harness-smoke, doc-smoke, project-manifest, project-resolve, project-smoke, spec-conformance, project-child-home, home-clone, home-tripwire, checkout-home, home-sync, ticket-lifecycle, project-env, project-libs, project-profiles, artifact-dag, onboarding, home-integrity, home-verdicts, sync-settles |
| OPT-IN | 4 | browser-auth, password-reset, refresh-flow, hyper-experiments |
| DEAD | 0 | — |

Opt-in reasons, printed by the command on every run so "did not run" can be
told apart from "is not run here":

- `browser-auth`, `password-reset` — boot chromedriver and a real browser.
- `refresh-flow` — boots a browser **and** is excluded outright: a 3s token TTL
  verified by a live round-trip that takes 7.6–8.6s, ~1-in-4 flake
  (skill-manager-integration-repository#53).
- `hyper-experiments` — reaches github, npm and the live RunPod API (#143);
  already opt-in at the build level via `HYPER_EXPERIMENTS=1` / `HYPER_LOCAL_DIR`.

### Verdicts

- **Locally, through the new command**: `home-integrity` ran green in 154.2s,
  19/19 nodes, with all four opt-ins printed as NOT RUN and their reasons. That
  is one graph, run here, to prove the front door executes and reports.
- **The other 25 RUN graphs were not executed on this machine.** They are
  reported green on the evidence of nightly CI run **35441292782** (schedule,
  2026-09-19, conclusion success): 26 matrix graph jobs and 2 selenium jobs, all
  `success`. That is an observed run of the same registrations, one day old — it
  is not a run in this ticket, and it is stated as CI evidence, not as something
  SI-13 measured.
- `refresh-flow` and `hyper-experiments` have **no** observed verdict here or in
  that run. They are UNDECIDED by construction, which is what opt-in means.

### Dead artifacts, not dead graphs

No *registered* graph is dead. Two rendered DAGs in `test_graph/docs/` are:
`skill-dev-smoke.*` and `specExternalPhase.*` have no registration and no source
directory, and twelve registered graphs have no doc at all (`SI-13-DF-04`).
`sources/lib` has no registered node but is not dead either — it holds shared
helper classes pulled in by 206 `//SOURCES` lines.

## Nothing here refuses

Both commands always exit 0. A red graph, an unmeasured graph and an opt-in
graph are all printed; none of them becomes a non-zero exit or a new refusal
path. `GOAL-no-new-gates` adds no check in this ticket, so its local signal is
N/A by the plan's own words.
