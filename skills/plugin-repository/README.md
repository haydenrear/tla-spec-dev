# plugin-repository

A skill-manager skill for **plugin repositories**: one git repo that is
simultaneously a **skill-manager plugin** (`.claude-plugin/plugin.json`,
contained skills under `skills/<name>/`) and an **integration repository**
(`integration.toml`, each of those skills a constituent tracked as ordinary
files — no submodules, no gitlinks).

Downstream it is **one unit at one version**: one install, one sync, one
notification, one PR to improve it. Upstream each skill keeps its own repo and
its own history, and a change made in the parent fans back out to them as
branches and MRs.

## Install

This skill now ships as a **contained skill of the `tla-spec-dev` plugin**, so
the thing you install is the bundle, not this unit. `skill-manager install
plugin-repository` refuses — a contained skill is not a separately addressable
unit — and installing from this repo's own coord would give you a second,
standalone copy alongside the bundled one.

```bash
skill-manager install github:haydenrear/tla-spec-dev-plugin --yes
skill-manager sync tla-spec-dev --git-latest
```

`git-integration-repo` is no longer a separate install: it is a **sibling
contained skill in the same bundle**, so it arrives with the plugin at the same
version. The `skill_reference` that used to name its coord was removed for
exactly that reason — see `skill-manager.toml`.

Invoke the skill as `tla-spec-dev:plugin-repository`.

## Why

One repo per skill is right for distribution and wrong for change. A single
improvement that spans three skills costs three branches, three PRs, three
syncs that land at different times, and a window in which a consumer's home is
internally inconsistent. A plugin repository makes the **bundle** the unit of
change: the parent's merge commit is the coherence boundary, so consumers never
observe half a change.

That makes it a self-improvement substrate — one artifact an agent reasons
about, changes, and pulls — and makes an *integrating agent* possible: one that
watches several plugin repos plus their upstream skill repos and decides when a
set of changes is coherent enough to be cut as a version. Full argument in
`references/why.md`.

## What it gives you

- **Scaffolding** — plugin markers and integration markers in one directory,
  with `constituents/` replaced by `skills/`. (`scripts/init-plugin-repo.sh`)
- **Onboarding a skill** — clone, validate it can *be* a contained skill (root
  `SKILL.md`, name agrees with the directory, not itself a plugin), strip
  `.git`, register at `skills/<name>`. (`scripts/add-skill.sh`)
- **Verification of both halves** — the dependency's integration checks, plus
  manifest agreement, contained-skill loadability, and a grep for sibling
  resolvers broken by the store-path move. (`scripts/verify.sh`)
- **Releases** — one version into both manifests, which must agree.
  (`scripts/release.sh`)
- **The flows it does not own** — `refresh.sh` (pull every skill's upstream in
  atomically) and `propagate.sh` (fan a merged change back out) are
  `git-integration-repo`'s and are run directly. `references/lifecycle.md`
  sequences them, including which one is destructive.

## The three facts that bite

1. **Bundling changes a skill's identity.** It is invoked `<plugin>:<skill>`,
   `skill-manager show <skill>` answers "unit not found", its bytes are at
   `plugins/<plugin>/skills/<skill>/`, and a `skill-imports: unit: <skill>`
   elsewhere now fails validation. A git-coord reference to it does *not* fail —
   it installs a duplicate standalone copy, which is worse.
2. **Change management is fine, at plugin granularity.** `skt` sees one unit,
   one version, one notification; `skt publish` pushes to the plugin repo, which
   is the point.
3. **`refresh.sh` skips a skill with local changes** rather than clobbering it,
   so an unpropagated edit *blocks* that skill's pull instead of dying. Read the
   SKIPPING lines, or you cut a version on a partial pull.

`references/imports.md` has fact 1 with measured evidence and one known
skill-manager bug; `references/lifecycle.md` has 2 and 3.

## Companion edits this skill implies

Shipping a skill does not update its neighbours, and two of them now describe
the world incompletely. Neither is required for this skill to work; both are
required for an agent to *find* it:

1. **`git-integration-repo`** — an agent asked to "put these skill repos in one
   repo" matches its description, runs `add-constituent.sh`, and gets
   `constituents/<name>/`: not a plugin, and not convertible without moving
   every directory. It needs one row in its workflow table and one clause in its
   description pointing here — the same fix that skill applied to itself when
   `wt` moved to `git-issue-workflow`.
2. **`git-integration-repo`'s `finalize-constituents.sh`** — its
   commit-before-`.git` guard is the pathspec `-- constituents`, so it cannot
   fire for any integration repo that puts constituents elsewhere. The real fix
   is upstream: derive the pathspec from the manifest's `path` values.
   `scripts/finalize.sh` here is the local guard until that lands.

## Layout

```
plugin-repository-skill/
├── SKILL.md                    # the skill an agent loads
├── skill-manager.toml          # unit manifest: the one hard reference
├── skill-project.toml          # what an agent working in THIS checkout needs
├── references/
│   ├── why.md                  # the argument, and which skills belong together
│   ├── layout.md               # the two identities, paths, manifests, ignores
│   ├── imports.md              # what bundling does to a skill's identity (+ a known bug)
│   ├── lifecycle.md            # the four flows + releases + integrating agent
│   └── migration.md            # standalone skills or a harness -> a bundle
├── scripts/
│   ├── plugin-repo-lib.sh      # resolves the dependency; unit_dir; manifests
│   ├── init-plugin-repo.sh
│   ├── add-skill.sh
│   ├── verify.sh
│   ├── release.sh
│   └── selftest.sh             # static sweep + a real end-to-end build
└── assets/                     # plugin.json, sidecar TOML, PLUGIN-REPO.md, ignores
```

## Prove it

```bash
bash scripts/selftest.sh
```

Static checks (help guards, no duplicated dependency library, no relative rung,
and that this skill obeys its own store-path rule) plus a live phase that
scaffolds a plugin repo in a temp dir, onboards a local skill repo, commits,
finalizes and verifies. Needs `git` and `git-integration-repo`; the live phase
skips loudly without the latter, and nothing needs the network.

## License

MIT.
