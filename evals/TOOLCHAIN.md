# The curated home: every unit, and what names it

SI-14. *Curating* the plugin home means **every unit in it is there because
something names it.** This page is the audit: one row per installed unit, with
what requires it, or a statement that nothing does.

**Nothing here was deleted.** A unit nobody can name is a *finding*, not a
quiet removal — and the project home is reconciled by the epic agent at wave
close, not by a ticket. The findings are filed in
`specs/results/deferred_findings_final.yaml` as `SI-14-DF-04` and `SI-14-DF-05`.

## Two homes, held apart

| home | what it is | this ticket |
|---|---|---|
| **root** `$HOME/.skill-manager` | the operator's live home, 27 units | **not touched, not read for resolution** |
| **project** `<repo>/.skill-manager` | this checkout's home, 25 units | audited below |
| **eval toolchain** `.toolchain/` | materialised from the lock, 2 units | curated *by construction* |

The third is the answer to the ticket's question. The eval toolchain is not a
home that accumulates; it is fetched from `evals/lib/toolchain.lock.toml` on
every run, and a unit is in it **if and only if the lock names it**. Nothing
gets in by accident because nothing gets in without a commit and a `role`.

## The method

A unit is *named* when a file that **declares a need** mentions it. Run
evidence does not count: `specs/results/**` and the agent-integration evidence
trees record what past runs happened to load, which is the accident this audit
exists to separate from intent. The sweep ran over **3,206 declaring files**
(of 25,230 tracked) with an explicit non-vacuity assertion on both the unit
population (25) and the file population.

Substring matching over-counts — `debugging` is also an English word — so every
low count below was read line by line rather than trusted.

## The audit

### Named by this repository (9)

| unit | kind | what names it |
|---|---|---|
| `tla-spec-dev` | plugin | **this repository is it** (`.claude-plugin/plugin.json`); 623 declaring files |
| `skt` | plugin | `skill-project.toml` `[plugins.skt]`; the front door the workflow skills tell agents to run; **pinned for eval use** |
| `spec-double-compiler` | skill | contained at `skills/spec-double-2/` — **also installed standalone** |
| `test-graph` | skill | contained at `skills/test-graph/`; owns the three graphs — **also installed standalone** |
| `git-issue-workflow` | skill | contained at `skills/git-issue-workflow/` — **also installed standalone** |
| `git-integration-repo` | skill | contained at `skills/git-integration-repo/` — **also installed standalone** |
| `plugin-repository` | skill | contained at `skills/plugin-repository/` — **also installed standalone** |
| `deploy-helm` | skill | named by `git-integration-repo`'s SKILL.md and the nested skills' own `skill-project.toml` as optional composition |
| `debugging` | skill | named by `README.md` — and named there precisely as the one that **stays outside** the bundle, because nothing in it depends on `debugging` |

**The five marked "also installed standalone" are `GOAL-one-unit` clause 1,
unmet.** The bundle contains them *and* the project home carries separate,
separately-versioned installs of the same five skills. Filed as `SI-14-DF-04`.

### Named only by another unit's descriptor, never by this repository (7)

These are real requirements — but the requirement lives in the **home**, not in
this repository. A harness descriptor installed alongside them names them:

| unit | kind | what names it |
|---|---|---|
| `code-reviewer` | harness | `harnesses/code-reviewer/harness.toml` |
| `repo-coder` | harness | `harnesses/repo-coder/harness.toml`, and `live-swarm-agent`'s |
| `repo-tester` | harness | `harnesses/repo-tester/harness.toml` |
| `run-tracer` | harness | `harnesses/run-tracer/harness.toml` |
| `live-swarm-agent` | harness | `harnesses/live-swarm-agent/harness.toml` |
| `tracer-agent` | skill | `live-swarm-agent/harness.toml` |
| `slm-agent` | skill | `live-swarm-agent/harness.toml` |

**Nothing in this repository asks for the swarm/tracer harness bundle**, and no
eval case loads any of them. They are coherent as a group and unrelated to this
loop. The honest verdict is *named, but not by us*.

### Named incidentally — a comment or a skip message, not a requirement (4)

| unit | the single mention |
|---|---|
| `acp-cdc-ai-python` | a `pytest.skip` message in a vendored test-graph SDK test |
| `tracing-observability` | one comment inside `git-issue-workflow`'s bootstrap script |
| `hyper-experiments` | comments and a worked example in two other skills' docs |
| `hyper-experiments-finance` | a test fixture name and a migration table in test-graph's scripts |

A mention in a comment is not a declaration of need. None is required to run a
graph, a case, or the CLI.

### Named by nothing at all (5)

`andrej-karpathy-skills` (plugin) · `cdc-agent-substrate-plugin` (plugin) ·
`doc-repo-devops` (doc-repo) · `llm-wiki` (skill) · `vision-toolbelt-skill`
(skill)

Zero declaring files. Zero harness descriptors. Zero eval cases. These are the
units the ticket's phrase "present by accident" describes exactly. Filed as
`SI-14-DF-05` **as a finding, not a deletion.**

## What an eval actually loads today

Worth stating plainly, because the audit above is about the ambient home and an
eval run does not use it:

* **`tla-spec-dev`** — the staged view of this checkout; the plugin under test.
* **`skt` at the pinned commit** — materialised, verified, staged into the view
  and recorded. **Not loaded through `plugins:`** (see `evals/README.md`, "What
  is not yet wired"), so today it is present and recorded rather than exercised.
* **`skill-manager` at the pinned commit** — reached by PATH through
  `evals/bin/skill-manager`, which is what makes the epic branch's CLI the one
  under test.

Everything else in either home is **absent from the run by construction**: the
staged view excludes `.skill-manager` entirely, so no ambient home reaches an
eval. That is why curating for eval use is a matter of the lock, and why the 16
units above are a finding about the home rather than a defect in the suite.
