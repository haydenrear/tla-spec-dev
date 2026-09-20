# The scored run SI-14 never made — one case, and what it cost

**SI-08, 2026-09-20, base `2131cdad`.** SI-14 shipped the pin without running a
scored eval case through it, so nothing proved a pinned ref reaches a score.
**This ticket ran one.** It is the first scored case in this suite's history.

## What was run, and what it cost

```
./evals/run.sh --case use-the-front-door
```

| | |
|---|---|
| cases | **1** (`evals/git-issue-workflow/use-the-front-door`) |
| runs | 1 (`runsPerCase: 1`) |
| **cost** | **$0.5380525** |
| wall clock | 106 s (case), ~3 min including the fetch |
| `claudeVersion` | 2.1.276 |
| score | **0.67**, `passed: false` (threshold 1) |
| `run.sh` exit | **1** — the case scored under threshold. The *run* succeeded; the *case* did not pass. |

The case's two graders: `starts-at-the-front-door` (weight 2, `file_exists`)
**passed**; `the-first-command-is-quoted` (weight 1, `regex` over `last_message`
for `skt ticket new|wt new|git worktree add`) **failed** — "pattern not found in
last_message". That is a case result and this ticket did not touch it
(measurement only, no behavioural delta).

## What it proves for the goal

**The toolchain record is written by a scored run, and it names the commits.**

```
eval: toolchain -- single case ('use-the-front-door'); DEFAULTING to the pinned
      286a3694a815c6f6a9e76bffcb03a1fd8100cce3
  skill-manager: 6ffacb88ff96 (pinned in evals/lib/toolchain.lock.toml)
      the CLI says: skill-manager 0.28.1+g6ffacb88ff96
  skt: 286a3694a815 (pinned in evals/lib/toolchain.lock.toml)
      staged -> /private/tmp/tla-spec-dev-eval-view/toolchain/skt
  drift: skt: main HAS MOVED to 0f3807811e1d since the pin at 286a3694a815
  record -> evals/results/toolchain/20260920T164507Z.json
```

`verified_head == pinned_commit` for both units. The pinned skt's skills were
**staged into the view** (`skill-manager skt unit-authoring`), so the case loaded
its subject at the pinned commit rather than from the operator's home — which,
the same record says, would have supplied `0f3807811e1d` instead.

The run also exercised the single-case branch of the ask: it **named what it
defaulted to** rather than defaulting silently.

## Three things it does NOT prove, stated rather than smoothed over

1. **The ref is not next to the score.** `aggregate-result.json` — the artifact
   that carries the 0.67 — contains **zero** occurrences of `toolchain`, the
   pinned shas, or `pinned` (measured: `grep -c` → 0). The ref lives in a
   *sibling* file under `evals/results/toolchain/`, and the two are joined by
   **nothing but timestamp proximity**: the record is `20260920T164507Z`, the run
   directory is `2026-09-20T16-45-12-045Z`, five seconds apart, sharing no run id.
   A reader with two runs a week apart can pair them by hand; no key does it.
   Filed as `SI-08-DF-05`.

2. **The run record is gitignored.** `.gitignore:32` ignores `evals/results/`, so
   `20260920T164507Z.json` is **not committed by the run that made it**. The
   *pin* appears in the repository (`evals/lib/toolchain.lock.toml`, which is
   what the goal's harness requires); the *run records* do not. This ticket
   copied both artifacts into `first-scored-run/` in this evidence root so that
   at least one survives. Filed as `SI-08-DF-06`.

3. **A ref has not been shown to MOVE a score.** One run at one ref is one data
   point. Demonstrating that the pin changes an outcome needs the same case at
   two refs, which would cost roughly $1.08 and was not run. The honest claim is
   *"a pinned ref reaches a scored run and is recorded"*, not *"a pinned ref
   changes a score"*.

## Why only one case

The full suite is 61 cases. At this case's $0.54 a run, a full sweep is on the
order of **$33** — over the wide lane's $25 cap — and 6 of the 61 are UNDECIDED
by construction (`SI-15-DF-05`: they need a ~41,000-entry branched home, and
`claude plugin eval` refuses a plugin directory over 20,000 entries; the view
already holds 18,025 after staging). One case was enough to decide the clause
this ticket owns: whether a scored run records its ref. It does.
