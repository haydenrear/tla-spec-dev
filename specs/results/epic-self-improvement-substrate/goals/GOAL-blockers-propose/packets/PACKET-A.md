======================================================================
SUBJECT: pull request #349 (ticket SI-01), subject_shape=ticket
======================================================================

ITEM 1 — THE PULL REQUEST BODY, VERBATIM
----------------------------------------------------------------------
SI-01: migrate the skill surface into a plugin (`tla-spec-dev` / `skills/spec-double-2`)

Refs #333. Epic `self-improvement-substrate`, branch `epic/self-improvement-substrate`,
workflow `self-improvement-substrate`, assigned spec ticket `SI-01`, wave 1.

Base: `epic/self-improvement-substrate` @ `4d563e2d` (still the remote tip at PR time —
re-checked after implementation, so no reconcile was needed).
`depends_on: []`, `promotion_predecessor: null` — nothing to wait for.

## What moved

The repo root is now a skill-manager **plugin**: `.claude-plugin/plugin.json` +
`skill-manager-plugin.toml` (`tla-spec-dev` 0.1.0, names and versions agree, checked).
The skill surface — `SKILL.md`, `references/`, `scripts/`, `templates/`, `prompts/`,
`spec_double_compiler/`, `skill-scripts/`, `skill-manager.toml` — moved to
`skills/spec-double-2/` as 101 detected renames. The root keeps `tests/`, `specs/`,
`examples/`, `test_graph/`. The `spec_double_compiler` package and the `tla-spec-dev`
CLI keep their names, as decision 2 of the kickoff review requires.

`integration.toml` was **not** added — see *Decisions and overrides*.

## Validation

| matrix entry | command | result |
|---|---|---|
| repository_unit | `uv run --python 3.12 --with pytest ... -m pytest tests -q --ignore=tests/test_score_tools.py` | **10 failed, 1551 passed, 5 skipped — zero new**, identical counts and identical failure IDs to the pre-move baseline (`comm -13` of the two lists is empty) |
| spec_unit | assignment's `... --ticket SI-01` **errors** (no such workspace); ran `... run spec-unit-tests --scope project` instead | 7 failed, 49 passed — **byte-identical to the same command on a pristine `git archive` of `4d563e2d`**, so the red is pre-existing, not this ticket's |
| graphs | `specWorkflow`, `cliWorkflow`, `effectProviderExamples` | **all three BUILD SUCCESSFUL.** `effectProviderExamples` failed twice first, and the first failure was mine (see *Where I'd look for bugs* #1) |
| `test_score_tools.py` (the "run once before close" file) | `... -m pytest tests/test_score_tools.py -q` | 1 failed → fixed → that test green on a targeted re-run. A pre-move baseline of the same file is **116 passed**, which is what establishes the failure was *mine* rather than pre-existing |
| tlc | `N/A` — the epic agent owns the model for this epic | not run by this ticket |

Evidence: `specs/results/epic-self-improvement-substrate/tickets/SI-01/`.

**The red floor is pre-existing, and it was measured rather than asserted.** The suite ran
on the pinned base BEFORE any file moved: **10 failed, 1551 passed, 5 skipped**
(`pytest-before-migration.txt`). The move initially produced **26 new failures**; all 26
are fixed, and the final run reproduces the baseline exactly. The spec-unit floor was
measured the same way, on a pristine `git archive` of `4d563e2d` extracted outside the
worktree (`spec-unit-baseline-at-4d563e2d.txt`). Those same 10 are still red and are not
this ticket's:
three stale `spec_manifest.yaml` citations, the corpus/verdict gate pair, the instrument
fast-demonstration slot, `test_the_same_tag_control_holds`, and ticket-retirement receipts.

## Goal contribution

| goal | kind | expected effect | measured | classification | decided by |
|---|---|---|---|---|---|
| `GOAL-one-unit` | enabling | none on its own — it unblocks SI-02, which is what moves the unit count | `python3 skills/spec-double-2/scripts/tla_spec_dev.py --help` and `--version` both exit 0 from the checkout (`local-signal-GOAL-one-unit.txt`), and all three declared graphs are green | **no measurable movement** — as expected for an enabling slice | SI-08 |

The installed-unit count is unchanged by this PR and is meant to be: nothing is installed
or uninstalled here. `skill-manager install --dry-run <checkout>` resolves the repo through
the **plugin** path ("reject if a contained skill name is already claimed"), which is the
property SI-02 needs.

## A structural finding for the epic agent

**`specs/tickets/SI-01/` does not exist on the epic branch.** The assignment's
`validation.spec_unit` command is
`... run spec-unit-tests --ticket SI-01`, and it exits with
`ERROR: spec-unit target does not exist: .../specs/tickets/SI-01/desired`.
The *Model ownership* block says the epic agent "scaffolds this ticket's `desired` and
`current` state before dispatch"; that did not happen for SI-01. Per the same block I did
not run `open ticket`, so I did not create it. I ran the spec units at **project scope**
instead and recorded that. This is reported rather than repaired — creating the ticket
workspace is the epic agent's move, not mine.

## Deferred findings

| ID | severity | summary |
|---|---|---|
| `SI-01-DF-01` | minor | Sealed analysis scripts under `specs/results/scorecards/**` find the repo by walking for `references/eval_scorecard.md`, which moved. Three were made tolerant because a test executes them; the rest were left sealed, including a `stage_judge_trees.sh` `rm -f` that now removes nothing. |
| `SI-01-DF-02` | minor | `examples/effect_providers/PREREGISTRATION.yaml` still names pre-migration `forbidden_rescue_surfaces`; the two live guards enforcing it were repointed (they are git pathspecs and would otherwise match nothing), so document and code now disagree. |

Appended to `specs/results/deferred_findings_final.yaml` (35 → 37 rows; cumulative file,
appended, never re-templated). Budget 5, mode `batch` — 2 used.

## Skill changes proposed

`none met` — no blocker in the substrate stopped this ticket. Two notes that are *not*
blockers but are the kind of thing SI-06 will want:

- `git-issue-workflow` / `git-epic-workflow` say the ticket agent opens its own spec
  ticket; this epic reverses that. The reversal is in the issue body and in
  `planning_rules.model_ownership_rule`, and SI-07 already owns writing it into the skill.
  Nothing to propose beyond what SI-07 has.
- `skt ticket new` worked first time here **because** the kickoff had already found the
  exported-`SKILL_MANAGER_HOME` trap and the issue documents the remedy. See
  *Machinery friction*.

## Review input

### Hot spots

- `skills/spec-double-2/scripts/scaffold_spec.py` — `SKILL_ROOT_BOOTSTRAP`. The
  enclosing-checkout candidate now also tries `<parent>/skills/spec-double-2`. Without it
  the reference example imports an **installed** skill instead of the checkout, silently
  retiring `G-12`. `examples/distributed_history/specs/program_model/adapters.py` carries
  the byte-identical block and both are pinned by
  `tests/test_reference_adapters_carry_the_bootstrap.py`. **Read this one first.**
- The home-resolution order also gained the plugin path
  (`<home>/plugins/tla-spec-dev/skills/spec-double-2`) ahead of the old standalone path,
  which is kept for one release. `references/runtime_requirements.md` documents it.
- `specs/{program_model,current,desired_program_model}/{production_adapters,adapter_case_runtime}.py`
  — `repo_root()` used to key on `skill-manager.toml` at the root, which moved. It now
  keys on `skills/spec-double-2/scripts/tla_spec_dev.py`. All three copies were identical
  before and after.
- **Silent-vacuity class.** Several declared scopes are matched as strings against the
  tree, so a stale prefix does not fail — it stops matching anything: the instrument
  registry's `[registry.enumeration] roots`, the A/B `FORBIDDEN_FRAMEWORK_SURFACES` git
  pathspecs, `subjects.toml` scopes, `EXECUTABLE_SURFACES`, `CITATION_SCOPE`. Each was
  repointed. A reviewer who wants to check one thing should check these.
- `tests/conftest.py` puts both roots on `sys.path`; ~42 test modules gained
  `SKILL_ROOT`.
- **9 files under `examples/effect_providers/` and `examples/validation/ab/eval/`** now add
  the skill root wherever they added `REPO_ROOT`, because that insertion is what made
  `import spec_double_compiler` work. This is the change that took `effectProviderExamples`
  from red back to green, and one of its edits landed as an `IndentationError` that only a
  compile sweep caught — so every `.py` I touched (118) is now checked with
  `python -m py_compile`.

### Decisions and overrides

- **`integration.toml` / `INTEGRATION.md` not added**, although the issue's prose Summary
  names `integration.toml`. The canonical plan's `implementation_scope` lists only
  `.claude-plugin/plugin.json` and `skill-manager-plugin.toml`, and per `epic-ticket.md` §1
  the plan wins on mismatch. Adding both markers would flip every later ticket into
  `git-issue-workflow`'s INTEGRATION mode before any constituent exists. SI-02 nests the
  five skills and is where those markers earn their place.
- **The contained skill is named `spec-double-2`** (`SKILL.md` frontmatter and
  `skill-manager.toml`), per kickoff decision 1. The package and CLI keep their names.
- **Three sealed analysis scripts under `specs/results/` were edited** to accept either
  card location, because a live test executes them. Everything else under `specs/results/`
  was left as sealed record and filed as `SI-01-DF-01` instead.
- **The old install coordinate stays resolvable for one release**: the resolver still
  tries `<home>/skills/spec-double-compiler` after the plugin path. The issue allowed
  either that or recording why not.
- `skill-project.toml` `[project] name` is now `tla-spec-dev`.
- **A declared measurement scope was changed**, which is more than a path edit and is worth
  a reviewer's eye: `examples/validation/scorecards/subjects.toml` declares
  `rm04_scripts` with `scope = ["scripts"]`, and that scope is what the complexity
  instrument is pointed at. Left alone it would have aimed at a directory that no longer
  exists and the measurement would have gone quietly vacuous, so it now reads
  `skills/spec-double-2/scripts`. `test_score_tools` pinned the old literal and was updated
  with it. The scope is deliberately visible on a blinded card ("what to read: kept"); the
  new path names the **skill**, never the arm label, so nothing identifying is disclosed.
- No guardrail was weakened: no test skipped, no matrix entry downgraded, no
  `--force` / `SKILL_GATES=off`, no `--accept-new`, no `open`/`close ticket`.

### Where I'd look for bugs in my own change

1. **The example import-path class — this one already bit me.** Every
   `examples/effect_providers/*` runner and test put `REPO_ROOT` on `sys.path` for one
   reason: to make `import spec_double_compiler` resolve. The package moved, so the
   import died, and `effectProviderExamples` went red. Fixed by adding
   `SKILL_ROOT = REPO_ROOT / "skills" / "spec-double-2"` at all 9 injection sites. It is
   first on this list because a *string* path that stops matching fails loudly here but
   silently elsewhere, and I found these one graph run at a time rather than by
   enumeration. Cheapest experiment: `git grep -n 'sys.path.insert(0, str(REPO_ROOT))'`
   over `examples/` and check each hit is paired with a `SKILL_ROOT` insert — it is, 5 of
   5, but a 10th site that spells the insertion differently would not show up.
2. **The two-candidate resolver, in a downstream project.** In this repo it is exercised
   constantly; in an adopter's tree neither candidate matches and it must fall through
   unchanged. Cheapest experiment: scaffold a project outside this checkout and import its
   `adapters.py` with no home reachable — `specWorkflow`'s `reference_adapters_resolve`
   node does exactly this and is green, but only for the in-repo shape.
3. **Doc command paths rewritten by regex.** I repointed `python3 scripts/...` forms across
   README/references/prompts/templates. A downstream reader's command is `tla-spec-dev`,
   not a repo-relative path, so a line that was *already* about an adopter's tree may now
   read as if it were about this one. Cheapest check: grep the docs for
   `skills/spec-double-2/` in any paragraph addressed to an adopter.
4. **The citation path rewrite.** `--fix` repairs numbers, never paths, so I repointed the
   paths by regex in the three `spec_manifest.yaml` and three `TlaSpecDevCli.tla` copies
   and then ran `--fix`. Checked tool-against-tool: the checker run in a pre-move checkout
   of `4d563e2d` and the checker run here both emit 23 lines, and the two outputs are
   **identical once the `skills/spec-double-2/` prefix is normalized away**
   (`citations-vs-4d563e2d.diff`) — the evidence that I moved paths without moving lines.
   Worth naming how close this came to being reported wrong: I first "compared" the counts
   with two different `grep` patterns, got 21 against 22, and nearly wrote that down as a
   change. The numbers were not comparable; only running the same tool on both trees was.
5. **`skill-script:` resolution for a *contained* skill.** `skill-scripts/` sits under the
   contained skill, which is what `references/skill-scripts.md` specifies
   (`<skill>/skill-scripts/`), and `plugins.md` separately describes a *plugin-level*
   `skill-scripts/` for plugin-owned CLIs. I did not install the plugin into a real home,
   so the end-to-end install path is verified by the graph's install node and by
   `--dry-run`, not by a live `skill-manager install`.

### Machinery friction

- **`skt ticket new` worked in one command** — declared path, pinned base, retention ref
  and the worktree's own home together. I was *not* on the by-hand
  `git worktree add` + `bootstrap-home.sh` route. `SKILL_MANAGER_HOME` was already unset in
  my environment, so the kickoff's rollback did not recur.
- **`command -v tla-spec-dev` resolves to the operator's root-home shim**, not this
  checkout (`SIS-KICKOFF-F-02`, already filed). I used
  `python3 skills/spec-double-2/scripts/tla_spec_dev.py` throughout. After this PR that
  installed shim points at a path that no longer exists in an un-synced home, which makes
  the already-filed finding sharper rather than new.
- **The migration checklist really is a grep, and the grep is not sufficient.** The issue's
  grep finds the *named* paths. It does not find the resolvers that locate the repository
  by *walking up for a marker that moved* — `references/eval_scorecard.md` (score_tools,
  architecture_tags, three sealed analysis scripts), `skill-manager.toml` (the spec
  adapters), and a `spec_double_compiler` sibling directory (the scaffold bootstrap). Those
  produced 26 of the 26 new failures, and every one of them failed at a distance. A
  "markers a tree is located by" list belongs in the substrate.
- `--tb=line` on a 5-minute suite, then one file at a time, was the only way to separate my
  breakage from the 10 pre-existing failures. Recording the baseline suite BEFORE touching
  anything was the single highest-value thing I did.

## home close-out

**Clean — the gate was already green.** Run read-only as

```
<main-working-tree>/.skill-manager/bin/cli/skill-manager home close-out \
    --home ../wt-334-plugin-migration/.skill-manager \
    --into <main-working-tree>/.skill-manager --json
```

→ `"safe": true, "exitCode": 0, "blockers": []`, with all 28 units reporting
`unchanged — already byte-identical to the source`. I changed no skill inside my worktree
home, so nothing was published with `unit publish` and there is nothing in that home for
the wave-close reconciliation to carry.

Worktree `../wt-334-plugin-migration` is left standing for the epic agent to reconcile and
sweep. No `home sync` into the project home was run.

## Reconcile onto `56227e50`

The epic tip moved after this branch was cut. **Merged, not rebased** — both evidence
commits were already pushed under this PR, and rebasing would rewrite them.

**One conflicted path**, `specs/results/deferred_findings_final.yaml`, resolved by taking
the epic's file whole and appending this ticket's two rows, so no pre-existing row and no
row of the epic agent's can be touched by construction: 35 shared + `SIS-KICKOFF-F-03` +
`SI-01-DF-01` + `SI-01-DF-02` = **38 rows**, parses, no duplicate IDs, **zero deleted or
changed lines against either parent**.

### The scaffolded ticket workspace was broken by this migration — repaired here

`specs/tickets/SI-01/desired/` was scaffolded from the **pre-migration** model, so on this
branch it could not locate the toolchain at all:

| | before | after |
|---|---|---|
| `could not locate tla-spec-dev repository root` | 94 | **0** |
| result | 47 failed, 6 passed | **7 failed** |

Those 7 are the **identical set** (path-normalized) to the pristine `4d563e2d` baseline.
The repair is provable rather than asserted: the two files were byte-identical to the
*pre-migration* `program_model` before and are byte-identical to the *fixed* one after — no
action, state, invariant or test semantics changed. Under `model_ownership_rule` this is
the "small correction" a ticket agent may make to `desired/`, and it reverts with one
`git checkout` if the epic agent disagrees.

### Substrate finding this surfaced (not filed as a row — the epic agent fixed the total at 38)

`run spec-unit-tests --ticket <id>` **resolves 2 targets and executes 1**. The loop is
`for label, command, env in commands: ... if result.returncode != 0: return result.returncode`
and `specs/current` is ordered first, so its 7 pre-existing failures mean the ticket-local
target is never reached. On this repository that command cannot validate a ticket
workspace, and it prints no indication that a target was skipped — the reason this PR
measures the ticket target with `--target` directly. It affects all ten tickets, not just
this one.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DUdxjqPbjrJ45Bpxw8uZeS



ITEM 2 — THE SUBJECT'S OWN COMMITS (git log --stat)
----------------------------------------------------------------------
commit 058beb3d514fe0968ccf937d386928e560169eb6
Merge: 56227e50 5b929e17
Author: Hayden Rear <hayden.rear@gmail.com>
Date:   Thu Sep 17 16:53:36 2026 -0400

    Merge pull request #349 from haydenrear/feature/334-plugin-migration
    
    SI-01: migrate the skill surface into a plugin (tla-spec-dev / skills/spec-double-2)


ITEM 3 — THE BACKLOG ROWS THIS SUBJECT FILED
----------------------------------------------------------------------
[
 {
  "id": "SIS-KICKOFF-F-03",
  "found_by": "SI-01 ticket agent; confirmed by the epic agent",
  "found_at_commit": "09d8108d",
  "schedule_revision": 1,
  "severity": "major",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "The epic agent's own defect, found by a ticket agent. All TEN assignments carry `spec_unit: ... run spec-unit-tests --ticket <id>`, but that command reads `specs/tickets/<id>/`, which only `open ticket <id>` creates -- and this epic's model_ownership_rule reserves `open ticket` to the epic agent, which never ran it. So the REQUIRED spec-unit entry was unrunnable as written for every ticket in the epic, from dispatch.",
  "reproduction": "On the epic branch at 4d563e2d: `ls specs/tickets/` shows MF-021, MF-027, RD-06 and no SI-* workspace, while every issue body from #334 to #343 names `--ticket SI-0N` in its validation matrix.",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-01/spec-unit-tests.txt",
   "specs/results/epic-self-improvement-substrate/tickets/SI-01/spec-unit-baseline-at-4d563e2d.txt"
  ],
  "why_out_of_scope": "Not in SI-01's slice: the ticket agent could not fix it without running a command the ownership rule forbids it. It reported the gap and ran the spec units at project scope instead, which is the correct behaviour and exactly what the epic wants a blocked agent to do.",
  "suggested_fix": "The epic agent scaffolds each ticket's workspace BEFORE dispatching it -- that is what model_ownership_rule already promises (\"scaffolds this ticket's desired and current state before dispatch\") and what was not done. SI-07 should make the promise checkable: validate_epic_plan.py warns when a ticket's assignment names --ticket <id> and no workspace exists on the epic branch.",
  "blast_radius": "All ten tickets. Left alone, every ticket agent either reports the same gap or silently substitutes a different command, and the REQUIRED matrix stops meaning anything. SI-01's workspace was scaffolded at wave-1 review; the remaining nine are scaffolded before their waves dispatch.",
  "disposition": "pending",
  "disposition_ticket": null,
  "disposition_note": "The first evidence FOR this epic's thesis: the substrate got a defect reported rather than worked around, by an agent that could not fix it itself. Instrument change belongs to SI-07 (#340)."
 },
 {
  "id": "SIS-KICKOFF-F-04",
  "found_by": "SI-01 ticket agent; source verified by the epic agent",
  "found_at_commit": "5b929e17",
  "schedule_revision": 1,
  "severity": "major",
  "surface": {
   "production": [
    "skills/spec-double-2/scripts/tla_spec_dev.py"
   ],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "`run spec-unit-tests --ticket <id>` resolves BOTH targets and executes only the first. It builds commands for every target, prints a \"spec-unit target:\" line for each, then runs them in a loop that returns on the first nonzero exit. `specs/current` is ordered first and carries 7 pre-existing failures in this repository, so the ticket-local target is never executed -- and nothing in the output says a target was skipped. The REQUIRED spec_unit entry of all ten assignments is therefore weaker than it reads: it can only ever report the project-scope result.",
  "reproduction": "skills/spec-double-2/scripts/tla_spec_dev.py, run_spec_unit_tests, the execution loop verbatim: `for label, command, env in commands: result = subprocess.run(command, cwd=repo_root, env=env); if result.returncode != 0: return result.returncode`. Run `run spec-unit-tests --ticket SI-01` on 058beb3d: the output lists two spec-unit targets, exits after the first, and the ticket target's tests never run. Measuring the ticket target needs `--target` directly.",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-01/reconcile-spec-unit-ticket-SI-01.txt",
   "specs/results/epic-self-improvement-substrate/tickets/SI-01/reconcile-ticket-target-after-repoint.txt"
  ],
  "why_out_of_scope": "Outside SI-01's slice, and the ticket agent deliberately did not file it: the epic agent had fixed the post-merge backlog total at 38 rows, and adding a row would have contradicted that instruction. Filed here by the epic agent instead, which is the right division -- the agent reported it with evidence and left the record to the owner.",
  "suggested_fix": "Run every resolved target and aggregate the exit codes, or at minimum name the targets that were skipped. A silent skip is worse than a failure here, because the printed \"spec-unit target:\" line reads as evidence the target ran. Pairs with SIS-KICKOFF-F-03: that one makes a MISSING workspace visible, this one makes a PRESENT workspace actually exercised.",
  "blast_radius": "All ten tickets, and every repository whose specs/current is not green -- the normal state of a repository carrying known failures. Any close-out that cited spec-unit as passing for a ticket target cited a run that did not happen.",
  "disposition": "pending",
  "disposition_ticket": null,
  "disposition_note": "Natural home is SI-07 (#340) with SIS-KICKOFF-F-03. Owner triages at the wave-2 review."
 },
 {
  "id": "SI-01-DF-01",
  "found_by": "SI-01",
  "found_at_commit": "4d563e2d",
  "schedule_revision": 1,
  "severity": "minor",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "Sealed analysis scripts under specs/results/scorecards/** locate the repository by walking their ancestors for `references/eval_scorecard.md`, or name it as a literal. SI-01 moved the card to skills/spec-double-2/references/eval_scorecard.md, so those walks no longer terminate. Three were made TOLERANT of both spellings in this ticket because a repository test executes them (SV-03/analysis/baseline_is_a_card.py, SV-03/analysis/no_card_project_unaffected.py, SV-06/analysis/goal_score_survey.py). The rest were left exactly as sealed: SV-02/analysis/carrier_cost.py (`RUBRIC = pathlib.Path(\"references\") / \"eval_scorecard.md\"`), subtract-to-measure/SM-06/run_dup_mutants.py (`CARD = ROOT / \"references/eval_scorecard.md\"`), and subtract-to-measure-sm05/packet/stage_judge_trees.sh (`rm -f \"$root/references/eval_scorecard.md\"`, which now removes nothing).",
  "reproduction": "python3 specs/results/scorecards/score-drives-validation/GOAL-validation-is-scorable/SV-02/analysis/carrier_cost.py from the repository root after SI-01: the rubric path it names does not exist. The stage_judge_trees.sh case is the quiet one -- `rm -f` on a missing path exits 0, so a judge tree that was meant to have the card removed would now be staged WITH it.",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-01/pytest-after-migration.txt"
  ],
  "why_out_of_scope": "specs/results/** is append-only record and is in no conflict key of this ticket. Editing sealed evidence to satisfy a path move is the opposite of what that tree is for; the three exceptions were made only where a live test executes the script, and each carries a comment saying so.",
  "suggested_fix": "Decide once, for the whole tree, whether a sealed analysis script is expected to remain runnable. If yes, give them the same two-spelling walk the three exceptions now carry. If no, record that they are records rather than tools and stop executing any of them from tests. Do not repoint the literals silently -- that rewrites the record without saying so.",
  "blast_radius": "No shipped behaviour. The stage_judge_trees.sh case could silently weaken a future blind judging round by leaving the card in a tree meant to be without it, which is why this is filed rather than left unsaid.",
  "disposition": "pending",
  "disposition_ticket": null,
  "disposition_note": "Natural home is whichever ticket next touches the scorecard tree; SI-03 builds the improvement card and is the closest. Not retrofitted."
 },
 {
  "id": "SI-01-DF-02",
  "found_by": "SI-01",
  "found_at_commit": "4d563e2d",
  "schedule_revision": 1,
  "severity": "minor",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "examples/effect_providers/PREREGISTRATION.yaml declares `forbidden_rescue_surfaces` as repository-relative paths (scripts/tla_spec_dev.py, spec_double_compiler/**, templates/**). The two live guards that enforce it -- FORBIDDEN_FRAMEWORK_SURFACES in atomic_publisher/run_experiment.py and legacy_payment_http/scripts/run_experiment.py -- were repointed in this ticket because they are git PATHSPECS and a stale prefix matches nothing, making the guard silently vacuous. The sealed preregistration was NOT repointed, so the document and the code that enforces it now spell the same surfaces differently.",
  "reproduction": "diff the `forbidden_rescue_surfaces` list in examples/effect_providers/PREREGISTRATION.yaml against FORBIDDEN_FRAMEWORK_SURFACES in either run_experiment.py after SI-01.",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-01/pytest-after-migration.txt"
  ],
  "why_out_of_scope": "A preregistration is a sealed statement of what was forbidden before a measurement ran. Rewriting it after the fact is precisely the move the preregistration exists to prevent, and it is in no conflict key here.",
  "suggested_fix": "Add a dated migration note UNDER the preregistration saying the surfaces moved and where, rather than editing the list in place. Anyone re-running the experiment reads both.",
  "blast_radius": "None while the experiment is not re-run. If it is re-run without reading this, the guard is correct and the document is misleading about which paths it names.",
  "disposition": "pending",
  "disposition_ticket": null,
  "disposition_note": "Owner triages at the wave boundary; no ticket owns examples/effect_providers."
 }
]

ITEMS THAT DO NOT EXIST FOR THIS SUBJECT (absent, not withheld):
  close_summary
