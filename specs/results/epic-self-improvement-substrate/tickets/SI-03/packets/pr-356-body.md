SI-11 closes the resolution gap SI-02's nesting left: every executable and every
generated binding now finds the toolchain under the plugin layout, and a test
fails when a new standalone-only rung appears.

Refs #333

- **Epic branch**: `epic/self-improvement-substrate` (base for this PR)
- **Workflow**: `self-improvement-substrate`
- **Spec ticket**: `SI-11` — **not closed and not promoted**. The epic agent owns
  the model for this epic (`planning_rules.model_ownership_rule`); I ran no
  `open ticket`, `close ticket`, `close_tickets.py` or `--accept-new`.
- **Dependency check**: `SI-02` (#335) merged as PR #350, merge commit
  `a42e0f7e` — verified reachable from `origin/epic/self-improvement-substrate`
  at `994f650c`, which is the pinned base this branch was cut from.
- **Promotion predecessor**: `SI-10`. Not applicable to this PR — predecessor
  serialisation gates ticket-scoped *promotion*, and this ticket performs none.
- **Assignment vs canonical plan**: equal on every scheduling field.

## Goal contribution

| Goal | Kind | Expected effect | Measured | Classification | Decided by |
|---|---|---|---|---|---|
| `GOAL-one-unit` | direct | live stale paths go 2 → 0; the three graphs run from bindings naming an in-bundle path | **3 stale paths removed, not 2**; all three graphs green from `../skills/test-graph` | **moved as expected** (on the effect; see below on the instrument) | SI-08 |
| `GOAL-no-new-gates` | guard | the new regression test reports; it does not refuse | `grep -nE 'SystemExit\|sys\.exit\([^0]'` over the new check → **no matches**; the `bootstrap-home.sh` guard warns and `continue`s | **moved as expected** (flat, as a guard should be) | SI-08 |

Evidence: `specs/results/epic-self-improvement-substrate/tickets/SI-11/`.

**The declared local signal for `GOAL-one-unit` cannot reach its target, and I
did not tune anything to make it.** The signal is the Discovery-notes grep with
"expected zero non-comment hits". It measured **10 before and 20 after**. That is
not a regression: *the correct two-rung form contains the standalone substring
the grep matches*, so a file that probes `$SKILL_MANAGER_HOME/skills/test-graph`
before `$SKILL_MANAGER_HOME/plugins/*/skills/test-graph` counts as a hit by the
fix exactly as by the defect. Zero is reachable only by deleting every rung. The
increase is entirely two-rung pairs and new test fixtures. Filed as
`SI-11-DF-05` with the property the goal actually wants, now executable as
`tests/test_plugin_layout_resolution.py`. **SI-08 should decide `GOAL-one-unit`
on that check, not on the grep count.**

Also worth one line for whoever re-runs it: the signal command as written is
shell-fragile. Under zsh, `skills/*/skill-scripts` matches nothing after this
ticket, which aborts the whole glob and prints **0 hits for the wrong reason** —
a false green indistinguishable from success. I hit exactly that and re-ran it
under `bash` with `nullglob`. Both runs are in the evidence root.

## What changed, and what each was measured to be

**1. `skills/test-graph/scripts/github-action.py`** — `TEST_GRAPH_SKILL_HOME` was
`f"{skill_manager_home}/skills/test-graph"` in a workflow-level `env:` block. A
GitHub Actions `env:` value is a literal string: it cannot probe the filesystem,
so *there is no two-rung form that can be written there at all* — the docstring's
`$(for d in ...)` would have been emitted verbatim and never evaluated. The
resolve moved into the install step, which publishes the answer via `$GITHUB_ENV`.
It defaults rather than refuses, so the pre-existing `test -d` lines still produce
the same failure and this adds no new failure path.

Same file, a second one nobody had named: `_infer_skill_manager_home` matches the
suffix `skills/test-graph/project_sdk_sources/<name>`, which a plugin path
satisfies too — it would have inferred `<home>/plugins/<plugin>` **as the home**,
making every path built from it (`bin/cli`, `pm/uv`) resolve to nothing.

**2. `test_graph/provider-bindings.json`** — the answer here matters more than the
repoint, and it is not the one the issue predicted. The stale candidate was **not
unexercised**. `select_provider_root` takes the first *complete* provider, and the
worktree home still carries the retired standalone `test-graph` install, so
`../.skill-manager/skills/test-graph` **won**, and the three graphs built against
a copy of the SDK the bundle no longer versions. It resolved, so nothing failed.
Now `../skills/test-graph`, materialising as in-tree relative links.

One correction to the issue: this manifest is **tracked**. Only the three
directories it generates are gitignored.

**3. `skill-project.toml` `[[vendored]]` — deleted, not repaired.** SI-02 flagged
this as its highest-uncertainty line and never ran `project resolve`. I ran it: it
**fails**, with three `MISPOINTED` errors whose computed `expected` path
(`<home>/skills/tla-spec-dev/skills/test-graph/...`) can never exist, because
`from_unit` resolves only at the skill rung with no plugin rung. Editing the two
fields cannot fix it. It is also obsolete: those paths no longer enter a home at
all. `project resolve` now exits 0 — `vendored: 0 checked, 0 finding(s)`.

**4. `SIS-W2-F-05`** — reproduced verbatim in a scratch HOME
(`cli: 15 installed, 2 failed`), and **fixed by moving ownership, not the
scripts.** A `skill-script:` installer is resolved by the *installed unit's* name;
`PluginUnit.unionCli` flattens every contained skill's deps onto the plugin and
`CliDependency` carries no owner field, so `spec-double-2` is not a name the
resolver ever has. There are exactly two rungs and no contained-skill rung, so the
dep had **no working spelling** — the error names the standalone rung it probed
first, which is why it read as a migration leftover. `tlc2` and `tla-spec-dev` are
the whole bundle's toolchain, so the plugin is the honest owner even setting the
resolver aside. Verified from a local install: **`cli: 17 installed`, zero failed.**

**5. The regression test** — `tests/test_plugin_layout_resolution.py`. A file
naming a *home-anchored* standalone rung must also name the plugin rung. It found
a real false positive in its own first draft (`$SKILL_DIR/skills/spec-double-2` is
a plugin-root path, not a home rung), which is why it anchors on a home.

**6. `selftest.sh`** — item 4 said the suite "enumerates only the standalone
layout". It was worse: **the suite died at step 15 of 30 and still exited 0.**
`done < <( ... )` fails at runtime on bash 3.2 — `/bin/bash` on every macOS — with
`bad substitution: no closing ')' in <(`, and `bash -n` parses it clean. Every
check below that point, *including both sections this ticket adds*, reported
nothing and was indistinguishable from passing. Found by counting `step "` in the
file (30) against `^== ` in the output (15). The sweep now lands in a file.

**7. `SI-06-DF-03`, handed to me mid-ticket — the exclude guard.** Taken, as the
epic agent advised. `bootstrap-home.sh` now refuses to write an exclude rule for
a path the repository **tracks**. The guard is on the *pattern*, so
`/.skill-manager/`, `/.claude/`, `/.codex/`, `/.gemini/` keep working. Proven by
hand, independently of the selftest, in `exclude-guard-proof.txt`: `?? specs/results/`
collapses to the bare entry `specs/` that the loop acts on; `git ls-files -- specs/`
is non-empty so the rule is refused; `.skill-manager/` is untracked so its rule is
still written.

## Validation

| Entry | Result |
|---|---|
| `specWorkflow` / `cliWorkflow` / `effectProviderExamples` | **all three green (RC=0)**, matching the pre-edit baseline, from regenerated in-bundle bindings |
| Repository suite | **10 failed / 1601 passed** — byte-identical failure set to the baseline **by name**: zero new, zero fixed |
| Spec-unit (`--target specs/tickets/SI-11/desired`) | **7 failed / 46 passed — the same 7 names as baseline**, no regression |
| `skill-manager project resolve` | exits 0, `vendored: 0 checked, 0 finding(s)` (was 3 errors) |
| `home close-out` | **clean** — `"safe": true, "exitCode": 0, "blockers": []` |
| TLC | `N/A` — epic agent owns the model |

`run spec-unit-tests --ticket` is known-weak (`SIS-KICKOFF-F-04`), so I used
`--target specs/tickets/SI-11/desired` and am saying so. There is no ticket-local
`current/` (`current_dir: null`), so that target is the ticket's whole spec-unit
surface.

### `git-issue-workflow` selftest — read the attribution before the number

`169 passed / 63 failed`, exit 1, **30 of 30 steps run**. Compare by name, not
count, and note that the denominator changed *because of this ticket*:

- **Before SI-11, no run of this suite had ever reached steps 16–30** — it died at
  step 15 and exited 0. The prior baseline is therefore 15 steps / 50 failures,
  and I re-ran it on the unmodified epic worktree to confirm: **identical 50
  names**.
- All **50** of those pre-existing failures are still present, by name, unchanged.
- **13 failures are newly reachable**, not new. Eleven are in `wt close`, `--log`
  and lifecycle-callback sections whose code this ticket never touched.
- The remaining two are `*_fixture_bootstrapped` ("bootstrap exited 1"). One of
  them, `the_clean_tree_fixture_bootstrapped`, belongs to a **pre-existing**
  section I did not write and fails identically — so the mode is environmental
  (the same projection failure that blocked `skt ticket new` for this worktree),
  not something the exclude guard introduced.

**My two new sections:**

| Section | Result |
|---|---|
| `agent-home.sh finds the bootstrap inside a PLUGIN` (rung 5b, `SI-02-DF-02`) | **4/4 PASS** — including that the standalone rung still wins, and that the fixture is genuinely empty first |
| `bootstrap-home.sh never excludes a directory the repository tracks` (`SI-06-DF-03`) | **5/6 PASS**; the 6th is the environmental bootstrap exit above |

The exclude assertions are **not vacuous despite that exit**:
`the_home_artefacts_are_still_excluded_in_the_same_run` passes, which requires
`/.skill-manager/` to actually be in the exclude file — so the run wrote rules,
wrote the artefact rule, and refused the tracked one, in one pass.

Worth saying plainly: **the first version of my exclude fixture was wrong, and its
own non-vacuity check is what caught it.** It emptied the tracked directory
expecting `?? specs/`; git does not do that while the index entry survives. The
guard assertion "passed" while asserting nothing. That is the argument for
writing the non-vacuity check, and it is why the guard is *also* proven by hand in
`exclude-guard-proof.txt`.

## Deferred findings

| ID | Severity | Summary |
|---|---|---|
| `SI-11-DF-01` | major | skill-manager's `skill-script:` resolver has no contained-skill rung, and reports only the first rung it missed. Root cause of `SIS-W2-F-05`; `dependencies.md` still advises the broken shape. |
| `SI-11-DF-02` | minor | Same missing-rung defect in `project resolve`'s `[[vendored]] from_unit`. Why the block was deleted rather than repaired. |
| `SI-11-DF-03` | minor | `skill_feedback.py:354` emits `~/.skill-manager/skills/spec-double-compiler` — retired rung *and* pre-migration unit name. Outside my conflict keys; SI-10 owns that surface. |
| `SI-11-DF-04` | major | The unfixed half of `SI-06-DF-02`. `new-change.sh` exits 3 correctly and `wt` propagates it; the suspect is `wt.py:main()` returning `proc.returncode` to an entry point that never `sys.exit()`s it. |
| `SI-11-DF-05` | minor | `GOAL-one-unit`'s declared local signal cannot reach zero and is shell-fragile. For SI-08. |

Appended after re-fetching the tip (unchanged at `994f650c`); 45 → 50 rows, YAML
re-validated.

## Skill changes proposed

| Unit | What I hit | Change |
|---|---|---|
| `git-issue-workflow` (in-repo) | `bootstrap-home.sh` wrote exclude rules for tracked directories, destroying evidence silently | **Applied** — tracked-path guard + a selftest section with a non-vacuity check |
| `git-issue-workflow` (in-repo) | `selftest.sh` died at step 15/30 on bash 3.2 and exited 0 | **Applied** — sweep lands in a file |
| `git-issue-workflow` (in-repo) | rung 5b covered "by the live homes", i.e. not at all | **Applied** — a plugin-layout locator section |
| `test-graph` (in-repo) | standalone-only `TEST_GRAPH_SKILL_HOME` and home inference | **Applied** |
| `skill-manager` (external repo) | no contained-skill rung for `skill-script:` or `[[vendored]]`; error names only the first missed rung | **Proposed** — `SI-11-DF-01`, `SI-11-DF-02`. Not applied: different repository, outside conflict keys |
| `skt` (external unit) | `ticket new` rolled back and reported success | **Proposed** — `SI-11-DF-04` |

## Review input

**Hot spots**

- `skill-manager-plugin.toml` + `skills/spec-double-2/skill-manager.toml` +
  `skill-scripts/` — moving CLI-dep ownership changes what `SKILL_DIR` means, and
  **three callers encoded the old meaning**. I found them one at a time, each from
  a failure: the graph node, the pytest test, and the ticket's own `desired`
  adapter. `specs/current/`, `specs/program_model/` and
  `specs/desired_program_model/production_adapters.py` carry the **same two
  lines** and I did not touch them — they are the epic agent's under model
  ownership. **They need the same correction at promotion or `BuildSkillCli` will
  report `accepted: false`.** This is the single most likely thing to bite.
- `test_graph/sources/tla_spec_dev_cli_install.py` — outside my declared
  `test_graph` conflict keys (which name `provider-bindings.json` and the three
  generated dirs). I edited it because leaving it red failed all three graphs.
- `skills/git-issue-workflow/scripts/selftest.sh` — +185 lines. SI-06 and SI-04
  are also in this file's skill this wave.

**Decisions and overrides nobody asked for**

- **Deleted** `[[vendored]]` rather than repairing it. Evidence in the file and in
  `SI-11-DF-02`; reversing it needs a resolver change first.
- Moved CLI-dep ownership to the plugin. The issue said "do not just move the
  scripts to satisfy the lookup" — moving *only* the scripts would in fact have
  satisfied rung 2 without touching a manifest, and that is the hack I avoided.
- **Widened scope three times**, each a direct consequence of my own change and
  each outside my conflict keys: `tests/test_tla_spec_dev_cli.py`,
  `test_graph/sources/tla_spec_dev_cli_install.py`, and
  `specs/tickets/SI-11/desired/production_adapters.py`.
- Fixed `selftest.sh`'s process substitution — not in the issue, but without it
  neither section I added could run at all.
- Took `SI-06-DF-03` (exclude guard) and **declined** `SI-06-DF-02`, as advised.
- Reverted incidental regenerated files (`examples/**/case_coverage.json` absolute
  paths, `test_graph/docs/*.dot|png`) to keep the diff to the slice.
- **Front-door defect, reported as required**: `skt ticket new` resolved and
  **failed** — `error: this home holds 15 skill(s) and an agent launched here can
  reach 12` — then rolled the worktree back. It does not forward
  `--allow-unprojected`, so I used the documented by-hand pair from
  `epic-ticket.md` §2 with that flag. The three unreachable units are exactly the
  three this epic moved into the plugin, so the refusal may itself be a false
  positive of the migration.

**Where I'd look for bugs in my own change**

1. **The `specs/current` / `specs/program_model` adapters above.** Cheapest
   experiment: `grep -rn 'spec-double-2. / .skill-scripts' specs/current
   specs/program_model` and run `BuildSkillCli`.
2. **The `github-action.py` workflow is emitted but never executed by any test.**
   The generator has no test at all. I verified the emitted YAML by generating it
   and reading the step; nothing ran it on a runner. Cheapest experiment: trigger
   the generated workflow once via `workflow_dispatch`.
3. **`_infer_skill_manager_home`'s `plugins/<plugin>` strip is legacy-only** and
   unreachable from any managed project. I reasoned it out rather than executing
   it. Cheapest experiment: a unit test on the function with a plugin-shaped link.
4. **The regression test's regex.** It over-matches the standalone rung on purpose
   (a plugin rung also matches it). Safe for the "if standalone then plugin"
   assertion, but do not reuse it as a counter.

**Machinery friction** — my worktree home is gitignored and dies with this
worktree, so this list is the only place these survive.

- `skt ticket new` failing on projection and not forwarding `--allow-unprojected`
  cost the first 20 minutes. I bootstrapped by hand with
  `SKILL_MANAGER_CLI=<project>/.skill-manager/bin/cli/skill-manager
  bootstrap-home.sh --root <wt> --allow-unprojected`, which also printed
  `skill-manager: ignoring SKILL_MANAGER_CLI=… it resolves to this shim` and then
  `error: verify: … refuses to act on …` — the home was nonetheless usable and
  `home close-out` reports it clean.
- **Four sibling worktrees (`wt-337`, `wt-338`, `wt-339`, `wt-343`) have no
  `.skill-manager` at all.** Agents launched there write the operator's global
  home. Worth checking before wave close.
- `selftest.sh` dying at step 15 and exiting 0 meant my first validation of both
  new sections was **vacuous and looked fine**. I only caught it by counting steps
  in the file against steps in the output. That count is worth making a check.
- Running a failing `test_graph` graph **deleted 27 tracked files of `test_graph/`
  itself** — its cleanup node ran after `spec.cli.install` failed and took the
  next two graphs with it (`not inside a test_graph project`). Restored with
  `git checkout`. A validation harness that deletes its own project on failure is
  worth a ticket; I did not file one because my deferment budget was spent.
- I changed nothing inside the home itself, so there is nothing to `unit publish`;
  every skill edit in this PR is a tracked file in the repository.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DUdxjqPbjrJ45Bpxw8uZeS


---

## Correction: my "sibling worktrees have no Skill Manager home" claim was wrong

I reported that `wt-337`, `wt-338`, `wt-339` and `wt-343` had no `.skill-manager`
at all. **That is false as a standing claim and I withdraw it.** All eight
worktrees have a home, each with 15 skills and 4 plugins, and three of those
agents have since run `home close-out` against theirs with clean verdicts.

What I actually ran, and why it read as absent — this was **a race I mistook for
a property**, not a lookup error:

```
ls -a <worktree> | grep -E '^\.(skill-manager|claude|codex|gemini)$'
ls <worktree>/.skill-manager/skills
```

The first printed nothing and the second printed
`No such file or directory`. Both were **true at the instant I ran them**.
Directory creation times explain why:

```
wt-351-plugin-plumbing (mine)   07:42:32
wt-337-improvement-record       07:42:45
wt-339-skills-propose           07:43:15
wt-343-plugin-evals             07:45:45
wt-338-close-out-owes-change    07:47:01
```

I ran those checks at roughly **07:42**, while investigating my own failed
`skt ticket new` — before or within seconds of my own home being written. At that
moment the sibling homes genuinely did not exist: `wt-343`'s appeared three
minutes later, `wt-338`'s four and a half. The sibling tickets were
mid-provisioning.

So the observation was accurate and stale within minutes, and the error was
promoting **a point-in-time sample to a durable fact** — without re-reading before
writing it down, and without recording *when* I had looked. That is
`single-example-generalisation` in a new costume: one reading, reported as a
property.

**Why this belongs in this ticket specifically.** It is the same class SI-11 owns:
*a check that reports absence for the wrong reason.* It sits beside the three this
PR already fixes — the `/specs/` exclude rule that hid files while `git status`
stayed clean, the selftest that died at step 15 and exited 0, and the stale
binding that resolved to a retired copy instead of erroring. In every one, the
negative result was indistinguishable from the healthy one. Mine differs only in
that I was the instrument.

The cheap generalisable fix, which I would rather offer than an apology: **an
observation about another agent's in-flight workspace needs a timestamp and a
re-read before it becomes a claim.** A bare `ls` of a directory being provisioned
concurrently answers "not yet" and "not ever" identically.

Nothing in my slice depended on this. No evidence, validation result, or finding
in this PR is affected.


---

## Reconcile onto the final wave tip

Merged, **not rebased** — this branch is published under an open PR, and rebasing
would rewrite sealed evidence commits. Merge commit `d306daa8`, parents
`bf2c5650` (this branch) + `c987fcf7` (the tip after SI-04 #353, SI-05 #354,
SI-10 #355 and SI-06 #352 landed).

Exactly one conflicted path, as predicted: `specs/results/deferred_findings_final.yaml`,
where five branches appended to the end of the same 45-row cumulative file from
the same base.

**Resolved deterministically, not by hand** — copying SI-06's method, because git
aligns similar YAML structures against each other across several marker regions
and hand-resolving invites silently dropping or re-templating a row. Both sides
were first *proven* to be pure tail-appends over the base (`head -n <base-lines>`
of each side is byte-identical to the base), so the result is literally
`tip ++ my_block`, where `my_block` is this branch's own bytes beyond the base.

| Check | Result |
|---|---|
| Lines present in a parent but absent from the result | **0 vs ours, 0 vs theirs, and 0 vs the merge base** — the check a row count cannot make |
| Rows / unique ids | **58 / 58**, no duplicates |
| Nothing re-templated | tip's 53 rows and this ticket's 5 rows each **byte-identical** to their staged originals |
| Conflict markers | 0 |
| Parses | `uv run --with pyyaml` (plain `python3 -c "import yaml"` fails in these worktrees) |

45 shared + SI-04's 4 + SI-10's 1 + SI-06's 3 + SI-11's 5 = **58**. Nothing
renumbered.

**No suites re-run.** This is a YAML append, and the epic agent has already
verified this branch's evidence: 0 new failures by name, three graphs green, and
`SIS-W2-F-05` going from `15 installed / 2 failed` to `17 installed / 0 failed`.

### Three notes for finalization

**DCO is red on this PR and it should stay that way for now.** The bot's remedy is
`rebase --signoff` plus a force-push, which would rewrite the sealed evidence
commits this ticket's close record points at. The branch is unprotected so the
check is advisory. It fails identically on every PR in this epic, including the
ones already merged — this is an epic-wide finalization decision for the owner,
not something to fix on one branch.

**The scratchpad collision at 08:32 was mine.** SI-06 found that our scratchpad
directory is shared across concurrent agents and that several of us wrote the
generic filename `pr-body.md`; the write that overwrote its copy was this
ticket's. It caught it only by grepping the file before use. I have moved to
`si11-` prefixes for every temp file. Worth recording that this is the *same
class* as the two defects this PR fixes and the one it corrects — a shared
mutable namespace where the wrong answer is indistinguishable from the right one,
and nothing announces the collision.

**One thing to re-measure, which I am deliberately not reporting as a result.** A
suite run against an earlier, since-discarded merge showed two failures beyond the
tip's known set, both citation checks on `skills/spec-double-2/scripts/improvement_ledger.py`
— a file this ticket never touches and that arrived with SI-10:

```
tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[skills/spec-double-2/scripts/improvement_ledger.py]
tests/test_source_citations.py::test_no_citation_leaves_its_file_to_the_reader[skills/spec-double-2/scripts/improvement_ledger.py]
```

That run is **void** — it validated a discarded merge and its tree was mutated
mid-run — so the numbers mean nothing and I am not presenting them as evidence.
But the two names are specific and inherited, and SI-05's attached baseline
predates SI-10's merge, so nothing in the wave has yet measured the tip *with*
that file present. Cheap to settle: run those two node ids on the integrated tip.

