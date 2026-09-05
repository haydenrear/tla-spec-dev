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
CLAUDE_CODE_WALNUT_SPIRE=1 claude plugin eval examples/agent_integration/eval-plugin \
    --allow-tools Bash --scaffold --runs 1
```

`--scaffold` runs each case's `scaffold_script` as you; it places the fixture
and makes the first commit. `--allow-tools Bash` is the operator grant — without
it the agent has read-only tools and cannot do the work.

The ablation arm is on by default: each case also runs **without** the plugin and
reports the delta. That is a control the hand-rolled harness never had.

## KNOWN BLOCKER on this machine, and it is not the suite

A Bash-granting run refuses:

> the Docker (`~/.docker`, `DOCKER_CONFIG`) credential store on this machine
> holds a symbolic link inside it, so the Bash sandbox cannot reliably exclude it

`~/.docker` holds **18 symlinks** — 7 in `bin/`, 11 in `cli-plugins/` — all of
them Docker Desktop's own CLI shims, none of them credentials. Measured:

* pointing `DOCKER_CONFIG` at a plain directory with zero symlinks **does not
  help**; the message is byte-identical, so the check reads `~/.docker`
  regardless of the override it names;
* overriding `HOME` so `~/.docker` resolves elsewhere **does fix it** -- and then
  the session cannot authenticate, even with `.claude`, `.claude.json` and the
  skt token symlinked in. `Not logged in - Please run /login`.

**The two requirements are mutually exclusive here**: the sandbox needs a `HOME`
whose `.docker` is plain, and authentication needs the real `HOME`. The remaining
lever is moving Docker Desktop's `bin/` and `cli-plugins/` out from under
`~/.docker`, which is a change to the machine, not to this suite.

Without the Bash grant the whole pipeline runs -- 13 turns, $0.24, both graders
scored, JSON written -- so what is blocked is the agent's ability to work, not
the harness.
