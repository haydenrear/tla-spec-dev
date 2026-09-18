#!/bin/sh
# WHAT THE AGENT WAKES UP TO. The staged plugin's `SessionStart` hook, run with
# the workspace as its working directory, before the first turn.
#
# Why a hook and not `scaffold_script:`
# ------------------------------------
# A case may declare `scaffold_script:` and `--scaffold` promises to run it.
# **It is never executed.** Measured in 2.1.261 at every placement -- top
# level, `execution:`, `setup:`, `workspace:`, `sandbox:`, `scaffold.script` --
# and in both forms, a file name and inline bash. The decisive probe was an
# inline body of `echo ... >&2; exit 3`: the case still scored 1.00, so the
# script was not failing quietly, it was never invoked.
#
# Why this file is not loaded from the repository root
# ---------------------------------------------------
# Hooks belong to the PLUGIN, and this plugin is the repository, so a
# `hooks/hooks.json` committed at the root would run in every session of every
# user who installs tla-spec-dev. `evals/run.sh` stages it into the throwaway
# view instead. See evals/hooks/hooks.json.
#
# How one hook serves many cases
# ------------------------------
# Hooks belong to the plugin, not to a case, so this file has to know which
# case is running. `execution.env` in case.yaml is the channel, and it is
# deliberately narrow: setting any non-`EVAL_*` key is refused with *"only
# EVAL_* keys can be set from case.yaml. Anything else must come from the
# operator's shell."* So each case sets `EVAL_CASE`, and this dispatches on it.
set -u

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
plugin=$(CDPATH= cd -- "$here/../.." && pwd)
# The view IS a copy of the checkout, so the fixtures the cases draw on -- the
# examples/ trees -- are inside the plugin root. There is no `../../..` walk any
# more, and that is the difference the nesting bought: the plugin is the
# repository rather than a thin directory beside it.
repo="$plugin"
case_name="${EVAL_CASE:-}"

# EXIT 2, NOT 1. Claude Code treats exit 2 as blocking and every other non-zero
# code as advisory, so `exit 1` printed a complaint and let the session start
# anyway -- on a workspace it had just failed to set up. Where a case seeds a
# deliberate fault, that is the difference between refusing and handing the
# agent a program with nothing wrong with it, which scores well for doing
# nothing.
#
# THIS IS NOT A NEW GATE. It can only fire inside an eval run, because this
# file is only ever loaded from a staged view; nothing a user of the plugin
# does reaches it.
fail() { echo "place: $*" >&2; exit 2; }

git_init() {
    git init -q -b main . 2>/dev/null || return 0
    git config user.email harness@tla-spec-dev.invalid
    git config user.name "eval harness"
    git add -A
    git commit -q -m "$1"
}

# The shortlink fixture: a small program with no spec. Used by more than one
# case, so it is a function rather than three copies that drift apart.
place_shortlink() {
    fixture="$repo/examples/agent_integration/fixture"
    test -f "$fixture/shortlink.py" || fail "no fixture at $fixture -- refusing to hand the agent an empty repository, which would score 0 for the wrong reason"
    cp "$fixture/shortlink.py" ./shortlink.py
    cp "$fixture/test_shortlink.py" ./test_shortlink.py
}

# The ecommerce backend and the model that describes it, unfaulted.
place_ecommerce() {
    src="$repo/examples/distributed_history"
    test -d "$src/ecommerce_backend" || fail "no distributed_history example at $src"
    mkdir -p specs
    cp -R "$src/ecommerce_backend" ./ecommerce_backend
    cp -R "$src/specs/program_model" ./specs/program_model
    cp "$src/specs/__init__.py" ./specs/__init__.py 2>/dev/null || true
    rm -rf ./specs/program_model/__pycache__ ./ecommerce_backend/__pycache__
}

case "$case_name" in

  scaffold-a-program-model)
    place_shortlink
    git_init "shortlink: the program, and the tests that hold it up"
    echo "place: the fixture is a link shortener with no spec"
    ;;

  catch-the-drift)
    # The break is not invented here. It is mutant `store-account_store` from
    # examples/distributed_history/specs/program_model/kill_mutants.toml, which
    # that example already declares as a real reviewable behavioural fault:
    # creating an account returns 201 and writes nothing to the account store.
    # Using the project's own seeded fault rather than a fresh one keeps this
    # case honest about what it measures -- MF-020, do not fit a recogniser to
    # an answer you invented for it.
    place_ecommerce
    git_init "ecommerce backend, and the model that describes it"

    # The seed. `find` must match EXACTLY ONCE: a formatter that reflows the
    # line -- double quotes to single, say -- makes this refuse rather than
    # hand the agent a program with nothing wrong with it.
    python3 - <<'SEED' || fail "could not seed the mutant; the case would run on an UNFAULTED program and pass for free"
import pathlib
p = pathlib.Path("ecommerce_backend/domain.py")
find = '            self._conn.execute("insert or ignore into accounts(account_id) values (?)", (account_id,))'
replace = "            pass  # a change from an earlier commit"
text = p.read_text(encoding="utf-8")
n = text.count(find)
if n != 1:
    raise SystemExit(f"the anchor line appears {n} times in domain.py, expected exactly 1")
p.write_text(text.replace(find, replace, 1), encoding="utf-8")
SEED
    git add -A && git commit -q -m "accounts: simplify creation"

    # AND THE SEED IS CONFIRMED BY BEHAVIOUR, not by the edit returning 0.
    # A successful string replacement is not a broken program.
    python3 - <<'CHECK' || fail "the seeded fault did not change the program's behaviour; refusing to run a case that would pass for free"
import pathlib, sys
sys.path.insert(0, str(pathlib.Path.cwd()))
from ecommerce_backend.domain import EcommerceStore
b = EcommerceStore()
b.create_account("acct-seed-check")
if "acct-seed-check" in repr(b.snapshot()):
    raise SystemExit("create_account still persists: the fault was not seeded")
CHECK
    echo "place: an ecommerce backend, its TLA+ model, and two commits"
    ;;

  start-from-the-spec-not-the-source)
    # discovery's question. The same repository as catch-the-drift and
    # deliberately NOT faulted: nothing here is broken, and the only thing
    # being measured is whether the account of the program comes from the
    # model that is sitting there or from a re-derivation of it by grep.
    place_ecommerce
    git_init "ecommerce backend, its TLA+ model, and its test graph"
    echo "place: an ecommerce backend with a program model already in specs/program_model"
    ;;

  a-work-order-not-a-wish)
    place_shortlink
    cat > README.md <<'EOF'
# shortlink

A link shortener. `reserve(slug, owner)` claims a slug for an owner,
`release(slug, owner)` gives it up, and `resolve(slug)` returns the target.

Known problem, reported twice this month: a slug released by one owner can be
re-reserved by a different owner while the first owner still believes it holds
it. Nobody has written down what the correct behaviour is.
EOF
    git_init "shortlink, and a problem report nobody has turned into work yet"
    echo "place: a small program and an unwritten problem"
    ;;

  use-the-front-door)
    place_shortlink
    # An ordinary work order: no epic marker anywhere in it. What the case
    # measures is the FIRST move, which this skill is emphatic about and which
    # four measured eval runs got wrong in four different ways.
    cat > ISSUE.md <<'EOF'
# SL-14: resolve() should not answer for a released slug

## Summary
`resolve()` returns the old target for a slug whose owner has released it,
until something else re-reserves it. It should report the slug as unclaimed.

## References
- `shortlink.py` -- `reserve`, `release`, `resolve`
- `test_shortlink.py` -- the existing behavioural tests

## Regression checklist
- [ ] `pytest test_shortlink.py` stays green
- [ ] a new test covers release-then-resolve
EOF
    git_init "shortlink, and an issue somebody has to pick up"
    echo "place: a repository and one ordinary (non-epic) work order in ISSUE.md"
    ;;

  epic-mode-is-not-main)
    place_shortlink
    # The same shape as the assignment blocks this repository's own epics use,
    # trimmed to what the decision needs. The marker is the whole point: it
    # selects epic mode BEFORE ordinary provisioning, and an agent that misses
    # it branches from and targets the default branch.
    cat > ISSUE.md <<'EOF'
# SL-21: reserve() should refuse a slug that is already claimed

Epic: #77 (`shortlink-hardening`). Stable ticket ID `SL-21`.

## Summary
`reserve()` overwrites an existing claim. It should refuse one.

<!-- git-epic-workflow:assignment:start -->
## Epic execution — REQUIRED

```yaml
version: 1
epic:
  id: shortlink-hardening
  workflow: shortlink-hardening
  branch: epic/shortlink-hardening
  base_sha: 0000000000000000000000000000000000000000
  default_branch: main
ticket:
  spec_id: SL-21
  feature_branch: feature/77-refuse-claimed-slug
  worktree: ../wt-77-refuse-claimed-slug
  pr_base: epic/shortlink-hardening
  wave: 1
  role: implementation
review:
  mode: external
  ticket_agent_stops_after: pr_open
  merged_by: epic-owner
```
<!-- git-epic-workflow:assignment:end -->

## References
- `shortlink.py` -- `reserve`
EOF
    git_init "shortlink, and an epic-assigned ticket in ISSUE.md"
    echo "place: a repository and an EPIC-ASSIGNED work order in ISSUE.md"
    ;;

  compose-a-behavioural-graph)
    place_shortlink
    git_init "shortlink: the program, and the unit tests that hold it up"
    echo "place: a link shortener with unit tests and no behavioural validation"
    ;;

  "")
    fail "EVAL_CASE is unset. Every case must set it under execution.env, or this hook cannot tell which fixture to place"
    ;;

  *)
    fail "unknown EVAL_CASE '$case_name'"
    ;;
esac

# ------------------------------------------------------------ the toolchain
#
# NAMED, NOT HUNTED. The first scored run of the first case spent 39 of its 40
# turns on `find / -maxdepth 8 -iname "tla2tools*.jar"`, a scan of
# /Library/Java/JavaVirtualMachines and an `unzip` of the jar, hit the turn
# ceiling, and left behind a scratch module about a counter mod 3. The
# trace-property grader then voted FAIL, which reads as *the model is wrong*
# and meant *no model was ever attempted*.
#
# Nothing below is hardcoded. Another machine gets its own paths, or gets told
# the tool is missing -- a truthful input rather than a silent 0.
#
# A CASE THAT GRANTS NO BASH CANNOT USE ANY OF IT, and that is fine: the lines
# still land in the trace, where they answer "was the environment able to do
# this at all" for whoever reads the score.
echo "place: the toolchain, so the session does not have to go looking:"

cli=$(command -v tla-spec-dev 2>/dev/null || true)
if [ -n "$cli" ] && [ "$cli" = "$repo/evals/bin/tla-spec-dev" ]; then
    echo "  tla-spec-dev: $cli  (THE VIEW's shim)"
elif [ -n "$cli" ] && [ -n "${SI10_CHECKOUT:-}" ] && [ "$cli" = "$SI10_CHECKOUT/evals/bin/tla-spec-dev" ]; then
    echo "  tla-spec-dev: $cli  (THE CHECKOUT under review)"
elif [ -n "$cli" ] && [ "${cli##*/evals/bin/}" != "$cli" ]; then
    echo "  tla-spec-dev: $cli  (a checkout's evals/bin shim)"
elif [ -n "$cli" ]; then
    echo "  tla-spec-dev: $cli"
    echo "    WARNING: this is not a checkout's shim. The run will grade"
    echo "    whichever copy is installed, not the branch. Re-run through"
    echo "    evals/run.sh, which prepends the checkout's evals/bin."
else
    echo "  tla-spec-dev: NOT ON PATH"
fi

java=$(command -v java 2>/dev/null || true)
if [ -z "$java" ]; then
    for j in /Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java \
             /usr/lib/jvm/*/bin/java; do
        [ -x "$j" ] && { java="$j"; break; }
    done
fi
echo "  java:         ${java:-NOT FOUND} ${java:+(export PATH=\"$(dirname "$java" 2>/dev/null):\$PATH\")}"

jar=""
for c in "${TLA2TOOLS_JAR:-}" \
         "$repo/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar" \
         "$HOME/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar"; do
    [ -n "$c" ] && [ -f "$c" ] && { jar="$c"; break; }
done
echo "  tla2tools:    ${jar:-NOT FOUND}"

# The rest of what skill-manager.toml declares. A dependency that is missing is
# said out loud here rather than discovered as a confusing failure on turn 30.
for tool in python3 pytest jinja2 tlc2 git gradle; do
    p=$(command -v "$tool" 2>/dev/null || true)
    echo "  ${tool}: ${p:-NOT ON PATH}"
done
exit 0
