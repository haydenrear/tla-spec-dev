# The eval suite

Seven cases, one per nested skill, run against **this checkout** in one command.

```bash
evals/run.sh                                  # all of them
evals/run.sh --case use-the-front-door        # one
evals/run.sh --case 'git-*'                   # a glob
```

| skill | case | the question |
|---|---|---|
| `spec-double-2` | `scaffold-a-program-model` | given a program with no spec, does the model represent the one property that is only true over a trace? |
| `spec-double-2` | `catch-the-drift` | given a program and the model it already has, can you find where they stopped agreeing — and repair the program rather than the model? |
| `discovery` | `start-from-the-spec-not-the-source` | does the account of the program come from the map the repository carries, or from a re-derivation of it? |
| `git-issue` | `a-work-order-not-a-wish` | does the issue carry what an implementer needs, or restate the complaint? |
| `git-issue-workflow` | `use-the-front-door` | is the first move `wt new`, or a bare `git worktree add` that leaves the agent writing the operator's global home? |
| `git-epic-workflow` | `epic-mode-is-not-main` | does the assignment marker change the branch point, the PR base, and the stopping point? |
| `test-graph` | `compose-a-behavioural-graph` | does a registered graph with a node in it come out, or another unit test in a new directory? |

Full method — what a grader can see, what a case can observe, how to keep a
score attached to something that happened — is
`skills/spec-double-2/references/plugin_evals.md`. This page is how to run
*these*.

## Which toolchain the score belongs to

Every run resolves a toolchain, and until SI-14 **no run recorded which one**.
`skt` came from the operator's live home at whatever `main` pointed to that day:
the project home's record said `gitRef main, gitHash 286a3694, installed
2026-09-14`, and by 2026-09-19 `main` was `0f380781`. Five days, two different
toolchains, one name — so no two runs a week apart were known to be comparable,
and a score that moved could not be attributed to the change meant to move it.

**The pin is `evals/lib/toolchain.lock.toml`**, under change control, naming a
**commit** for each unit. It cannot be declared to the CLI — `claude plugin
eval` has no version pinning for plugin dependencies, and `plugins:` takes
relative filesystem paths only — so `evals/lib/toolchain.py` **materialises**
it: fetches each pinned commit, verifies the checkout *is* that commit, stages
it beside the view, and writes a run record that the `SessionStart` hook prints
into the run's own trace.

```bash
evals/run.sh                                   # asks which skt, at a terminal
evals/run.sh --toolchain-ref <commit>          # answer it up front
SI14_TOOLCHAIN_REF=<commit> evals/run.sh       # same, from the environment
python3 evals/lib/toolchain.py print-ref       # what is pinned, no network
python3 evals/lib/toolchain.py materialise --check-drift   # and has it moved?
```

* **A full-suite run ASKS**, because a silent default is the defect this closes.
  Pressing Enter takes the pin; asking is not refusing.
* **With no terminal** (CI) it takes the pin and *says so*. Refusing there would
  block a run on a question nobody can answer, which is a gate.
* **A single-case run defaults** to the pin and **says what it defaulted to**.
* Anything you answer other than the pin is recorded as an `OVERRIDE`.

Each run writes `evals/results/toolchain/<timestamp>.json` — origin, pinned
commit, the verified `HEAD`, whether the branch has drifted since, and what the
operator's ambient home *would* have used instead.

### The CLI under test is the epic branch's, not the brew install

`evals/bin/skill-manager` is a shim, the sibling of `evals/bin/tla-spec-dev` and
for the same measured reason. It execs `./skill-manager` — the 346-byte wrapper
in the materialised checkout — so reaching the epic branch's CLI is a PATH entry,
**not a rebuild and not an install**, and nothing is written over
`/opt/homebrew/Cellar/skill-manager`. Like its sibling it exits 127 rather than
falling through to the installed copy. The wrapper names its own commit, so the
record quotes the CLI's own account of what ran:

```
skill-manager 0.28.1+g6ffacb88ff96
build:  6ffacb88ff96 (detached)
```

The materialised checkouts live in `.toolchain/` at the repository root
(gitignored) — **not** under `evals/`, because case discovery is a recursive
glob over the eval dir and the skill-manager checkout ships 56 `case.yaml` files
of its own, which would otherwise be discovered, scored and billed as ours.

### What is not yet wired, and why

The pinned unit is materialised, verified, staged and recorded — but **no case
loads it through `plugins:`**, and that is deliberate. Measured over 4 runs on
2.1.276: a case declaring `plugins:` **silently loses the target plugin's
hooks**, scoring 1.00 either way.

```
si14-target-noplug     hook fired 2 of 2 runs    score 1.00
si14-target-withplug   hook fired 0 of 2 runs    score 1.00
```

Every fixture in this suite is placed by `lib/place.sh`, a `SessionStart` hook.
A `plugins:` entry added to any case here would hand the agent an **empty
workspace** and score it 0 — reported as a skill failure. `tests/test_eval_toolchain_pin.py`
holds that line until the defect is resolved upstream.

## Why there is a script and not a command to copy

The command underneath is this, and every part of it is load-bearing:

```bash
PATH="$PWD/evals/bin:$PATH" CLAUDE_CODE_WALNUT_SPIRE=1 \
  claude plugin eval <a staged view of this checkout> \
      --ablation none --runs 1 --allow-tools Bash Write Edit
```

Four of those five parts were learned from a run that scored 0 for a reason
that was not the agent's, and the fifth is a directory that has to be built.

* **the staged view** — `claude plugin eval` refuses a plugin directory over
  20,000 entries, and this repository **is** the plugin. See below.
* **`CLAUDE_CODE_WALNUT_SPIRE=1`** — the subcommand is gated behind it and does
  not exist without it.
* **`PATH="…/evals/bin:$PATH"`** — without it the run grades whichever
  `tla-spec-dev` the operator has installed, not this checkout. Measured: a
  run's `which -a tla-spec-dev` returned the installed wrapper three times and
  nothing else. A plugin `bin/` directory does not reach the eval's PATH, and
  `execution.env` refuses `PATH` — *"only EVAL_\* keys can be set from
  case.yaml. Anything else must come from the operator's shell."* The operator's
  shell is the only channel, which is what `run.sh` is.
* **`--allow-tools`** — a tool named in a case's `allowed_tools:` is still
  refused unless the operator ALSO grants it. `--allow-tools Bash` against a
  case declaring `[Bash, Write, Edit]` produced `not granted (missing
  --allow-tools grant, or a malformed entry): Write, Edit` and a score of 0 — an
  agent that could read the program and could not write one line of the spec,
  reported as a failure to model. `run.sh` **derives the grant from the cases it
  is about to run**, so a new case cannot fall out of step with a README.
* **`--ablation none`** — the second arm loads no plugin, so the fixture hook
  does not fire and the baseline gets an empty repository. Its 0 would read as
  "the skill is what scored" when it means "the fixture was never placed".

`run.sh` does those, stages the hooks, and harvests the report back out of the
view into `evals/results/`.

## The 20,000-entry limit, and what was done about it

```
a plugin directory holds more than 20000 entries to check for eval directories
  — point the case at a smaller plugin directory
```

Measured on Claude Code 2.1.275 at `994f650c`: this checkout is **70,741
entries** and the refusal fires — with or without an explicit `plugins:` entry
in the case. It is not marginal. `specs/.history`, the append-only record, is
19,154 of it; the gitignored per-checkout `.skill-manager` home is another
41,169.

**There is no exclusion mechanism to reach for.** No `.gitignore`, no
`.claudeignore`, no manifest key, no flag, no environment variable. The
traversal skips version-control metadata (`.git`, `.svn`, `.hg`) and nothing
else. `--eval-dir` moves where *cases* are found, not what gets counted.

So the ticket's question — *a plugin directory that excludes the append-only
record, or a documented exclusion* — has only one honest answer here, and
`run.sh` implements it: **stage a plugin directory that excludes the record.**
A copy of the working tree without `specs/.history`, without `.skill-manager`,
without the agent homes, made fresh on every run. **6,264 entries**, and the CLI
accepts it.

Three things worth knowing about that choice:

* **It is a copy, and copies drift — this one cannot.** It is built at the top
  of every run from the working tree it is testing, and deleted the next time.
  Nothing commits it, and nothing has to remember to update it.
* **It replaced a committed symlink shim that had already gone stale.**
  `examples/agent_integration/eval-plugin/` carried the skill surface by name —
  `skills/spec-double-2` — and after the skills were nested there were six.
  A directory that has to be hand-edited whenever a skill is added shows one
  skill and reports nothing about the other five.
* **The record is what is excluded, and that is not a loss.** `specs/.history`
  is a record of what was true when it was written. No case reads it.

If you run `claude plugin eval .` directly you will get the refusal above. That
is the CLI telling you to use `run.sh`.

## The hooks are staged, not committed at the root

A plugin's hooks live at `<plugin>/hooks/hooks.json`. This plugin is the
repository, so a `hooks/hooks.json` committed at the root would run a
`SessionStart` shell script in **every session of every user who installs
tla-spec-dev** — and a fixture hook's blocking `exit 2` would be able to refuse
somebody's ordinary session.

So `evals/hooks/hooks.json` is copied into the staged view by `run.sh` and
loaded from there. The shipped plugin gains no hooks and no new way to refuse.

Two hooks do the work that no grader can:

* **`SessionStart` → `lib/place.sh`** places the fixture and names the
  toolchain. It is a hook and not `scaffold_script:` because that key is
  accepted by the loader and **never executed** — measured at every placement,
  in both forms, including a body that exits 3, which changed nothing.
* **`Stop` and `SessionEnd` → `lib/verify.sh`** runs the real checks and writes
  the verdict paths the graders read. Both events, because a run that ends
  `error_max_turns` fires `SessionEnd` and not `Stop`: a sibling suite
  registered only on `Stop` and lost every verdict on 12 capped runs, scoring
  them red.

## Five cases need no shell, and that is deliberate

Only `scaffold-a-program-model`, `catch-the-drift` and
`compose-a-behavioural-graph` grant `Bash`. The other four ask for a document —
a plan, an issue, an account — and grade it with a program.

That is not a compromise on rigour; it is what makes the suite runnable. A
Bash-granted run on a machine with Docker Desktop refuses:

> the Docker (`~/.docker`, `DOCKER_CONFIG`) credential store on this machine
> holds a symbolic link inside it, so the Bash sandbox cannot reliably exclude it

`~/.docker` holds 18 of Docker's own CLI shims, none of them credentials, and
`DOCKER_CONFIG` pointed elsewhere does not help — the message is byte-identical,
so the check reads `~/.docker` regardless. Overriding `HOME` fixes the sandbox
and breaks authentication, because the login credential is in the keychain and
the keychain path is HOME-relative. Both hold at once only if the scratch home
symlinks `Library/Keychains`:

```bash
EVAL_HOME=/path/to/scratch/evalhome
mkdir -p "$EVAL_HOME/.docker" "$EVAL_HOME/Library"
cp ~/.docker/config.json "$EVAL_HOME/.docker/config.json"   # the file only
for p in .claude .claude.json .config .cache .local; do ln -s "$HOME/$p" "$EVAL_HOME/$p"; done
ln -s "$HOME/Library/Keychains" "$EVAL_HOME/Library/Keychains"
export EVAL_HOME
```

`run.sh` honours `EVAL_HOME` and says so when a Bash-granted case is selected
without one. It does not build the home itself: that copies a credential file
and links a keychain, which is the operator's call to make once, not something
a run script should do behind them.

## Reading a score

* **A red is not always the work's.** `file_exists` has no UNDECIDED state, so a
  verifier whose `java` or `tla2tools.jar` did not resolve leaves the same
  absent path as a genuine failure. `.eval/UNDECIDED-toolchain` is written in
  that case, `.eval/UNDECIDED-unconfined` when `sandbox-exec` was unavailable,
  and `.eval/verify.log` records what was missing. Check them before reading a 0
  as the agent's.
* **A run that ended `error_max_turns` has no closing report**, so every
  response grader votes FAIL on work that may be finished. Read the `error:`
  column beside the score.
* **A majority is not a consensus.** The `llm` grader takes three votes, and a
  run whose artefact was plainly correct has passed FAIL PASS PASS. One run of
  one case is not evidence of much.
* **Four cases grade a document.** `use-the-front-door`,
  `epic-mode-is-not-main`, `a-work-order-not-a-wish` and
  `start-from-the-spec-not-the-source` check what an agent *wrote*, mechanically
  and against the workspace's own contents, not what it would do. Each grader
  body says so in its own words. That bound is smaller than it sounds — the
  three moves `epic-mode-is-not-main` checks are the ones that cannot be taken
  back — but it is a bound, and a score from this suite should be quoted with
  it.

## Debugging a run

`--keep-temp` preserves each run's sandbox and prints its path. The workspace is
sealed at mode 000; open it with

```bash
chmod 700 <kept>/ <kept>/sealed && chmod -R u+rX <kept>/sealed
```

then read the workspace at `<kept>/sealed/home/cwd` and the event stream at
`<kept>/out/trace.jsonl`. The trace is where the hook's `exit_code`, the
per-turn tool calls and the turn-ceiling error are visible; the summary line
shows none of them.
