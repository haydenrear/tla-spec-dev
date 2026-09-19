# Where the plugin is installed from, and pulling the five skills in

## The install coordinate (owner decision, 2026-09-18)

The plugin is installed from **`github:haydenrear/tla-spec-dev-plugin`**, a
private repository created at the wave-2 gate.

> **SUPERSEDED IN PART AT REVISION 4, 2026-09-19.** Everything in this section
> about *pushing the epic tip to the plugin repo* is retired — read
> **The mirror is retired** at the end of this section before acting on any
> command here. The install coordinate itself is unchanged.

Two options were measured before choosing. `skill-manager install` **does**
accept a branch through `--ref`, so
`install github:haydenrear/tla-spec-dev --ref epic/self-improvement-substrate`
resolves and installs cleanly — the plugin layout exists only on the epic
branch, since `main` here is still pre-migration. The owner chose the separate
repository instead. No skill-manager migration machinery was needed for either:
`spec-double-compiler` was already uninstalled from the project home as part of
the wave-2 home migration, so nothing had to be renamed in place.

**The obligation this created — RETIRED, see below.** As originally written,
this section said the plugin repo does not update itself, so the epic tip had to
be pushed to it at every wave close:

```bash
# RETIRED AT REVISION 4 -- DO NOT RUN. Kept so the retired practice is legible.
git push tla-spec-dev-plugin origin/epic/self-improvement-substrate:refs/heads/main
```

## The mirror is retired (owner decision, 2026-09-19)

**Do not push the epic branch to `tla-spec-dev-plugin` mid-epic.** The epic
agent started that practice in wave 3 and repeated it at every wave close
without once stating what it implied: **the install source was tracking
unmerged, mid-epic work.** At the wave-6 gate the plugin repo's `main` was
`45dae6eb`, the epic tip — **354 commits ahead of `tla-spec-dev`'s `main`**
(`5d05ba7f`). Anyone installing the coordinate got work that had not passed a
default-branch merge, presented as if it were releasable.

The sentence this replaces also predicted that "when the epic merges to `main`
here … the two stop diverging." **That merge will never happen.**
`planning_rules.no_default_branch_merge` (revision 4): the epic branch never
merges to `tla-spec-dev`'s default branch, because that repository must keep
shipping the `spec-double-compiler` **skill** — everyone who has it installed
syncs from there, and landing a **plugin** layout on its `main` would break
those syncs.

**How the plugin repo gets the result instead: by cutover, once, at epic
close.** Until then its `main` stays where it is and is deliberately stale
relative to the epic branch. The remote stays configured; only the mid-epic
push is retired.

**Known defect at the coordinate:** installing from either git source fails the
toolchain's own two CLI installers (`SIS-W2-F-05`) — `tlc2` and `tla-spec-dev`
are declared on the contained skill but resolved under the plugin's name. The
project home is unaffected because its shims predate the migration; a **fresh**
home gets no toolchain. SI-11 owns the fix.

# Pulling the five skills in from the project root

Written at kickoff, 2026-09-17, for SI-02 (#335) and for anyone integrating
upstream skill work before the freeze. **The freeze happens after migration, not
before it**, so until SI-02 lands and the owner declares the freeze, changes
pushed to the five skill repositories must still be able to reach this one.

Every command below runs from the repository root. Nothing needs a second
checkout, and nothing here uses submodules.

## The remotes

Added 2026-09-17 to `tla-spec-dev` itself, so `git fetch <name>` works from the
project root:

| remote | repository |
|---|---|
| `git-epic-workflow` | `https://github.com/haydenrear/git-epic-skill.git` |
| `git-issue-workflow` | `https://github.com/haydenrear/git-issue-workflow-skill.git` |
| `git-issue` | `https://github.com/haydenrear/git-issue-skill.git` |
| `discovery` | `https://github.com/haydenrear/discovery-skill.git` |
| `test-graph` | `https://github.com/haydenrear/test_graph_skill.git` |

Added 2026-09-18 by SI-12, when the last two dependent skills were nested:

| remote | repository |
|---|---|
| `git-integration-repo` | `https://github.com/haydenrear/git-integration-skill.git` |
| `plugin-repository` | `https://github.com/haydenrear/plugin-repository-skill.git` |

Both were nested the same way as the first five — `git subtree add`, FULL
history, no `--squash` — so `git subtree pull` stays available for them too
until the freeze. Note that each coord names the REPO, not the installed unit,
and for both of these the two names differ:
`git-integration-skill` installs `git-integration-repo`, and
`plugin-repository-skill` installs `plugin-repository`.

They are fetch-only in practice: this repository never pushes to them.
Publishing an edit back to a skill's own repository stays `skt publish <unit>`
from the home that holds the edit, until the freeze retires that path.

## Nesting a skill the first time (SI-02)

```bash
git fetch <remote> main
git subtree add --prefix=skills/<name> <remote> main
```

Verified on `discovery` at kickoff, on a throwaway branch that was then
removed. It produced ordinary tracked files under `skills/discovery/` — no
submodule, no gitlink — plus one merge commit recording which upstream commit
the subtree came from. That is the `git-integration-repo` model
(`references/git-model.md`: constituents are plain tracked files, never
submodules) reached by a command that also leaves a pull path open.

`--squash` would keep the upstream history out of this repository's log. The
decision is permanent per skill — a subtree added with `--squash` must also be
pulled with `--squash` forever after.

**Owner decision, 2026-09-17: full history, for all five skills.** Do not pass
`--squash`. The reason is the pull path: until the freeze, `subtree pull` has to
stay cheap and conflict-legible, and squashed subtrees make every later merge
harder to read. The cost accepted in exchange is five skills' commit history
entering this repository's log at SI-02.

## Integrating new upstream work, until the freeze

```bash
git subtree pull --prefix=skills/<name> <remote> main
```

Verified to re-run cleanly with nothing to do ("Already up to date"). Once this
repository has edited the same files, this is an ordinary merge: conflicts are
resolved here, in the parent, and that resolution is the point — it is where the
two lines of work meet.

## What the owner still decides

- **When the freeze starts.** After SI-02, on the owner's word. Until then this
  file is the integration path.
- **`--squash` or full history**, per skill, at SI-02.
- **What happens to the five repositories at freeze**: archived, left readable
  with a pointer to this repository, or kept live for a while. The epic does not
  publish to them during its run (`#333` § "What this epic does not do").

## The one thing that must not be lost

`git-issue` (`1f91074b`) and `git-issue-workflow` (`4eeb350b`) carried commits
that existed **only** in this repository's gitignored project home — the
predecessor epic's "spec workflow NOT REQUIRED by default" and "no ticket-local
current/" work. They were pushed upstream at kickoff, on the owner's decision,
precisely so that `git subtree add` from `main` carries them rather than
silently reverting them. Before nesting, confirm each remote's `main` contains
them:

```bash
git fetch git-issue main && git log --oneline -1 git-issue/main          # expect 1f91074b or a descendant
git fetch git-issue-workflow main && git log --oneline -1 git-issue-workflow/main  # expect 4eeb350b or a descendant
```

If either check fails, stop and reconcile: nesting an older tip over them is a
silent loss that no test in this repository would catch.
