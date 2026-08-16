# Migration: standalone skills (or a harness) → a plugin repository

Bundling changes three things a consumer can observe: the store path, the
invocation name, and the coord. Every consumer-side file that names a bundled
skill has to move with it. Work the checklist; the failures are quiet.

A worked precedent to compare against: `skill-publisher` was a standalone skill
and is now `skt:unit-authoring`, a contained skill of the `skt` plugin, whose
repo is still called `skill-publisher-skill`. Every row of the table in step 3
is a thing that had to change for it.

## 0. Decide membership first

`why.md` § *Which skills belong in one plugin repo*. Membership is the expensive
part to reverse: taking a skill back out means consumers that only wanted it are
already installing the bundle, and its invocation name changes again.

## 1. Build the bundle

```bash
P="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/plugin-repository/scripts"
S="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-integration-repo/scripts"

$P/init-plugin-repo.sh my-plugin ~/IdeaProjects/my-plugin-repo
cd ~/IdeaProjects/my-plugin-repo
$P/add-skill.sh alpha-skill git@github.com:owner/alpha-skill.git main
$P/add-skill.sh beta-skill  git@github.com:owner/beta-skill.git  main
git add -A && git commit -m "bundle alpha-skill, beta-skill"    # BEFORE finalize
$S/finalize-constituents.sh
$P/verify.sh
```

The upstream repos are untouched. Nothing is decided yet — the bundle is
additive until a consumer switches to it.

## 2. Fix the resolvers before anyone installs it

`verify.sh` reports every `$SKILL_MANAGER_HOME/skills/<unit>/…` reference inside
the bundled skills that names a unit in this bundle, or any other unit that is
already plugin-contained. Each one is a script that will refuse at source time
once the path moves. Fix them in the constituent (so the fix reaches the skill's
own repo too, via flow C), giving each resolver a plugin rung:

```bash
for c in ${PIN:+"$PIN/lib.sh"} \
         "$H/skills/<unit>/scripts/lib.sh" \
         "$H"/plugins/*/skills/<unit>/scripts/lib.sh; do
  [ -f "$c" ] && { LIB="$c"; break; }
done
```

Search the whole world you control, not just the bundle — the caller may be a
skill you are *not* bundling:

```bash
grep -rn 'skill-manager/skills/\|SKILL_MANAGER_HOME}/skills/\|SKILL_MANAGER_HOME:-\$HOME/.skill-manager}/skills/' \
  ~/IdeaProjects --include='*.sh' --include='*.md' --include='*.py' | grep -E 'alpha-skill|beta-skill'
```

Prose counts as much as shell: a `SKILL.md` that tells an agent to run
`$SKILL_MANAGER_HOME/skills/alpha-skill/scripts/x.sh` is an instruction that
will fail, and no test catches it.

## 3. Switch the consumers

Per consuming home or project, in this order:

```bash
# a. install the bundle
skill-manager install github:owner/my-plugin-repo --yes

# b. remove the now-duplicated standalone units — otherwise the home carries the
#    same skill twice, at two versions, with two sync paths and no rule about
#    which one an agent read
skill-manager uninstall alpha-skill
skill-manager uninstall beta-skill

# c. confirm
skill-manager list                      # KIND=plugin, one row
ls ~/.skill-manager/plugins/my-plugin/skills/
```

Then update the files that name them:

| File | Before | After |
|---|---|---|
| `skill-project.toml` | `[skills.alpha-skill] source = "github:owner/alpha-skill"` | `[skills.my-plugin] source = "github:owner/my-plugin-repo"` (one entry) |
| `harness.toml` | `units = ["github:owner/alpha-skill", "github:owner/beta-skill"]` | `units = ["github:owner/my-plugin-repo"]` |
| `skill-manager.toml` `skill_references` in *other* units | `"github:owner/alpha-skill"` | `"github:owner/my-plugin-repo"` |
| Prose / skill invocation | `alpha-skill` | `my-plugin:alpha-skill` |
| `skill-imports:` frontmatter | `unit: alpha-skill, path: SKILL.md` | `unit: my-plugin, path: skills/alpha-skill/SKILL.md` |

The `skill-imports` row follows the shape `skt`'s own contained skills take
(`unit: skt, path: skills/unit-authoring/SKILL.md`) — the import is against the
installed **unit**, and the path is relative to that unit's root. Confirm with
`skill-manager project resolve` on a real project before relying on it: resolve
validates imports against installed units and will name what it cannot find.

## 4. Keep the upstream repos alive

Do **not** archive the skill repos. They are the skills' identity and the target
of every fan-out; a bundle whose members have no upstream is just a monorepo
that has lost its history story. What changes is only that consumers stop
installing them directly.

If a skill is genuinely bundle-only from now on, say so in its README rather
than deleting it — the fan-out still needs a place to push.

## From a harness

A harness that exists only to list units:

```toml
# before
units = ["github:owner/alpha-skill", "github:owner/beta-skill", "github:owner/gamma-skill"]
```

Bundle those three, then either

- **the harness shrinks** — `units = ["github:owner/my-plugin-repo"]`, keeping
  `docs = [...]` and its instance lifecycle, which a plugin cannot do; or
- **the harness disappears** — when it had no `docs` and no `[[mcp_tools]]`
  selection, everything it did is now the plugin's, and the plugin can
  additionally carry `hooks/`, `commands/` and `agents/`.

Instances first: `skill-manager harness rm <id>` for each live instance before
uninstalling the template, or the projections outlive it.

## Rollback

Cheap while nothing has been fan-out-only. Uninstall the plugin, re-install the
standalone skills, revert the consumer-side edits from step 3. The skill repos
still hold every change, provided flow C (`propagate.sh`) kept up — which is the
other reason not to let propagation lag.
