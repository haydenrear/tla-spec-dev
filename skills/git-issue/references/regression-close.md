# Regression & close-out

The issue's final section is a checklist that tells the implementer exactly how
to prove the change is safe and finish it. Name these concretely during
discovery so the implementer runs them without guessing.

## Epic assignment override

When the issue contains an epic assignment, its validation matrix and evidence
root are mandatory and override generic examples below. Run the exact TLC,
spec-unit, repository-unit, and named graph commands (or retain the explicit
`N/A: <reason>`), store their reports below `validation.evidence_root`, and pass
those paths to `tla-spec-dev ... close ticket <stable-ticket-id>`. Close and
promote only the assigned ticket after reconciling the latest epic tip and
rerunning the full matrix; never use `--accept-new` or the whole-workflow close
script.

Use the repository-specific graph names in the assignment. `specWorkflow` is
the tla-spec-dev repository's own CLI-lifecycle graph and is not implicitly
required in other repositories.

```bash
tla-spec-dev --spec-root specs close ticket <stable-ticket-id> \
  --summary "<what landed>" \
  --result <evidence-path> \
  --result <another-evidence-path>
```

After commit and push, open a PR whose base is `ticket.pr_base` (the epic branch)
and whose body uses `Refs #<issue-number>`. Include the exact commands, evidence
paths, close-history path, resulting commit SHA, the `## Goal contribution`
section below, a `## Deferred findings` section (each backlog ID filed with its
severity and one-line summary, or `None`), the worktree `home close-out`
verdict, and a `## Review input` section — then stop for external review. The
epic-owner agent merges this PR into the epic branch at wave close; do not
self-merge, target the default branch, or close the GitHub issue.

## 1. Run the regression test graphs

List the specific `test_graph` graphs that cover the changed surface (from
discovery). These run via the **test-graph** skill. Always include, when the
issue had a spec workflow, the **tla-spec-dev spec-graph integration graph** —
the graph that exercises the generated spec doubles against the real adapters,
so a spec/impl divergence fails loudly.

Where the deciding instrument records **notes** as well as scores, a note that
names a gap in the changed surface is answered here: name the graph or test
that now covers it, and say which note it answers. The score movement that
follows is an **observation**, never the objective — validation tuned to raise
a number is the failure the instrument's own rules exist to prevent.

```bash
# in the test_graph project (see the test-graph skill for exact invocation)
# run the named graphs, e.g.:
./gradlew testGraph --graph <named-graph>
# and the spec-graph integration graph when a spec workflow ran
```

## 2. Attach reports to the spec ticket

The test-graph run produces aggregated reports. Attach those reports to the
**in-repo spec ticket** that this issue closes out (the ticket opened during the
spec workflow — `references/spec-workflow.md`). This ties the passing evidence to
the ticket that gets closed, not just to the PR.

## 3. Close the spec ticket via spec-double-compiler + tla-spec-dev

Close the in-repo spec ticket using **spec-double-compiler + tla-spec-dev** (the
`tla-spec-dev` CLI ticket-close path). This records that the spec, doubles,
graph cases, and adapters all landed and passed together.

## 4. Run spec unit tests and unit tests

Before committing, run both layers and require green:

- **Spec unit tests** — the generated/spec-double unit tests (spec-double-compiler).
- **Unit tests** — the repo's own unit test suite for the changed code.

## 5. Report the goal contribution

Steps 1–4 prove nothing broke. This step reports whether anything got better.
The PR body carries a `## Goal contribution` section with **one row per goal**
the issue declared in `## Goals & evaluation`:

```markdown
## Goal contribution

| Goal | Contribution | Expected effect | Measured local signal | Decided by |
| --- | --- | --- | --- | --- |
| <goal or N/A: reason> | direct \| enabling \| guard | <what this change should produce> | <number the signal reported, or N/A: reason> | <evaluation ticket, or this issue's own harness run> |
```

Run the declared local signal in the ticket worktree before opening the PR,
store its output with the other evidence, and record which of these happened:
moved as expected, moved less than expected, no measurable movement, or moved
the wrong way. An issue that recorded `N/A: <reason>` for its goal keeps the row
and reproduces that reason; an issue that declared no goal at all writes
`None declared`, so a reader can tell that apart from a goal that was ignored.

**The local signal is a signal, not a gate.** It does not decide whether the
ticket passes — the required tests and graphs do that, and the deciding harness
decides the goal. So:

- a missed or wrong-way signal is **reported, never hidden**. "No measurable
  movement" is a legitimate, useful row;
- it never justifies weakening a required test, loosening an assertion, marking
  a graph node skipped, or relaxing an invariant to make a number look better;
- it never justifies tuning to the metric or widening the change beyond the
  issue's stated scope. A signal showing the goal is unreachable from this slice
  is *plan feedback*: finish the stated change, report the finding, and let the
  goal be re-scoped.

### Evaluation issues report `## Goal verdicts` instead

An issue whose slice **is** the measurement — an eval, perf, or integration
issue that decides a goal — reports baseline → measured → target with a verdict
rather than an expected effect, under a differently named heading so the two are
never confused:

```markdown
## Goal verdicts

| Goal | Clause | Kind | Baseline | Measured | Target | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <goal> | <clause, or —> | perf \| eval \| integration \| quality | <value + commit it was measured on> | <what the instrument reported> | <threshold> | met \| missed \| unmeasured | <evidence path> |
```

Verdicts are exactly `met`, `missed`, or `unmeasured` (with a reason). Run the
harness from a fresh start on the integrated branch, after the work it evaluates
has landed. Then: **never edit a target to match a result**, and never re-run
selectively until a number passes — report the run that happened. A missed goal
is a decision for the owner (add work, accept the shortfall with a recorded
reason, or re-scope the goal), not something for the evaluation issue to fix by
adjusting what it measures. A silently unmeasured goal is the failure this whole
section exists to prevent.

**One row per clause, not per goal.** A target with several clauses can settle
differently on each — met on one, missed on another — and a single token has to
pick which clause it refers to, which is how the flattering one gets picked. Use
`—` in the Clause column when there is only one. A goal whose target is
deliberately not a threshold still gets a row: `Measured` is what the instrument
produced on its first real run, `Target` restates the no-threshold decision, and
the verdict says whether the instrument ran and discriminated.

Where the deciding instrument is a **judged** one, its own documentation governs
how the result is produced, sealed, and compared — rubric version, blinding,
sealing, and the rules for when two numbers are comparable at all. Cite it and
follow it; this skill restates none of it. For `tla-spec-dev` that is
`references/eval_scorecard.md`.

The implementer's half of this contract — how the signal is run and classified,
and how an evaluation ticket executes — is `git-issue-workflow`'s
`references/goal-signal.md`. These two headings and their columns must stay
identical on both sides: this skill tells the author what to ask the implementer
for, and that skill tells the implementer what to produce.

## 6. Commit and push to the feature branch

Only after 1–5 pass:

```bash
git add -A
git commit -m "<issue-number>: <what changed> — specs, graph, adapters, tests"
git push -u origin feature/<issue-number>-<slug>
```

Then open the PR (`Closes #<issue-number>`) or close the issue with a summary of
the graphs run and reports attached (`references/github-gh.md`).

That final sentence applies only to an ordinary issue. Epic ticket PRs use
`Refs` and stop at PR open: the epic-owner agent merges them into the epic
branch at wave close, and issue closing is left to epic finalization.

## 7. Close out the worktree's Skill Manager home before removing it

The last thing an implementer does is delete the worktree, and that deletes
`<worktree>/.skill-manager` with it — without asking, and just as quietly whether
the home held a week of skill edits or nothing. The home is gitignored, so steps
1–6 have proved nothing about it: no graph report, no spec ticket, no PR and no
fan-out contains any of it.

So the issue has to name the gate. It is one command, and it writes nothing:

```bash
skill-manager home close-out --home <worktree>/.skill-manager \
                             --into <repo-root>/.skill-manager
```

`--into` is the **project** home the worktree's was cloned from, never
`~/.skill-manager`. Exit 0 means there is provably nothing to lose. Of the three
non-zero exits, only **exit 1** is a verdict about the work, and only it prints
blockers: **exit 2** means the `--home` path is not a home at all (usually the
worktree directory instead of its `.skill-manager`) and **exit 9** means the
destination home is frozen so nothing was attempted. Tell the implementer to
distinguish them, or a frozen destination reads as "blocked" and a typo reads as
"broken".

Exit 1 names every blocking unit with the literal command that clears it, and
there are two shapes, answering different questions:

- `skill-manager home sync --from <worktree>/.skill-manager --to <repo-root>/.skill-manager --merge`
  moves the edit **up a tier** so the teardown does not take it. Local to this
  machine. A conflict is reported, never resolved, and a conflicted unit writes
  nothing.
- `skill-manager unit publish <unit> --ticket <issue-number>` puts it in the
  **unit's own git repository**. This is the only route that reaches another
  project or outlives this machine, and it is the one owed for a skill the
  implementer improved while working the ticket.

Tell them to run the wrapper instead of the two steps by hand — it is one
command, it is the same in a plain repo and an integration repo, and it runs the
gate and the removal in that order, refusing on a non-zero verdict:

```bash
WT="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/wt"
"$WT" close <ticket>
```

If the repository has no per-checkout home, say so explicitly rather than omitting
the step — an omitted step reads as "nothing to do here", which is exactly the
state this gate exists to distinguish from "checked, nothing to lose".

An epic ticket runs the gate but neither remedy-by-`home sync` nor the removal.
The close-out is read-only there — its verdict goes in the PR body — and only
`unit publish` is the ticket agent's to run: the project home is one shared
destination that a ticket agent cannot see the other tickets writing, so the
epic agent reconciles every worktree's home into it in serial at wave close.
The worktree is left standing; the epic agent removes every worktree in one
sweep at the end of the epic, acting on the recorded verdict. Write the epic
form of these two lines into the issue instead of the ordinary form
(`references/epic-assignment.md`).

## Checklist to embed in the issue

- [ ] Named test graphs pass (incl. tla-spec-dev spec-graph integration graph)
- [ ] Test-graph reports attached to the in-repo spec ticket
- [ ] Spec ticket closed via spec-double-compiler + tla-spec-dev
- [ ] Spec unit tests pass
- [ ] Unit tests pass
- [ ] Local signal run and recorded; `## Goal contribution` in the PR body names
      the expected effect, the measured result (or `N/A: reason`), and what
      decides the goal — including "no measurable movement"; `None declared`
      when the issue declared no goal
- [ ] Evaluation issues only: `## Goal verdicts` instead — baseline → measured →
      target with a `met` / `missed` / `unmeasured` verdict per goal, from the
      run that actually happened
- [ ] Committed and pushed to `feature/<issue-number>-<slug>`
- [ ] Worktree torn down with `"$WT" close <issue-number>-<slug>` (the gate runs
      first; clear every blocker it names with `unit publish` / `home sync
      --merge` and re-run — never `git worktree remove`)
- [ ] Epic tickets instead: `home close-out` run as a read-only gate and its
      verdict in the PR body, every unit changed named under `## Review input` →
      *Machinery friction*, blockers cleared only with `unit publish`, and the
      worktree left standing for the epic agent's end-of-epic sweep
