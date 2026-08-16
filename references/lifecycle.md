# Lifecycle: the four flows, and the one that is destructive

A plugin repository sits between N upstream skill repos and M downstream
consumers, so changes move in both directions. Keeping them straight is most of
the operational work.

```
   skill repos  ──(A) refresh ──▶  PLUGIN REPO  ──(D) install/sync ──▶  consumers
        ▲                          ▲   │                                    │
        └──(C) propagate ──────────┘   └──(B) edit in a ticket worktree     │
                                                                            │
                     (E) an edit made in a consumer's home ──── skt publish ┘
```

## A. Pull upstream skill changes in, atomically

The skills' own repos moved (someone published from a home, or a fan-out was
merged). Bring them into the bundle as **one** change:

```bash
S="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-integration-repo/scripts"  # dependency
P="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/plugin-repository/scripts"     # here
git checkout -b feature/pull-upstream
$S/refresh.sh                    # fetch --all + reset --hard per constituent — DESTRUCTIVE
git status                       # the parent now shows exactly what moved upstream
git add -A && git commit -m "pull skills to upstream tips"
$P/release.sh minor              # bump plugin.json + skill-manager-plugin.toml together
$P/verify.sh
# PR → review the whole cross-skill delta in one place → merge
```

`refresh.sh` **discards** anything in a constituent that its own remote does not
have. Run flow C first if the parent carries skill edits, or you will lose them
with no diff to recover from. `verify.sh` refuses to be a substitute for
remembering this — check `git log` on the parent for unpropagated skill changes
before refreshing.

Refresh per skill rather than wholesale when only one moved and you do not want
the others' churn in this version: `git -C skills/<name> fetch --all && git -C
skills/<name> reset --hard origin/<branch>`, then commit the parent.

## B. Change several skills at once, in the parent

This is the flow the bundle exists for.

```bash
skt ticket new PLUG-12          # worktree + its own Skill Manager home
#   ...in the worktree: edit across skills/alpha-skill, skills/beta-skill, hooks/…
#      the worktree holds plain files — no constituent .git — which is what makes
#      one commit able to span skills at all
git add -A && git commit -m "PLUG-12: unify the vocabulary across the bundle"
```

Then merge back into the parent main tree and cut a version:

```bash
git -C <repo-root> merge --no-ff feature/PLUG-12
$P/release.sh patch && git commit -am "release <version>"
$P/verify.sh
```

Review happened once, over the whole change. Consumers get it whole.

## C. Fan the merged change back out to the skill repos

Now each skill's own repo needs its slice, or the bundle and the upstreams
diverge and the next refresh reverts your work.

```bash
$S/propagate.sh PLUG-12                 # dry run: branch + commit per changed skill, no network
$S/propagate.sh PLUG-12 --push --mr     # push, open an MR each, file ONE tracking issue
```

Semantics — per-skill `feature/PLUG-12`, skipping unchanged constituents,
idempotent on re-run, the tracking issue for a downstream agent to test and
merge — are `git-integration-repo`'s `references/propagation.md` and are not
restated here. Two things are specific to a plugin repo:

- **Propagation is not optional maintenance, it is how the bundle stays a
  cache.** The skill repo is the skill's identity; a bundle that stops fanning
  out has forked its members silently.
- **Order: propagate, then refresh.** After the MRs merge, flow A brings the
  merge commits back and the parent tree should end up clean — that round trip
  is the evidence the fan-out was complete.

## D. Consumers

```bash
skill-manager install github:owner/my-plugin-repo --yes
skt check                       # ONE notification for the whole bundle
skill-manager sync my-plugin --git-latest
skill-manager list              # SHA column must match the pushed parent HEAD
```

A sync that exits 0 is not evidence the bytes moved — the store pulls from the
**remote**, so an unpushed commit leaves it on the old bytes with a green
report. The only proof is `gitHash` in
`$SKILL_MANAGER_HOME/installed/<plugin>.json` matching the pushed `HEAD`.
(`skt`'s `unit-authoring`, § *Shipping edits to an installed unit*.)

Consumers address contained skills as `<plugin>:<skill>`. A consumer's
`skill-project.toml` or `harness.toml` names **the plugin repo's coord**, once,
instead of one entry per skill — that collapse is most of the win at the
consuming end.

## E. An edit made inside a consumer's home

An agent edits `plugins/my-plugin/skills/alpha-skill/SKILL.md` in its own home
and wants it to survive. `skt publish` moves the home edit one tier up and then
publishes the **unit** — and the unit here is the *plugin*, whose store copy is
a checkout of the **plugin repo**. So the edit lands on the plugin repo.

**That is the design working, not a gap.** Change management is at plugin
granularity throughout: `skt`'s `_store_dir` resolves `skills|plugins|docs|
harnesses`, so a plugin is a first-class unit with one origin, one `gitHash` and
one notification, and a self-improvement PR against the substrate is a PR
against this one repo. Nothing about that wants to be per-contained-skill.

What the edit has *not* done is reach `alpha-skill`'s own repo — the plugin repo
is also a cache of the upstreams, and only flow C empties that queue. So:

- `alpha-skill`'s repo knows nothing about it yet;
- `refresh.sh` (flow A) would **revert it**, because `reset --hard` restores
  upstream's version of those files.

The completion step is flow C in a development checkout of the plugin repo.
Treat unpropagated skill edits as work in progress, and look for them before
flow A — the same "propagate first, then refresh" ordering any integration repo
has, for the same reason.

## Releases

`scripts/release.sh <patch|minor|major|X.Y.Z>` writes the same version into
`.claude-plugin/plugin.json` and `skill-manager-plugin.toml`, because they must
agree and hand-editing one is the standard way to make them not. Guidance:

- **patch** — one skill's wording, a fix inside a skill.
- **minor** — a skill added to or removed from the bundle, new hooks/commands,
  a routine upstream pull.
- **major** — a contained skill's `name` changes (its invocation name changes
  for every consumer), a skill leaves the bundle, or a convention lands that
  consumers must act on.

Tag if the consumers pin refs; nothing here requires it — `sync --git-latest`
follows the installed `gitRef`.

## The integrating agent

The loop that becomes possible once bundles exist. Give an agent the plugin
repos and their upstream skill repos, and have it run:

1. **Watch.** For each bundle, which constituents' remotes are ahead of the
   parent's copy? (`git -C skills/<n> fetch && git -C skills/<n> rev-list --count HEAD..origin/<b>`)
2. **Judge coherence.** Do the pending upstream changes across the bundle *fit
   together*, and with what consumers currently expect? A rename that landed in
   one skill and not its caller is a reason to wait, not to pull.
3. **Pull and cut** — flow A — when they do, one PR, one version.
4. **Sweep the other direction.** Any skill edits sitting in a plugin repo
   unpropagated (flow E)? Fan them out — flow C.
5. **Report.** Which bundles moved, which consumers should sync, what was held
   back and why.

Step 2 is the judgment that has no home under one-repo-per-skill: there, every
skill publishes independently and "when does this reach consumers" is decided by
whenever each consumer happens to sync. Here it is a decision with an owner.
