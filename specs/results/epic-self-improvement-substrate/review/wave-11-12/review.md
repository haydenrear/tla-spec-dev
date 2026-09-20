# Waves 11–12 review — the substrate becomes one plugin

Range: `308d2732` → `7e180ea2`. Two tickets: SI-16 (#365, PR #378) and SI-17
(#366, PR #379), both merged. 211 files, `+34,527 / −399` — most of it skt's
own history arriving by subtree.

**This is the wave where the epic's title goal became physically true.** The
substrate now installs as one plugin. Whether it *holds* is SI-23's to decide,
not mine.

---

## Block 1 — Model delta applied

**None owed.** Neither ticket touched TLA+. `specs/` changes in the range are
entirely under `specs/results/`, `specs/tickets/SI-16|SI-17/` (scaffolds) and
`specs/desired_program_model/ticket_plan.yaml` (plan revision 5, status
updates). No action, state or invariant moved, so no TLC re-check is owed.

## Block 2 — Anchors placed

**None placed.** All ten findings across the two tickets are harness, manifest
or instrument defects, attributable `UNMODELED/`.

## Block 3 — Improvement-card row

**No round run.** Neither ticket is an evaluation. The card next runs at SI-23.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| `parse_simple_yaml` cannot parse `\|` literal blocks | **applied by the epic agent** (`a9e3c0da`) — root cause, so SI-17's file needed no edit |
| `skills/skt/skill-project.toml` truncated to zero tables | **applied by the epic agent** (`a9e3c0da`) — SI-16's breakage, found by SI-17 |
| `SI-16-DF-04`: contained skills still declared in constituents | **applied by the epic agent** (`8fbe91a2`) — 16 declarations, not the 8 filed |
| `--only` could not reach an OPT-IN graph | **applied** (`d4c91275`) |
| the cumulative backlog has no `target` field | **applied** (`769b723d`) — 7 rows, deliberately not 79 |
| `SI-16-DF-02` eval hooks overwrite, `SI-16-DF-03` retired pin | **deferred, correctly** — both move eval scores, and neither ticket was about evals |
| `SI-17-DF-03` no per-skill CI has ever run | **proposed, not applied** — repo-wide CI is outside a ticket's conflict keys |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Eighth consecutive wave clean.

---

## What actually landed

**SI-16 is the first plugin→plugin migration in this epic**, and the framing I
first briefed was wrong. SI-02 and SI-12 nested *skills*; skt is a *plugin*, so
absorbing it meant demoting it to a contained skill while lifting its
plugin-level surface onto the carrier. Hooks travelled **up** to the plugin
root (which had never shipped a hook), `src/` travelled **down** into
`skills/skt/`. `${CLAUDE_PLUGIN_ROOT}` survived while silently coming to mean
something else.

It subtreed from `b7ea313a` — the open PR haydenrear/skt#54 — rather than
`main`, so the two-rung front-door fix arrived with it instead of the ninth
recurrence of a defect this epic keeps tripping over.

**SI-17 moved `wt` into `skills/skt/`**, four paths not the three I listed; it
found a test suite whose only subject was `wt.py` and moved that too, flagging
the scope correction rather than doing it silently. The real work was what
*didn't* move: `wt` gained a three-rung resolver for the `lib.sh` and
`new-change.sh`/`close-change.sh` that stayed in git-issue-workflow.

## Both ticket agents corrected me, and both were right

**The pinned card control is stale and I kept briefing it.** SI-17 checked
SI-09's own evidence: 1,839 is `spec-double-2`'s **pre-cut** body count, and
SI-09 then cut that very card to **1,499**. It stopped being a control the
moment it became a subject. Measured live: `spec-double-2` = 1499,
`git-issue` = 1499. Anyone measuring against 1,839 concludes every card shrank
~340 words when nothing moved. The stale number was in my memory and my
briefs, **not** in the plan — `git grep 1839` finds no such assertion in the
tracked tree.

**My "exactly 10 `CLAUDE_PLUGIN_ROOT` references" was wrong in both
directions.** SI-16 found the 2 in `hooks/hooks.json` must *not* change — they
address `${CLAUDE_PLUGIN_ROOT}/hooks/`, still correct once hooks sit at the
carrier root — and that the count *missed* one: `test_artifact_notify.py:491`
resolved a hook path that never spells the env var, so no grep for it could
see it. Counting a path migration by one variable's name undercounts it.

**SI-16 also caught a failure every cheap instrument called green.** Its first
fresh-home install cloned a *second, standalone* skt because
`git-epic-workflow/skill-manager.toml` still carried a hard
`skill_references` coord; that copy's installer ran second and overwrote the
wrapper with the pre-demotion path. Unit suites, hook log and manifest checks
all passed while the shipped artifact was wrong.

## Two defects of mine, fixed at the root

**`_BLOCK_INDICATORS` declared six indicators; both dispatch sites tested
three.** So every `\|` literal block fell through and kept its indicator as
text — `k: \|` parsed to `'\| hello world'` where PyYAML gives `'hello\nworld\n'`.
A constant advertising support the code never implemented, unexercised until
SI-17 wrote the epic's first `\|` scalar. Fixed by making both sites read the
constant, so they cannot drift again.

**SI-16 commented skt's `[project]` table out of existence** while rewriting
that file's header — 4,352 bytes to 659, still parsing because comments are
valid TOML. `check_units` caught it: `declares no [project] table`.

## The sweep was wider than the finding

`SI-16-DF-04` filed 8 declarations across 4 constituents. Measured: **16
across 7**. `discovery` and `git-integration-repo` were not in its list, and
discovery carried two beyond skt — including `[skills.spec-double-compiler]`
pointing at the repository now being archived. Every one named a skill the
bundle contains; `plugin-repository`'s `[skills.skt]` declared a *plugin as a
skill*, which `project resolve` refuses outright.

After the sweep: **zero live `source =` lines** of any kind in those manifests.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| SI-16: 0 new failures | failure **NAMES**, merged tip | 10 / 1710, the known ten |
| SI-17: 0 new failures | failure **NAMES**, on a worktree at `569a472c` | 11 → the known ten + one |
| that one extra | ran the single test | `\|` literal block, **root-caused and fixed** |
| merge kept both sides | `merge-base --is-ancestor`, both parents | `d692d6a1` = `a9e3c0da` + `569a472c` |
| plugin main content | **fresh clone**, not a local ref | 11 skills, `wt` at new path, old path gone |
| skt manifest | `tomllib` + `check_units` | parses, `[project]`, problems 3 → 2 |
| sweep deleted only declarations | diff audit for non-declaration deletions | **empty** |
| comment prose preserved | per-file `deploy-cdc` counts before/after | identical |
| blast radius | read each row individually | **7**, not 21 |

## My verification was the recurring defect again, and worse than usual

Five vacuous results in one wave, each of which *looked* like a finding:

- a `check_units` run against a path that doesn't exist, its error swallowed by
  a grep, reported as "no skt-related output"
- two more `check_units` runs killed by ambient `python3` 3.14 having no
  `yaml` — and my "negative control" printed the *same* traceback, proving only
  that neither ran
- a `grep -c` for hardcoded indicator triples that returned **0** because of a
  `\+` escaping bug — contradicting evidence I had read minutes earlier
- a `1839` search whose emptiness I nearly read as "not asserted anywhere"

Plus: the **zsh `:s` modifier** twice, the second time inside the very command
written to confirm the merge hadn't lost my work (it reported `[project]
table: 0`, i.e. "your fix was clobbered"); a full suite run against the **wrong
worktree** — the epic branch, which doesn't contain SI-17's moves; a `comm`
diff that listed all ten failures as "fixed" because its right-hand side was
empty; a stash list reported as "empty = clean" when `stash@{0}` exists; and
four extra suite failures I nearly attributed to the parser fix which were
**my own `sktHooks` build output** — 73,487 entries under `test_graph/build/`
that repo-walking tests were scanning.

Every one was caught by a non-vacuity control or a second look. **None was
caught by reading the output.**

## Suggested next steps

**Wave 13 is SI-24**, the root-home rebuild, and it is the epic agent's to
perform. `SI-08-DF-04` — *"GOAL-one-unit clause 1 is NOT MET in the root
home"* — is precisely what it closes.

Then the owner's validation sequence: test graphs, manual testing with bug
attribution, and the eval ladder. **Two eval defects must land before any
scored run**: `SI-16-DF-02` (the runner overwrites the plugin's now-real
`hooks.json`, so eval scores are not evidence about hooks) and `SI-16-DF-03`
(nesting silently retired the skt pin). And the staging itself is already
broken — measured at **28,603 entries against a 20,000 ceiling**, so a
full-suite run would be refused today.
