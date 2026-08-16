#!/usr/bin/env bash
# verify.sh
# Assert this repo is BOTH halves of a plugin repository:
#   integration  — delegated in full to git-integration-repo's verify.sh
#                  (parent tree clean, no gitlinks, constituents wired)
#   plugin       — markers present and agreeing, every constituent at skills/,
#                  every contained skill loadable, and no sibling resolver that
#                  the move to plugins/<plugin>/skills/ has already broken
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$SCRIPT_DIR/plugin-repo-lib.sh"

usage() {
  cat >&2 <<'EOF'
usage: verify.sh

  Takes no arguments. Runs git-integration-repo's verify.sh, then the checks
  that are specific to a plugin repository.

  -h, --help  This message.

Exit codes: 0 healthy - 1 something failed
EOF
}
help_guard "$@"
[ $# -eq 0 ] || { usage; die "verify.sh takes no arguments, got: $*"; }

ROOT="$(repo_root)"; cd "$ROOT"
require_plugin_repo "$ROOT"
fail=0

# ---------------------------------------------------------- the integration half
# Not reimplemented, and its failure is this script's failure. Its checks are
# the ones that catch a broken git model, which is the expensive kind. Its own
# "== Result ==" belongs to that half; this script's verdict is the last line.
step "Integration half — delegated to git-integration-repo's verify.sh"
"$(gir_script verify.sh)" || fail=1

step "Plugin markers"
PNAME="$(plugin_json_get "$ROOT" name)"
PVER="$(plugin_json_get "$ROOT" version)"
[ -n "$PNAME" ] || { info "$PLUGIN_JSON declares no name"; fail=1; }
[ -n "$PVER" ]  || { info "$PLUGIN_JSON declares no version"; fail=1; }

if [ -f "$PLUGIN_TOML" ]; then
  TNAME="$(plugin_toml_get "$ROOT" name)"
  TVER="$(plugin_toml_get "$ROOT" version)"
  drift=0
  if [ "$TNAME" != "$PNAME" ]; then
    info "name drift: $PLUGIN_JSON says '$PNAME', $PLUGIN_TOML says '$TNAME'"; drift=1
  fi
  if [ "$TVER" != "$PVER" ]; then
    info "version drift: $PLUGIN_JSON says '$PVER', $PLUGIN_TOML says '$TVER' (use scripts/release.sh — it writes both)"; drift=1
  fi
  if [ "$drift" -eq 0 ]; then info "$PNAME $PVER — both manifests agree"; else fail=1; fi
else
  info "no $PLUGIN_TOML — the plugin installs, but declares no skill-manager-side deps or references"
fi

# A SKILL.md at the plugin ROOT is never loaded: the resolver sees plugin.json
# first and the file is silently dead. Contained skills go under skills/.
if [ -f SKILL.md ]; then
  info "SKILL.md at the plugin root — it is NEVER loaded (the resolver detects the plugin first). Move it to skills/<name>/."
  fail=1
fi

step "Constituents are contained skills"
count=0
names=""
while IFS=$'\t' read -r name path remote branch; do
  [ -n "$name" ] || continue
  count=$((count + 1))
  names="$names $name"
  if ! is_contained_skill_path "$path"; then
    info "$name: path '$path' is not under skills/ — skill-manager and the plugin runtime will not find it (see references/layout.md)"
    fail=1; continue
  fi
  if [ ! -f "$path/SKILL.md" ]; then
    info "$name: no SKILL.md at $path/SKILL.md"; fail=1; continue
  fi
  declared="$(awk '
    /^---[[:space:]]*$/ { seen++; if (seen == 2) exit; next }
    seen == 1 && /^name:[[:space:]]*/ { sub(/^name:[[:space:]]*/, ""); gsub(/["'"'"']/, ""); print; exit }
  ' "$path/SKILL.md" | tr -d '\r' | sed 's/[[:space:]]*$//')"
  if [ -z "$declared" ]; then
    info "$name: SKILL.md declares no frontmatter name:"; fail=1
  elif [ "$declared" != "$name" ]; then
    info "$name: SKILL.md declares name: $declared — agents would invoke ${PNAME:-<plugin>}:$declared from a directory called $name"; fail=1
  else
    info "$name: ok (skills/$name, invoked as ${PNAME:-<plugin>}:$name)"
  fi
done < <(manifest "$ROOT" constituents)
[ "$count" -gt 0 ] || info "no constituents registered yet"

# A skills/<dir> that is not a constituent is legitimate — a skill this bundle
# owns outright, with no upstream repo of its own — but it will never receive a
# fan-out, so say so once rather than let it be assumed.
if [ -d skills ]; then
  for d in skills/*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d")"
    case " $names " in *" $n "*) continue ;; esac
    info "note: skills/$n is not in integration.toml — bundle-owned (refresh/propagate will skip it)"
  done
fi

# ------------------------------------------------------------ the silent one
#
# A contained skill's bytes live at plugins/<plugin>/skills/<unit>/, so any
# resolver written as $SKILL_MANAGER_HOME/skills/<unit>/… stops resolving the
# day <unit> is bundled — at SOURCE time, in a script that may already be
# halfway through a fan-out. Grep for the bare form naming a unit THIS bundle
# carries. Reported, not failed: the caller may be a repo you do not control
# yet, and a check that blocks `verify.sh` on someone else's file gets disabled
# rather than fixed.
step "Store-path resolvers (references/layout.md)"
hits=0
for n in $names; do
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    info "$line"
    hits=$((hits + 1))
  done < <(grep -rn --exclude-dir=.git "skills/$n\b" skills hooks commands agents 2>/dev/null \
             | grep -E 'SKILL_MANAGER_HOME|\.skill-manager/skills/' || true)
done
if [ "$hits" -eq 0 ]; then
  info "none — no bundled unit is resolved through the standalone \$SKILL_MANAGER_HOME/skills/<unit> path"
else
  info "^ $hits reference(s) resolve a BUNDLED unit at its standalone store path. Add a"
  info "  plugins/*/skills/<unit> rung (references/layout.md § Store paths) before this ships."
fi

# ------------------------------------------------------- the one that fails LATER
#
# `skill-imports: unit: <name>` resolves against INSTALLED UNITS, and a contained
# skill is not one — `skill-manager show <contained>` answers "unit not found".
# So an import naming a bundled skill fails validation on the IMPORTING unit's
# next publish or sync, with:
#
#   skill-imports[0] references missing unit `<name>`; install it or fix the `unit` value
#
# Inside this bundle that is a defect we can see and must report; outside it, it
# is a sweep migration.md § 2 describes and this script cannot reach.
step "skill-imports naming a bundled skill (references/imports.md)"
ihits=0
for n in $names; do
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    info "$line"
    ihits=$((ihits + 1))
  done < <(grep -rn --include='*.md' --exclude-dir=.git -E "^[[:space:]]*-?[[:space:]]*(unit|skill):[[:space:]]*[\"']?$n[\"']?[[:space:]]*$" \
             skills hooks commands agents 2>/dev/null || true)
done
if [ "$ihits" -eq 0 ]; then
  info "none"
else
  info "^ $ihits import(s) name a bundled skill as a UNIT. Rewrite each as"
  info "  'unit: ${PNAME:-<plugin>}' with 'path: skills/<skill>/<file>' — the contained"
  info "  skill is not an installed unit and the validator will refuse it."
  fail=1
fi

step "Result (plugin repository: both halves)"
if [ "$fail" -eq 0 ]; then info "PASS"; else info "FAIL"; fi
exit $fail
