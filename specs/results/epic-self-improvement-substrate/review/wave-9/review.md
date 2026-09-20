# Wave 9 review — epic/self-improvement-substrate

Range: `06df2b70` → `1b8d4094` (+ corrections at `d27fc035`). One ticket:
SI-15 (#362), PR #375 merged. Wave 9 is not a gate; **wave 10 is SI-08, the
first evaluation.**

---

## Block 1 — Model delta applied

**None owed.** `specs/` files outside `results/` touched by SI-15: **0**. No
TLA+ action, state or invariant change; no `open ticket`, `close ticket` or
`--accept-new`.

## Block 2 — Anchors placed

**None placed.** All five findings are harness and tooling defects, attributed
`UNMODELED/`.

## Block 3 — Improvement-card row

**No round run, and SI-15 is explicit about why it cannot claim one:**
*"I did not execute the 61 cases. That is 61 billed agent runs. No score is
claimed."* It verified that cases load, declare no `plugins:`, match their
`EVAL_CASE` directory, and have an arm in both hooks — and stopped there.
Green/red per case belongs to SI-08.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| vendor `expect.py` into `evals/lib/checks/` | **applied** — self-tested on 3.9 and current python |
| `run.sh` stages the **pinned** skt's skills into the view | **applied** — 18 `w-skt`/`w-sm` cases load their subject at the pinned commit, serving `GOAL-pinned-eval-toolchain` |
| retire `units-template/` | **applied, and the reason is the finding** — it exists *only* to deliver hooks via `plugins:`, the mechanism wave 8 proved silently disables them. Moving it would re-import the defect. |
| retire `wide/` | **applied** — it *is* the second harness the goal names. `units-override.txt` machinery dies with it; **0 of 55** sources carried one, verified by `rglob` over the checkout. |
| `skt` exit-status / bootstrap resolution | **proposed upstream** — see below |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Sixth consecutive wave clean.

---

## The per-ticket backlog worked on its first use

Adopted at the wave-8/9 boundary, exercised immediately: SI-15 filed **5 rows to
`specs/results/deferred/SI-15.yaml`** and made **zero** changes to the cumulative
79-row file. No reconcile, no collision, nothing to merge by hand. Six waves of
deferral ended at the one boundary where it would have started to cost.

## SI-15 corrected two numbers I had been repeating

**1. The eval count is 55, not 63 — and my brief was self-contradictory.**
`find ... -name case.yaml` returns 63 only when generated copies under `build/`
are counted. I took the with-build figure at revision 3, called it sources, then
told SI-15 to *"count 63 sources, not build output"* — an instruction that cannot
be satisfied. It caught the contradiction instead of picking one.

Corrected in five places at `d27fc035`, **two of them goal baselines** that SI-08
and SI-23 measure against. A wrong baseline is worse than wrong prose: it is what
a later evaluation compares to, so it would have propagated into a verdict.

**2. The 17,370 entry-ceiling figure is not reproducible.** I relayed it from
`SI-14-DF-03` as fact and briefed it as *"the likeliest thing to bite you."*
SI-15 measured the view by replicating `run.sh`'s own tar-exclude list:

| | entries |
|---|---|
| before the move | 6,712 |
| toolchain staged | 6,848 |
| after 54 cases moved | 7,288 |
| **ceiling** | **20,000** |

Headroom **12,712**. The likely source of 17,370 is a count over `.toolchain/`
rather than the view — the pinned `skill-manager` checkout is 11,522 entries and
declares `stage_into_view = ""`, deliberately never staged. **Both numbers I gave
this ticket as measured facts were wrong**, and in both cases the agent
re-measured rather than trusting me.

## The front door is broken, and I broke it

**`SI-15-DF-04`, reproduced by me directly:**

```
skt ticket new … → rc=3
error: bootstrap-home.sh not found in this home; worktree rolled back
PATH ABSENT
```

`skt/ticket.py:150` resolves
`candidate = <home>/skills/git-issue-workflow/scripts/bootstrap-home.sh` —
a **standalone-only rung with no `plugins/*/skills/` fallback.** That is
precisely the two-rung defect SI-12 fixed twice elsewhere.

**I exposed it.** Refreshing the project home removed the standalone
`git-issue-workflow` — which is exactly what made `GOAL-one-unit` clause 1 hold.
So satisfying the goal broke the tooling, and `GOAL-one-unit`'s instrument never
checked whether the front door still worked.

**But the goal and the front door are not actually in conflict.**
`bootstrap-home.sh` **is already in the project home**, one rung over at
`plugins/tla-spec-dev/skills/git-issue-workflow/scripts/`. Adding the plugin rung
fixes it with the standalone copy staying absent.

**The tool's own suggested remedy is the wrong one.** It prints
`install github:haydenrear/git-issue-workflow-skill` and *"add it to
skill-project.toml"* — which would re-materialise a standalone copy of a
contained skill and un-satisfy the clause. Filed upstream rather than followed.

One correction to SI-15's account: it exited **3**, not 0, in my reproduction —
the exit-status half of `SI-11-DF-04` did **not** reproduce. What failed is
resolution alone.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| 0 new failures | failure **NAMES**, merged tip | **10 / 1683**, the known ten |
| the 55 count | `find` with and without `build/` | **55 sources** confirmed |
| the entry ceiling | read its method and evidence | view ≈7,288; **17,370 not reproducible** |
| front-door break | **reproduced it myself** | `rc=3`, path absent |
| per-ticket backlog | diff vs cumulative | 5 rows in `SI-15.yaml`, **0** to cumulative |
| territory | file list vs `evals/**` | **0 `specs/` outside `results/`** |
| suite landed | `find evals -name case.yaml` | **61** |

## Where the bugs probably are

1. **61 cases exist and none has been scored.** The suite is assembled, not
   validated. SI-08 is the first run that scores anything.
2. **Six cases need a real branched home (~41,000 entries, above the ceiling
   alone)** and are declared **UNDECIDED** rather than handed an empty workspace
   and scored 0 (`SI-15-DF-05`). That is the honest disposition and also a real
   gap in coverage.
3. `sandbox-probe` did not move: its grader is a deliberate standing red that
   this repo's own test forbids (`SI-15-DF-02`).
4. The 16 re-quoted regex patterns round-trip through YAML (asserted) but are
   only truly exercised by a scored run.

## Suggested next steps

**Wave 10 is SI-08 (#341)** — Evaluation A, freezing the four goals no later
ticket can move. Two things it must know: `GOAL-one-unit` clause 1 **now holds**
in the refreshed project home, and the front door is **currently broken** for any
agent using `skt ticket new` against that home.

**Fix the front door before dispatching SI-08**, or dispatch with the by-hand
`git worktree add` route named explicitly in the brief. A ticket agent that hits
a rolled-back worktree burns turns rediscovering what is already filed.

**Deferred findings: 79 cumulative + 5 in SI-15's file.** I concatenate at wave
close per the new policy.
