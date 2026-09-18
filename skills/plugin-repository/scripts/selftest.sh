#!/usr/bin/env bash
# selftest.sh
# Prove this skill's own scripts, from a CHECKOUT of it. Two phases:
#
#   STATIC   properties that must hold for every script here, including ones
#            added later: a help guard, no second copy of a dependency's
#            library, no rung that resolves the dependency relative to this
#            file, and a plugins/*/skills rung in the unit search (this skill
#            failing its own rule 2 would be the joke that writes itself).
#
#   LIVE     a real plugin repository, end to end, in a temp dir: scaffold,
#            onboard a local skill repo, commit, finalize, verify. Skipped —
#            loudly — when git-integration-repo is not installed, because the
#            static phase is still worth running in that state.
#
# Needs no skill-manager CLI and no network.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
pass=0; fail=0
ok()   { printf '  ok   %s\n' "$*"; pass=$((pass + 1)); }
bad()  { printf '  FAIL %s\n' "$*"; fail=$((fail + 1)); }
phase(){ printf '\n== %s ==\n' "$*"; }

ENTRYPOINTS=()
for f in "$HERE"/*.sh; do
  case "$(basename "$f")" in
    plugin-repo-lib.sh|selftest.sh) continue ;;
  esac
  ENTRYPOINTS+=("$f")
done

phase "STATIC: every entry point guards its arguments"
for f in "${ENTRYPOINTS[@]}"; do
  n="$(basename "$f")"
  grep -q '^usage()' "$f"    || bad "$n defines no usage()"
  grep -q '^help_guard "\$@"' "$f" || { bad "$n does not call help_guard \"\$@\""; continue; }
  # help_guard must run before anything that touches the filesystem or the
  # network. git-integration-skill#7 was exactly this ordering: `--help` read as
  # a positional and a real fan-out ran.
  #
  # The scan skips the body of usage() — its heredoc is prose that names the
  # very commands being looked for, and a check that flags documentation is a
  # check that gets deleted.
  gline="$(grep -n '^help_guard "\$@"' "$f" | head -1 | cut -d: -f1)"
  bline="$(awk '
    /^usage\(\)/      { inusage = 1 }
    inusage && /^}/   { inusage = 0; next }
    inusage           { next }
    /^[[:space:]]*(git|mkdir|rm|cp|mv|sed)[[:space:]]/ { print NR; exit }
  ' "$f")"
  if [ -n "$bline" ] && [ "$bline" -lt "$gline" ]; then
    bad "$n acts (line $bline) before help_guard (line $gline)"
  else
    ok "$n guards first"
  fi
done

phase "STATIC: no second copy of a dependency's library"
for forbidden in lib.sh integration-lib.sh _manifest.py; do
  if [ -e "$HERE/$forbidden" ]; then
    bad "$forbidden exists here — it belongs to a dependency; one definition, one home"
  else
    ok "no local $forbidden"
  fi
done

phase "STATIC: the dependency is resolved by store path, never relatively"
if grep -qE '\.\./\.\./(git-integration-repo|skills/)' "$HERE/plugin-repo-lib.sh"; then
  bad "plugin-repo-lib.sh has a relative rung — where this file sits is evidence about the checkout, not about which copy should run"
else
  ok "no relative rung"
fi
grep -q 'GIT_INTEGRATION_REPO_SCRIPTS' "$HERE/plugin-repo-lib.sh" \
  && ok "an explicit pin can override the installed copy" \
  || bad "plugin-repo-lib.sh honours no \$GIT_INTEGRATION_REPO_SCRIPTS pin"

phase "STATIC: this skill obeys its own rule 2 (contained-skill store paths)"
if grep -q 'plugins/\*/skills/' "$HERE/plugin-repo-lib.sh"; then
  ok "unit_dir searches plugins/*/skills/<unit>"
else
  bad "unit_dir has no plugins/*/skills rung — this skill would break the day its own dependency is bundled"
fi

phase "STATIC: assets the scaffolders read"
for a in plugin.json.scaffold skill-manager-plugin.toml.scaffold PLUGIN-REPO.md.scaffold gitignore.plugin-repo.scaffold; do
  [ -f "$ROOT/assets/$a" ] && ok "assets/$a" || bad "assets/$a is missing"
done

# ------------------------------------------------------------------ LIVE phase
DEP=""
if [ -n "${GIT_INTEGRATION_REPO_SCRIPTS:-}" ] && [ -f "${GIT_INTEGRATION_REPO_SCRIPTS}/integration-lib.sh" ]; then
  DEP="$GIT_INTEGRATION_REPO_SCRIPTS"
else
  H="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"
  for c in "$H/skills/git-integration-repo/scripts" "$H"/plugins/*/skills/git-integration-repo/scripts; do
    [ -f "$c/integration-lib.sh" ] && { DEP="$c"; break; }
  done
fi

if [ -z "$DEP" ]; then
  phase "LIVE: SKIPPED"
  printf '  git-integration-repo is not installed, so the end-to-end phase cannot run.\n' >&2
  printf '  It is a contained skill of the tla-spec-dev plugin, so install the BUNDLE:\n' >&2
  printf '    skill-manager install github:haydenrear/tla-spec-dev\n' >&2
  printf '    (or GIT_INTEGRATION_REPO_SCRIPTS=/path/to/scripts %s)\n' "$0" >&2
else
  phase "LIVE: scaffold -> add-skill -> commit -> finalize -> verify"
  PY_BIN="$(command -v python3 || command -v python)" || { bad "no python interpreter for the LIVE phase"; PY_BIN=false; }
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  export GIT_AUTHOR_NAME=selftest GIT_AUTHOR_EMAIL=selftest@example.com
  export GIT_COMMITTER_NAME=selftest GIT_COMMITTER_EMAIL=selftest@example.com
  # Neutralize the operator's global git config. Without this, a machine with
  # commit.gpgsign=true or an init.templateDir hook fails these commits and the
  # suite reports failures that are not about this skill.
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

  # An upstream "skill repo" to onboard, local so this needs no network.
  UP="$TMP/upstream/demo-skill"
  mkdir -p "$UP"
  printf -- '---\nname: demo-skill\ndescription: A demo.\n---\n\n# demo-skill\n' > "$UP/SKILL.md"
  printf '[skill]\nname = "demo-skill"\nversion = "0.1.0"\ndescription = "A demo."\n' > "$UP/skill-manager.toml"
  git -C "$UP" init -q -b main >/dev/null 2>&1
  git -C "$UP" add -A >/dev/null && git -C "$UP" commit -qm init >/dev/null

  PR="$TMP/demo-plugin-repo"
  if "$HERE/init-plugin-repo.sh" demo-plugin "$PR" >/dev/null 2>&1; then
    ok "init-plugin-repo.sh scaffolded"
  else
    bad "init-plugin-repo.sh failed"
  fi
  [ -f "$PR/.claude-plugin/plugin.json" ] && ok "plugin.json written" || bad "no plugin.json"
  [ -f "$PR/integration.toml" ]           && ok "integration.toml written" || bad "no integration.toml"
  [ -d "$PR/constituents" ] && bad "constituents/ survived — a plugin repo's constituents live at skills/" \
                            || ok "no constituents/ directory"

  ( cd "$PR" && "$HERE/add-skill.sh" demo-skill "$UP" main ) >/dev/null 2>&1 \
    && ok "add-skill.sh onboarded demo-skill" || bad "add-skill.sh failed"
  [ -f "$PR/skills/demo-skill/SKILL.md" ] && ok "skill landed at skills/demo-skill" || bad "skill is not at skills/demo-skill"
  [ -e "$PR/skills/demo-skill/.git" ] && bad ".git survived the add — the parent would track a gitlink" \
                                     || ok ".git stripped before the first commit"
  grep -q 'path = "skills/demo-skill"' "$PR/integration.toml" \
    && ok "registered with a skills/ path" || bad "integration.toml has no skills/ path for demo-skill"

  # The name-mismatch refusal, and that it leaves nothing behind.
  ( cd "$PR" && "$HERE/add-skill.sh" wrong-name "$UP" main ) >/dev/null 2>&1 \
    && bad "add-skill.sh accepted a directory name the SKILL.md disagrees with" \
    || ok "add-skill.sh refused a name mismatch"
  [ -e "$PR/skills/wrong-name" ] && bad "the refused clone was left behind at skills/wrong-name" \
                                 || ok "the refused clone was cleaned up"

  git -C "$PR" add -A >/dev/null && git -C "$PR" commit -qm "bundle demo-skill" >/dev/null
  if git -C "$PR" ls-files -s | awk '$1=="160000"{found=1} END{exit !found}'; then
    bad "a gitlink is in the parent index"
  else
    ok "parent tracks blobs, not gitlinks"
  fi

  ( cd "$PR" && "$HERE/finalize.sh" ) >/dev/null 2>&1 \
    && ok "finalize.sh restored the constituent" || bad "finalize.sh failed"

  if ( cd "$PR" && "$HERE/verify.sh" ) >/dev/null 2>&1; then
    ok "verify.sh PASSES on a freshly built plugin repo"
  else
    bad "verify.sh fails on a freshly built plugin repo"
    ( cd "$PR" && "$HERE/verify.sh" ) 2>&1 | sed 's/^/      /'
  fi

  # --- the checks verify.sh EXISTS for. Without these, a regression in any of
  #     them ships green: the happy path above passes either way. Each mutation
  #     is reverted before the next, so they stay independent.
  vfail() { ( cd "$PR" && "$HERE/verify.sh" ) >/dev/null 2>&1; }

  cp "$PR/.claude-plugin/plugin.json" "$TMP/plugin.json.bak"
  "$PY_BIN" - "$PR/.claude-plugin/plugin.json" <<'PYX'
import json, sys
p = sys.argv[1]
d = json.load(open(p)); d["version"] = "9.9.9"
json.dump(d, open(p, "w"), indent=2)
PYX
  vfail && bad "verify.sh passed with plugin.json/toml version drift" || ok "verify.sh catches version drift"
  cp "$TMP/plugin.json.bak" "$PR/.claude-plugin/plugin.json"

  printf -- '---\nname: stray\ndescription: d\n---\n' > "$PR/SKILL.md"
  vfail && bad "verify.sh passed with a SKILL.md at the plugin root" || ok "verify.sh catches a root SKILL.md"
  rm -f "$PR/SKILL.md"

  printf 'See $SKILL_MANAGER_HOME/skills/demo-skill/scripts/x.sh\n' >> "$PR/PLUGIN-REPO.md"
  # Captured, not piped into `grep -q`: under `pipefail` an early-exiting grep
  # SIGPIPEs the writer and the pipeline reports failure even on a match. That
  # is the same defect this suite checks for elsewhere, and it produced a false
  # FAIL here first.
  vout="$( ( cd "$PR" && "$HERE/verify.sh" ) 2>&1 || true )"
  case "$vout" in
    *PLUGIN-REPO.md*) ok "verify.sh scans ROOT prose for store-path resolvers" ;;
    *) bad "verify.sh missed a store-path resolver in root-level prose" ;;
  esac
  git -C "$PR" checkout -- PLUGIN-REPO.md 2>/dev/null || true

  mkdir -p "$PR/skills/demo-skill/.selftest" 2>/dev/null || true
  printf -- '---\nname: demo-skill\ndescription: d\nskill-imports:\n  - unit: demo-skill\n    path: SKILL.md\n    reason: r\n---\n' > "$PR/skills/demo-skill/SKILL.md"
  vfail && bad "verify.sh passed with a bare-name skill-import of a bundled skill" \
        || ok "verify.sh catches a bare-name skill-import"
  git -C "$PR" checkout -- skills/demo-skill/SKILL.md 2>/dev/null || true
  rmdir "$PR/skills/demo-skill/.selftest" 2>/dev/null || true

  # The three verdicts the first cut of these checks got wrong, in a sandbox
  # exercise: a two-line resolver idiom passed, the plugins/*/skills rung that
  # IS the fix was flagged, and a fenced counter-example in documentation
  # FAILED the run.
  mkdir -p "$PR/skills/demo-skill/scripts"
  printf '#!/bin/sh\nH="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"\nLIB="$H/skills/demo-skill/scripts/go.sh"\n' \
    > "$PR/skills/demo-skill/scripts/two-line.sh"
  vout="$( ( cd "$PR" && "$HERE/verify.sh" ) 2>&1 || true )"
  case "$vout" in
    *two-line.sh*) ok "verify.sh catches the TWO-LINE store-path idiom" ;;
    *) bad "verify.sh missed a two-line store-path resolver (marker and path on separate lines)" ;;
  esac
  printf '#!/bin/sh\nH="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"\nfor c in "$H/skills/demo-skill/x" "$H"/plugins/*/skills/demo-skill/x; do :; done\n' \
    > "$PR/skills/demo-skill/scripts/two-line.sh"
  vout="$( ( cd "$PR" && "$HERE/verify.sh" ) 2>&1 || true )"
  case "$vout" in
    *two-line.sh*) bad "verify.sh flagged a resolver that already carries the plugins/*/skills rung" ;;
    *) ok "verify.sh stays quiet on a resolver that is already fixed" ;;
  esac
  rm -rf "$PR/skills/demo-skill/scripts"

  mkdir -p "$PR/skills/demo-skill/references"
  printf 'Do NOT write this:\n\n```yaml\nskill-imports:\n  - unit: demo-skill\n    path: SKILL.md\n```\n' \
    > "$PR/skills/demo-skill/references/dont.md"
  # Exit code is the wrong signal here: the new file is untracked, so the
  # DELEGATED half fails on a dirty tree for reasons that have nothing to do
  # with imports. Ask the import step itself.
  vout="$( ( cd "$PR" && "$HERE/verify.sh" ) 2>&1 || true )"
  case "$vout" in
    *"import(s) name a bundled skill"*)
      bad "verify.sh flagged a fenced counter-example in documentation (frontmatter scoping is broken)" ;;
    *) ok "verify.sh does not flag a fenced counter-example in documentation" ;;
  esac
  rm -rf "$PR/skills/demo-skill/references"

  # The guard the DEPENDENCY cannot enforce here: its finalize refuses on a
  # `constituents` pathspec that a plugin repo does not have, so finalize.sh
  # re-asks against the manifest's real paths. If this ever stops refusing, an
  # uncommitted bundle becomes gitlinks.
  printf 'uncommitted\n' > "$PR/skills/demo-skill/UNCOMMITTED.md"
  ( cd "$PR" && "$HERE/finalize.sh" ) >/dev/null 2>&1 \
    && bad "finalize.sh ran with uncommitted skill files — the gitlink invariant is unguarded" \
    || ok "finalize.sh refuses while skill files are uncommitted"
  rm -f "$PR/skills/demo-skill/UNCOMMITTED.md"

  # release.sh moves both manifests together, which is its only reason to exist.
  ( cd "$PR" && "$HERE/release.sh" minor ) >/dev/null 2>&1 || bad "release.sh failed"
  jv="$(grep -o '"version"[^,}]*' "$PR/.claude-plugin/plugin.json" | head -1)"
  tv="$(grep -E '^version' "$PR/skill-manager-plugin.toml" | head -1)"
  case "$jv$tv" in
    *0.2.0*0.2.0*) ok "release.sh bumped both manifests to 0.2.0" ;;
    *) bad "release.sh left the manifests disagreeing: json=[$jv] toml=[$tv]" ;;
  esac
fi

phase "Result"
printf '  %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ] || exit 1
