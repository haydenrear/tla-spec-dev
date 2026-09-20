# Wave 8 review — epic/self-improvement-substrate

Range: `cc3941d4` → `e367f027`. One ticket: SI-14 (#361), PR #374 merged.
Wave 8 is not a gate. Wave 9 (SI-15) may dispatch.

---

## Block 1 — Model delta applied

**None owed.** `specs/` files outside `results/` touched by SI-14: **0**. No
TLA+ action, state or invariant change; the ticket made no structural edit to
`desired/` and ran no `open ticket`, `close ticket` or `--accept-new`.

## Block 2 — Anchors placed

**None placed.** All five findings are eval-harness and home-curation defects,
attributed `UNMODELED/`. None sits inside a `TlaSpecDevCli` action.

## Block 3 — Improvement-card row

**No round run, and SI-14 is explicit that nothing here is evidence about any
skill:** *"No scored eval case was run at all."* Every run was a $0.00 load-only
probe or a $0.06 synthetic probe plugin. Recorded for SI-23: this PR would score
high on I5 — it lists five unverified claims including the one that undercuts its
own headline, and it found two defects in its own work before review.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| `plugin_evals.md` corrected on `scaffold_script` semantics | **applied** — $0.32 of probes; both our prior accounts were half wrong |
| `--max-cost-usd 0` as a free pre-check | **applied** to `plugin_evals.md` |
| `run.sh` `grant_args[@]: unbound variable` | **applied** — *pre-existing* bash 3.2 bug; any run selecting no cases crashed the runner |
| cache moved out of `evals/` | **applied** — its own sweep went red first: discovery was finding skill-manager's **56 case.yaml** files, which would have scored and billed as ours |
| load skt via `plugins:` | **declined, and correctly** — see below |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Fifth consecutive wave clean.

---

## SI-14-DF-01 is the finding of the wave, and I confirmed it

**A case that declares `plugins:` silently loses the target plugin's hooks.**
Four runs, $0.26. The hook marker fired **2 of 2** without `plugins:` and
**0 of 2** with it — and **both arms scored 1.00.**

That second fact is the important one. *The score is blind to the failure.* Every
fixture in this suite is placed by a `SessionStart` hook in `evals/lib/place.sh`,
so adding `plugins:` to any case here would hand the agent an empty workspace and
report it as a skill failure. SI-14 abandoned the `plugins:`-based design on that
evidence rather than shipping it, and said plainly that the pin therefore reaches
runs through PATH and the record — **not** through case plugin-loading. It does
not claim the loop is pinned end to end. That restraint is worth more than the
feature would have been.

## The shim works, demonstrated not asserted

```
PATH=evals/bin:$PATH  skill-manager --version
  skill-manager 0.28.1+g6ffacb88ff96
  build:  6ffacb88ff96 (detached)        <- skill-manager epic branch tip
brew copy, untouched:
  skill-manager 0.28.1
  build:  artifact 641625cd3baf ...      <- /opt/homebrew/Cellar
```

The CLI names its own commit, so the run record quotes the CLI's own account of
itself rather than an assertion about it. Exactly the owner's instruction: alias
for the eval environment, brew copy untouched.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| 0 new failures | failure **NAMES**, suite run by me on the merged tip | **10 failed / 1675 passed**, the known ten |
| the 11th baseline failure | reproduced, then bisected to my own commit | **mine** — see below |
| `plugins:` disables hooks | read the probe's own marker counts | **2/2 vs 0/2**, both scoring 1.00 |
| the shim | `--version` through `evals/bin` vs brew | epic tip vs `0.28.1`, brew untouched |
| territory | file list vs conflict keys | **0 `specs/` outside `results/`** |
| backlog delta | count both sides | 74 → **79** |
| graphs | run **through the skill runner** | three, all BUILD SUCCESSFUL |

## The 11th failure was mine, and SI-14 caught it because I got my own dispatch wrong

I told SI-14 the repository carries **10** known failures. Its baseline measured
**11**. The extra one was
`test_parse_simple_yaml_differential[specs/desired_program_model/ticket_plan.yaml]`
— and it was **my defect**, introduced in `cc3941d4` when I wrote the SI-14 shim
scope as three `- >-` **block-scalar list items** where every other entry in that
file is a quoted scalar. The repository's own `parse_simple_yaml` keeps the
literal `">- "` prefix; PyYAML strips it; the two disagree.

**PyYAML parses the file fine, which is why every check I ran was green** —
`--strict`, the DAG sweep, the goal-ownership audit, all clean at that commit and
three before it. The differential test is the only instrument that could see it,
and it was not one I was running. That is this epic's signature defect once more,
in my own hands: *a green check that does not cover the property you care about.*

Fixed at `11a77deb`; the merged tip measures 10.

## GOAL-one-unit clause 1 is not measurable from the project home as it stands

SI-12 reported clause 1 satisfied. SI-14 reports it unmet. **Both are honest, and
they measured different homes.** The project home's plugin install record reads
`gitHash df1f992a`, installed 2026-09-18 — a **wave-4-era tip, predating SI-12
entirely.** So that home carries a *six*-skill plugin, not the eight SI-12
nested, and still holds standalone copies SI-12 removed in its own worktree home.

The duplicate count differs by definition, and both figures are correct:

- **2** standalone *directories* that are also contained: `git-issue-workflow`,
  `test-graph`.
- **5** nested-in-repo skills that still hold an *install record*: those two plus
  `git-integration-repo`, `plugin-repository`, `spec-double-compiler`.
- Plus **6 ghost records** with no directory at all (`code-reviewer`,
  `doc-repo-devops`, `live-swarm-agent`, `repo-coder`, `repo-tester`,
  `run-tracer`).

**This is a result about the instrument, not about the goal.** SI-08 is scheduled
to *freeze* `GOAL-one-unit`, and it cannot honestly do so against a home pinned
to a stale install. Either the home is refreshed to the epic tip before SI-08
runs, or SI-08 records the clause as unmeasurable and says why. **Owner decision,
and it should be taken before wave 10.**

## Where the bugs probably are

1. `SI-14-DF-01` — upstream in the CLI, and it constrains every future case.
2. `SI-14-DF-03` — the staged view is at **17,370 of 20,000** entries, and
   `run.sh`'s header still claims 6,264. SI-15 moves **63 more cases** in. That
   ceiling is closer than the file says.
3. `SI-14-DF-05` — 16 of 25 home units are required by nothing this repo names;
   5 by nothing at all. Nothing deleted, correctly.
4. The pin covers skt and skill-manager. **Nothing yet proves a pinned ref
   changes a score**, because no scored case ran.

## Suggested next steps

**Wave 9 is SI-15 (#362)** — move skill-manager's 63 cases in. Two things from
this wave land directly on it: the 17,370-entry ceiling, and `SI-14-DF-01`
(no moved case may carry `plugins:`).

**Deferred findings: 79.** `per_ticket_backlog` still unadopted; SI-23 files
against six goals into this one file.
