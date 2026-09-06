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
# exit codes. All three limits were measured, not assumed.
#
# That set cannot grade a toolchain. The first passing run of the first case
# scored 1.00 while `tla-spec-dev scaffold project` failed with exit 1 on all
# three attempts, and the `spec_manifest.yaml` its artefact grader accepted as
# proof the pipeline had run was typed by the agent's own `Write` tool. A
# separate probe scored that same grader green on a manifest whose entire
# contents were `placeholder: true`.
#
# A hook is the way out, for a reason worth stating: **the sandbox that stops
# the agent does not apply here.** The Bash TOOL runs under a profile denying
# filesystem writes to every subprocess it spawns, which is why TLC aborts
# creating its metadir and why a CLI that writes files cannot run. Hooks are
# outside it. Measured: a Stop hook's `python3 -c "open(...,'w')"` and its
# `mkdir` both succeed in the same workspace where the Bash tool is refused.
#
# Three rules make the verdicts sound:
#
#   1. EVERY VERDICT PATH IS DELETED FIRST. The agent has Write and can create
#      any filename it can guess. Measured: an agent told to write
#      `VERIFIED.txt` itself scored FAIL once the hook erased it before looking.
#   2. NOTHING HERE TRUSTS THE RESPONSE. A verdict is written only after a real
#      program -- SANY, TLC, a Python behavioural check, a diff -- succeeds.
#   3. `exit 0`, ALWAYS. A Stop hook that fails non-zero can push the session
#      onward, and a verifier that changes the run it measures is not a
#      verifier.
set -u

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
plugin=$(CDPATH= cd -- "$here/.." && pwd)
repo=$(CDPATH= cd -- "$plugin/../../.." && pwd)
case_name="${EVAL_CASE:-}"

VD=".eval"
rm -rf "$VD"                       # RULE 1, and it must stay above every write
mkdir -p "$VD" 2>/dev/null || exit 0
log="$VD/verify.log"
: > "$log"
say() { echo "$@" >> "$log" 2>/dev/null; }
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
jar=""
for c in "$repo/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar" \
         "$HOME/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar"; do
    [ -f "$c" ] && { jar="$c"; break; }
done
say "java=${java:-MISSING} jar=${jar:-MISSING}"

MODEL="specs/program_model"

# ------------------------------------------------- V1: every module parses
# SANY, over every module the workspace holds. A `.tla` that does not parse is
# not a model, whatever the report says about it.
sany() {
    [ -n "$java" ] && [ -n "$jar" ] || { say "V1 skipped: no java or jar"; return 1; }
    [ -d "$MODEL" ] || { say "V1: no $MODEL"; return 1; }
    mods=$(cd "$MODEL" && ls *.tla 2>/dev/null)
    [ -n "$mods" ] || { say "V1: no .tla modules"; return 1; }
    ok=1
    for m in $mods; do
        # Run FROM the model directory on a bare filename. SANY resolves
        # `EXTENDS Internal` against the working directory, so invoking it from
        # the workspace root reported `Cannot find source file for module
        # Internal` on a module that parses perfectly -- a verifier failing the
        # artefact for the verifier's own mistake, which is the false negative
        # this whole apparatus exists to remove.
        if (cd "$MODEL" && "$java" -cp "$jar" tla2sany.SANY "$m") >>"$log" 2>&1; then
            say "SANY ok: $m"
        else
            say "SANY FAILED: $m"
            ok=0
        fi
    done
    [ "$ok" = 1 ]
}

# ------------------------------------------- V2: TLC explores a finite model
# The check the sandbox denies the agent.
tlc() {
    [ -n "$java" ] && [ -n "$jar" ] || { say "V2 skipped: no java or jar"; return 1; }
    found=0
    for cfg in "$MODEL"/*.cfg; do
        [ -f "$cfg" ] || continue
        base=$(basename "$cfg" .cfg)
        [ -f "$MODEL/$base.tla" ] || continue
        say "TLC on $base"
        out=$(cd "$MODEL" && "$java" -XX:+UseParallelGC -cp "$jar" tlc2.TLC \
                 -config "$base.cfg" -workers 1 -cleanup "$base.tla" 2>&1)
        echo "$out" >> "$log" 2>/dev/null
        if echo "$out" | grep -q "Model checking completed. No error has been found"; then
            say "TLC clean: $base"
            echo "$base" >> "$VD/checks"
            found=1
        else
            say "TLC did not complete cleanly: $base"
        fi
    done
    [ "$found" = 1 ]
}

case "$case_name" in

  scaffold-a-program-model)
    sany && echo "every module parses" > "$VD/parses"
    tlc || rm -f "$VD/checks"

    # V3: the manifest is a manifest, not a token. `placeholder: true` passed
    # the grader this replaces.
    python3 - "$MODEL/spec_manifest.yaml" "$VD/manifest" >>"$log" 2>&1 <<'PY'
import sys, pathlib
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
if not src.is_file():
    print("no manifest"); raise SystemExit(0)
try:
    import yaml
    doc = yaml.safe_load(src.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"manifest did not parse: {exc}"); raise SystemExit(0)
if not isinstance(doc, dict):
    print("manifest is not a mapping"); raise SystemExit(0)
keys = set(doc)
wanted = {"module", "modules", "ports", "invariants", "finite_model", "codegen"}
hit = sorted(keys & wanted)
if len(keys) < 3 or not hit:
    print(f"manifest is a token, not a manifest: keys={sorted(keys)}")
    raise SystemExit(0)
out.write_text("keys: " + ",".join(hit) + "\n", encoding="utf-8")
print(f"manifest ok: {hit}")
PY
    ;;

  catch-the-drift)
    sany && echo "every module parses" > "$VD/parses"

    # V2': the program does what its model says again.
    #
    # The seeded fault is mutant `store-account_store` -- create_account
    # returns 201 and writes nothing. This exercises the real object and looks
    # at the real store, so the only way to earn the verdict is to make the
    # program behave. A confident paragraph moves nothing here.
    python3 - "$VD/behaviour" >>"$log" 2>&1 <<'PY'
import pathlib, sys
out = pathlib.Path(sys.argv[1])
if not pathlib.Path("ecommerce_backend/domain.py").is_file():
    print("no ecommerce_backend/domain.py"); raise SystemExit(0)
# A PLAIN IMPORT, not spec_from_file_location. The first version loaded the
# file by path without registering it in sys.modules, and `@dataclass` looks up
# `sys.modules[cls.__module__].__dict__` -- so exec_module died with
# `'NoneType' object has no attribute '__dict__'` and the verdict was withheld
# for the VERIFIER's mistake, on a workspace that may have been repaired. That
# is the false negative this apparatus exists to remove, produced by the
# apparatus. Caught by running the positive control before shipping it.
sys.path.insert(0, str(pathlib.Path.cwd()))
try:
    from ecommerce_backend.domain import EcommerceStore as cls
except Exception as exc:
    print(f"domain.py does not import: {exc!r}"); raise SystemExit(0)
try:
    backend = cls()
    backend.create_account("acct-eval")
    snap = backend.snapshot()
except Exception as exc:
    print(f"exercising the backend raised: {exc}"); raise SystemExit(0)
blob = repr(snap)
if "acct-eval" not in blob:
    print("create_account did not persist: the account is absent from snapshot()")
    raise SystemExit(0)
out.write_text("create_account persists\n", encoding="utf-8")
print("behaviour ok: the account survives into snapshot()")
PY

    # V3': the repair is in the PROGRAM, not in the model.
    #
    # Deleting the invariant that catches a fault also makes the fault stop
    # being caught. This compares the model tree byte-for-byte against the one
    # the example ships, so a model edited into agreement earns nothing.
    if [ -d "$MODEL" ] && [ -d "$repo/examples/distributed_history/specs/program_model" ]; then
        if diff -r -x '__pycache__' -x '*.pyc' \
             "$repo/examples/distributed_history/specs/program_model" "$MODEL" >>"$log" 2>&1; then
            echo "model untouched" > "$VD/model-intact"
            say "model matches the shipped tree"
        else
            say "the model tree was modified -- the fix belongs in the program"
        fi
    fi
    ;;

  "")
    say "EVAL_CASE unset; nothing verified"
    ;;
  *)
    say "unknown EVAL_CASE '$case_name'; nothing verified"
    ;;
esac

say "verdicts: $(ls "$VD" 2>/dev/null | tr '\n' ' ')"
exit 0
