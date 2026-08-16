#!/usr/bin/env bash
# add-skill.sh <skill-name> <remote-url> [default-branch]
# Clone a skill repo into skills/<name>/, STRIP its .git (so its files become
# plain files the parent tracks), and register it in integration.toml as a
# constituent. Does NOT commit and does NOT restore .git — that is the
# finalize.sh — this skill's guarded wrapper — run AFTER you commit. That ordering is
# git-integration-repo's load-bearing invariant and this script does not change
# it; what it changes is the PATH (skills/, not constituents/) and the refusals.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$SCRIPT_DIR/plugin-repo-lib.sh"

usage() {
  cat >&2 <<'EOF'
usage: add-skill.sh <skill-name> <remote-url> [default-branch]

  skill-name      Directory name under skills/. MUST equal the skill's own
                  SKILL.md `name:` — that is what agents invoke as
                  `<plugin>:<skill-name>`.
  remote-url      Clone source, kept as the constituent's origin.
  default-branch  Branch to clone. Default: the remote's HEAD.
  -h, --help      This message, answered BEFORE the clone.

Clones into skills/<name>, strips .git, and registers the constituent. Refuses a
repo a plugin cannot carry: no root SKILL.md, a name that disagrees with the
directory, or a nested plugin. Does not commit; run finalize.sh after you do
(NOT the dependency's finalize-constituents.sh: its "did you commit first" guard
is scoped to a constituents/ directory a plugin repo does not have).

Why not git-integration-repo's add-constituent.sh: it hardcodes
constituents/<name>, and skill-manager + the harness plugin runtime find
contained skills only under skills/. Every OTHER script of that skill reads the
path from integration.toml and works here unmodified.
EOF
}
help_guard "$@"

NAME="${1:-}"; REMOTE="${2:-}"; BRANCH="${3:-}"
[ -n "$NAME" ] && [ -n "$REMOTE" ] || { usage; die "a skill name and a remote url are required"; }
require_unit_name "$NAME" "skill name"

ROOT="$(repo_root)"; cd "$ROOT"
require_plugin_repo "$ROOT"

REL="skills/$NAME"
[ -e "$REL" ] && die "$REL already exists"

# Registered already? _manifest.py add refuses a duplicate name, but only after
# the clone; asking first keeps a re-run from leaving a half-added tree behind.
# `grep -q` exits on its first match, which can SIGPIPE the writer and, under
# `pipefail`, make a FOUND duplicate report as not-found. Collect, then test.
# `-F` because a skill name is a literal, not a BRE.
if [ -n "$(manifest "$ROOT" constituents | cut -f1 | grep -Fx -- "$NAME" || true)" ]; then
  die "'$NAME' is already a constituent in integration.toml
  Update it in place (git -C $REL fetch && git -C $REL reset --hard origin/<branch>)
  or remove the block first."
fi

mkdir -p skills

step "Cloning skill '$NAME'"
if [ -n "$BRANCH" ]; then
  git clone -q --branch "$BRANCH" "$REMOTE" "$REL"
else
  git clone -q "$REMOTE" "$REL"
  BRANCH="$(git -C "$REL" symbolic-ref --quiet --short HEAD || echo main)"
fi
info "cloned into $REL (default branch: $BRANCH)"

# Refuse BEFORE stripping .git, and take the directory with us on the way out:
# a half-added skills/<name> is exactly the state that gets committed by a later
# `git add -A` and becomes a constituent nobody registered.
bail() { cd "$ROOT"; rm -rf "$REL"; die "$*"; }

step "Checking it can be a contained skill"

[ -f "$REL/SKILL.md" ] || bail "$REMOTE has no SKILL.md at its root, so it cannot be a plugin's contained skill.
  A plugin finds contained skills at skills/<name>/SKILL.md — nested one level
  deeper is not found. If this repo is a doc-repo or a harness, it does not
  belong in a plugin bundle; reference it by coord instead."

[ -f "$REL/.claude-plugin/plugin.json" ] && bail "$REMOTE is itself a PLUGIN (.claude-plugin/plugin.json at its root).
  Plugins do not nest. Bundle that plugin's constituent SKILL repos here, or
  reference the plugin by coord from skill-manager-plugin.toml."

# The frontmatter `name:` is the invocation name. A directory that disagrees
# with it gives `<plugin>:<one>` for a skill everything else calls <other>.
DECLARED="$(awk '
  /^---[[:space:]]*$/ { seen++; if (seen == 2) exit; next }
  seen == 1 && /^name:[[:space:]]*/ { sub(/^name:[[:space:]]*/, ""); gsub(/["'"'"']/, ""); print; exit }
' "$REL/SKILL.md" | tr -d '\r' | sed 's/[[:space:]]*$//')"
if [ -z "$DECLARED" ]; then
  info "WARNING: $REL/SKILL.md declares no frontmatter name: — skill-manager will not install it"
elif [ "$DECLARED" != "$NAME" ]; then
  bail "name mismatch: SKILL.md declares name: $DECLARED, you asked for skills/$NAME.
  The directory and the declared name must agree — agents invoke
  <plugin>:<name>. Re-run as:
    $0 $DECLARED $REMOTE ${BRANCH:-}"
fi

[ -f "$REL/skill-manager.toml" ] || info "WARNING: no skill-manager.toml in $REL — check it declares [skill] name/version, or its deps will not be unioned into the plugin"

info "ok: root SKILL.md, name '$NAME'"

step "Stripping .git and registering"
rm -rf "$REL/.git"
info "removed $REL/.git — the skill is now plain files the parent can track"

# Through `bail` as well: a registration that fails here leaves plain files at
# skills/<name> that no manifest declares, and the next `git add -A` commits
# them as a constituent nobody can refresh or propagate.
manifest "$ROOT" add "$NAME" "$REL" "$REMOTE" "$BRANCH" >/dev/null \
  || bail "could not register '$NAME' in integration.toml (is it writable?). The clone was removed."
info "registered in integration.toml (path: $REL)"

cat >&2 <<EOF

'$NAME' staged as plain files at $REL. When you have added every skill:
  git add -A && git commit -m "bundle <skills>"     # BEFORE finalize — the invariant
  $SCRIPT_DIR/finalize.sh                           # guards the invariant, restores each .git
  $SCRIPT_DIR/verify.sh
EOF
