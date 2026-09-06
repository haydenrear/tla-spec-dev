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

**This home is not hermetic, and you should know what it leaks.** Symlinking
`.claude` loads the operator's personal skills into every run — a passing run's
`init` event listed `deep-research`, `dataviz`, `code-review` and six others
beside the plugin under test. Anything those contribute is in your score and in
your baseline arm. Symlink the narrowest set that authenticates.

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

Place fixtures from a **`SessionStart` hook** in `hooks/hooks.json`:

```json
{"hooks": {"SessionStart": [{"hooks": [
  {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/evals/<case>/scaffold.sh"}
]}]}}
```

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

Verified both ways on the real artefact: the passing run's model produced
`parses`, `checks` and `manifest`; a workspace holding `placeholder: true` and
three forged verdicts produced none.

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
- [ ] you have read `trace.jsonl`, not only the summary line

The last one catches the others.
