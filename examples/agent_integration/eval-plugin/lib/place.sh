#!/bin/sh
# WHAT THE AGENT WAKES UP TO. The plugin's `SessionStart` hook, run with the
# workspace as its working directory, before the first turn.
#
# Why a hook and not `scaffold_script:`
# ------------------------------------
# A case may declare `scaffold_script:` and `--scaffold` prints a warning about
# running it. **It is never executed.** Measured in 2.1.261 at every placement
# -- top level, `execution:`, `setup:`, `workspace:`, `sandbox:`,
# `scaffold.script` -- and in both forms, a file name and inline bash. The
# decisive probe was an inline body of `echo ... >&2; exit 3`: the case still
# scored 1.00, so the script was not failing quietly, it was never invoked.
# The first run under that assumption handed the agent an empty repository and
# scored 0, and the agent is what caught it: *"I stopped before writing a spec,
# because there's nothing to specify. The repository is empty."*
#
# How one hook serves many cases
# ------------------------------
# Hooks belong to the PLUGIN, not to a case, so this file has to know which
# case is running. `execution.env` in case.yaml is the channel, and it is
# deliberately narrow: setting any non-`EVAL_*` key is refused with *"only
# EVAL_* keys can be set from case.yaml. Anything else must come from the
# operator's shell."* So each case sets `EVAL_CASE`, and this dispatches on it.
# Verified: a case setting `EVAL_CASE` had it visible here.
set -u

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
plugin=$(CDPATH= cd -- "$here/.." && pwd)
repo=$(CDPATH= cd -- "$plugin/../../.." && pwd)
case_name="${EVAL_CASE:-}"

fail() { echo "place: $*" >&2; exit 1; }

git_init() {
    git init -q -b main . 2>/dev/null || return 0
    git config user.email harness@tla-spec-dev.invalid
    git config user.name "eval harness"
    git add -A
    git commit -q -m "$1"
}

case "$case_name" in

  scaffold-a-program-model)
    fixture="$repo/examples/agent_integration/fixture"
    test -f "$fixture/shortlink.py" || fail "no fixture at $fixture -- refusing to hand the agent an empty repository, which would score 0 for the wrong reason"
    cp "$fixture/shortlink.py" ./shortlink.py
    cp "$fixture/test_shortlink.py" ./test_shortlink.py
    git_init "shortlink: the program, and the tests that hold it up"
    echo "place: the fixture is a link shortener with no spec"
    ;;

  catch-the-drift)
    # The OTHER example, and a different question: not "can you build a model"
    # but "can you find where a program stopped matching the one it has".
    #
    # The break is not invented here. It is mutant `store-account_store` from
    # examples/distributed_history/specs/program_model/kill_mutants.toml, which
    # that example already declares as a real reviewable behavioural fault:
    # creating an account returns 201 and writes nothing to the account store.
    # Using the project's own seeded fault rather than a fresh one keeps this
    # case honest about what it measures -- MF-020, do not fit a recogniser to
    # an answer you invented for it.
    src="$repo/examples/distributed_history"
    test -d "$src/ecommerce_backend" || fail "no distributed_history example at $src"
    mkdir -p specs
    cp -R "$src/ecommerce_backend" ./ecommerce_backend
    cp -R "$src/specs/program_model" ./specs/program_model
    cp "$src/specs/__init__.py" ./specs/__init__.py 2>/dev/null || true
    rm -rf ./specs/program_model/__pycache__ ./ecommerce_backend/__pycache__
    git_init "ecommerce backend, and the model that describes it"

    python3 - <<'PY' || fail "could not seed the mutant"
import pathlib
p = pathlib.Path("ecommerce_backend/domain.py")
find = '            self._conn.execute("insert or ignore into accounts(account_id) values (?)", (account_id,))'
replace = "            pass  # a change from an earlier commit"
text = p.read_text(encoding="utf-8")
if find not in text:
    raise SystemExit("the mutant's anchor line is not in domain.py")
p.write_text(text.replace(find, replace, 1), encoding="utf-8")
PY
    git add -A && git commit -q -m "accounts: simplify creation"
    echo "place: an ecommerce backend, its TLA+ model, and two commits"
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
echo "place: the toolchain, so the session does not have to go looking:"

cli=$(command -v tla-spec-dev 2>/dev/null || true)
if [ -n "$cli" ] && [ "$cli" = "$plugin/bin/tla-spec-dev" ]; then
    echo "  tla-spec-dev: $cli  (THE CHECKOUT under review)"
elif [ -n "$cli" ]; then
    echo "  tla-spec-dev: $cli"
    echo "    WARNING: this is not the checkout's shim. The run will grade"
    echo "    whichever copy is installed, not the branch. Re-run with"
    echo "    PATH=\"$plugin/bin:\$PATH\"."
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
for c in "$repo/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar" \
         "$HOME/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar"; do
    [ -f "$c" ] && { jar="$c"; break; }
done
echo "  tla2tools:    ${jar:-NOT FOUND}"

# The rest of what skill-manager.toml declares. A dependency that is missing is
# said out loud here rather than discovered as a confusing failure on turn 30.
for tool in python3 pytest jinja2 tlc2 git; do
    p=$(command -v "$tool" 2>/dev/null || true)
    echo "  ${tool}: ${p:-NOT ON PATH}"
done
exit 0
