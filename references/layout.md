# Layout: one repo, two identities

A plugin repository must satisfy two resolvers at the same time. Neither knows
about the other, and both key off root marker files.

```
my-plugin-repo/
├── .claude-plugin/plugin.json        # PLUGIN marker  (skill-manager + harness)
├── skill-manager-plugin.toml         # plugin sidecar: name/version/deps
├── integration.toml                  # INTEGRATION marker (constituent list)
├── INTEGRATION.md                    # from git-integration-repo's assets
├── PLUGIN-REPO.md                    # the dual-identity note; from assets/ here
├── .gitignore                        # parent-root ignores ONLY
├── skills/
│   ├── alpha-skill/                  # == constituent, path "skills/alpha-skill"
│   │   ├── SKILL.md                  #    required at the contained-skill root
│   │   ├── skill-manager.toml        #    with [skill]
│   │   └── …                         #    its own .git in a dev checkout only
│   └── beta-skill/
├── hooks/  commands/  agents/        # optional harness runtime surface
└── README.md
```

Detection is unambiguous because the two markers are different files:
`skill-manager`'s resolver sees `.claude-plugin/plugin.json` at the root and
routes the whole thing through the plugin path; this skill's and
`git-integration-repo`'s scripts see `integration.toml` and walk the constituent
list. They never collide.

## Constituents must be at `skills/<name>/`

The contained-skill path is not a convention, it is where the plugin runtime and
`skill-manager` look. `integration.toml` records `path` per constituent and
every `git-integration-repo` script reads it from there — `finalize-constituents.sh`,
`verify.sh`, `refresh.sh` and `propagate.sh` are all path-agnostic and work
unmodified.

The single exception is `add-constituent.sh`, which hardcodes
`constituents/$NAME`. That is why `scripts/add-skill.sh` exists here: it does
the same clone → strip `.git` → register, into `skills/<name>`, and additionally
refuses input a plugin cannot carry:

- no `SKILL.md` at the cloned repo's root (a plugin's contained skill needs one
  *there*, not nested);
- a `SKILL.md` whose frontmatter `name:` disagrees with the directory name;
- a name already registered in `integration.toml`;
- a repo that is itself a plugin (`.claude-plugin/plugin.json` at its root) —
  plugins do not nest.

Everything after that is the dependency's ordinary onboarding, and its ordering
invariant is unchanged and unforgiving: **`git add` + commit the skill's files
while it has no `.git`, and only then run `finalize-constituents.sh`.** See
`git-integration-repo`'s `references/git-model.md`.

## Store paths, and the resolvers they break

The disk half of a bigger subject: **everything that addresses a bundled skill
by its old identity** — store paths, `skill-imports`, git-coord references, the
invocation name — is `references/imports.md`, with measured evidence and one
real skill-manager bug. This section is the path part, because it is the part
this skill's own scripts have to survive.

| | standalone skill | contained in a plugin |
|---|---|---|
| Store path | `$SKILL_MANAGER_HOME/skills/<unit>/` | `$SKILL_MANAGER_HOME/plugins/<plugin>/skills/<unit>/` |
| Installable by name | yes | no — the resolver refuses; the plugin owns the identity |
| Invoked as | `<unit>` | `<plugin>:<unit>` |
| `skt` change-management granularity | the skill | **the plugin** |

Verified on a live home: `skt`'s contained skills are at
`~/.skill-manager/plugins/skt/skills/{skt,unit-authoring}/`, appear to agents as
`skt:skt` and `skt:unit-authoring`, and nothing named `unit-authoring` exists
under `skills/`.

So a script in some *other* unit that says

```bash
"${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/<unit>/scripts/lib.sh"
```

stops resolving the moment `<unit>` is bundled — and the failure is at source
time in a script that may be halfway through a fan-out. This pattern is real and
load-bearing today (`git-integration-repo`'s `integration-lib.sh` reaches
`git-issue-workflow`'s `lib.sh` exactly like that). Before bundling a skill that
others resolve by path, give those resolvers a plugin rung:

```bash
for c in ${PIN:+"$PIN/lib.sh"} \
         "$HOME_DIR/skills/<unit>/scripts/lib.sh" \
         "$HOME_DIR"/plugins/*/skills/<unit>/scripts/lib.sh; do
  [ -f "$c" ] && { LIB="$c"; break; }
done
```

`scripts/plugin-repo-lib.sh` here ships that search as `unit_dir <name>` — use
it rather than writing a fourth copy — and `scripts/verify.sh` greps the bundled
skills for the bare `skills/<unit>` form and reports each hit, because the whole
point is to find them before a consumer does.

## The two manifests must agree

`.claude-plugin/plugin.json` and `skill-manager-plugin.toml` both carry `name`
and `version`. `skill-manager` warns when they drift; the harness silently
prefers one, so drift shows up later as an inexplicable version. `verify.sh`
fails on it, and `scripts/release.sh` is the only sanctioned way to change a
version because it writes both.

The plugin's **name is `plugin.json`'s**, not the repo's. Convention:
repo `<name>-plugin` (or `-plugin-repo`), plugin `<name>`.

## Dependencies: plugin level or contained-skill level

Unchanged from `skt`'s `references/plugins.md`, which is the authority — the
short version:

- Keep CLI/MCP deps **on the contained skill** by default. It keeps each skill
  self-describing and installable standalone from its own repo, which is exactly
  the property a plugin repo is trying not to destroy upstream.
- Move a dep **to the plugin** only when two contained skills share one MCP
  server (registering it twice races on init params) or one CLI.
- `skill_references` on a contained skill still work and are still unioned at
  install; a reference to a skill that is *also* a member of this bundle is
  redundant at best and an install-time cycle at worst — drop it and rely on the
  bundle.

## `.gitignore`, and where it may not go

Root `.gitignore` only, path-scoped — the parent rule from
`git-integration-repo` applies verbatim, because `refresh.sh` runs
`reset --hard` inside each `skills/<name>/` and would wipe anything you put
there. What a plugin repo adds beyond the dependency's scaffold:

```gitignore
# per-checkout Skill Manager and agent homes (machine-local, never committed)
.skill-manager/
.claude/
.claude.json
.codex/
.gemini/

# skill-dev worktrees
skill-dev/

# path-scoped skill artifacts
skills/*/.venv/
skills/**/__pycache__/
```

A constituent's own `.gitignore` is *more specific* than the root's, so a
negation inside it beats a root rule. Confirm with `git check-ignore -v <path>`
and read which file it names.

## Homes carry no constituent `.git`

Worth internalizing, because it explains why consumers never see any of this
machinery: the fan-out apparatus exists **only in a development checkout** of
the plugin repo. `skill-manager install` clones the plugin repo, whose tree
holds `skills/<name>/` as ordinary files, so the store copy is one git checkout
of one repo with no nested `.git` anywhere. `skt` treats it as one unit, one
`gitHash`, one notification. The upstream skill repos are invisible downstream —
which is the point.
