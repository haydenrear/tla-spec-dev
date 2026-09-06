# The eval suite, and what it replaces

`claude plugin eval` runs each case in a **fresh isolated `claude -p` session
with its own `CLAUDE_CONFIG_DIR` and `HOME`**, enforces a timeout, grades the
resulting workspace, and writes non-overwriting JSON per run.

`run_agent_integration.py` hand-rolled every one of those, and **every defect in
the harness landed in the hand-rolled part** — `H-02` (agents writing into the
operator's memory), `G-05`–`G-07` (the launch substrate), `H-07a` (timeout
killing only the child), `H-07c`/`H-07d` (evidence ordering and path leakage).
The parts nothing else does — the transcript harvest, the attribution probe —
produced the findings and no defects.

## Why a thin plugin rather than the repository

`claude plugin eval` resolves a skills directory, so the repository itself was
the obvious target. It refuses:

> a plugin directory holds more than 20000 entries to check for eval directories

`specs/` alone is 20,493 files, almost all of it append-only `.history` and
`results` — a record of what was true when written, and nothing to do with the
skill's surface. So this directory carries that surface and nothing else:
`SKILL.md`, `references`, `scripts`, `templates`, `spec_double_compiler`, **all
as symlinks**. 21 entries instead of 25,000, and nothing is copied, so nothing
can drift from the repository (`E-14`).

## Running it

```bash
EVALHOME=<a scratch directory>          # see "The home" below -- not your $HOME
BIN=$PWD/examples/agent_integration/eval-plugin/bin

PATH="$BIN:$PATH" HOME=$EVALHOME CLAUDE_CODE_WALNUT_SPIRE=1 \
  claude plugin eval examples/agent_integration/eval-plugin \
      --ablation none --runs 1 --allow-tools Bash Write Edit
```

Add `--case <name>` to run one of them; there are two:

| case | the question |
|---|---|
| `scaffold-a-program-model` | given a program with no spec, does the model represent the one property that is only true over a trace? |
| `catch-the-drift` | given a program and the model it already has, can you find where they stopped agreeing -- and repair the program rather than the model? |

Every part of that line is load-bearing, and each one was learned by a run that
scored 0 for a reason that was not the agent's:

* **`CLAUDE_CODE_WALNUT_SPIRE=1`** — `plugin eval` is gated behind it. Without
  it the subcommand does not exist.
* **`--allow-tools Bash Write Edit`** — the operator grant. `--allow-tools Bash`
  alone produced `not granted (missing --allow-tools grant, or a malformed
  entry): Write, Edit` and a score of 0: the agent could read the program and
  could not write a line of the spec. A tool named in the case's
  `allowed_tools:` is still refused unless it is *also* granted here.
* **`PATH="$BIN:$PATH"`** — **without it the run grades whichever
  `tla-spec-dev` the operator has installed, not this checkout.** Measured: a
  run's `which -a tla-spec-dev` returned
  `/Users/hayde/.skill-manager/bin/cli/tla-spec-dev` three times and nothing
  else, and a traceback resolved the code from
  `~/.skill-manager/skills/spec-double-compiler/scripts/`. Three fixes that do
  not work: a plugin `bin/` directory (documented to join the Bash tool's PATH;
  inside `plugin eval` it never appears), `execution.env: {PATH: ...}` in
  case.yaml (refused — *"only EVAL_\* keys can be set from case.yaml. Anything
  else must come from the operator's shell."*), and a shim under `/tmp` (the
  PATH reaches the run, but the sandbox cannot see `/private/tmp`). `bin/`
  here holds a shim that execs this tree's `scripts/tla_spec_dev.py` and
  **exits 127 rather than falling through** to an installed copy. The
  `SessionStart` hook prints which one it got, so the trace answers the
  question without anyone reconstructing it.
* **`--ablation none`** — see "Why the baseline arm is off" below.
* **`HOME=$EVALHOME`** — see "The home".

## The home

The Bash sandbox refuses to run when `~/.docker` contains a symbolic link:

> the Docker (`~/.docker`, `DOCKER_CONFIG`) credential store on this machine
> holds a symbolic link inside it, so the Bash sandbox cannot reliably exclude it

`~/.docker` here holds **18 symlinks** — 7 in `bin/`, 11 in `cli-plugins/` — all
of them Docker Desktop's own CLI shims, none of them credentials. Pointing
`DOCKER_CONFIG` at a plain directory **does not help**: the message is
byte-identical, so the check reads `~/.docker` regardless of the override it
names. Overriding `HOME` fixes the sandbox and breaks authentication —
`Not logged in - Please run /login` — even with `.claude`, `.claude.json` and
the skt token symlinked in.

The missing piece is that **the login credential lives in the keychain, and the
keychain path is HOME-relative**. Symlink `Library/Keychains` and both
requirements hold at once. Build the home once:

```bash
EVALHOME=/path/to/scratch/evalhome
mkdir -p "$EVALHOME/.docker" "$EVALHOME/Library"
cp ~/.docker/config.json "$EVALHOME/.docker/config.json"   # the file only; no bin/, no cli-plugins/
for p in .claude .claude.json .claude-skt-token .config .cache .local; do
    ln -s "$HOME/$p" "$EVALHOME/$p"
done
ln -s "$HOME/Library/Keychains" "$EVALHOME/Library/Keychains"   # <- the piece that fixes auth
```

`.docker` must be a real directory holding a real file. A symlink to `~/.docker`
puts the 18 shims back and the sandbox refuses again.

## What places the fixture: a hook, not `scaffold_script`

`case.yaml` accepts a `scaffold_script:` key and `--scaffold` promises to run
it. **It never runs.** Measured in 2.1.261 across every placement — top level,
under `execution:`, `setup:`, `workspace:`, `sandbox:`, and as `scaffold.script`
— and in both forms, a file name and inline bash. The decisive probe was an
inline body of `echo ... >&2; exit 3`: the case still scored 1.00, so the script
was not merely failing quietly, it was never invoked.

So the fixture is placed by `hooks/hooks.json`, a `SessionStart` hook that runs
`lib/place.sh` with the workspace as its working directory. One hook serves
both cases and dispatches on `EVAL_CASE`. This is the mechanism the CLI's own
grader warning names — *"a plugin hook still could"* create a file the run is
graded on — and it is verified: the trace records a `hook_response` for
`SessionStart` carrying the hook's `place: …` output at `exit_code 0`, before
the first turn.

(An earlier draft of this paragraph cited a `scaffold.sh` that no longer exists
and quoted a message this code cannot emit — a measurement claim citing the
output of a deleted implementation. A blind review caught it. The lesson is
narrow and worth keeping: prose that quotes evidence has to be re-read whenever
the thing producing the evidence is renamed.)

The hook also **names the toolchain** rather than leaving the session to find
it. The first scored run spent 39 of its 40 turns on environment archaeology —
`find / -maxdepth 8 -iname "tla2tools*.jar"`, a scan of
`/Library/Java/JavaVirtualMachines`, an `unzip` of the jar to locate the
standard modules — hit the turn ceiling, and left behind `Probe.tla`, a counter
mod 3. The trace-property grader then voted FAIL, which reads as *the model is
wrong* and means *no model was ever attempted*.

## A run that ends on the turn ceiling has no report, and FAIL is the wrong word for that

Naming the toolchain worked: at 60 turns the archaeology was gone (Bash 39 →
32) and the freed turns went into the work (Write 5 → 22, Edit 0 → 12). The
session produced a real spec tree — `Core.tla`, `Internal.tla`, `External.tla`,
a manifest, adapters, conformance tests — with `Release` as an action and the
handoff property stated as a step formula, which is precisely what the fixture
exists to elicit.

**It scored 0.50.** The session ended `error_max_turns` at turn 61, its last
words *"Now full verification of everything I can execute."*, so there was no
closing report and the response grader read nothing.

An absent report is not a wrong report, and this suite cannot say so. Read every
`0.50` against the run's `error:` line before reading it as "modelled half of
it": the two are indistinguishable in the score. `max_turns` is now 120 and
`timeout_seconds` 2700, which makes the truncation rarer without making the
score honest when it happens.

**At 120 turns the case scores 1.00** — 103 turns, `subtype: success`, 1781s,
$10.59. That is the working reference point: a passing run of this case costs
about ten dollars and half an hour. Note the response grader passed **FAIL PASS
PASS**, a majority rather than a consensus, on a run whose artefact is plainly
correct — one run's score from this case is not evidence of much.

## What this suite cannot measure: TLC never runs

The passing run reported its own largest gap without being asked:

> **TLC has never been run on this model.** Not on `Internal.cfg`, not on
> `External.cfg`, not on `Witness.cfg`.

```
$ mkdir -p "$TMPDIR/x"
mkdir: /private/tmp/e-3WvvbF/tmp/x: Operation not permitted
```

**The eval sandbox denies filesystem writes to spawned subprocesses.** The
agent's own `Write` tool works — the CLI mediates it — but TLC creates a metadir
before exploring anything, so it aborts having checked nothing. Every
allowlisted scratch location behaves the same way; this is not a matter of
choosing a directory, and no `--allow-tools` grant changes it.

So **this suite measures whether a model gets AUTHORED, and can never measure
whether it CHECKS.** Any score from it must be read inside that bound. The run
substituted a Python reachability check — 2,325 states, 111,600 transitions,
each `(state, call)` pair matched against the real `Shortener` — which is a real
cross-check and is not model checking.

## What the two cases score

Measured, both cases, one run each, with the checkout's shim on `PATH` and the
verdict graders hardened after a blind review:

| case | score | cost | evidence behind it |
|---|---|---|---|
| `catch-the-drift` | **1.00** | $1.86 | the account survives into `snapshot()`; the model tree matches the shipped one byte for byte |
| `scaffold-a-program-model` | **1.00** | $12.02 | SANY on every module; TLC clean on `Internal` (2,325 distinct states), `External` (223) and a `Scenario_ReleaseHandoff` witness the session wrote itself (13) |

**Read the middle of that table, not the left.** Three earlier runs of the same
case scored 1.00, 0.75, 0.25 and 0.50, and only one of those numbers was about
the model: the 1.00 was scored while `tla-spec-dev` failed on all three
attempts, the 0.25 was the verifier's own `$HOME` assumption, and the 0.50 was a
run cut off mid-sentence. The scores became worth quoting when the evidence
column became something a program had checked.

Judge triples observed across this suite's development: `FAIL PASS PASS`,
`PASS PASS PASS`, `FAIL PASS FAIL`, `PASS PASS PASS`. **A majority is not a
consensus**, and one run's `llm` score is not evidence of much — which is why
the verdict graders carry most of the weight and the response graders are a
minority voice.

## Why the baseline arm is off

Under `--ablation with-without` the second arm loads no plugin, so **the hook
does not fire and the baseline gets an empty repository**. Its 0 would read as
"the skill is what scored" when it means "the fixture was never placed" — a
false attribution, and precisely the confusion this suite exists to remove. Run
with `--ablation none` until the fixture can be placed independently of the
plugin.

Related, and worth knowing before reading any delta: the sandbox is not
hermetic. The first scored run read `/Users/hayde/.skill-manager/skills/
spec-double-compiler/references/*` and the repository checkout directly. The
plugin arm and a hypothetical baseline arm can both reach the installed skill.

## What each grader can actually see

**The `llm` grader sees the agent's final response and nothing else.** Not the
workspace, not tool output. Measured with a probe case whose hook wrote
`banana` into `SECRET.txt` and whose criterion was "score 1 only if SECRET.txt
contains banana":

| what the agent did | judge votes |
| --- | --- |
| never mentioned the file | FAIL FAIL FAIL |
| **read** the file, did not quote it | FAIL FAIL FAIL |
| quoted its contents in the reply | PASS PASS PASS |

`models-the-trace-property.md` used to direct the judge at the generated
modules rather than the reply. That instruction could never be followed, so what
it scored was the claim while reading as though it scored the artefact —
`SS-02` with the grader itself as the absent input. It now says what it grades,
and the case prompt requires the response to quote the module's `Next`
disjuncts so there is real text to grade.

There is no content-matching grader to fall back on: `regex` matches the
response only and rejects `path:` and `file:`; `file_exists` rejects
`contains:`. The grader types are `regex | tool_order | tool_used | file_exists
| llm | baseline`, and only `file_exists` observes the workspace — by path.

So the artefact evidence is a path, and it must be a path nothing cheaper than
the work can produce. **No grader here reads the work directly**: every
`file_exists` path is a verdict under `.eval/`, written by `lib/verify.sh` after
a real program succeeded, and a pin enforces that. An intermediate design did
point a grader at `specs/program_model/spec_manifest.yaml` — better than the
`*.tla` glob a scratch `Probe.tla` satisfied, and still a file the agent types
itself.

## Debugging a run

`--keep-temp` preserves each run's sandbox and prints its path. The workspace is
sealed at mode 000; open it with

```bash
chmod 700 <kept>/ <kept>/sealed && chmod -R u+rX <kept>/sealed
```

then read the workspace at `<kept>/sealed/home/cwd` and the full event stream at
`<kept>/out/trace.jsonl`. The trace is where the hook's `exit_code`, the per-turn
tool calls, and the turn-ceiling error are visible; the summary line is not
enough to tell "modelled it wrong" from "never got there".
