#!/usr/bin/env bash
# THE ONE COMMAND.
#
#   evals/run.sh                       every case
#   evals/run.sh --case catch-the-drift        one of them
#   evals/run.sh --case 'git-*' --runs 2       any claude-plugin-eval flag
#
# What it does, and why each part is here rather than in a README somebody has
# to follow by hand. Every one of the five was learned from a run that scored 0
# for a reason that was not the agent's.
#
# 1. STAGES A VIEW OF THIS CHECKOUT THAT EXCLUDES THE APPEND-ONLY RECORD.
#    `claude plugin eval` refuses a plugin directory over 20,000 entries:
#
#      a plugin directory holds more than 20000 entries to check for eval
#      directories -- point the case at a smaller plugin directory
#
#    Measured on 2.1.275 at 994f650c: this checkout is 70,741 entries, and the
#    refusal fires. It is not close -- `specs/.history` is 19,154 of it and the
#    gitignored `.skill-manager` home another 41,169. There is no ignore file,
#    no flag and no manifest key that excludes anything from that count (the
#    traversal skips `.git`, `.svn`, `.hg` and nothing else), so the only way to
#    hand the CLI a small plugin directory is to hand it a different directory.
#    This stages one: a copy of the working tree with the record and the home
#    left out, 6,264 entries, made fresh on every run so it cannot drift from
#    the checkout it was copied from.
#
#    The previous answer was a committed symlink shim carrying one skill's
#    surface. It could not grow to the nested skills -- it named
#    `skills/spec-double-2` explicitly, and there are six -- and a committed
#    directory that has to be edited whenever a skill is added goes stale
#    silently. A staged copy carries whatever the checkout carries.
#
# 2. STAGES THE HOOKS. `evals/hooks/hooks.json` is copied to
#    `<view>/hooks/hooks.json`. It is NOT committed at the repository root,
#    because the repository IS the plugin: a root `hooks/hooks.json` would run
#    a SessionStart script in every session of every user who installs
#    tla-spec-dev, and a fixture hook's blocking exit 2 would be able to refuse
#    somebody's ordinary session. Staging keeps the shipped plugin hookless.
#
# 3. PUTS THE CHECKOUT'S CLI FIRST ON PATH. Without `evals/bin` first, the run
#    grades whichever `tla-spec-dev` the operator has installed. Measured: a
#    run's `which -a tla-spec-dev` returned the installed wrapper three times
#    and nothing else. A plugin `bin/` directory does not reach the eval's
#    PATH, and `execution.env` refuses `PATH` ("only EVAL_* keys can be set
#    from case.yaml"), so the operator's shell is the only channel -- which is
#    what this script is.
#
# 4. DERIVES `--allow-tools` FROM THE CASES IT IS ABOUT TO RUN. A tool named in
#    a case's `allowed_tools:` is still refused unless the operator ALSO grants
#    it. `--allow-tools Bash` against a case declaring `[Bash, Write, Edit]`
#    produced `not granted (missing --allow-tools grant, or a malformed
#    entry): Write, Edit` and a score of 0 -- an agent that could read the
#    program and could not write one line of the spec, reported as a failure to
#    model. A README cannot keep that in step; this reads the cases.
#
# 5. HARVESTS THE RESULTS BACK. The CLI writes its report next to the plugin,
#    which is the throwaway view, so the report would vanish with it.
#
# 6. MATERIALISES THE PINNED TOOLCHAIN, ASKS ABOUT IT, AND RECORDS IT. (SI-14.)
#    Before this, every run resolved its toolchain from the OPERATOR'S LIVE
#    HOME: the project home's `skt` said `gitRef main, gitHash 286a3694,
#    installed 2026-09-14`, and by 2026-09-19 `main` was `0f380781`. Zero runs
#    recorded what they ran against, so no two runs a week apart were known to
#    be comparable and a score that moved could not be attributed to the change
#    that was supposed to move it.
#
#    `claude plugin eval` cannot help: its `plugins:` field takes relative
#    filesystem PATHS only -- no git ref, no marketplace constraint, no
#    lockfile, no manifest-level plugin-depends-on-plugin. So the pin cannot be
#    DECLARED to the CLI, only MATERIALISED: `lib/toolchain.py` fetches each
#    commit named in `lib/toolchain.lock.toml`, verifies the checkout IS that
#    commit, stages it beside the view and writes a run record that
#    `lib/place.sh` prints into the run's own trace.
#
#    "Which version?" is therefore a RUNNER obligation, not a schema one: there
#    is no field for the CLI to prompt about, and `execution.env` refuses
#    everything but `EVAL_*`, so the operator's shell is the only channel.
#
# NOTHING HERE REFUSES -- with one bounded exception added in SI-14, below.
# Every check warns on one line and carries on: an eval is an instrument, and an
# instrument that blocks the work is a gate wearing a lab coat. The exception is
# not a gate either: on a FULL-SUITE run at a terminal the script ASKS which
# toolchain to use, because a silent default is the defect SI-14 exists to
# close. Asking is not refusing -- pressing Enter takes the pin -- and with no
# terminal to ask at, it takes the pin and SAYS SO rather than blocking a CI
# run. A single-case run defaults to the pin and says what it defaulted to.
set -euo pipefail

here=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(CDPATH= cd -- "$here/.." && pwd)

# A path the eval sandbox can reach. The operator's home is not one: the same
# command succeeded in an ordinary shell and failed inside a run, and
# /private/tmp is where the CLI keeps its own temporaries.
view="${SI10_VIEW:-/private/tmp/tla-spec-dev-eval-view}"

# ---------------------------------------------------------------- the view
echo "eval: staging a plugin view of $repo"
rm -rf "$view"
mkdir -p "$view"
tar -cf - -C "$repo" \
    --exclude='./.git' \
    --exclude='./.skill-manager' \
    --exclude='./.claude' \
    --exclude='./.codex' \
    --exclude='./.gemini' \
    --exclude='./.pytest_cache' \
    --exclude='./.idea' \
    --exclude='./specs/.history' \
    --exclude='./evals/results' \
    --exclude='./.toolchain' \
    . | tar -xf - -C "$view"

entries=$(find "$view" | wc -l | tr -d ' ')
echo "eval: the view holds $entries entries (the limit is 20000; this checkout is $(find "$repo" -path "$repo/.git" -prune -o -print | wc -l | tr -d ' '))"
if [ "$entries" -ge 20000 ]; then
    # WARN, NEVER REFUSE. The run that follows will fail with the CLI's own
    # message, which is more informative than anything this script could say;
    # what this line adds is where the entries went.
    echo "eval: WARNING -- the view is over the 20000-entry limit and the run below will be refused."
    echo "eval:            the biggest directories in it are:"
    (cd "$view" && for d in */ .[!.]*/; do [ -d "$d" ] && echo "  $(find "$d" | wc -l | tr -d ' ') $d"; done | sort -rn | head -5) || true
fi

mkdir -p "$view/hooks"
cp "$here/hooks/hooks.json" "$view/hooks/hooks.json"

# ------------------------------------------------------------- the grant
# Read the cases this invocation will actually run, and grant exactly the gated
# tools they declare. `--case` is a glob, so the filter here is the same glob.
case_glob='*'
toolchain_ref=''
args=()
while [ $# -gt 0 ]; do
    case "$1" in
        --case) case_glob="${2:-*}"; args+=("$1" "$2"); shift 2 ;;
        --case=*) case_glob="${1#--case=}"; args+=("$1"); shift ;;
        # CONSUMED HERE, NOT PASSED ON: `claude plugin eval` has no such flag,
        # and passing it through would fail the run with an unknown-option error
        # that says nothing about toolchains.
        --toolchain-ref) toolchain_ref="${2:-}"; shift 2 ;;
        --toolchain-ref=*) toolchain_ref="${1#--toolchain-ref=}"; shift ;;
        *) args+=("$1"); shift ;;
    esac
done

grant=$(python3 "$here/lib/grant.py" "$here" "$case_glob") || grant=""

if [ -n "$grant" ]; then
    echo "eval: granting $grant (derived from the cases' allowed_tools)"
    # shellcheck disable=SC2206
    grant_args=(--allow-tools $grant)
else
    grant_args=()
fi

# A Bash-granted run needs a scratch HOME on a machine with Docker Desktop: the
# sandbox refuses while `~/.docker` holds a symlink, and `~/.docker` here holds
# 18 of Docker's own CLI shims. Overriding HOME fixes the sandbox and breaks
# authentication, because the login credential is in the keychain and the
# keychain path is HOME-relative -- so the home has to symlink
# `Library/Keychains`. evals/README.md builds one in six lines. It is not built
# here: it copies a credential file and links a keychain, which is the
# operator's call to make, once, rather than something a run script does behind
# them.
if [[ " $grant " == *" Bash "* ]] && [ -z "${EVAL_HOME:-}" ]; then
    echo "eval: NOTE -- a Bash-granted case may need EVAL_HOME (see evals/README.md, 'The home')."
fi

# --------------------------------------------------------- the toolchain pin
# WHICH skt, AND SAID OUT LOUD. See header item 6. The rule this implements:
# a full-suite run ASKS and never guesses silently; a single-case run may
# default, but it must say what it defaulted to. A silent default is the defect;
# a loud one is a convenience.
pinned=$(python3 "$here/lib/toolchain.py" print-ref --unit skt 2>/dev/null || echo "")
ref_args=()
if [ -n "$toolchain_ref" ]; then
    ref_args=(--ref "$toolchain_ref")
    echo "eval: toolchain -- using the ref you named: $toolchain_ref (recorded as an OVERRIDE)"
elif [ -n "${SI14_TOOLCHAIN_REF:-}" ]; then
    ref_args=(--ref "$SI14_TOOLCHAIN_REF")
    echo "eval: toolchain -- using SI14_TOOLCHAIN_REF=$SI14_TOOLCHAIN_REF (recorded as an OVERRIDE)"
elif [ "$case_glob" = '*' ] && [ -t 0 ]; then
    # THE ASK. Only for a full suite, and only where there is somebody to answer.
    echo "eval: ------------------------------------------------------------"
    echo "eval: this is a FULL-SUITE run. Which skt is it graded against?"
    echo "eval:   pinned:  ${pinned:-UNREADABLE} "
    echo "eval:            (evals/lib/toolchain.lock.toml, under change control)"
    echo "eval:   the operator's home would instead have used whatever its"
    echo "eval:   install record says today -- that is what the pin replaces."
    printf 'eval: press Enter to use the pin, or type a commit/branch: '
    read -r answer || answer=''
    if [ -n "$answer" ]; then
        ref_args=(--ref "$answer")
        echo "eval: toolchain -- you answered $answer (recorded as an OVERRIDE)"
    else
        echo "eval: toolchain -- using the pin ${pinned:-?}"
    fi
    echo "eval: ------------------------------------------------------------"
elif [ "$case_glob" = '*' ]; then
    # NO TERMINAL. Refusing here would block CI on a question nobody can answer,
    # which is a gate. Taking the PIN is not a guess -- it is the declared value,
    # read from a file under change control -- so it is taken, and announced.
    echo "eval: toolchain -- FULL SUITE with no terminal to ask at."
    echo "eval:   using the PINNED ${pinned:-?} from evals/lib/toolchain.lock.toml."
    echo "eval:   Nothing was guessed. To choose: --toolchain-ref <commit> or SI14_TOOLCHAIN_REF."
else
    echo "eval: toolchain -- single case ('$case_glob'); DEFAULTING to the pinned ${pinned:-?}"
    echo "eval:   (override with --toolchain-ref <commit>)"
fi

record_dir="$repo/evals/results/toolchain"
mkdir -p "$record_dir" "$view/toolchain"
record="$record_dir/$(date -u +%Y%m%dT%H%M%SZ).json"
echo "eval: materialising the toolchain (this fetches pinned commits)"
# `${arr[@]+"${arr[@]}"}` AND NOT `"${arr[@]}"`: macOS ships bash 3.2.57, where
# an EMPTY array expanded under `set -u` is an "unbound variable" error. Measured
# here -- the first version of this line died with
# `run.sh: line 217: ref_args[@]: unbound variable` on the ordinary path where
# the operator took the pin and named no override, i.e. on almost every run.
if python3 "$here/lib/toolchain.py" materialise \
        ${ref_args[@]+"${ref_args[@]}"} --check-drift --stage-into "$view" --record "$record"; then
    cp "$record" "$view/toolchain/RECORD.json"
    echo "eval: the run record is $record (and staged for the hook to print)"
else
    # WARN, NEVER REFUSE -- but be explicit about what the run now cannot say.
    echo "eval: WARNING -- the toolchain could not be materialised."
    echo "eval:            The run below will proceed, and it will NOT be able to"
    echo "eval:            name the toolchain it used. Do not quote its score"
    echo "eval:            against a toolchain version."
fi

# The entry count above was taken BEFORE the toolchain was staged, so re-check:
# a view that crosses 20,000 is refused by the CLI with a message about plugin
# directory size, which reads as a repository problem rather than as this.
entries_after=$(find "$view" | wc -l | tr -d ' ')
echo "eval: the view holds $entries_after entries after staging the toolchain"
if [ "$entries_after" -ge 20000 ]; then
    echo "eval: WARNING -- staging the toolchain pushed the view over the 20000-entry limit."
fi

export SI10_CHECKOUT="$repo"
export PATH="$repo/evals/bin:$PATH"
export CLAUDE_CODE_WALNUT_SPIRE=1
[ -n "${EVAL_HOME:-}" ] && export HOME="$EVAL_HOME"

echo "eval: running"
set +e
# `${arr[@]+"${arr[@]}"}` FOR BOTH ARRAYS. macOS ships bash 3.2.57, where an
# EMPTY array expanded under `set -u` is an "unbound variable" error. This was a
# latent defect here before SI-14 and it fired the moment a run selected no
# cases -- `--case` with a typo in it, say:
#
#   evals/run.sh: line 250: grant_args[@]: unbound variable
#
# which reads as a broken runner rather than as "that glob matched nothing".
claude plugin eval "$view" \
    --ablation none \
    --runs 1 \
    --trust-plugin \
    ${grant_args[@]+"${grant_args[@]}"} \
    ${args[@]+"${args[@]}"}
status=$?
set -e

# -------------------------------------------------------------- harvest
if [ -d "$view/evals/results" ]; then
    mkdir -p "$repo/evals/results"
    cp -R "$view/evals/results/." "$repo/evals/results/" 2>/dev/null || true
    echo "eval: results harvested into $repo/evals/results"
fi
exit "$status"
