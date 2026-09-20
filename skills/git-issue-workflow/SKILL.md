---
name: git-issue-workflow
description: >-
  Use when handed a GitHub issue to implement — a body, a URL, a bare "#N", or
  `gh issue view` output — or asked to start, pick up, complete or close out a
  ticket, including one assigned from a shared epic workflow. Ships the worktree
  front door every ticket starts and ends with: `skt ticket new|close`, or this
  skill's `scripts/wt`. Read before touching the repo — a
  `git-epic-workflow:assignment` marker selects epic mode. Trigger on "implement
  this issue", "complete this ticket", "work this epic ticket", "run the
  evaluation ticket", "open the MR", or receiving an agent-tagged PR.
skill-imports:
  - unit: tla-spec-dev
    path: skills/git-issue/SKILL.md
    reason: This skill executes the worktree/spec/close-out moves that a git-issue work order names; the issue body is the input to provisioning.
  - unit: tla-spec-dev
    path: skills/git-epic-workflow/references/goals-and-evaluation.md
    reason: Source of truth for goal field names and semantics — goal kinds, contribution kinds, baselines, and the evaluation-ticket contract this skill consumes from the assignment's `goals:` block.
  - unit: tla-spec-dev
    path: skills/spec-double-2/SKILL.md
    reason: The spec workflow — open/close ticket, spec-unit-tests, current→desired promotion — runs through the tla-spec-dev CLI this skill installs.
  - unit: tla-spec-dev
    path: skills/test-graph/SKILL.md
    reason: The validation loop runs named test_graph graphs (incl. the spec graph) via the test-graph scripts and its smart failure loop.
  - unit: deploy-helm
    path: SKILL.md
    reason: Tickets touching deployable surfaces validate against deploy-helm environments inside the test graph.
  - unit: tla-spec-dev
    path: skills/skill-manager/references/workflows.md
    reason: This skill is installed and synced as a skill-manager unit.
---

# git-issue-workflow

The **implementer side** of `git-issue`. A work order names the moves — worktree,
spec workflow, regression graphs, close-out; this skill runs them. An epic
assignment stops at a PR into its shared epic branch; an ordinary ticket runs end
to end, and an integration repo fans out to every constituent.

## The one command: `wt`

First and last thing every ticket does. Ask the shell, do not look around:

```bash
command -v skt    # prints a path -> use `skt ticket new|close <ticket>` and stop looking
```

`skt` is a **plugin**, so it is never under a home's `skills/` — an agent listing
that directory concludes it is absent from a home that has it. Its whole surface:
`skt ticket new <ticket> [<base>] [--base <ref>] [--path <dir>]` and `skt ticket
close <ticket>`; a dirty parent tree goes through the environment,
`WT_DIRTY_OK=1`. Only when `command -v skt` prints nothing, resolve this skill's
own `scripts/wt` — the two-rung spelling is `references/worktrees.md`
§ *Resolving `wt` when `skt` is absent*.

**`cd` to the path `new` printed** — `<parent>/<repo>-<ticket>`, not
`../wt-<ticket>`, so do not guess it. Anything a caller acts on is a keyed
contract line: `"$WT" info <ticket>`, or `--verbose` on the creating run, which
is the only run that measured `BASE`.

**Do not substitute `git worktree add`.** It produces a worktree with no Skill
Manager home, and an agent launched there writes the operator's global
`~/.skill-manager`. Do not substitute `git worktree remove` either: it deletes
the home, and every unpushed skill edit in it, without a word.

Same command in a plain repo, an integration repo, and a constituent of one.
A failure is three lines and the second runs **as printed** (`fix:`). What each
provisioning exit means — **3** no project home yet, **7** the base is behind its
remote, **1** the parent tree is not clean, **79** a home mismatch — is
`references/worktrees.md` § *The exit codes `wt new` refuses with*. Never stash,
commit or discard someone's edits to get past exit 1, and never upgrade
skill-manager to get past 79.

## Reaching a by-hand route is itself a finding

This skill spells out a manual equivalent in two places: the chained `git
worktree add && bootstrap-home.sh` in `references/epic-ticket.md` §2, and the raw
`home close-out && git worktree remove` under close-out step 4. Each is written
for a repository that genuinely has no front door — **and because each one works,
an agent that merely could not *find* the front door lands on it, produces a
plausible result, and leaves no trace but the cost.** Four eval runs did exactly
that, for four different reasons, and none reported a problem.

So run `command -v skt` first. If it printed nothing and neither `wt` path
exists, the by-hand route is correct and there is nothing to report. If either
resolved and you are on the by-hand route anyway, say so in one line, naming
which: `skt` installed but not on `PATH`; you looked where a plugin never is
(`skills/`); you found it and it **failed** (quote its `error:` line verbatim);
or you found it and could not read the home it pointed at. All four are
front-door defects, not facts about the repository. Put the line in the PR body,
or to the user when there is no PR, and file it against this skill.

## A blocker you met is a change you propose

Whenever something in the substrate blocked you — this skill, a script, the CLI,
a validator, an unrunnable instruction — the PR body carries a `## Skill changes
proposed` section: one row per blocker you actually met, three columns (the unit,
what you hit, the proposed change as a diff or the commit that applied it).

`none met` is legitimate and common, and it is written rather than left out. Run
nothing new for it — every row already happened while you did the ticket. Apply
the change where the unit is a file in this repository and inside your conflict
keys; otherwise put the diff in the row. Being blocked from fixing it is still a
row. Nothing blocks on it. Worked examples: `references/complete.md` §5a for an
ordinary ticket, `references/epic-ticket.md` §7 for an epic ticket.

## Select epic mode before any provisioning

Read the complete issue body before choosing a branch, worktree, repository mode
or spec command. Search for `<!-- git-epic-workflow:assignment:start -->`.

- **Marker present:** epic ticket mode. Follow `references/epic-ticket.md`
  instead of Role 2, Role 3, the ordinary close-out, or integration fan-out. The
  assignment's declared branch, worktree, ticket, validation, promotion and PR
  base are authoritative, even when the checkout also has integration markers. A
  `ticket.role` of `evaluation` decides goals rather than producing a behavioral
  delta — read `references/goal-signal.md` too. Where the plan carries
  `planning_rules.model_ownership_rule` the **epic owns the model**: you run
  neither `open ticket` nor `close ticket` nor `--accept-new`, you move `current`
  toward `desired`, correct `desired` only in small ways, and return structural
  changes in the PR.
- **Marker absent:** continue with the PLAIN/INTEGRATION detection below.

Do not scaffold a workflow, create a default-branch worktree, or run an
integration provisioning script until this check is complete.

## Three load-bearing rules for ordinary and integration tickets

1. **Operate specs and the test graph only from the parent.** When the ticket
   spans sub-repos, run the TLA+ workflow and the `test_graph` graphs **once, at
   the integration parent**. Constituents re-run their own loops after fan-out.
2. **Same branch name everywhere** — one ticket id drives `feature/<ticket>` on
   the parent and every constituent.
3. **A ticket lives in a worktree, never the primary checkout.**

## Your Skill Manager home IS the worktree's

Three tiers, each a real copy, not a symlink: root `~/.skill-manager` → project
`<repo>/.skill-manager` → worktree `<worktree>/.skill-manager`, yours for this
ticket and gitignored. Copies, because a link is one shared object and two
tickets editing "their" copy would be editing each other's.

Two consequences, neither optional. **Launch through the home's shims**,
`<worktree>/.skill-manager/bin/launch/{claude,codex,gemini}`, or `skill-manager
exec` — exporting `SKILL_MANAGER_HOME` by hand gets you only the part you
remembered. And **an edit to a skill inside that home is in no diff**: the home
is gitignored, the PR cannot carry it, and `git worktree remove` deletes it
without a word. Getting it out is close-out step 4, and it is a gate.

Downward is a copy and needs nothing from you; **upward is the whole difficulty**.
Why the isolation needs the shims, what a home inherits versus declares, and how
to tell a broken home from a healthy one: `references/skill-homes.md`. **Do not
diagnose a new worktree home from the CLI source.**

## Is this an integration repo?

```bash
test -f INTEGRATION.md && test -f integration.toml && echo INTEGRATION || echo PLAIN
```

**PLAIN** → one worktree, one feature branch, one PR via `gh`. **INTEGRATION** →
one parent worktree spanning constituents, the spec/graph loop at the parent
only, then fan-out. The worktree command is the same in both; this fork decides
spec/graph scope and whether there is a fan-out.

## Ordinary close-out sequence

An unmarked ticket is done when these five moves have happened, **in order** — no
exceptions, no leaving a PR "ready for someone to merge later". Epic tickets do
not run this sequence. Each step in full, including the INTEGRATION variant, is
`references/complete.md`.

1. **Close every open spec ticket, then the workflow** with the `tla-spec-dev`
   CLI — each ticket still open in `ticket_plan.yaml` by id, not just the last —
   then `close_tickets.py` to promote.
2. **Commit and push** implementation, spec changes and evidence together.
3. **Rebase-merge the PR into `main` with `gh`** — land it yourself. A declared
   goal also puts `## Goal contribution` in the PR body.
4. **Close out the worktree's home, THEN remove the worktree, then sync the root.**
   The gate runs *before* the removal — after it there is nothing left to save.
   `"$WT" close <ticket>` does both and removes only on a clean verdict; two
   commands on separate lines would run the removal whatever the gate returned.
   Exit 0 is the only "proceed".
5. **Close the GitHub issue with `gh`** — confirm a `Closes #<n>` merge did it,
   do not assume.

**INTEGRATION repos** skip step 3's `gh pr merge` — land it with `git merge
--no-ff` and `verify.sh` — but still run 1, 2, 4 and 5 at the parent, then fan
out (`references/integration-fanout.md`).

## Reference map

| You are… | Read |
|---|---|
| Assigned one ticket from a shared epic workflow | `references/epic-ticket.md` |
| Kicking off a ticket (Role 2: provisioning, index-base pinning, opening the workflow) | `references/provision.md` |
| Completing a ticket (Role 3), or reading a `wt close` exit | `references/complete.md` |
| Running the green loop — at most two laps per layer, then record what stayed red | `references/validation-loop.md` |
| Fanning out to sub-repos | `references/integration-fanout.md` |
| Handed an agent-tagged PR | `references/agent-tag-pr.md` |
| A ticket that declares a goal, or whose slice **is** the measurement | `references/goal-signal.md` |
| Resolving `wt`, or reading a `wt new` refusal | `references/worktrees.md` |
| Working on, or debugging, a per-checkout Skill Manager home | `references/skill-homes.md` |

## Boundaries

- This skill **executes** a ticket; it does not author the issue. Issue creation,
  the References section and the spec-required decision are `git-issue`'s.
- It does not create or amend an epic assignment. In epic mode it consumes the
  assignment, stops only when the PR base or branch would be wrong, and otherwise
  proceeds on the plan's values, listing any mismatch in the PR. `SKILL_GATES=off`
  lets `wt new` proceed from a dirty parent tree and forces the tla-spec-dev
  close gates; `wt close` still takes an explicit `--force`.
- It does not reimplement the spec, test-graph or fan-out mechanics — it
  **sequences** them, from `spec-double-compiler`, `test-graph` and
  `git-integration-repo`.
- The **worktree lifecycle it does own**: `scripts/wt`, `new-change.sh`,
  `close-change.sh`, `bootstrap-home.sh`, `agent-home.sh` and `lib.sh`, because a
  ticket and a worktree exist for every repo while an integration repository is a
  specialization. They used to live in `git-integration-repo`, and an agent
  working a plain repo — reading that skill's description and correctly
  concluding it was irrelevant — never learned `wt` existed and wrote its own
  worktree script. The dependency runs specialized → general:
  `git-integration-repo` → `git-issue-workflow` → `git-issue`.
- It never runs per-constituent specs/graphs during a ticket.
- It does not invent goals, baselines or targets, and never edits one to match a
  result. **It does not tune to a metric**: the local signal is measured,
  recorded and reported — never gated on, never re-run for a better number, never
  a reason to widen scope or weaken a REQUIRED validation entry. A goal
  unreachable from this slice is a deferred finding for the plan owner.
