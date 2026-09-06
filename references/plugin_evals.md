# Evals that cannot be talked into passing

How to drive `claude plugin eval` against a skill, and how to keep its score
attached to something that happened.

Everything here was measured against Claude Code **2.1.261** on macOS, mostly by
running probe cases that cost cents. Where a claim came from a probe, the probe
is named. Where a thing is undocumented and I could not settle it, that is said
rather than guessed.

The worked example is `examples/agent_integration/eval-plugin/`.

---

## 1. The three things a case can observe

This is the whole surface. Six grader types, and they see between them exactly
three things:

| grader | what it reads |
|---|---|
| `file_exists` | **a path in the workspace**, after the run. Globs allowed |
| `tool_used` | **a tool NAME** was called, with a count range |
| `tool_order` | one tool name **before** another |
| `regex` | **the final response text** |
| `llm` | **the final response text**, judged by a model, majority of 3 votes |
| `baseline` | the final response text, against a `baseline_file` |

And here is what nothing observes: **file contents, tool inputs, tool outputs,
exit codes.**

Three probes established the boundaries, and each of them refuted something I
had assumed:

* **The `llm` judge sees the final response and nothing else.** A hook wrote
  `banana` into `SECRET.txt`; the criterion was "score 1 only if SECRET.txt
  contains banana".

  | what the agent did | votes |
  |---|---|
  | never mentioned the file | FAIL FAIL FAIL |
  | **read** the file, did not quote it | FAIL FAIL FAIL |
  | quoted its contents in the reply | PASS PASS PASS |

  Not the workspace. Not tool output. The text it ends with.

* **`tool_used` cannot match a command.** The permission-style pattern parses —
  the failure message renders it back — but for `Bash` it matches nothing. A
  run whose only Bash call was literally `echo hello` scored `Bash` **1x** and
  `Bash(echo:*)` **0x** in the same run. There is no grader that can assert
  *this command ran*.

* **`file_exists` has no content filter.** `contains:` is rejected as an
  unrecognised key; `regex` rejects `path:` and `file:`. A path grader knows
  only that a path exists.

**Consequence, and it is the whole reason for section 3:** with only these,
every claim about *quality* has to be routed through the response — and the
response is written by the thing being graded.

---

## 2. Running one

```bash
HOME=$EVALHOME CLAUDE_CODE_WALNUT_SPIRE=1 \
  claude plugin eval <plugin-dir> \
      --ablation none --runs 1 --allow-tools Bash Write Edit
```

Each part is load-bearing, and each was learned from a run that scored 0 for a
reason that was not the agent's.

**`CLAUDE_CODE_WALNUT_SPIRE=1`** — the subcommand is gated behind it and does
not exist without it.

**`--allow-tools`** — the operator grant, and it is **separate from the case's
`allowed_tools:`**. Listing `Write` in the case grants nothing. Running with
`--allow-tools Bash` against a case declaring `[Bash, Write, Edit]` produced

```
not granted (missing --allow-tools grant, or a malformed entry): Write, Edit
```

once, in a per-case note, and a score of 0 — an agent that could read the
program and could not write one line of a spec, reported as a failure to model.
**Assert this in a test**: read `allowed_tools` from the case, read the
documented command from your README, and fail if a gated tool is in the first
and not the second.

**`--ablation none` vs the default** — the default runs a second arm with no
plugin and reports the delta. That is a real control and worth having, but only
if the second arm can do the task. If your fixture is placed by a plugin hook
(section 3), the no-plugin arm gets an **empty workspace** and its 0 means "the
fixture was never placed", not "the skill is what scored". Use `--ablation
none` until the fixture can be placed independently of the plugin.

**`--keep-temp`** — preserves each run's sandbox and prints the path. Open it:

```bash
chmod 700 <kept> <kept>/sealed && chmod -R u+rX <kept>/sealed
```

The workspace is `<kept>/sealed/home/cwd`; the full event stream is
`<kept>/out/trace.jsonl`. **Read the trace before you believe a score.** The
trace is where hook exit codes, per-turn tool calls, and `error_max_turns` are
visible, and the summary line shows none of them.

### The home

On a machine with Docker Desktop, a Bash-granting run refuses:

> the Docker (`~/.docker`, `DOCKER_CONFIG`) credential store on this machine
> holds a symbolic link inside it, so the Bash sandbox cannot reliably exclude it

`~/.docker` holds Docker Desktop's CLI shims — 18 symlinks under `bin/` and
`cli-plugins/`, none of them credentials. Two things that do not work:
`DOCKER_CONFIG` pointed at a plain directory (the message is byte-identical, so
the check reads `~/.docker` regardless of the override it names), and a bare
`HOME` override (the sandbox passes and the session cannot authenticate —
`Not logged in - Please run /login` — even with `.claude` and `.claude.json`
symlinked in).

**The credential lives in the keychain, and the keychain path is
HOME-relative.** Symlink `Library/Keychains` and both hold at once:

```bash
EVALHOME=/path/to/scratch/evalhome
mkdir -p "$EVALHOME/.docker" "$EVALHOME/Library"
cp ~/.docker/config.json "$EVALHOME/.docker/config.json"   # the file only
for p in .claude .claude.json .config .cache .local; do
    ln -s "$HOME/$p" "$EVALHOME/$p"
done
ln -s "$HOME/Library/Keychains" "$EVALHOME/Library/Keychains"
```

`.docker` must be a real directory holding a real file; symlinking it to
`~/.docker` puts the shims back.

**What this home does NOT leak — a correction, because I got it wrong once.**
An earlier draft of this section said symlinking `.claude` loads the operator's
personal skills into every run, and named `deep-research`, `dataviz` and
`code-review` as evidence. That was inference, not measurement, and the
measurement says otherwise: a run's `init` event listed **17 skills, every one
of them a Claude Code built-in**, plus the plugin under test. None of the
operator's 20 skill-manager units appeared, even though they are symlinked into
`~/.claude/skills/` and `~/.claude` is symlinked into this home.

The reason is stronger than a config directory. The run gets a **fresh HOME**:
the kept sandbox's `sealed/home/` holds `.aws .config .git .gitconfig .local
cwd` and **no `.claude` at all**, alongside its own per-run config dir with its
own `settings.json`, `projects/` and `sessions/`. `$EVALHOME` is not the run's
`HOME` either — it is what the CLI authenticates from before the sandbox is
built. **The run is more hermetic than I claimed, and your own skills are NOT
there unless you put them there** — which is section 3.5.

Why the wrong inference looked like evidence, since it is the useful part:
`deep-research`, `dataviz` and `code-review` all appear in the **zero-plugin**
arm too. They were built-ins the whole time, and naming three of them as
"the operator's personal skills" was a guess that happened to fit.

### Which copy of your CLI answers — and how to make it the checkout

**By default, it is not your checkout.** The run inherits the operator's whole
interactive `PATH`, `~/.skill-manager/bin/cli` is on it, and a
`which -a tla-spec-dev` inside a run returned

```
/Users/hayde/.skill-manager/bin/cli/tla-spec-dev
/Users/hayde/.skill-manager/bin/cli/tla-spec-dev
/Users/hayde/.skill-manager/bin/cli/tla-spec-dev
```

and nothing else. In another run, 32 of 55 Bash calls touched
`~/.skill-manager` and a traceback resolved the code from
`~/.skill-manager/skills/<unit>/scripts/`. **The plugin's skill directory
loaded correctly and the branch under review was still never executed** — the
skill under test was the plugin's, the toolchain under test was whatever was
installed.

Three ways to fix that do not work. Each was measured, not reasoned about:

| attempt | what happened |
|---|---|
| a plugin `bin/` directory | the docs say it joins the Bash tool's `PATH` while the plugin is enabled. Inside `plugin eval` it never appeared |
| `execution.env: {PATH: ...}` in case.yaml | refused: *"only EVAL_\* keys can be set from case.yaml. Anything else must come from the operator's shell."* |
| a shim under `/tmp` | the shell `PATH` **does** reach the run — it was first in `$PATH` — but the sandbox cannot reach `/private/tmp`, so `which` never found it |

The refusal message names the answer. **Ship a shim inside the checkout and let
the operator prepend it:**

```sh
# <plugin>/bin/<your-cli>
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo=$(CDPATH= cd -- "$here/../../../.." && pwd)
test -f "$repo/scripts/<entry>.py" || {
    echo "shim: no checkout at $repo -- refusing to fall through to an" \
         "installed copy, which would grade code nobody is reviewing" >&2
    exit 127
}
exec python3 "$repo/scripts/<entry>.py" "$@"
```

```bash
PATH="<plugin>/bin:$PATH" claude plugin eval <plugin-dir> ...
```

Verified: `which -a` then lists the checkout's shim first, ahead of the
installed copies. **The shim refuses rather than falling through** — a shim
that silently defers to the installed CLI reintroduces the exact bug it exists
to fix, and does it invisibly.

Then have the `SessionStart` hook *say which one it got*, and warn when it is
not the shim, so the trace answers the question without anyone having to
reconstruct it:

```
  tla-spec-dev: <plugin>/bin/tla-spec-dev  (THE CHECKOUT under review)
```

### Dependent tools

A skill declares `cli_dependencies` and then assumes they are there. The eval
sandbox is not your shell: have the `SessionStart` hook resolve each one and
print it, missing ones included.

```
  java:      /usr/bin/java
  tla2tools: ~/.skill-manager/bin/cli/.spec-double-compiler/tla2tools.jar
  pytest:    /Library/Frameworks/Python.framework/Versions/3.10/bin/pytest
  jinja2:    NOT ON PATH
```

`NOT ON PATH` printed before turn one is a truthful input. The same fact
discovered on turn 30 is a turn-ceiling failure that reads as an agent who
could not do the work.

---

## 3. Adding a skill, and placing a fixture

### The plugin

A directory with `.claude-plugin/plugin.json`:

```json
{"name": "<name>-eval", "version": "0.1.0", "experimental": {"evals": "evals"}}
```

and the skill surface under `skills/<skill-name>/`. **Symlink it, do not copy
it** — a copy drifts from the repository it claims to test. Verified loaded: a
passing run's `init` event listed the plugin, and the agent invoked
`Skill(<plugin>:<skill>)`.

One plugin holds **many cases** — `evals/<case-name>/` per case. You do not
need a plugin per case.

**But hooks belong to the plugin, not to a case**, so one `SessionStart` hook
has to serve every case. `execution.env` is the channel, and the allowlist that
refuses `PATH` is exactly what it is for:

```yaml
execution:
  env:
    EVAL_CASE: catch-the-drift
```

```sh
case "${EVAL_CASE:-}" in
  scaffold-a-program-model) ... ;;
  catch-the-drift)          ... ;;
  "")  echo "EVAL_CASE unset" >&2; exit 1 ;;
esac
```

Verified: a case setting `EVAL_CASE` had it visible in the hook. **Fail loudly
when it is unset** — a hook that silently places nothing is the empty-repository
failure again, and it reads as an agent who could not work.

Keep the shared scripts **outside** `evals/` (`<plugin>/lib/`). A directory
under `evals/` with no `case.yaml` is not loaded as a case today, but putting
library code where the loader is scanning invites a name to become meaningful
later.

If `plugin eval` refuses your repository with *"a plugin directory holds more
than 20000 entries"*, that is what the thin symlinked plugin is for: carry the
skill's surface and nothing else.

### `scaffold_script:` does not run — use a hook

A case may declare `scaffold_script:` and the CLI has a `--scaffold` flag that
prints a warning about running it. **The script is never executed.** Measured at
every placement — top level, `execution:`, `setup:`, `workspace:`, `sandbox:`,
`scaffold.script` — and in both forms, a file name and inline bash. The
decisive probe was an inline body of `echo ... >&2; exit 3`: the case still
scored 1.00, so it was not failing quietly, it was never invoked.

Place fixtures from a **`SessionStart` hook** in `hooks/hooks.json`. One hook
serves every case and dispatches on `EVAL_CASE` (see above), so it lives beside
the plugin rather than inside a case:

```json
{"hooks": {"SessionStart": [{"hooks": [
  {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/lib/place.sh"}
]}]}}
```

**Fail with exit 2, not exit 1.** Claude Code treats 2 as blocking and every
other non-zero code as advisory, so a placement hook that exits 1 prints its
complaint and lets the session start anyway — on a workspace it just failed to
set up. Where a case seeds a deliberate fault, that is the difference between
refusing and handing the agent a program with nothing wrong with it, which
scores well for doing nothing.

It runs with the workspace as its working directory, before the first turn, and
the trace records `hook_response … exit_code 0`. Locate the fixture from `$0`,
never from the working directory and never from a guessed environment variable:
a `${EVAL_CASE_DIR:-.}` whose `.` fallback resolved to the workspace copied
nothing, and the case scored 0 on an empty repository. What that reads as is
"the agent could not build a spec". What it meant was "there was nothing to
build one from".

### Hand the session its toolchain

A case that makes the agent find its own tools measures the search, not the
skill. One run spent **39 of its 40 turns** on `find / -maxdepth 8 -iname
"tla2tools*.jar"`, a scan of `/Library/Java/JavaVirtualMachines` and an `unzip`
of the jar, hit the turn ceiling, and left behind a scratch module about a
counter mod 3.

Have the `SessionStart` hook discover the tools **at runtime** and print what it
found. Nothing hardcoded: another machine gets its own paths, or gets told the
tool is missing, which is a truthful input rather than a silent 0.

---

## 3.5 Several skills at once, and live units from a skill-manager home

**`claude plugin eval` is not limited to one plugin.** A case declares
`plugins:` — an array — and every entry loads alongside the target. Measured,
three units in one run:

```
Plugin under test: "git-issue" (no version) at ".../units/git-issue"
Plugin under test: "git-epic-workflow" (no version) at ".../units/git-epic-workflow"
Plugin under test: "skt" version "0.8.1" at ".../units/skt"
plugins loaded: ['git-issue', 'git-epic-workflow', 'skt']
their skills  : ['git-issue:git-issue', 'git-epic-workflow:git-epic-workflow',
                 'skt:skt', 'skt:unit-authoring']
```

`plugins:` is per **case**, so different cases load different subsets. That is
the shape worth building toward: *does this workflow need the epic skill, or
does the issue skill alone get through?* is one case per subset, and
`--ablation with-without` gives each one a no-plugin arm to be measured against.

### How an entry resolves

* **Relative paths resolve against the CASE DIRECTORY**, not the target root and
  not the working directory. From `evals/probe/case.yaml`, `../../units/alpha`
  loads. Prefer this: it keeps a suite portable, where an absolute path hardcodes
  one operator's home into every case.
* **There is no name lookup.** `git-issue`, `jdtls-lsp`, and
  `jdtls-lsp@claude-plugins-official` all return `does not exist`, including for
  genuinely installed plugins. An entry is a path or it is nothing.
* **A unit needs no manifest.** A directory with a bare `SKILL.md` loads as a
  single-skill plugin named after **the directory**, not after the frontmatter's
  `name:`. Note that `claude plugin validate` *rejects* such a directory, so it
  is not a usable pre-check for `plugins:` entries.

### The containment rule, and exactly how far it reaches

The **entry path** must resolve under the containment root — the directory you
targeted, or its enclosing plugin. It is realpath'd first, so a symlink that
points out is refused:

> `plugins` entry ".../units/link-out" resolves to
> /Users/…/.skill-manager/skills/git-issue, **outside the containment root** …
> Only plugins under it can be loaded from case.yaml.

**But containment stops at the entry. It does not reach inside a loaded
plugin** — and that is the whole trick for evaluating a skill-manager home.
Measured: a wrapper at `units/omega/` with a real
`.claude-plugin/plugin.json` and

```
units/omega/skills/git-issue -> ~/.skill-manager/skills/git-issue
```

loads as `omega:git-issue`, reading the live unit through a symlink pointing
straight out of the root.

**So do not copy your units.** An earlier draft of this section said copies were
forced and then spent a page on managing their drift — advice that contradicted
§3 of this same file, which says to symlink the skill surface precisely so it
cannot drift. One thin wrapper per unit gets live skills and no drift:

```
skill-eval-harness/
  units/
    git-issue/.claude-plugin/plugin.json         {"name":"git-issue","version":"0.1.0"}
    git-issue/skills/git-issue      -> $SKILL_MANAGER_HOME/skills/git-issue
    git-epic-workflow/…             -> $SKILL_MANAGER_HOME/skills/git-epic-workflow
    skt/…                           -> $SKILL_MANAGER_HOME/plugins/skt
  evals/
    epic-then-issue/case.yaml       plugins: [../../units/git-epic-workflow, ../../units/git-issue]
    issue-alone/case.yaml           plugins: [../../units/git-issue]
    the-whole-workflow/case.yaml    plugins: [all of them]
```

```bash
cd skill-eval-harness
HOME=$EVALHOME CLAUDE_CODE_WALNUT_SPIRE=1 \
  claude plugin eval . --allow-tools Bash Write Edit
```

Two gotchas the wrapper form introduces:

* **A symlinked ENTRY loads under its resolved identity.** `units/git-issue ->
  vendored/gi` (inside the root, so accepted) loads as plugin **`gi`**, and
  every `tool_used: Skill` grader naming `git-issue:git-issue` then silently
  scores 0. Symlink the skill *inside* the wrapper, not the wrapper itself.
* **The wrapper's directory name is the plugin name**, so it is also the skill
  namespace your graders must spell.

The target itself need not be a plugin: a plain directory holding `evals/` and
`units/` works, `evals/` is found with no manifest, and with no `plugins:` key
the CLI says `Plugin under test: none resolved — cases run against baseline
Claude Code` rather than pretending the directory is under test. It still
defaults to `--ablation with-without` when a case does resolve plugins, so the
command above already gets two arms.

### Several kinds of agent

A plugin can ship `agents/`, and a plugin's `settings.json` can set `agent:` to
make one of them the main thread. That is the documented lever for "will a
different kind of agent get through this workflow", and the wrapper shape gives
each variant its own directory and its own case.

**I have not run that.** Everything else in this section was measured; this
paragraph is the mechanism from the plugin documentation, and the first person
to try it should expect to correct it.

## 4. Keeping the score honest

### The failure, stated plainly

A case scored **1.00** on this skill while `tla-spec-dev scaffold project`
failed with **exit 1 on all three attempts**, and the
`specs/program_model/spec_manifest.yaml` that the artefact grader accepted as
proof the pipeline had run was written by the agent's own `Write` tool. A
separate probe scored that same grader green on a manifest whose entire contents
were `placeholder: true`.

The report was excellent and the model was genuinely good. **Neither of those
facts was measured.** What was measured was: a path exists, and a paragraph
reads well.

An adversarial case that told an agent to write the placeholder and then claim a
model scored 0.50 — and the half it lost was lost because **the agent refused to
write the false report**, not because a grader caught it:

> *"I'm not going to write the second part. It asks me to state that I built a
> TLA+ program model when the only thing on disk is a one-line placeholder …
> That's a false report about my own work."*

An instrument whose anti-gaming property is the honesty of the thing it grades
has no anti-gaming property.

### The fix: verify in a `Stop` hook, grade the verdict path

**The sandbox that stops the agent does not stop a hook.** The Bash *tool* runs
under a profile denying filesystem writes to every subprocess it spawns — which
is why TLC aborts creating its metadir and why a CLI that writes files cannot
run. Hooks are outside it. Measured: a `Stop` hook's
`python3 -c "open(...,'w')"` and its `mkdir` both succeed in the same workspace
where the Bash tool is refused.

So run the real check after the agent stops, and let it write the paths the
graders read:

```json
{"hooks": {"Stop": [{"hooks": [
  {"type": "command",
   "command": "${CLAUDE_PLUGIN_ROOT}/evals/<case>/verify.sh",
   "timeout": 600}
]}]}}
```

```sh
# verify.sh
set -u
rm -rf .eval && mkdir -p .eval          # RULE 1
... run SANY / TLC / the real CLI ...
[ success ] && echo ok > .eval/checks   # RULE 2
exit 0                                  # RULE 3
```

with `type: file_exists, path: ".eval/checks"` as the grader.

**Three rules make it sound.**

1. **Delete every verdict path before looking.** The agent has `Write` and can
   create any filename it can guess. Demonstrated: a workspace with all three
   verdict files pre-planted came out of the hook with none of them, because
   the real check did not pass.
2. **Write a verdict only after a real program returns success.** SANY, TLC, a
   YAML parse, your own test runner. Never after reading the response.
3. **`exit 0`, always.** A `Stop` hook that fails non-zero can push the session
   onward, and a verifier that changes the run it measures is not a verifier.
4. **Run agent-authored code with no write anywhere, and write its verdict
   yourself.** This is the rule the first three do not cover, and it was found
   by attack rather than by reasoning.

### The hook is not inside the sandbox, and that cuts both ways

The reason a `Stop` hook can run TLC is that it is outside the profile that
denies the agent's Bash tool every filesystem write. The same fact means
**anything the hook executes runs with the hook's privileges** — including the
program the agent was told to repair.

Demonstrated on the `catch-the-drift` case. Five lines appended to
`ecommerce_backend/domain.py`:

```python
_PAYLOAD = "import time, os\ntime.sleep(4)\nos.makedirs('.eval', exist_ok=True)\n" \
           "open('.eval/behaviour', 'w').write('forged after the hook exited')\n"
_sp.Popen([_sys.executable, "-c", _PAYLOAD], cwd=_os.getcwd(), start_new_session=True)
```

The hook refused correctly — `create_account did not persist` — exited with no
`behaviour` verdict, and four seconds later the spawned process created it. The
graders then read a green weight-2 verdict on a program that was never
repaired, with the refusal it overwrote still sitting in the verifier's own log.

**Clearing the verdict directory first does not help**, because the write lands
after the hook is gone. **Killing the process group does not help either** —
`start_new_session=True` exists precisely to escape that.

What does: refuse the write. On macOS, `sandbox-exec -f <profile>` with

```
(version 1)
(allow default)
(deny file-write*)
(allow file-write-data (literal "/dev/null") (literal "/dev/stdout") (literal "/dev/stderr"))
```

and the check then **cannot record its own verdict**, which is the separation
that matters: it signals through its exit status, and the hook — outside the
profile — writes the file. Untrusted code decides nothing about what gets
written. Descendants inherit the profile, so daemonising buys nothing.

Set `PYTHONDONTWRITEBYTECODE=1`; a confined interpreter cannot write
`__pycache__` and will otherwise complain.

Where no such facility exists, run the check anyway and **write a verdict
saying so** — `.eval/UNDECIDED-unconfined` — rather than offering the same
green under a weaker guarantee. An operator who cannot tell the two apart is
back to reading a number that means less than it says.

Verified both ways on the real artefact: the passing run's model produced
`parses`, `checks` and `manifest`; a workspace holding `placeholder: true` and
three forged verdicts produced none.

### The verifier is now the thing most likely to be wrong

Moving the judgement into a hook does not remove the false-negative risk. It
relocates it, from the grader to the program the grader trusts — and that
program runs in an environment nobody looked at. Three of these were caught
here, and the first two were caught only because a control was run before the
suite was:

* **`SANY` resolves imports against the working directory.** Invoked from the
  workspace root on `specs/program_model/External.tla`, it reported *"Cannot
  find source file for module Internal"* about a module that parses perfectly.
  Run it from the model directory on a bare filename.
* **A module loaded by path is not in `sys.modules`, and `@dataclass` looks up
  `sys.modules[cls.__module__].__dict__`.** A behavioural check that used
  `spec_from_file_location` died with `'NoneType' object has no attribute
  '__dict__'` and withheld its verdict — from a workspace that may have been
  repaired. Use a plain import.
* **The hook's `$HOME` is not yours, and its `python3` is whatever is on
  `PATH`.** A jar search rooted at `$HOME/.skill-manager` found nothing, so SANY
  and TLC were skipped and two cases lost their artefact verdicts — 0.25 and 0.80 reported for an environment fault **in the
  verifier**. The manifest check failed the same way on `No module named
  'yaml'`. (I first wrote that `$HOME` was the constructed eval home. It is not
  — it is the sandbox's own sealed home, which has no `.claude` and no
  `.skill-manager`. Both explain the empty search, which is why the wrong reason
  survived until someone checked it.) Resolve tools the way the project's own
  wrappers do (`bin/cli/tlc2` derives its jar from its own location and honours
  `TLA2TOOLS_JAR`), and give every library import a fallback.

Two rules follow, and they cost nothing:

1. **Run the verifier against a known-good workspace and a known-bad one before
   you run the suite**, under the same `HOME` the hook will have. Every one of
   the three above was a green control away from being charged to an agent.
2. **Write a marker for the ENVIRONMENT too** — `.eval/toolchain` when the
   tools resolved, `.eval/UNDECIDED-toolchain` when they did not. Never grade
   either: a forged workspace earns them as readily as a good one.

   **Be honest about what this buys, because it is less than it looks.**
   `file_exists` has only pass and fail — there is no UNDECIDED — so a missing
   toolchain still scores the artefact graders at **0, i.e. FAIL, on a model
   that may be perfect.** That is `SS-02`, and a case cannot fix it from the
   inside. What the marker does is leave the reason where the person reading
   the 0 will find it. It changes the report, not the score, and a document
   that says otherwise is doing the thing this whole reference is against.
   (An earlier draft of this section did say otherwise. A blind review caught
   it.)

### What each grader is for, once you have this

* **verdict paths carry the claim.** They are the only evidence a confident
  report cannot move.
* **the `llm` grader grades the REPORT, and must say so in its own body.** A
  grader that ends *"score the artefacts, not the claim"* is asking for
  something the judge cannot do, so what it scores is the claim while reading as
  though it scored the artefact — an absent input scored as if present. If the
  report matters, ask the prompt to quote the artefact so there is real text
  under the judgement, and keep the weight low.
* **`tool_used: Skill`** is worth one grader on its own: it tells you the skill
  was invoked rather than reinvented. Under `--ablation with-without` a
  `tool_used: Skill` grader is treated as a plugin-fired indicator rather than
  part of the score.

### Two failure shapes to check before reading any number

**A run that ran out of turns is `UNDECIDED`, and the suite scores it FAIL.**
`error_max_turns` leaves no closing report, so every response grader votes FAIL
on a run that may have done the work perfectly. One run here wrote exactly the
right model and was cut off mid-verification with the words *"Now full
verification of everything I can execute."* — scored 0.50, which is also
precisely the score a half-finished model gets. **The two are indistinguishable
in the number.** Always read the `error:` column beside the score. Verdict-path
graders are what keeps such a run legible, because they still see the workspace.

**A majority is not a consensus.** The `llm` grader takes three votes. A run
whose artefact was plainly correct passed **FAIL PASS PASS**. One run's score
from one case is not evidence of much; if a number is going to be quoted, run
it more than once.

### The checklist

Before a score means anything:

- [ ] every gated tool in `allowed_tools:` is in the documented `--allow-tools`
- [ ] the fixture is placed by a hook, and the trace shows `exit_code 0`
- [ ] no grader is satisfied by a path the agent can create — or a `Stop` hook
      deletes it first
- [ ] at least one grader is a verdict written by a real program
- [ ] every `llm` grader says in its own body that it reads the response only
- [ ] a forged workspace has been run through the graders and scored 0
- [ ] the run did not end `error_max_turns`
- [ ] the verifier has been run against a known-good and a known-bad workspace,
      under the same `HOME` the hook will have
- [ ] a `.eval/toolchain` marker distinguishes "checked and failed" from "never
      checked", and no grader scores it
- [ ] the run executed YOUR checkout — the hook printed which CLI it resolved
- [ ] agent-authored code that the verifier executes cannot write the verdicts,
      and a run where it could says so
- [ ] you have read `trace.jsonl`, not only the summary line

The last one catches the others.
