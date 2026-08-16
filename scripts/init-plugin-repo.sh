#!/usr/bin/env bash
# init-plugin-repo.sh <plugin-name> [dir]
# Scaffold a plugin repository: the INTEGRATION markers (delegated to
# git-integration-repo's init-integration.sh) plus the PLUGIN markers that make
# the same directory installable as a skill-manager plugin. Run add-skill.sh
# next.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$SCRIPT_DIR/plugin-repo-lib.sh"
ASSETS="$SCRIPT_DIR/../assets"

usage() {
  cat >&2 <<'EOF'
usage: init-plugin-repo.sh <plugin-name> [dir]

  plugin-name  The PLUGIN's name — what consumers install and what prefixes its
               skills as `<plugin>:<skill>`. Written to .claude-plugin/plugin.json
               and skill-manager-plugin.toml. It is not the repo name; the
               convention is repo `<plugin-name>-plugin`.
  dir          Where to scaffold it. Default: the current directory.
  -h, --help   This message, answered BEFORE anything is created.

Delegates the integration half (integration.toml, INTEGRATION.md, root
.gitignore, git init) to git-integration-repo's init-integration.sh, then adds
.claude-plugin/plugin.json, skill-manager-plugin.toml, PLUGIN-REPO.md, skills/,
and the plugin-repo .gitignore rules.
EOF
}
help_guard "$@"

NAME="${1:-}"; [ -n "$NAME" ] || { usage; die "a plugin name is required"; }
case "$NAME" in
  */*|*' '*) die "'$NAME' is not a plugin name: no slashes or spaces (it is a unit name, not a path)" ;;
esac
DIR="${2:-.}"
mkdir -p "$DIR"; DIR="$(cd "$DIR" && pwd)"

step "Integration half (git-integration-repo)"
# Its scaffold owns integration.toml, INTEGRATION.md, the root .gitignore,
# constituents/ and `git init`. Delegated rather than reimplemented: this skill
# has no business owning a second copy of the integration markers.
"$(gir_script init-integration.sh)" "$NAME" "$DIR"

cd "$DIR"

step "Plugin half"

mkdir -p .claude-plugin skills
if [ -f "$PLUGIN_JSON" ]; then
  info "$PLUGIN_JSON exists — leaving it"
else
  sed -e "s/REPLACE_NAME/$NAME/" \
      -e "s/REPLACE_DESCRIPTION/Bundled skill-manager skills, versioned and changed as one unit./" \
      "$ASSETS/plugin.json.scaffold" > "$PLUGIN_JSON"
  info "wrote $PLUGIN_JSON"
fi

if [ -f "$PLUGIN_TOML" ]; then
  info "$PLUGIN_TOML exists — leaving it"
else
  sed -e "s/REPLACE_NAME/$NAME/" \
      -e "s/REPLACE_DESCRIPTION/Bundled skill-manager skills, versioned and changed as one unit./" \
      "$ASSETS/skill-manager-plugin.toml.scaffold" > "$PLUGIN_TOML"
  info "wrote $PLUGIN_TOML"
fi

[ -f PLUGIN-REPO.md ] || { cp "$ASSETS/PLUGIN-REPO.md.scaffold" PLUGIN-REPO.md; info "wrote PLUGIN-REPO.md"; }

# The dependency's scaffold made constituents/. A plugin repository does not use
# it — contained skills MUST be at skills/<name>/ — so drop it when it is the
# empty directory the scaffold just created, and leave it alone if it holds
# anything (that is a repo with both shapes, and deleting a constituent is not
# this script's call).
if [ -d constituents ] && [ -z "$(ls -A constituents 2>/dev/null)" ]; then
  rmdir constituents
  info "removed the empty constituents/ — this repo's constituents live at skills/"
fi
touch skills/.gitkeep

# Append the plugin-repo ignore rules once. Marker-guarded rather than
# `>>`-blind: init is expected to be re-runnable on an existing repo.
if grep -q '^# --- plugin repository additions' .gitignore 2>/dev/null; then
  info ".gitignore already carries the plugin-repo rules"
else
  cat "$ASSETS/gitignore.plugin-repo.scaffold" >> .gitignore
  info "appended the plugin-repo rules to .gitignore"
fi

cat >&2 <<EOF

Plugin repository '$NAME' scaffolded in $DIR

Next:
  1. Describe it:  edit .claude-plugin/plugin.json + skill-manager-plugin.toml
                   (both descriptions; keep name/version in agreement)
  2. Add skills:   $SCRIPT_DIR/add-skill.sh <skill-name> <remote-url> [branch]
  3. Commit them:  git add -A && git commit -m "bundle <skills>"      # BEFORE finalize
  4. Finalize:     $(gir_script finalize-constituents.sh)
  5. Verify:       $SCRIPT_DIR/verify.sh
EOF
