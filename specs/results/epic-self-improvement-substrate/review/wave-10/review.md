# Wave 10 review — Evaluation A, and the reading it froze

Range: `2131cdad` → `308d2732`. One ticket: SI-08 (#341), PR #376 merged.
Not a gate. **This is the epic's first evaluation, and its numbers become the
counterfactual half of every clause SI-23 later re-reads.**

---

## Block 1 — Model delta applied

**None owed.** 24 files, **all under `specs/results/`**, `+3753/-0`.
`specs/tickets/` untouched, neither home modified. Measurement only, as the role
requires.

## Block 2 — Anchors placed

**None placed.** Eleven findings, all harness/instrument defects, `UNMODELED/`.

## Block 3 — Improvement-card row

**Four cards run, and the goal they serve is NOT MET.** `GOAL-blockers-propose`
splits three ways: the card runs (MET), two judges agree within 1 (MET, spread 0
in 9 of 10 pairs), and it **does not discriminate** (NOT MET) — **I2 is 2 on all
four cards**, because no proposal anywhere in this epic is a diff, a commit, or
an issue carrying one. Everything hits the same rung-3 ceiling.

**The confound is stated, not smoothed.** SI-08 chose PR #349 as its negative
control for its `none met`, and both judges found it reported blockers elsewhere
in the same body. So this does **not** prove the card cannot discriminate — a
round against a genuine non-reporter has not been run. Saying so costs the
headline and is the right call.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| two `improvement_ledger.py` instrument defects | **declined deliberately, and correctly** — *"changing the instrument mid-measurement is the one edit an evaluation ticket may not make"* |
| `blind_dispatch.md`'s stale skill-listing warning | **filed, not edited** (`SI-08-DF-10`) — overstating blindness in the *other* direction is this project's most repeated error |
| eleven findings against a `budget: 5` | **flagged, not trimmed** — for an evaluation the findings are the deliverable. Owner's call whether to escalate. |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Seventh consecutive wave clean.

---

## The frozen reading — 12 clauses: 6 MET, 4 NOT MET, 1 SPLIT, 1 UNDECIDED

| goal | clause | verdict |
|---|---|---|
| `GOAL-one-unit` | one unit, zero standalone copies **root or project** | **NOT MET** |
| | graphs + eval cases green | **SPLIT** — graphs 3/3; eval half **UNDECIDED** |
| | change-managed | **MET** |
| `GOAL-findings-become-changes` | `recorded-local` 13 → 0 | **MET** |
| | every finding carries `skill_change` | **NOT MET** — 19 of 121 |
| | terminal disposition | **NOT MET** — 45 still `pending` |
| `GOAL-blockers-propose` | runs / judges agree / discriminates | **MET / MET / NOT MET** |
| `GOAL-pinned-eval-toolchain` | pin in repo, not home | **MET** |
| | asks and refuses | **MET**, and *exercised* |

## It corrected me on the goal it was sent to freeze

`GOAL-one-unit` clause 1 reads *"zero standalone copies of the five migrated
skills in **root or project home**."* I refreshed the project home, measured
zero duplicates there, and told the owner repeatedly that **clause 1 now holds**.

**It does not.** The root home still carries all 8 substrate skills standalone,
dirs *and* install records, with no plugin installed. I verified this myself
after the report. I read a two-home clause as a one-home clause, and I did it
while telling the owner the blocker to freezing this goal was cleared.

Its sweep asserted on population — 18 dirs / 48 records in root, 10 / 33 in
project — so the root's 8 hits prove the detector fires and the project's 0 is a
measurement rather than a miss. That is the discipline I have been asking for,
applied against me.

**It did not touch the root home** (rule 8). Closing this clause is an operator
action or an owner's target change, and **it is now the owner's decision.**

## Two instrument defects, one of which is mine

**`improvement_ledger.py` cannot see the per-ticket partition.** Verified in
source: `BACKLOGS` hardcodes `deferred_findings_final.yaml` and
`epic-close/deferred_findings_next.yaml`; `grep -c "deferred/"` returns **0**.

**I adopted `per_ticket_backlog` at the wave-8/9 boundary and never told the
instrument that decides `GOAL-findings-become-changes`.** 16 rows live in the
partition today and are invisible; **10 of 16 carry `skill_change`** — the very
field the goal is measured on. So the goal's number is **biased downward by the
epic's own filing convention, and the bias grows with every compliant ticket.**
True population **137, not 121**.

Second defect: under ambient `python3` (3.14, no PyYAML) the ledger **silently
skips both YAML backlogs** and prints a complete-looking table over 36 records.
Under `uv --with pyyaml` it reads 121 across 4 files. A complete-looking table
over a third of the data is this epic's signature failure shape, inside the
instrument that grades it.

## The front door, root-caused at last

`skt/src/skt/ticket.py:150` — `_bootstrap_script()` looks only in
`<home>/skills/git-issue-workflow/…`, never `<home>/plugins/*/skills/`. **The
migration this epic performed is what breaks ticket provisioning.** Ninth
occurrence, first root cause.

**And my fix landed in the wrong home.** I installed `skt` PR #54 into the
*project* home; the dispatch command is
`${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/bin/cli/skt`, which with the env
unset resolves to the **root** home — still unfixed. My own probe passed because
I ran the project home's shim directly. SI-08 hit the unfixed one and fell back
to `git worktree add`, correctly, **catching it by testing the PATH** — *through
a pipe the exit code was 0.*

## It closed the gap I flagged

I dispatched saying nothing proved a pinned ref reaches a score. SI-08 **ran the
suite's first ever scored eval case**: 1 case, 1 run, **$0.54**, 106 s, score
0.67, writing a toolchain record naming both pinned commits. Clause 1 of the pin
goal moves from 0/0 to 1/1.

It found two defects only a real run could: the score artifact contains **zero**
mention of the ref (record and score joined by nothing but a 5-second timestamp
gap), and **`evals/results/` is gitignored**, so a run does not persist its own
record.

**And it refused the tempting claim**: *"the 0% pass rate is a sample of one —
don't quote it."*

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| 0 new failures | failure **NAMES**, merged tip | **10 / 1692**, the known ten |
| clause 1 wording | read the plan's target text | **"root or project"** — it is right, I was wrong |
| root home state | listed dirs + install records | **8 standalone, no plugin** |
| ledger blindness | read `BACKLOGS` in source | **confirmed**, `grep "deferred/"` = 0 |
| findings + `skill_change` | counted on the branch | **11 filed, 11 carry it** |
| territory | file list | **24 files, 0 outside `specs/results/`** |

## Suggested next steps

**Two owner decisions, both before SI-23:**

1. **The root home.** Clause 1 cannot pass while it carries the standalone
   copies. Migrate it, or amend the clause — but amending it to mean "project
   home only" would make the sentence true by making it say less, which the
   owner rejected at the wave-4 gate.
2. **`skt` PR #54 into the root home**, so the front door works from the command
   every assignment names. That is a root-home mutation and needs say-so.

**Before SI-23 runs:** teach `improvement_ledger.py` the partition, or SI-23
re-reads a number biased by our own convention. **Keep SI-08's 121 as the
pre-fix reading** so the pair stays comparable.

**Wave 11 is SI-16 (#365)** — nest skt. Note it will land on the same
`ticket.py` this epic has now broken itself on twice.
