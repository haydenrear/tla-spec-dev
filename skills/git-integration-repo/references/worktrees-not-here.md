# Worktrees are not here, and why

Moved here from `SKILL.md` by SI-09 (progressive disclosure). The card carries
the rule and the `skt` test; this page carries the fallback command, the
selection failure that forced the split, and the one contribution this skill
still makes to a ticket.

## The fallback, when `skt` is absent

```bash
skt ticket new   TICKET-123   # preferred: on PATH in skt-carrying homes
skt ticket close TICKET-123

# fallback for a checkout without the skt COMMAND — same lifecycle underneath.
# `wt` ships with skt since SI-17; the scripts it delegates to are still
# git-issue-workflow's and it resolves them itself. Two rungs: skt is a
# CONTAINED SKILL of the tla-spec-dev plugin, so its bytes are under
# plugins/<plugin>/skills/, not skills/.
WT="$(for d in "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"/skills/skt "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"/plugins/*/skills/skt; do [ -d "$d" ] && { printf %s "$d"; break; }; done)/scripts/wt"
"$WT" new   TICKET-123     # worktree + its own Skill Manager home, launchable
"$WT" close TICKET-123     # teardown, through the close-out gate
```

**Which of those two, and what it means if you take the second.** skt is a
**plugin**, so it is never under a home's `skills/` — listing that directory
reports it absent from a home that has it. Test by path:

```bash
test -x "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/bin/cli/skt"
```

If it does not resolve, the `$WT` lines are correct and there is nothing to
report. If it resolves and you used `$WT` anyway — or read either script and
replayed its steps by hand — that is a front-door defect, not a fact about this
repository, and it is invisible unless you say so, because the fallback works.
Name which case on the PR (installed but not on `PATH`; looked under `skills/`;
found it and it **failed**, quoting its `error:` line; found it and could not
read the home it pointed at) and file it against the skill that owns the door.
Full statement of the rule: `git-issue-workflow`'s `SKILL.md`, §*Reaching a
by-hand route is itself a finding*.

Its contract, its one-line output, its refusals and the per-checkout home
mechanism are documented in git-issue-workflow's `references/worktrees.md` and
`references/skill-homes.md`; session orientation (what is loaded, which tier,
ticket/epic state) is `skt status`.

## Why they are there and not here

An integration repository is a **specialization**: it exists only when a repo has
constituents. A ticket and a worktree exist for **every** repo. So the general
machinery cannot live in the specialized skill, and the dependency has to run
specialized → general:

```
git-integration-repo  ->  git-issue-workflow  ->  git-issue
```

The failure that forced this was a **selection** failure, not a path failure. An
agent picks a skill by its `description`. This skill's says "onboard several
repos into one integration repo" — so an agent working a plain repo read it,
correctly concluded it was irrelevant, never opened it, never learned `wt`
existed, and wrote its own worktree script, which knew none of the rules those
files hold. Naming a resolvable path inside this page could not fix that: the
agent has to be *told* the command every time and can never *discover* the
capability. `git-issue-workflow`'s description is the one a ticket agent already
matches on, so that is where the capability is now announced.

## What this skill still contributes to a ticket

One key and one script: the constituent **fan-out**. `wt info TICKET-123` prints
a `PROPAGATE` key in an integration repo and only there, resolved to this skill's
`scripts/propagate.sh`; when the unit is not installed it prints the install
command instead of a dead path. `wt` decides that by looking for
`integration.toml` — an **artifact**, not an installed skill — which is
deliberate: the marker is already the thing every script here keys on, it costs
one `[ -f ]` per rung, and a plug-in mechanism for one boolean would be more
machinery than the question deserves.
