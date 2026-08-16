#!/usr/bin/env bash
# Shared helpers for plugin-repository's own scripts. Source this:
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$SCRIPT_DIR/plugin-repo-lib.sh"
#
# THE DEPENDENCY CHAIN, AND WHY IT IS A CHAIN
# -------------------------------------------
# A plugin repository IS an integration repository, so nothing here reimplements
# the git model, the constituent manifest, or the fan-out:
#
#   plugin-repository -> git-integration-repo -> git-issue-workflow
#
# This file resolves and sources ONE file — git-integration-repo's
# `integration-lib.sh` — which in turn resolves and sources git-issue-workflow's
# `lib.sh`. That gives every script here `die`/`info`/`step`/`help_guard`, the
# checkout predicates, `$PY`, and `manifest`, with exactly one definition of
# each, living where its owner keeps it. There is no copy of any of them in this
# repository and there must never be one: `help_guard`'s second spelling is the
# one measured in damage (git-integration-skill#7, `propagate.sh --help` running
# a real fan-out).
#
# WHICH COPY, AND IN WHAT ORDER
# -----------------------------
#   0. $GIT_INTEGRATION_REPO_SCRIPTS/integration-lib.sh   an explicit pin always
#                                                         wins — "the copy I am
#                                                         developing, not
#                                                         whatever a home
#                                                         carries".
#   1. $SKILL_MANAGER_HOME/skills/git-integration-repo/scripts/…   installed as
#                                                         a standalone skill.
#   2. $SKILL_MANAGER_HOME/plugins/*/skills/git-integration-repo/scripts/…
#                                                         installed as a
#                                                         CONTAINED skill of
#                                                         some plugin.
#
# Rung 2 is this skill taking its own advice. A contained skill's bytes live at
# `plugins/<plugin>/skills/<unit>/`, NOT `skills/<unit>/`, so every resolver
# written against the standalone path breaks the day its target is bundled —
# which is the single most likely silent failure a plugin repository causes, is
# documented in references/layout.md, is what verify.sh greps for, and would be
# embarrassing to reproduce here. `unit_dir` below is the same search, exported
# so nothing has to write a fourth copy.
#
# There is deliberately NO rung resolving the dependency relative to THIS file's
# location. Where this file happens to sit is evidence about the checkout, not
# about which copy should run.
#
# It REFUSES rather than degrading: a missing dependency is a missing
# dependency, and the remedy is one command, so the refusal prints it.
set -euo pipefail

PLUGIN_REPO_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SCRIPT_DIR:=$PLUGIN_REPO_LIB_DIR}"

_SM_HOME="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"

# The search every unit-path question in this repository goes through: store
# layout for standalone units, then for plugin-contained ones. Prints the unit's
# directory and returns 0, or returns 1 silently.
unit_dir() {
  local name="$1" c
  for c in "$_SM_HOME/skills/$name" "$_SM_HOME/plugins/$name" \
           "$_SM_HOME"/plugins/*/skills/"$name"; do
    [ -d "$c" ] && { printf '%s\n' "$c"; return 0; }
  done
  return 1
}

_GIR_SCRIPTS=""
if [ -n "${GIT_INTEGRATION_REPO_SCRIPTS:-}" ] && [ -f "${GIT_INTEGRATION_REPO_SCRIPTS}/integration-lib.sh" ]; then
  _GIR_SCRIPTS="$GIT_INTEGRATION_REPO_SCRIPTS"
else
  _gir_home="$(unit_dir git-integration-repo || true)"
  [ -n "$_gir_home" ] && [ -f "$_gir_home/scripts/integration-lib.sh" ] && _GIR_SCRIPTS="$_gir_home/scripts"
fi

if [ -z "$_GIR_SCRIPTS" ]; then
  printf 'error: the git-integration-repo library (integration-lib.sh) was not found, so nothing here can run.\n' >&2
  printf '  A plugin repository IS an integration repository: that unit owns the git\n' >&2
  printf '  model, the constituent manifest, refresh and propagate, and this one sources\n' >&2
  printf '  its shared vocabulary. Looked at:\n' >&2
  printf '    $GIT_INTEGRATION_REPO_SCRIPTS/integration-lib.sh  (%s)\n' \
    "${GIT_INTEGRATION_REPO_SCRIPTS:-unset}" >&2
  printf '    %s/skills/git-integration-repo/scripts/integration-lib.sh\n' "$_SM_HOME" >&2
  printf '    %s/plugins/*/skills/git-integration-repo/scripts/integration-lib.sh\n' "$_SM_HOME" >&2
  printf '  Install the dependency:\n' >&2
  printf '    skill-manager install github:haydenrear/git-integration-skill\n' >&2
  printf '  or point at the copy you are working on:\n' >&2
  printf '    GIT_INTEGRATION_REPO_SCRIPTS=/path/to/git-integration-repo/scripts %s\n' "$0" >&2
  exit 1
fi

# shellcheck source=/dev/null
. "$_GIR_SCRIPTS/integration-lib.sh"

# integration-lib.sh defines `manifest` as
#   "$PY" "${SCRIPT_DIR:-$INTEGRATION_LIB_DIR}/_manifest.py"
# and SCRIPT_DIR is OURS — every caller in this repository sets it to this
# repository's scripts/ before sourcing, which is where _manifest.py is NOT.
# That resolution is correct for its own callers (they sit beside the helper)
# and wrong for ours by exactly one directory, so redefine it against the
# resolved dependency instead of tampering with SCRIPT_DIR, which other things
# read.
manifest() { "$PY" "$_GIR_SCRIPTS/_manifest.py" "$@"; }

# Path to a dependency script, for the places that shell out rather than source
# (finalize/refresh/propagate stay the dependency's to run).
gir_script() { printf '%s/%s\n' "$_GIR_SCRIPTS" "$1"; }

# ------------------------------------------------------------ plugin identity
#
# `repo_root` (from lib.sh) walks up to the nearest integration.toml, which is
# the parent in an integration repo and therefore also here. A plugin repository
# additionally needs the PLUGIN marker, and needing both is the definition:
# without integration.toml the fan-out machinery has nothing to read, without
# plugin.json skill-manager will not install the result as a plugin.
PLUGIN_JSON=".claude-plugin/plugin.json"
PLUGIN_TOML="skill-manager-plugin.toml"

require_plugin_repo() {
  local root="$1"
  [ -f "$root/$PLUGIN_JSON" ] || die_fix 1 \
    "$PLUGIN_REPO_LIB_DIR/init-plugin-repo.sh <plugin-name> $root" \
    "not a plugin repository: no $PLUGIN_JSON at $root
  It may be a plain integration repo. A plugin repository needs BOTH markers:
  integration.toml (constituents) and $PLUGIN_JSON (skill-manager plugin)."
}

# One JSON reader, stdlib only, so this works on the same interpreters $PY picks.
plugin_json_get() {
  local root="$1" key="$2"
  "$PY" - "$root/$PLUGIN_JSON" "$key" <<'PY'
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        print(json.load(fh).get(sys.argv[2], "") or "")
except FileNotFoundError:
    print("")
except json.JSONDecodeError as exc:
    sys.exit(f"error: {sys.argv[1]} is not valid JSON: {exc}")
PY
}

# `[plugin] name`/`version`/`description` out of skill-manager-plugin.toml.
# Deliberately the same dependency-free subset _manifest.py parses (quoted
# scalars, one table) rather than tomllib, which the system python3 may lack.
plugin_toml_get() {
  local root="$1" key="$2"
  "$PY" - "$root/$PLUGIN_TOML" "$key" <<'PY'
import sys
path, key = sys.argv[1], sys.argv[2]
try:
    text = open(path, encoding="utf-8").read()
except FileNotFoundError:
    print(""); raise SystemExit(0)
table = None
for line in text.splitlines():
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    if s.startswith("["):
        table = s.strip("[]").strip()
        continue
    if table == "plugin" and "=" in s:
        k, _, v = s.partition("=")
        if k.strip() == key:
            v = v.strip()
            if v[:1] in "\"'" and v.count(v[0]) > 1:
                print(v[1:v.index(v[0], 1)])
            else:
                print(v.split("#")[0].strip().strip("\"'"))
            raise SystemExit(0)
print("")
PY
}

# A constituent path is only a contained skill when it is under skills/.
# Everything downstream of this predicate — the plugin runtime finding the
# skill, `plugin:skill` addressing it, install placing its bytes — depends on
# the directory name, so it is checked rather than assumed.
is_contained_skill_path() {
  case "$1" in skills/*) return 0 ;; *) return 1 ;; esac
}
