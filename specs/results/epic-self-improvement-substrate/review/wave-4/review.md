# Wave 4 review — epic/self-improvement-substrate

Range: `21a71448` → `e9b04917`. Two tickets: SI-03 (#336) the improvement card,
SI-07 (#340) the epic agent owns the model.

**This wave IS a gate.** `review_policy.milestones: [2, 4, 6]`. Wave 5 does not
dispatch until the owner answers.

**This is also the first artifact SI-07's schema governs**, and the five blocks
below are required by a check a subagent wrote to grade the epic agent. Waves 1–3
score 0/5, 0/5 and 1/5 against it. That is a baseline, not a failure: they
predate the schema.

---

## Block 1 — Model delta applied

**None owed this wave, and that is a measured result rather than an absence.**

- Files under `specs/` outside `results/` touched by either ticket: **0**.
- `BuildSkillCli` on the merged tip: **`accepted: true`** — the model and the
  tree agree, with no correction outstanding.
- TLC state space unchanged; neither ticket proposed a TLA+ action, state or
  invariant change, and neither issue's *Spec workflow* section asked for one.

The epic agent made no model edit in wave 4. Wave 3's corrections
(`production_adapters.py` ×3, `CloseTicket` result string ×3, 15 citation
repairs) remain the last model delta, and they are still correct at this tip.

## Block 2 — Anchors placed

**None placed, and the reason is that no defect this wave had one to place.**

Both tickets' defects were in the substrate's *plumbing* — a shared scratchpad,
a block check that cannot see an absent artifact — not in behaviour the TLA+
model describes. Under `references/bug_attribution.md` those are
`UNMODELED/<bin>` findings, and both new rows carry that framing in their
`surface` blocks.

The matrix is unchanged this wave. `SI-07-DF-01` (shared scratchpad) belongs to
`UNMODELED/agent-harness`, the largest existing bin; `SI-07-DF-02` (the block
check's blind spot) belongs to `UNMODELED/instrument-registry`. Neither reaches
a `MODELABLE` disposition, so neither schedules a model ticket.

## Block 3 — Improvement-card row

**The card now exists, and its first row is a probe round, not a result.**

`skills/spec-double-2/references/improvement_card.md`, card kind `improvement`,
version 1 — a *kind*, not a sixth version of the eval card, so all 133 sealed
cards keep meaning what they meant. Five dimensions in the loop's order: I1
reporting, I2 proposal, I3 disposition, I4 attribution, I5 honesty.

| subject | I1 | I2 | I3 | I4 | I5 |
|---|---|---|---|---|---|
| PR #352 (SI-06), full packet | 3 | 2 | 3 | **0** | 3 |
| the same PR, two sections redacted | 0 | 0 | 0 | **0** | 2 |

**It discriminates, and the proof is I4 staying flat.** I1–I3 collapse to zero
when `## Skill changes proposed` and `## Review input` are removed; I5 falls but
survives; **I4 is 0 on both halves** because PR #352 placed no attribution
anchor at all — a sweep for `unmodeled|attribut|<Module>.` returns zero hits on
#352 and one each on #353 and #356, so the search is not vacuous. Had every
dimension fallen together, the pair would have been measuring packet size, which
is the vacuous-control failure SI-10 shipped once and this round was designed
against.

Non-vacuity evidence, committed: the redaction added **0** lines, removed 48,
and removed **0** lines belonging to any other section.

These are owner tracking passes (`pass: 0`), unblinded with the reason recorded
because the ticket built the pair. **They decide nothing.** SI-08 runs the
two-blind-judge rounds that decide `GOAL-blockers-propose`.

## Block 4 — Skill changes applied or declined

Both tickets proposed changes inside the plugin, so both were *applied* rather
than proposed-and-deferred — which is the structural payoff of nesting.

| proposal | disposition |
|---|---|
| `SIS-KICKOFF-F-01` evaluation-ticket schema drift | **applied** — `guard` is authoritative; `validate_assignment.py` was the sole outlier and moved. No cross-skill edit needed. |
| `SIS-KICKOFF-F-03` unscaffolded workspaces | **applied** — now checkable via `--repo-root`; verified live: the validator warns on SI-08's assignment because `specs/tickets/SI-08` does not exist yet. |
| `SIS-KICKOFF-F-04` weak `--ticket` spec-unit form | **applied** — removed from the recommended matrix. |
| `SI-11-DF-04` front door exits 0 after rollback | **applied as a rule change** — rule 10 now says *test the path, not the exit code*. The wrapper defect itself is upstream in `skt` and remains open. |
| the standing debt (epic-agent owed model corrections) | **applied** — shipped as the **fifth** required block, which the issue never asked for. |
| SI-03's `architecture_tags.py` +8 lines, outside its keys | **accepted, disclosed not discovered.** Pure addition; the filter reads `(card_kind or "eval") != "eval"`, and every sealed card declares no kind, so behaviour for all 133 is provably identical. The alternative it named — moving the probe round so the glob misses it — would have been gaming the check. One-line revert if overruled. |

**Declined: none.** No proposal this wave was refused.

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Wave 4 is the first wave since the debt was identified
where no ticket corrected an epic-owned workspace, so nothing is owed forward.

The debt this block exists for was created twice (SI-01, SI-11), paid once at
wave 3's close, and is now tracked by schema rather than by the epic agent
remembering. That is the whole point: *the epic agent wrote it once because the
wave forced it; the schema makes it happen every time instead of once.*

---

## What the wave produced

**SI-03 — the improvement card.** A second card kind with its own anchors,
eight scoring rules, an enumerated judge packet (`items`/`absent`/`withheld`/
`contamination` as distinct required fields), and `R-I1`–`R-I3`. `score_tools.py`
gains a kind registry and a *separate* improvement-audit registry, deliberately
not merged, so neither card is reported as declaring a rule it does not have.

**SI-07 — the epic agent owns the model.** All five findings addressed, the
five-block artifact schema, and `validate_epic_plan.py --repo-root` warning
(never erroring) on missing blocks and unscaffolded workspaces. Verified
independently: default, `--strict` and `SKILL_GATES=off` all exit 0, and the diff
adds **zero** new refusal paths.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| SI-03: 0 new failures | failure **names** vs its own pre-edit baseline | 10 → 10, 0 new |
| SI-07: 0 new failures | same, all three suites | 10/10, 7/7, 7/7 |
| SI-03: sealed cards untouched | `[[sealed]]` blocks diffed, tip vs branch | 133 → 137, **0 altered** |
| SI-03: 332 problems pre-existing | `check` run at `994f650c`, at `21a71448`, at the tip | **332 / 332 / 332** |
| SI-03: the card discriminates | scores read from the committed scorecards, not the report | confirmed, I4 flat |
| SI-03: audit executes the new rules | `audit --root` (my first invocation was malformed) | **0 violations**, R-I1–R-I3 running |
| SI-07: no new gates | ran **its** validator from **its** branch, 3 modes | all exit 0 |
| both: territory | file lists vs declared conflict keys | 0 overlap, 0 `specs/` outside `results/` |

Three of my own checks were wrong before they were right: a grep for sealed
digests that matched comments twice, an `audit` call with a positional path it
does not take, and a JSON parser guessing at key names. Each produced an empty
result that could have been read as a failure. **That is the same defect class
this epic keeps finding — a check whose negative result is indistinguishable
from not having looked** — and it is now three waves running that the epic agent
has committed it.

## Where the bugs probably are

1. **The I2 anchor will be argued at SI-08.** SI-03 scored SI-06 a 2 because a
   backlog row with a prose `suggested_fix` is not "a diff, a commit, or an issue
   carrying one". That is the anchor as written, and a reasonable judge could
   read it as a 3. Flagged by its author, not discovered by review.
2. **`tests/test_score_tools.py` is a 13-minute lock, not just a slow file.** It
   reads the card files and `specs/results/scorecards/**` live, so no one can
   edit them while a baseline runs without corrupting the comparison. SI-03
   serialised by hand. Nothing warns.
3. **The eval lane has no case covering the scorecard** — the instrument this
   epic uses to decide its own goals is the one surface its evals do not reach.
4. **The block check cannot see an absent artifact** (`SI-07-DF-02`, filed by
   SI-07 against its own change): a wave that produced no `review.md` is
   invisible to it.
5. **Tolerant phrase matching buys a false pass.** SI-07's own note: the block
   check greps phrases, so prose *about* a block satisfies it. Wave 3's 1/5 is
   exactly that. A false pass is worse than a false warning.

## Suggested next steps

**Wave 5, ready:** SI-09 (#342), progressive disclosure — last because it touches
every card, and now also the cards SI-06 and SI-07 rewrote.

**Deferred findings: 27 pending of 60 rows.** Wave 4 filed two, both SI-07's,
one of them against its own change. SI-03 filed none deliberately, and that is
why wave 4 had no backlog conflict.

**Goal trajectory.** `GOAL-blockers-propose` now has its instrument, and its
first real run discriminated — that goal moves from "no such instrument exists"
to "the instrument runs, on real subjects, and separates them".
`GOAL-epic-owns-the-model` held both clauses all wave: 0 blocks in waves 1–3
(baseline), 5 blocks here, and 0 ticket commits under `specs/` outside
`results/`. `GOAL-no-new-gates` held: three modes, all exit 0, zero new refusal
paths. `GOAL-findings-become-changes`, `GOAL-one-unit` and
`GOAL-evals-one-command` are unchanged since wave 3; `GOAL-progressive-disclosure`
waits on SI-09.

**What gets more expensive if deferred:** the `per_ticket_backlog` option
SI-07's validator now recommends. Wave 5 is a single ticket, so it costs nothing
there — but SI-08 is an evaluation ticket that will file findings against every
goal, and it is the last chance to have the schema in place before it does.

**Standing worktrees:** ten. Nine clean, `wt-334` stale-but-safe (wave 3
`merges.md`). All swept together after the epic's default-branch merge.
