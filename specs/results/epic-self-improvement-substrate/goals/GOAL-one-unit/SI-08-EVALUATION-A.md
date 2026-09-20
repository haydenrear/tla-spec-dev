# `GOAL-one-unit` — Evaluation A (SI-08), frozen reading

**Measured 2026-09-20 at base `2131cdad`, worktree `../wt-341-evaluation`.**
**This is Evaluation A. SI-23 re-reads this goal beside its six; these numbers are
the counterfactual half of every clause in that comparison.**

> **Statement.** The substrate installs, syncs and improves as one plugin rather
> than seven separately versioned units.
>
> **Baseline (b7a7d203).** 6 units across 6 repositories (spec-double-compiler +
> the five workflow skills), each installed in root, project and every worktree
> home.

**The target is quoted verbatim below and was not edited.** Clause 1 names
*"root or project home"*, and the two homes disagree, so the clause is reported
NOT MET with the split shown rather than reported on the project home alone.

---

## Clause 1 — "one installed unit for this substrate and zero standalone copies of the five migrated skills in root or project home"

### VERDICT: **NOT MET** — met in the project home, not met in the root home.

Instrument: `skt status` / `skt status --json` in each home, plus a direct sweep
of `<home>/skills/` and `<home>/installed/*.json`. The sweep asserts its own
population before reporting (`specs/results/epic-self-improvement-substrate/tickets/SI-08/home-sweep.json`).

The plugin contains **8** skills, not five — the five workflow skills plus
`git-integration-repo` and `plugin-repository` (nested by SI-12) and
`spec-double-2` (renamed from `spec-double-compiler` by SI-01):

```
discovery  git-epic-workflow  git-integration-repo  git-issue
git-issue-workflow  plugin-repository  spec-double-2  test-graph
```

The duplicate sweep tested all 8 names **plus** the old spelling
`spec-double-compiler`, against both homes:

| home | skill dirs swept | install records swept | substrate dirs | substrate records | plugin installed |
|---|---|---|---|---|---|
| **project** (`tla-spec-dev/.skill-manager`) | 10 | 33 | **0** | **0** | **yes** |
| **root** (`~/.skill-manager`) | 18 | 48 | **8** | **8** | **no** |

- **Project home: MET.** 20 installed units, `tla-spec-dev` plugin present,
  zero standalone directory copies, zero standalone install records.
- **Root home: NOT MET.** All eight substrate skills are still installed
  standalone — as directories *and* as install records — and the plugin is not
  installed there at all. The baseline condition is unchanged in the root home.

**The root home was measured and deliberately not changed** (work order rule 8:
never modify the operator's root home). Closing this clause is an operator
action, not a ticket action.

**Non-vacuity.** The sweep asserts `len(contained) == 8` and refuses a home whose
install-record list is empty, so a mis-resolved path fails loudly instead of
reporting a clean zero. The root home's 8 hits prove the detector fires; the
project home's 0 is therefore a measurement and not a silent miss.

### A correction to the state handed to this ticket

The brief handed to this ticket said the project home was refreshed to the epic
tip at plugin `gitHash c27e40b5`. **Measured, the install record reads
`c8dc064a`:**

```
"gitHash" : "c8dc064accf2ea4c6aa99be0d6157cbc4ec1fbf6",
"gitRef"  : "epic/self-improvement-substrate",
"installedAt" : "2026-09-20T16:34:12.140604Z"
```

`c8dc064a` is an ancestor of the base `2131cdad`, **one commit behind it**, and
`skt check` in the project home says so: *"new version available for
tla-spec-dev"*. The refresh happened; it landed one commit short of the tip.
The 8-contained-skills and 0-duplicates half of the handed state reproduced
exactly.

---

## Clause 2 — "every listed graph and eval case green on the new layout"

### VERDICT: **SPLIT — graphs MET; eval cases UNDECIDED (not red).**

**Graphs: 3 of 3 green**, run through the skill runner
`python3 skills/test-graph/scripts/run.py <graph>`:

| graph | result | steps |
|---|---|---|
| `specWorkflow` | **BUILD SUCCESSFUL** (rc 0), 1m20s | see `graphs/` |
| `cliWorkflow` | **BUILD SUCCESSFUL** (rc 0), 10s | 2 steps, both green |
| `effectProviderExamples` | **BUILD SUCCESSFUL** (rc 0), 1m11s | see `graphs/` |

(The bare `cd test_graph && ./gradlew` path is not the instrument and was not
used.)

**Eval cases: UNDECIDED, and the reason is that the population does not exist in
the shape the target assumes.** The target says "both eval cases"; the harness
field says "the plugin's own eval cases (SI-10)". Measured at this base:

- `examples/agent_integration/eval-plugin/` **does not exist** — SI-15 moved the
  suite. The two-case population the target names has no referent at this tip.
- The suite is now `evals/`, holding **61** cases (`find evals -name case.yaml`
  = 61), and **none of the 61 has ever been scored**.
- **6 of the 61 are UNDECIDED by construction** (`SI-15-DF-05`): they need a
  ~41,000-entry branched home and `claude plugin eval` refuses a plugin
  directory over 20,000 entries. They are not failures and must not be scored 0.

This clause is **UNDECIDED, not red.** Nothing measured says the layout broke an
eval case; what is true is that no eval case has been scored on either layout,
so there is no before and no after. See `../GOAL-pinned-eval-toolchain/` for the
one case this ticket attempted and what it cost.

**Trap checked and clean.** All 61 cases declare **zero** `plugins:` blocks
(`grep -rln "^plugins:" evals --include=case.yaml` → 0). This matters because a
case declaring `plugins:` silently loses the target plugin's hooks while *both
arms still score 1.00* (`SI-14-DF-01`) — the score is blind to it.

---

## Clause 3 — "that unit is change-managed — a git source, no NEEDS_GIT_MIGRATION, and `skt sync` able to update it"

### VERDICT: **MET, with one sub-part verified by detection rather than by execution.**

| sub-part | evidence | verdict |
|---|---|---|
| a git source | install record `"installSource": "GIT"`, `"kind": "GIT"`, origin `https://github.com/haydenrear/tla-spec-dev.git`, `"errors": [ ]`; `skt status --json` reports `change_managed: true` | **MET** |
| no `NEEDS_GIT_MIGRATION` | `grep -rl NEEDS_GIT_MIGRATION <project home>/installed` → **no hits** | **MET** |
| `skt sync` able to update it | `skt check` detects and names the update: *"new version available for tla-spec-dev — pull with: `skt sync tla-spec-dev`"* | **MET by detection** |

**The sync was NOT executed and this is deliberate.** Running it would mutate the
project home in the middle of the measurement that reads that home, and the work
order forbids syncing into the project home (the epic agent reconciles homes in
serial at wave close). So the claim this clause supports is *"`skt sync` resolves
the unit, sees a newer commit and offers the update"* — which is what was
measured — and **not** *"the update was applied and worked"*, which was not.

Note also: `skt sync` on this project home exits **11** on two deliberately
malformed eval fixtures (`EA-DF-01`). That is a known, filed, fixture-shaped
failure and **not** a broken home — the front door works, `skt status` reads, and
all four CLIs resolve. It was not treated as a reinstall trigger.

---

## Summary

| clause | verdict |
|---|---|
| 1 — one unit, zero standalone copies in root **or** project | **NOT MET** (project met, root not met: 8 standalone copies, no plugin) |
| 2 — every listed graph and eval case green | **SPLIT**: graphs **3/3 MET**; eval cases **UNDECIDED** (61 cases, 0 ever scored, 6 undecidable by construction; the named two-case population no longer exists) |
| 3 — change-managed unit | **MET** (sync verified by detection, not execution) |
