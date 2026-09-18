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

# What both greps look at. The root markers are IN, and deliberately: the whole
# claim is that prose counts as much as shell — a PLUGIN-REPO.md or README.md
# line telling an agent to run $SKILL_MANAGER_HOME/skills/<bundled>/… is an
# instruction that will fail, and no validator anywhere checks prose.
SCAN_DIRS=""
for d in skills hooks commands agents; do [ -d "$d" ] && SCAN_DIRS="$SCAN_DIRS $d"; done
SCAN_FILES=""
for f in PLUGIN-REPO.md INTEGRATION.md README.md skill-manager-plugin.toml; do
  [ -f "$f" ] && SCAN_FILES="$SCAN_FILES $f"
done

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
#
# FILE-level, not line-level. The line-level form this replaced passed the very
# idiom these docs teach — `H="${SKILL_MANAGER_HOME:-…}"` on one line and
# `"$H/skills/<unit>/…"` on the next — because it demanded the marker and the
# path in one line. It also flagged the plugins/*/skills rung that IS the fix.
# So: a file that mentions a bundled unit's store path AND talks about the home
# AND carries no plugin rung for that unit is a hit; anything with the rung is
# already fixed and stays quiet.
hits=0
for n in $names; do
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    grep -qE 'SKILL_MANAGER_HOME|\.skill-manager' "$f" || continue
    grep -qE "plugins/[^[:space:]\"']*/skills/$n" "$f" && continue
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      info "$f:$line"
      hits=$((hits + 1))
    done < <(grep -nE "skills/$n/" "$f" | head -3)
  done < <(grep -rl --exclude-dir=.git -- "skills/$n/" . 2>/dev/null || true)
done
if [ "$hits" -eq 0 ]; then
  info "none — no file resolves a bundled unit at its standalone store path without a plugins/*/skills rung"
else
  info "^ $hits line(s), in files that name the home and carry no plugins/*/skills rung."
  info "  Add one (references/layout.md § Store paths) or, in prose, say <plugin>:<skill>."
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
#
# FRONTMATTER ONLY — between the first two `---` of a markdown file. A plain
# line grep failed this repo on its own documentation: a fenced ```yaml
# counter-example showing the WRONG form is not a wrong import, and a check that
# fails you for documenting a hazard is a check that gets deleted. (It would
# also have failed this very skill, whose SKILL.md frontmatter legitimately
# imports `unit: git-integration-repo`.)
ihits=0
for n in $names; do
  while IFS= read -r hit; do
    [ -n "$hit" ] || continue
    info "$hit"
    ihits=$((ihits + 1))
  done < <(
    find . -name '*.md' -not -path './.git/*' -print 2>/dev/null | while IFS= read -r f; do
      awk -v unit="$n" -v file="$f" '
        NR == 1 && $0 !~ /^---[[:space:]]*$/ { exit }        # no frontmatter at all
        /^---[[:space:]]*$/ { seen++; if (seen == 2) exit; next }
        seen == 1 && $0 ~ "^[[:space:]]*-?[[:space:]]*(unit|skill):[[:space:]]*[\"'\'']?" unit "[\"'\'']?[[:space:]]*$" {
          printf "%s:%d:%s\n", file, NR, $0
        }
      ' "$f"
    done
  )
done
if [ "$ihits" -eq 0 ]; then
  info "none"
else
  info "^ $ihits frontmatter import(s) name a bundled skill as a UNIT. Rewrite each as"
  info "  'unit: ${PNAME:-<plugin>}' with 'path: skills/<skill>/<file>' — the contained"
  info "  skill is not an installed unit and the validator will refuse it."
  fail=1
fi

# --------------------------------------------------- state, reported not judged
#
# Two questions verify.sh used to answer by accident, both wrongly:
#   * "did the fan-out happen?" It cannot tell. It printed the MANIFEST branch
#     and exited 0 whether propagate.sh had run or not.
#   * "is a skills/<dir> that the manifest does not list fine?" A bundle-owned
#     skill and the half-finished removal of a constituent look identical —
#     except that the half-removed one still has the .git its clone left.
step "Constituent state (evidence, not a verdict)"
for d in skills/*/; do
  [ -d "$d" ] || continue
  n="$(basename "$d")"
  case " $names " in
    *" $n "*)
      [ -d "$d/.git" ] || continue
      br="$(git -C "$d" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
      dirty=""; [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ] && dirty=" DIRTY(unpropagated edits)"
      ahead="$(git -C "$d" log --oneline "origin/$br..HEAD" 2>/dev/null | grep -c . || true)"
      case "$ahead" in ''|0) ahead="" ;; *) ahead=" ${ahead} commit(s) not on origin/$br" ;; esac
      info "$n: on '$br'$ahead$dirty"
      ;;
    *)
      if [ -d "$d/.git" ]; then
        info "$n: NOT in integration.toml but still has its own .git — a half-finished removal"
        info "  (a genuinely bundle-owned skill has no .git). Finish it: rm -rf $d and drop nothing else,"
        info "  or re-register it. Left as is, it ships to every consumer and receives no refresh or fan-out."
      else
        info "note: skills/$n is not in integration.toml — bundle-owned (refresh/propagate skip it)"
      fi
      ;;
  esac
done
info "this step never fails the run: 'DIRTY' before a fan-out is work in progress, and"
info "  verify.sh cannot tell a completed propagation from a dry run — lifecycle.md § C can."

step "Result (plugin repository: both halves)"
if [ "$fail" -eq 0 ]; then info "PASS"; else info "FAIL"; fi
exit $fail
