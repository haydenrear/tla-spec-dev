#!/bin/sh
# The fixture the agent is pointed at, placed BEFORE the session starts.
#
# Run as the plugin's SessionStart hook, NOT via `scaffold_script:`. That key
# is accepted by the case loader and never executed -- measured in 2.1.261 at
# every placement and in both forms (see the note in case.yaml). The hook is
# the mechanism the CLI's own grader warning names: "a plugin hook still
# could" create a file the run is graded on.
#
# LOCATED FROM $0, not from an environment variable and not from the working
# directory. The first version used `${EVAL_CASE_DIR:-.}` -- a variable name I
# guessed -- and its `.` fallback resolved to the workspace, so the copy found
# nothing and the case scored 0 with an empty repository. **That reads as "the
# agent failed" when it means "the fixture was never placed"**, which is the
# false-negative shape this whole epic is about.
#
# The agent is what caught it: *"I stopped before writing a spec, because
# there's nothing to specify. The repository is empty."*
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
fixture="$here/../../../fixture"

test -f "$fixture/shortlink.py" || {
    echo "scaffold: no fixture at $fixture -- refusing to hand the agent an" \
         "empty repository, which would score 0 for the wrong reason" >&2
    exit 1
}

cp "$fixture/shortlink.py" ./shortlink.py
cp "$fixture/test_shortlink.py" ./test_shortlink.py
git init -q -b main .
git config user.email harness@tla-spec-dev.invalid
git config user.name "eval harness"
git add -A
git commit -q -m "shortlink: the program, and the tests that hold it up"
echo "scaffold: placed the fixture and made the first commit"

# THE TOOLCHAIN, NAMED RATHER THAN HUNTED.
#
# The first scored run spent 39 of its 40 turns on environment archaeology --
# `find / -maxdepth 8 -iname "tla2tools*.jar"`, a scan of
# /Library/Java/JavaVirtualMachines, and an unzip of the jar to locate the
# standard modules -- and reached the turn ceiling having written one probe
# spec about a counter mod 3. The trace-property grader then voted FAIL, which
# reads as "the model is wrong" and means "no model was ever attempted".
#
# So the hook does the lookup once, at runtime, and says what it found. Nothing
# is hardcoded: an operator on another machine gets their own paths, or gets
# told the tool is missing, which is a truthful input rather than a silent 0.
echo "scaffold: the toolchain, so the session does not have to go looking:"
cli=$(command -v tla-spec-dev 2>/dev/null || true)
echo "  tla-spec-dev: ${cli:-NOT ON PATH}"

java=$(command -v java 2>/dev/null || true)
if [ -z "$java" ]; then
    for j in /Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java \
             /usr/lib/jvm/*/bin/java; do
        [ -x "$j" ] && { java="$j"; break; }
    done
fi
echo "  java:         ${java:-NOT FOUND} ${java:+(export PATH=\"$(dirname "$java"):\$PATH\")}"

jar=""
for candidate in "$HOME/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar" \
                 "${CLAUDE_PLUGIN_ROOT:-}/tla2tools.jar"; do
    [ -f "$candidate" ] && { jar="$candidate"; break; }
done
echo "  tla2tools:    ${jar:-NOT FOUND}"
