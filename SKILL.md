---
name: plugin-repository
description: >-
  Create and operate "plugin repositories" — a skill-manager PLUGIN whose
  `skills/` directory holds several skill repos as ordinary tracked files, so a
  bundle of skills versions, installs, syncs, reviews and improves as ONE unit
  while each skill keeps its own repo and its own history. Use when several
  skill-manager skills always ship together, when a change spans more than one
  skill and you do not want N repos / N PRs / N syncs that land out of order,
  when an agent needs a single self-improvement substrate it can PR against, or
  when a harness's `units = [...]` list should become one installable bundle
  with hooks/commands/agents attached. It is a SPECIALIZATION of
  `git-integration-repo`: that skill owns the git model (no submodules, strip
  `.git` before the first commit, fan-out with `propagate.sh`) and this one owns
  what makes the parent a valid plugin at the same time.
skill-imports:
  - unit: git-integration-repo
    path: SKILL.md
    reason: >-
      A plugin repository IS an integration repository. The git model, the
      onboarding order, propagation and refresh are that skill's and are never
      restated here.
  - unit: git-integration-repo
    path: references/git-model.md
    reason: Why committing constituent files before restoring .git is load-bearing.
  - unit: git-integration-repo
    path: references/propagation.md
    reason: Fan-out of a merged parent change back to each skill repo.
  - unit: skt
    path: references/plugins.md
    reason: >-
      Authority on plugin layout, .claude-plugin/plugin.json,
      skill-manager-plugin.toml, contained-skill semantics and plugin install.
  - unit: skt
    path: skills/unit-authoring/SKILL.md
    reason: Authoring and shipping edits to any installable unit.
  - unit: git-issue-workflow
    path: SKILL.md
    reason: Worktrees, per-checkout Skill Manager homes and the ticket lifecycle.
---

# plugin-repository

A **plugin repository** is one git repo that is two things at once:

```
my-plugin-repo/                      # ONE repo, ONE remote, ONE version
├── .claude-plugin/plugin.json       #   <- it is a skill-manager PLUGIN
├── skill-manager-plugin.toml
├── integration.toml                 #   <- it is an INTEGRATION REPO
├── INTEGRATION.md  PLUGIN-REPO.md
├── skills/
│   ├── alpha-skill/                 # plain files here; its own .git and its
│   │   └── SKILL.md                 # own remote in a DEV checkout only
│   └── beta-skill/
│       └── SKILL.md
├── hooks/ commands/ agents/         # optional harness runtime surface
└── README.md
```

Downstream it installs as **one unit at one version**: `skill-manager install
github:owner/my-plugin-repo` brings every contained skill in together, `skt
check` notifies about it once, one `sync` moves all of them, and improving it is
**one PR**. Upstream each skill is still its own repo with its own history,
independently useful to other bundles, and a change made in the parent fans back
out to those repos as branches and MRs.

That is the whole idea: **a plugin repository is a self-improvement substrate.**
An agent that consumes it has one thing to reason about, one thing to change,
and one thing to pull. `references/why.md` is the argument in full — read it
before designing a bundle, because which skills belong in one plugin repo is the
only decision here that is expensive to reverse.

## This skill owns the plugin half. It owns nothing else.

`git-integration-repo` is a **hard dependency**, declared in
`skill-manager.toml`, and every script here sources its `integration-lib.sh`
(which in turn sources `git-issue-workflow`'s `lib.sh`). The division is exact:

| Question | Owner |
|---|---|
| Constituents as plain files, never submodules; strip `.git` → commit → restore | `git-integration-repo` (`references/git-model.md`) |
| Pull every skill repo to its upstream tip at once | `git-integration-repo` — `scripts/refresh.sh` |
| Fan a merged parent change back out to each skill repo (branches, MRs, tracking issue) | `git-integration-repo` — `scripts/propagate.sh` |
| Worktree + its own Skill Manager home for a ticket | `git-issue-workflow` — `skt ticket new` / `wt` |
| `plugin.json`, `skill-manager-plugin.toml`, contained-skill semantics, deps | `skt` — `references/plugins.md`, `skills/unit-authoring` |
| **The parent being a valid plugin AND a valid integration repo at once** | **here** |
| **Why a bundle, which skills belong in one, and who watches it** | **here** — `references/why.md` |

Nothing in those rows is restated on this page. When a step is theirs, run their
script.

## The four rules that are only true here

1. **Constituents live at `skills/<name>/`, not `constituents/<name>/`.**
   skill-manager and the harness plugin runtime find contained skills only
   under `skills/`. Every other `git-integration-repo` script reads the path
   from `integration.toml`, so they are indifferent — but `add-constituent.sh`
   hardcodes `constituents/`, which is exactly why `scripts/add-skill.sh` exists
   here. Use it; do not hand-run `add-constituent.sh` in a plugin repo.

2. **A contained skill's store path is `plugins/<plugin>/skills/<skill>/`, not
   `skills/<skill>/`.** Moving a skill into a plugin repo therefore *breaks
   every sibling that resolves it as
   `$SKILL_MANAGER_HOME/skills/<unit>/...`* — a live pattern, e.g. how
   `git-integration-repo` reaches `git-issue-workflow`'s `lib.sh`. Resolvers
   need a plugin rung. `scripts/plugin-repo-lib.sh` ships `unit_dir` as the
   one correct search, `scripts/verify.sh` greps the bundle for the broken
   pattern, and `references/layout.md` § *Store paths* has the full story.

3. **A contained skill is invoked `plugin:skill`, and is no longer installable
   on its own.** `skt:unit-authoring`, not `unit-authoring`. Cross-references in
   prose, harness `units = [...]` lists and `skill-project.toml` entries all
   have to move to the plugin coord — `references/migration.md`.

4. **Propagate before you refresh.** An edit made in the parent (or published
   into the plugin's store copy by `skt publish`, which pushes to the *plugin*
   repo — the store copy is a checkout of it) exists nowhere else until
   `propagate.sh` sends it to the skill's own repo. `refresh.sh` is
   `reset --hard` per constituent and will discard it. `references/lifecycle.md`
   sequences both directions.

## Workflows

| Task | Read | Run |
|---|---|---|
| Decide whether a bundle is right, and which skills | `references/why.md` | — |
| Create a plugin repo | `references/layout.md` | `scripts/init-plugin-repo.sh`, then `scripts/add-skill.sh` per skill |
| Add a skill to an existing bundle | `references/layout.md` | `scripts/add-skill.sh` → commit → `finalize-constituents.sh` (dependency) → `scripts/verify.sh` |
| Pull every skill's upstream changes in, atomically | `references/lifecycle.md` | `refresh.sh` (dependency) → commit → `scripts/release.sh` |
| Change several skills at once and push it back out | `references/lifecycle.md` | `skt ticket new` → edit → merge → `propagate.sh` (dependency) |
| Cut a version consumers will be notified about | `references/lifecycle.md` | `scripts/release.sh` |
| Check the repo is a valid plugin *and* a valid integration repo | — | `scripts/verify.sh` |
| Move today's standalone skills or a harness into a bundle | `references/migration.md` | — |

## Quick reference

```bash
# this skill; add a `plugins/*/skills/` rung if it is itself bundled (rule 2)
P="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/plugin-repository/scripts"
S="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-integration-repo/scripts"   # the dependency

# --- create ---
$P/init-plugin-repo.sh my-plugin ~/IdeaProjects/my-plugin-repo   # plugin + integration markers, git init
cd ~/IdeaProjects/my-plugin-repo
$P/add-skill.sh alpha-skill git@github.com:owner/alpha-skill.git main
$P/add-skill.sh beta-skill  git@github.com:owner/beta-skill.git  main
git add -A && git commit -m "bundle alpha-skill, beta-skill"     # BEFORE finalize — the invariant
$S/finalize-constituents.sh                                      # restore each skill's .git + remote
$P/verify.sh                                                     # plugin checks + the dependency's

# --- pull every skill's upstream in, as one change ---
$S/refresh.sh
git checkout -b feature/pull-upstream && git add -A && git commit -m "pull skills to upstream tips"
$P/release.sh minor                                              # bump plugin.json + toml together
#   ...PR, merge, then consumers: skill-manager sync my-plugin --git-latest

# --- change several skills at once, then fan out ---
skt ticket new PLUG-12       # worktree + its own home (git-issue-workflow)
#   ...edit across skills/, commit, merge back to the parent main tree...
$S/propagate.sh PLUG-12 --push --mr                              # per-skill branches, MRs, one tracking issue
$P/verify.sh

# --- prove this skill itself ---
bash <checkout-of-this-skill>/scripts/selftest.sh
```

Every script here answers `-h/--help` before doing anything and refuses a first
positional beginning with `-`; that guard is `help_guard` from the dependency
chain, and `scripts/selftest.sh` sweeps this directory to keep it true for
scripts added later. The reason it is not politeness is in
`git-integration-repo`'s SKILL.md.

## Plugin repos and harnesses

A harness's `units = [...]` is a *list of coords resolved at install time*; a
plugin repo is *the bundle itself*, versioned. When a harness exists only to
name a set of skills that always travel together, that set wants to be a plugin
repo — and then the harness either disappears or shrinks to the part a plugin
cannot do: binding doc-repo sources into a project root and managing named
instances. A plugin repo also carries `hooks/`, `commands/` and `agents/`, which
no bare skill can. `references/why.md` § *Plugin repo or harness* decides it.
