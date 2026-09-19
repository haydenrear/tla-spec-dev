# Wave 6 review — epic/self-improvement-substrate

Range: `faf0aa33` → PR #364 (`2dd5bada`), **unmerged**. One ticket: SI-09 (#342),
progressive disclosure across eight cards.

**THIS WAVE IS A GATE.** `review_policy.milestones: [2, 4, 6]`. PR #364 is OPEN
and I have not merged it. Wave 7 does not dispatch, and this PR does not land,
without the owner's decision.

---

## Block 1 — Model delta applied

**None owed.** Files under `specs/` outside `results/` touched by SI-09: **0**.
No TLA+ action, state or invariant change was proposed; the plan block declares
none. `specs/tickets/SI-09/`, `specs/current`, `specs/desired_program_model` and
`specs/program_model` are untouched by the branch.

## Block 2 — Anchors placed

**None placed.** All three findings are `UNMODELED/` — two are epic-harness
defects (one of them mine) and one is a goal-reachability question. None sat
inside a `TlaSpecDevCli` action. The matrix is unchanged.

## Block 3 — Improvement-card row

**No round run.** Wave 6 is a single implementation ticket; scoring it here would
add a row that decides nothing and consume budget SI-08 needs. Recorded for
SI-08: PR #364 would score high on I5 — it declares four things it could not
verify, including the one that matters most (*"no check proves an instruction
survived the two full rewrites"*), and it named the unreachable target rather
than hitting the number by deleting content.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| `SI-12-DF-01`, four prose sites naming a retired standalone rung | **applied** — all four fixed; it also caught that `provision.md` mis-attributed `skill-homes.md` to `git-integration-repo` when it is `git-issue-workflow`'s own |
| one `skill-manager.toml` comment, **outside its conflict keys** | **applied, disclosed** — I read the diff: a one-line comment repointing the fan-out path to the plugin rung. Same class as DF-01, correctly surfaced rather than smuggled |
| `SI-12-DF-03` (widen the layout guard) | **declined** — `tests/` not in its keys. Correct; widening it here would have turned pre-existing lines red inside the ticket whose claim is "no new failures by name" |
| two "standalone-only rung" hits its own sweep flagged in scripts | **declined after verification** — both are correct two-rung constructs its line-based grep could not see. **It did not "fix" working code**, which is the right instinct |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** SI-09 made no edit to an epic-owned workspace. Third
consecutive wave clean on this debt.

---

## The goal: one clause met, one missed, and the miss is honest

Measured by me with the pinned instrument (frontmatter stripped), **not** the
agent's numbers taken on trust. The control holds: `spec-double-2` measures 1,839
at base, exactly the kickoff baseline table.

| | base | branch | target |
|---|---|---|---|
| descriptions, 8 cards | 1,212 | **594** | ≤ 600 ✅ |
| card bodies, 8 cards | 20,241 | **11,730** | — |
| cards over 1,500 words | 8 of 8 | **2 of 8** | 0 ❌ |

`git-epic-workflow` **1,820** and `git-issue-workflow` **1,775** miss the clause.
Filed as `SI-09-DF-03` for the owner rather than closed by deletion. I read both
cards' structure: what remains is Load-bearing rules / Preconditions / Scheduling
model / Operating flow / Boundaries / Reference map — the rationale is already
gone. Closing the gap means removing rules or pushing *instructions* behind
links, which is what the goal's own wording forbids. **Both are still 61% and 58%
smaller than at kickoff.** This is an owner decision, and it is the right one to
put in front of you rather than resolve quietly.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| 0 new failures | failure **NAMES**, suite run by me on the branch | 10 → 10, **same ten names** |
| the +6 passed | traced to source | **not SI-09's** — `specs/tickets/SI-09/` contributes 3 YAML files to two globbing tests (3+3); that is **my** scaffold commit |
| word counts | re-measured, pinned instrument, all 8 cards | **reproduce exactly**, 11,730 |
| descriptions ≤ 600 | frontmatter parsed per card | **594**, met with margin |
| territory | file list vs conflict keys | 7 outside, 5 its own evidence, 1 backlog, 1 disclosed TOML; **0 `specs/` outside `results/`** |
| backlog delta | count + parse + id scan | 66 → **69**, 3 new ids |
| moved text landed | reference page word deltas | 4 new pages (653/268/1,229/614); `worktrees.md` 3,982 → 4,515; `worktree-lifecycle.md` 3,066 → 3,869 |
| the append-not-void claim | searched the destination | **holds** — `## The exit codes `wt new` refuses with` with Exit 3 / Exit 7 now present; base had no such section |
| shared section heading survives | grep across SKILL.md **and** references/ | **4 citing files**, heading real at line 74 |

## My sweep was wrong twice; the agent's was right

I ran an independent broken-link sweep and it reported **7 broken citations**.
**All seven were false alarms of my own making**, and the correction matters more
than the finding:

- My first attempt matched only markdown `](path.md)` links and checked **7** of
  them; the cards cite references as backticked paths. Near-vacuous despite
  carrying a non-vacuity assert — *the assert fired on the wrong population.*
- My second attempt found 146 citations and flagged 7. Six explicitly **name
  their owning skill** (`spec-double-2 `references/ai_retrieval.md``,
  `` `git-issue-workflow`'s `references/skill-homes.md` ``), and every target
  exists there. I resolved them against the citing skill's own directory —
  exactly the false-alarm mode SI-09 said it designed its resolver around.
- The seventh, `plugin-repository` → `references/plugins.md`, is a **cross-unit
  import from the `skt` plugin**, declared `unit: skt` in frontmatter, present at
  `.skill-manager/plugins/skt/references/plugins.md`, and **identical at base**.

SI-09's 156-link sweep with per-skill attribution was the correct instrument.
**A non-vacuity assert does not save a check that is scanning the wrong thing** —
that is a sharper version of the lesson this epic has been filing for three
waves, and I am the one who just demonstrated it.

## `SI-09-DF-01` is MY defect, and it is the most useful finding of the wave

The assignment I rendered declared `base_sha: faf0aa33`. I then committed the
ticket workspace at `b0e6b54c`. **Confirmed by me:** `specs/tickets/SI-09/` has
**0 files at `faf0aa33`** and 29 at `b0e6b54c`. So I dispatched an agent to a base
that did not contain the workspace its own declared spec-unit command needs.

It fast-forwarded one commit — a strict descendant with no diff of its own — and
**told me**, rather than silently working from a different base. Its proposed
dispatch-time assert is right and I should adopt it before wave 7:
`git ls-tree -r <base_sha> -- specs/tickets/<id>/` must be non-empty.

Root cause is ordering: I re-render assignments *then* scaffold, when scaffolding
must come first. Three waves I got away with it because the workspace already
existed.

`SI-09-DF-02`: `skt ticket new` honours `--path` but derives the branch from the
ticket id, producing `feature/SI-09` instead of the declared
`feature/342-progressive-disclosure`. Renamed before any commit. **Four agents
this epic would have hit this**; it is upstream in `skt`.

## What the owner is being asked to decide

1. **Merge PR #364 or not.** My recommendation: **merge.** The goal's
   description clause is met, bodies fell 42%, no instruction was deleted, no new
   failures by name, territory clean.
2. **`SI-09-DF-03` — the two cards at 1,820 and 1,775.** Accept them as the
   floor, or direct a further cut knowing it removes instruction. I recommend
   accepting and letting SI-08 record the clause as partially met.
3. **DCO** fails on #364 as on every PR here. Unchanged, still yours.

## Where the bugs probably are

1. **No check proves an instruction survived the rewrite.** SI-09 said so itself.
   Links resolve and headings exist, but rule-level survival across two full
   rewrites is unautomated. This is the likeliest place for a real defect.
2. `tests/` assert **literal prose** in `spec-double-2/SKILL.md`; a reflow that
   breaks an asserted phrase across newlines fails them. SI-09 caught this before
   any test ran; a human editor probably would not.
3. The wide-lane budget clause (`Bash ≤ 4`) is **undecided** — SI-09 did not run
   it, and said so. It remains SI-08's.

## Suggested next steps

**Wave 7 is SI-13 (#360)** — and I have a head start for it that changes its
remedy. I traced `SI-12-DF-05` to its cause: `build-logic` is **deliberately**
untracked. Commit `175f5c7c` deleted the 24 tracked files and added the ignore
rule together, because those paths were tracked symlinks holding one developer's
absolute home path. They became *managed provider bindings*, with
`provider-bindings.json` as the committed record. **So "track it" would restore
the exact defect that commit fixed.** The real remedy already exists:
`skills/test-graph/scripts/prepare-bindings.py` materialises the links, takes no
required arguments, and nothing in the ticket front door runs it. SI-13's task is
to put one existing command into the front door, not to decide whether to track a
build directory.

**Deferred findings: 69 rows.** `per_ticket_backlog` still unadopted. Waves 5 and
6 were single tickets so it cost nothing again — but SI-08 files against **eight**
goals into this one file, and that is the run where it collides.
