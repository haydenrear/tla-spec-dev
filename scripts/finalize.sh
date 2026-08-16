#!/usr/bin/env bash
# finalize.sh
# Restore each bundled skill's own .git + remote, AFTER its files are committed
# to the parent. Delegates the work to git-integration-repo's
# finalize-constituents.sh and adds the one thing that script cannot do here:
# CHECK THE INVARIANT.
#
# WHY THIS WRAPPER EXISTS (it is not ceremony)
# -------------------------------------------
# The dependency guards the load-bearing invariant — constituent files must be
# committed to the parent BEFORE any constituent has a .git — like this:
#
#   git -C "$ROOT" status --porcelain -- constituents | grep -q .
#
# The pathspec is the literal directory `constituents`. A plugin repository has
# no such directory (init-plugin-repo.sh removes it: contained skills MUST live
# at skills/<name>/ or neither skill-manager nor the plugin runtime finds them),
# so the pathspec matches nothing, the guard produces empty output, and it never
# fires. Measured: `git status --porcelain -- constituents` exits 0 with no
# output in a repo whose skills/ tree is entirely uncommitted.
#
# What that costs, exactly: run finalize before committing and every
# skills/<name>/ gets a real .git; the parent's next `git add -A` then records
# each one as a GITLINK (mode 160000) instead of blobs, which is the submodule
# failure the whole model is built to prevent. The dependency's clean-tree check
# fires only afterwards, when the damage is already on disk.
#
# So this script re-asks the same question against the paths the manifest
# actually declares, refuses first, and only then execs the dependency. The
# better fix lives upstream — derive the pathspec from the manifest's `path`
# values rather than hardcoding one — and until that lands, this is the door.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$SCRIPT_DIR/plugin-repo-lib.sh"

usage() {
  cat >&2 <<'EOF'
usage: finalize.sh

  Takes no arguments. Asserts every registered skill's files are committed to
  the parent, then runs git-integration-repo's finalize-constituents.sh, which
  gives each skills/<name>/ its own .git, origin, fetch and reset --hard.

  -h, --help  This message.

Use this instead of calling finalize-constituents.sh directly in a plugin
repository: that script's "did you commit first" guard is scoped to a
constituents/ directory a plugin repo does not have, so it cannot fire here.

Exit codes: 0 finalized - 1 refused (uncommitted skill files) or delegate failed
EOF
}
help_guard "$@"
[ $# -eq 0 ] || { usage; die "finalize.sh takes no arguments, got: $*"; }

ROOT="$(repo_root)"; cd "$ROOT"
require_plugin_repo "$ROOT"

PATHS=()
while IFS=$'\t' read -r name path remote branch; do
  [ -n "$name" ] || continue
  PATHS+=("$path")
done < <(manifest "$ROOT" constituents)

# `${PATHS[@]}` on an empty array is an unbound-variable error under `set -u` in
# bash 3.2, which is what macOS ships as /bin/bash.
if [ "${#PATHS[@]}" -eq 0 ]; then
  info "no constituents registered — nothing to finalize"
  exit 0
fi

step "Invariant: skill files committed before any .git exists"
if [ -n "$(git -C "$ROOT" status --porcelain -- "${PATHS[@]}")" ]; then
  git -C "$ROOT" status --short -- "${PATHS[@]}" >&2
  die_fix 1 "git -C $ROOT add -A && git -C $ROOT commit -m 'bundle skills'" \
    "the skill files listed above are not committed to the parent yet.
  Finalizing now would give each one a .git, and the parent's next \`git add\`
  would record it as a gitlink (mode 160000) instead of blobs — the submodule
  failure this model exists to prevent. Commit first, then re-run."
fi
info "clean: ${#PATHS[@]} skill path(s) already committed"

exec "$(gir_script finalize-constituents.sh)"
