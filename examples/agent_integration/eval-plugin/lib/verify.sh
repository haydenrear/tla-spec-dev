#!/bin/sh
# THE GRADER THAT CAN LOOK. The plugin's `Stop` hook, run after the agent
# finishes and before the case is scored.
#
# Why this file exists
# --------------------
# A `claude plugin eval` case can observe exactly three things: paths in the
# workspace (`file_exists`), tool NAMES and their order (`tool_used`,
# `tool_order`), and the agent's final response text (`regex`, `llm`,
# `baseline`). It cannot observe file CONTENTS, tool inputs, tool outputs, or
# exit codes.
#
# That set cannot grade a toolchain. The first passing run of the first case
# scored 1.00 while `tla-spec-dev scaffold project` failed with exit 1 on all
# three attempts, and the `spec_manifest.yaml` its artefact grader accepted as
# proof the pipeline had run was typed by the agent's own `Write` tool.
#
# A hook is the way out: the sandbox that stops the agent does not apply here.
# The Bash TOOL runs under a profile denying filesystem writes to every
# subprocess it spawns; hooks are outside it, so SANY and TLC can run.
#
# THE ORDERING RULE, AND WHY IT IS NOT WHERE YOU WOULD FIRST PUT IT
# -----------------------------------------------------------------
# The first version cleared `.eval/` at the top and wrote verdicts as it went.
# A blind review broke it in one move: the `catch-the-drift` check IMPORTS
# `ecommerce_backend/domain.py`, which is the file the agent was told to edit.
# Importing it executes agent-authored module-level code -- here, outside the
# sandbox, with `.eval/` already created and writable. Five appended lines
# wrote all four verdicts at import time, and a workspace where nothing was
# repaired and the model had been illegally edited scored 4 of 5, while this
# file's own log recorded both failures.
#
# So verdicts are collected OUTSIDE the workspace, and `.eval/` is created and
# filled only after every line of agent-authored code has already run:
#
#   1. collect into $WORK, a temp dir the workspace cannot name;
#   2. run everything, including the imports;
#   3. THEN `rm -rf .eval`, recreate it, and copy the collected verdicts in.
#
# Step 3's clear is what defeats a forgery the agent wrote during its session
# or its own code wrote during step 2. It did NOT defend against a process
# spawned to write a verdict after this script exits -- see `run_confined`,
# which does, by denying agent-authored code every filesystem write.
#
# Two rules survive from the first version:
#   * NOTHING TRUSTS THE RESPONSE. A verdict is written only after a real
#     program -- SANY, TLC, a behavioural check, a diff -- succeeds.
#   * `exit 0`, ALWAYS. A Stop hook that fails non-zero can push the session
#     onward, and a verifier that changes the run it measures is not a verifier.
set -u

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
plugin=$(CDPATH= cd -- "$here/.." && pwd)
repo=$(CDPATH= cd -- "$plugin/../../.." && pwd)
case_name="${EVAL_CASE:-}"

VD=".eval"
WORK=$(mktemp -d 2>/dev/null) || exit 0
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/v" 2>/dev/null || exit 0
log="$WORK/verify.log"
: > "$log"
say() { echo "$@" >> "$log" 2>/dev/null; }
verdict() { echo "$2" > "$WORK/v/$1" 2>/dev/null; }

# RUN AGENT-AUTHORED CODE WITH NO WRITE ANYWHERE, AND WRITE ITS VERDICT HERE.
#
# A Stop hook is outside the sandbox that constrains the agent's Bash tool, so
# anything the hook executes runs with the hook's privileges. That was a real
# hole, not a theoretical one: five lines appended to `domain.py` spawning
# `Popen([...], start_new_session=True)` with a four-second sleep produced a
# `.eval/behaviour` AFTER this script exited and before the graders read it --
# on a workspace where the program was never repaired. The hook had refused
# correctly and the refusal was overwritten by the thing it refused.
#
# A process-group kill does not close that; the payload starts a new session to
# escape exactly that. Denying writes does, and it holds for descendants, which
# inherit the profile. The check therefore CANNOT record its own verdict and
# signals through its exit status instead, which is the separation that matters:
# untrusted code decides nothing about what gets written.
#
# Where `sandbox-exec` is unavailable the check still runs, but the run says so
# in a verdict of its own rather than quietly offering a weaker guarantee.
run_confined() {
    name=$1; script=$2; shift 2
    if [ -n "$SANDBOX" ]; then
        PYTHONDONTWRITEBYTECODE=1 "$SANDBOX" -f "$here/checks/nowrite.sb" \
            python3 "$script" "$@" >>"$log" 2>&1
    else
        PYTHONDONTWRITEBYTECODE=1 python3 "$script" "$@" >>"$log" 2>&1
    fi
}

SANDBOX=$(command -v sandbox-exec 2>/dev/null || true)
if [ -z "$SANDBOX" ]; then
    say "sandbox-exec not available: agent-authored code runs unconfined"
fi

say "verify.sh case=$case_name at $(date)"
say "cwd=$(pwd)"

# ---------------------------------------------------------------- toolchain
java=$(command -v java 2>/dev/null || true)
if [ -z "$java" ]; then
    for j in /Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java \
             /usr/lib/jvm/*/bin/java; do
        [ -x "$j" ] && { java="$j"; break; }
    done
fi

# The jar, resolved the way the project's own wrapper resolves it. A search
# rooted at `$HOME/.skill-manager` finds nothing here: inside the hook `$HOME`
# is the constructed eval home, which deliberately does not symlink it. That
# cost two cases their artefact verdicts once already.
jar="${TLA2TOOLS_JAR:-}"
if [ -z "$jar" ]; then
    tlc=$(command -v tlc2 2>/dev/null || true)
    if [ -n "$tlc" ]; then
        tlcdir=$(CDPATH= cd -- "$(dirname -- "$tlc")" && pwd)
        [ -f "$tlcdir/.spec-double-compiler/tla2tools.jar" ] &&
            jar="$tlcdir/.spec-double-compiler/tla2tools.jar"
    fi
fi
if [ -z "$jar" ]; then
    for c in "$repo/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar" \
             "$HOME/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar"; do
        [ -f "$c" ] && { jar="$c"; break; }
    done
fi
say "java=${java:-MISSING} jar=${jar:-MISSING}"

# WHAT THIS MARKER DOES AND DOES NOT DO.
#
# It records that the tools resolved, so a human reading `.eval/` can tell "the
# model does not parse" from "SANY never ran". IT DOES NOT CHANGE THE SCORE,
# and no grader may read it -- a forged workspace earns it too.
#
# `file_exists` has only pass and fail. There is no UNDECIDED. So when the
# toolchain is missing, `parses` and `checks` are absent and score FAIL on a
# model that may be perfect. That is SS-02 and this script cannot fix it from
# the inside; what it can do is leave the reason where the person reading a 0
# will find it, and refuse to pretend otherwise in its own documentation.
if [ -n "$java" ] && [ -n "$jar" ]; then
    verdict toolchain "java=$java jar=$jar"
else
    verdict UNDECIDED-toolchain "SANY and TLC could not run; parses/checks below are UNDECIDED, not failed"
    say "TOOLCHAIN INCOMPLETE -- every SANY/TLC verdict is UNDECIDED, not failed"
fi

if [ -z "$SANDBOX" ]; then
    verdict UNDECIDED-unconfined "sandbox-exec was unavailable, so agent-authored code ran unconfined and could have written any verdict below"
fi

MODEL="specs/program_model"

# ------------------------------------------------- V1: every module parses
sany() {
    [ -n "$java" ] && [ -n "$jar" ] || { say "V1 skipped: no java or jar"; return 1; }
    [ -d "$MODEL" ] || { say "V1: no $MODEL"; return 1; }
    any=0
    ok=1
    # Globbed rather than word-split from `ls`. The previous `for m in $mods`
    # split `My Mod.tla` into two names, failed both, and withheld the verdict
    # from a model that parses.
    for m in "$MODEL"/*.tla; do
        [ -f "$m" ] || continue
        any=1
        base=$(basename "$m")
        # Run FROM the model directory on a bare filename: SANY resolves
        # `EXTENDS Internal` against the working directory, and invoking it
        # from the workspace root reported `Cannot find source file for module
        # Internal` on a module that parses perfectly.
        if (cd "$MODEL" && "$java" -cp "$jar" tla2sany.SANY "$base") >>"$log" 2>&1; then
            say "SANY ok: $base"
        else
            say "SANY FAILED: $base"
            ok=0
        fi
    done
    [ "$any" = 1 ] || { say "V1: no .tla modules"; return 1; }
    [ "$ok" = 1 ]
}

# ------------------------------------------- V2: TLC explores a finite model
#
# A CONFIG THAT ASSERTS NOTHING IS NOT A CHECK. The first version accepted any
# config whose run printed "Model checking completed. No error has been found",
# and a six-line stub with a `.cfg` naming only `SPECIFICATION Spec` prints
# exactly that -- TLC checked nothing and reported success, and the grader that
# called itself "the one a confident report cannot move" went green on a model
# of nothing. So the config has to declare an INVARIANT or a PROPERTY first.
tlc() {
    [ -n "$java" ] && [ -n "$jar" ] || { say "V2 skipped: no java or jar"; return 1; }
    found=0
    for cfg in "$MODEL"/*.cfg; do
        [ -f "$cfg" ] || continue
        base=$(basename "$cfg" .cfg)
        [ -f "$MODEL/$base.tla" ] || { say "TLC: $base.cfg has no $base.tla"; continue; }
        if ! grep -qiE '^[[:space:]]*(INVARIANT|INVARIANTS|PROPERTY|PROPERTIES)\b' "$cfg"; then
            say "TLC: $base.cfg declares no INVARIANT and no PROPERTY -- a run over it asserts nothing"
            continue
        fi
        say "TLC on $base"
        out=$(cd "$MODEL" && "$java" -XX:+UseParallelGC -cp "$jar" tlc2.TLC \
                 -config "$base.cfg" -workers 1 -cleanup "$base.tla" 2>&1)
        echo "$out" >> "$log" 2>/dev/null
        if echo "$out" | grep -q "Model checking completed. No error has been found"; then
            states=$(echo "$out" | grep -oE '[0-9]+ distinct states found' | head -1)
            say "TLC clean: $base (${states:-state count not reported})"
            echo "$base ${states:-}" >> "$WORK/v/checks"
            found=1
        else
            say "TLC did not complete cleanly: $base"
        fi
    done
    [ "$found" = 1 ]
}

case "$case_name" in

  scaffold-a-program-model)
    sany && verdict parses "every module parses"
    tlc || rm -f "$WORK/v/checks"

    if run_confined manifest "$here/checks/manifest.py" "$MODEL/spec_manifest.yaml"; then
        verdict manifest "a manifest, not a token"
    fi
    ;;

  catch-the-drift)
    sany && verdict parses "every module parses"

    # V2': the program does what its model says again.
    #
    # THIS EXECUTES AGENT-AUTHORED CODE -- `domain.py` is the file the agent was
    # told to edit -- so it runs confined and writes nothing. The verdict below
    # is written by this script, from the exit status.
    if run_confined behaviour "$here/checks/behaviour.py"; then
        verdict behaviour "create_account persists"
    fi

    # V3': the repair is in the PROGRAM, not in the model. The cheapest way to
    # make a program agree with its model is to change the model.
    shipped="$repo/examples/distributed_history/specs/program_model"
    if [ ! -d "$MODEL" ]; then
        say "model-intact: no $MODEL in the workspace"
    elif [ ! -d "$shipped" ]; then
        say "model-intact UNDECIDED: no reference tree at $shipped to compare against"
        verdict UNDECIDED-reference "the shipped model tree is missing; model-intact could not be decided"
    elif diff -r -x '__pycache__' -x '*.pyc' "$shipped" "$MODEL" >>"$log" 2>&1; then
        verdict model-intact "model untouched"
        say "model matches the shipped tree"
    else
        say "the model tree was modified -- the fix belongs in the program"
    fi
    ;;

  "")
    say "EVAL_CASE unset; nothing verified"
    verdict UNDECIDED-nocase "EVAL_CASE was not set, so no case arm ran and nothing was checked"
    ;;
  *)
    say "unknown EVAL_CASE '$case_name'; nothing verified"
    verdict UNDECIDED-nocase "unknown EVAL_CASE '$case_name'"
    ;;
esac

# ---------------------------------------------------------------- publish
# ONLY NOW. Every line of agent-authored code has already run; anything it
# wrote under `.eval/` dies here.
say "verdicts: $(ls "$WORK/v" 2>/dev/null | tr '\n' ' ')"
rm -rf "$VD"
mkdir -p "$VD" 2>/dev/null || exit 0
for v in "$WORK/v/"*; do
    [ -f "$v" ] && cp "$v" "$VD/$(basename "$v")" 2>/dev/null
done
cp "$log" "$VD/verify.log" 2>/dev/null
exit 0
