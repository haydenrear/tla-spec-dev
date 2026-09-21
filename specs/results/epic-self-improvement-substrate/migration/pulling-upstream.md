# Where the plugin is installed from, and pulling the five skills in

## The install coordinate (owner decision, 2026-09-18)

The plugin is installed from **`github:haydenrear/tla-spec-dev-plugin`**, a
private repository created at the wave-2 gate.

> **CURRENT AS OF 2026-09-21.** `tla-spec-dev-plugin`'s `main` **is** the
> epic's delivery surface, and every wave lands on it. The revision-4 note that
> retired the mid-epic push is itself superseded — read **The plugin's `main`
> IS the delivery surface** below. The install coordinate is unchanged.

Two options were measured before choosing. `skill-manager install` **does**
accept a branch through `--ref`, so
`install github:haydenrear/tla-spec-dev --ref epic/self-improvement-substrate`
resolves and installs cleanly — the plugin layout exists only on the epic
branch, since `main` here is still pre-migration. The owner chose the separate
repository instead. No skill-manager migration machinery was needed for either:
`spec-double-compiler` was already uninstalled from the project home as part of
the wave-2 home migration, so nothing had to be renamed in place.

**The obligation this created is LIVE again, and deliberately so.** The plugin
repo does not update itself, so the epic tip is pushed to its `main` at every
wave close:

```bash
git push tla-spec-dev-plugin HEAD:refs/heads/main
```

## The plugin's `main` IS the delivery surface (owner decision, 2026-09-20, reaffirmed 2026-09-21)

**Push the epic tip to `tla-spec-dev-plugin`'s `main` at every wave close.**
This is the authoritative rule and it is the plan's, not just this file's —
`planning_rules.no_default_branch_merge` records that the plugin's `main` "was
cut over on 2026-09-20 at wave 10 by owner decision" and that "from that point
`tla-spec-dev-plugin`'s `main` IS the epic's delivery surface and later waves
land on it".

**Why it has to be `main` specifically: `skill-manager onboard` points at
`main`.** There is no branch to aim it at. So the plugin's `main` must BE the
real thing before SI-18 dispatches, or the skill-manager agent onboards against
a stale bundle and every eval it runs measures the wrong substrate. "Ready by
handoff" is the requirement the push exists to satisfy.

**What the epic still never does: merge to `tla-spec-dev`'s default branch.**
That half of the original rule stands. `tla-spec-dev` keeps shipping the
`spec-double-compiler` **skill** — everyone who has it installed syncs from
there — and landing a **plugin** layout on its `main` would break those syncs.
Two repositories, two surfaces: the skill ships from `tla-spec-dev`, the plugin
ships from `tla-spec-dev-plugin`.

### The retirement that was itself retired, kept legible

Between 2026-09-19 and the 2026-09-20 cutover this practice was **banned**, and
for a reason worth remembering rather than deleting. The epic agent had pushed
at every wave close since wave 3 without once stating what it implied: **the
install source was tracking unmerged, mid-epic work.** At the wave-6 gate the
plugin's `main` was `45dae6eb` — 354 commits ahead of `tla-spec-dev`'s `main`
— and anyone installing the coordinate got work that had passed no review gate,
presented as releasable.

The cutover resolved that by changing what the plugin repo *is*: it is no
longer a mirror of unmerged work, it is the delivery surface, and the waves
landing on it have passed their gates. The hazard the ban addressed is real and
returns the moment someone pushes an ungated tip. Push at wave close, after the
review artifact, not mid-wave.

**Correction, 2026-09-21:** this file asserted the retired-mirror rule for a
full day after the plan had superseded it, and the epic agent escalated the
disagreement to the owner as an unresolved conflict rather than reading
`planning_rules.no_default_branch_merge` two files away. The authoritative rule
lives in the plan; this file describes it.

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
