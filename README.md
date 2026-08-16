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

```bash
skill-manager install github:haydenrear/plugin-repository-skill --yes
# or, locally during development:
skill-manager install file:///Users/hayde/IdeaProjects/plugin-repository-skill --yes
skill-manager sync plugin-repository
```

Requires `git-integration-repo`
(`skill-manager install github:haydenrear/git-integration-skill`), which is
declared as a hard `skill_reference` and installs with it.

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
3. **`refresh.sh` is `reset --hard` per skill.** Propagate first, or lose the
   edit that only exists in the parent.

`references/imports.md` has fact 1 with measured evidence and one known
skill-manager bug; `references/lifecycle.md` has 2 and 3.

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
