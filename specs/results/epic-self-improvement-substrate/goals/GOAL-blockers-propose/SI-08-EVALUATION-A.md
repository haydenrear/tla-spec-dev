# `GOAL-blockers-propose` — Evaluation A (SI-08), frozen reading

**Measured 2026-09-20 at base `2131cdad`.** Instrument, as the plan names it:
*the improvement card (SI-03), two blind judges per subject, dispatched per
`references/blind_dispatch.md`.*

> **Statement.** An agent that hits a blocker in the substrate proposes the
> change, in the PR or in its response.
>
> **Baseline (b7a7d203).** No such instrument exists.
>
> **Target.** NO TARGET ON THE NUMBER — the goal is decided by whether the card
> **runs**, **discriminates** between a PR that proposes and one that does not,
> and the two judges **agree within 1**.

## VERDICT: **NOT MET** — two of the three conditions hold; **discrimination does not.**

| condition | verdict |
|---|---|
| the card **runs** | **YES** — 4 judges, 2 subjects, 4 usable cards, 0 failures |
| the two judges **agree within 1** | **YES** — max spread **1**, on one dimension of one subject; **0** on the other nine |
| it **discriminates** between a PR that proposes and one that does not | **NO** — see below |

---

## The round

Four judges, two per subject, each in its own `claude --safe-mode -p` process in
its own neutral cell built by
`examples/validation/instruments/blind_dispatch.py cell`. Judges of the same
subject received **byte-identical** packets (one rendered prompt file per judge,
written from the same source). No judge saw another's reply; none was the agent
that produced either subject (rule 8).

| | subject | `subject_ref` | the designated section says |
|---|---|---|---|
| **A** | negative control | **PR #349 / SI-01** | `## Skill changes proposed` → **`none met`** |
| **B** | positive control | **PR #375 / SI-15** | five rows, each naming a unit and a specific change |

Packets, enumerated (the card requires enumeration, not description):
`pr_body`, `commits` (`git log --stat`), `deferred_findings_backlog_rows`, plus
`skill_changes_proposed` / `review_input` / `deferred_findings` where the body
carried them. `packet.absent` = `close_summary` for both (the epic agent closes
spec tickets in this epic; a ticket has none). `packet.withheld` = **empty** for
both. A = 28,513 bytes over 4 backlog rows; B = 44,556 bytes over 5.
The rubric was **rendered from parsed structure** — anchor bullets and the eight
scoring rules only — never served as `improvement_card.md`, whose prose states
how its own dimensions have scored. Renderer and packets are in `packets/`.

## The scores

| judge | subject | I1 reporting | I2 proposal | I3 disposition | I4 attribution | I5 honesty |
|---|---|---|---|---|---|---|
| a1 | A (`none met`) | 3 | **2** | 2 | 1 | 3 |
| a2 | A (`none met`) | 3 | **2** | 2 | 1 | 3 |
| b1 | B (proposes) | 3 | **2** | 2 | 1 | 3 |
| b2 | B (proposes) | **4** | **2** | 2 | 1 | 3 |

**Agreement: within 1 on every dimension of both subjects** — spread 1 once
(I1/B), spread 0 in the other nine pairs. The agreement condition is met, and
comfortably.

**Discrimination: absent where the goal needs it.** I2 — *proposal*, the
dimension that exists to separate a PR that proposes from one that does not —
is **2 for all four cards**. I3, I4 and I5 are likewise identical across
subjects. The only movement is I1, at **+0.5 median** for the proposer.

## Why it did not discriminate, in the judges' own words

Both subjects hit the **same two ceilings**, for the same reasons, in all four
cards:

- **I2 rung 3** requires a diff, a commit, or an issue. Neither subject has one.
  B1 on the proposer: *"no proposal is delivered as a diff, a commit, or an
  issue carrying one, and the PR states affirmatively… 'No commit, branch or PR
  was made against skill-manager'."* A1 on the non-proposer: *"not one proposal
  is a diff, a commit, or an issue carrying one."* **Both stop at rung 2.**
- **I3 rung 2 is the ceiling** because a route is not a disposition. B2: *"none
  of the five names an existing successor… 'the epic agent', 'the skt plugin',
  'the epic' are roles, not successors that resolve."* A2: *"all four are
  `pending` with `disposition_ticket: null`."*

So the card is not failing to read the subjects — the rationales are specific,
cite openable paths, and differ from each other. **It is compressing two
genuinely different subjects onto the same rung because both fall short of the
same bar.** On this population the card measures *"did anyone carry a change"*,
and the answer for the whole epic is no.

## The confound, stated rather than smoothed over

**Subject A was chosen as the negative control on the strength of its
`none met`, and it is not a clean negative control.** Both A-judges found the
subject reported blockers *elsewhere in the same body* — under
*"A structural finding for the epic agent"* and *"Machinery friction"* — and
scored I1 = 3 on that evidence. A2 named the contradiction directly: `none met`
appears *"two sections after reporting a substrate defect that made a REQUIRED
validation entry unrunnable"*.

So this round **does not** establish that the card cannot tell a proposer from a
non-proposer. What it establishes is narrower and still worth freezing:

1. Declaring `none met` in the designated section **does not lower the score**
   when the blockers are reported elsewhere — the card scores the record, not
   the declaration, exactly as rule 1 asks.
2. **Two real subjects that differ visibly in their proposal sections score
   identically on the proposal dimension**, because the epic-wide ceiling
   (nothing became a diff, a commit or an issue) binds before any difference
   between them can register.

A round with a genuine non-reporter as the negative arm has **not** been run.
`SI-23` should run one before treating this goal as decided in either direction;
this reading is the counterfactual half, not the conclusion.

## Controls and non-vacuity

- Both controls are **real subjects**, not synthetic — the card marks a round
  whose negative control is constructed, and this one is not.
- The negative control **did not behave as a negative control** and is marked as
  such above.
- **The redaction pair the card names as the cheapest non-vacuity check was NOT
  run** (it doubles the judge count). What is available instead: the four
  rationales cite different evidence, reach different citation counts (4–6), and
  one judge moved a dimension — so the judges were reading their packets rather
  than emitting a constant. That is weaker than a redaction pair and is not
  offered as equivalent.

## `packet.contamination` — what each judge actually received

**Dispatch: `blind_dispatch.py cell` + `claude --safe-mode -p`, the path
`references/blind_dispatch.md` §3 prescribes. Every judge was asked to disclose
its pre-prompt context verbatim before reading the packet, and did.**

`blind_dispatch.py check` was run on all four replies against this repository and
the dispatching session's live auto-memory:

```
needles   4  harness block label
needles  25  operator memory entry
needles   5  repository commit subject
PASS. None of the operator's conclusions appear in this report.   [×4]
```

**All four PASS.** The disclosures agree with the check and add detail:

- **Received:** the `userEmail` system reminder; the commit-attribution reminder;
  an `# Environment` block naming **only the neutral cell**
  (`/private/tmp/blind-si08-a2`, *"Is a git repository: false"*); an auto-mode
  instruction block; a deferred-tool listing; an agent-type listing; a generic
  Claude Code **skill listing** (`dataviz`, `update-config`, `code-review`,
  `schedule`, `init`, …); a session-guidance block about `/code-review`.
- **Not received**, each judge stating so explicitly: **no `MEMORY.md` or memory
  file**, no `CLAUDE.md`, **no git-status or commit-subject block**, no
  `SessionStart` hook output, no MCP server listing, and **no repository path
  other than the cell**.

**This is the strongest blindness this project has achieved, and one standing
warning is now out of date.** `blind_dispatch.md` warns that *"the skill listing
still names its toolchain"*. Measured here: the listing arrived, and it carried
**no project skill** — not `spec-double-2`, not `git-epic-workflow`, not
`tla-spec-dev`. In the neutral cell the listing is the generic harness set.

**What this round is still NOT blind to, and the card forbids claiming
otherwise: the subject names the project in every line.** Both packets are PR
bodies citing this repository's paths, skills and ticket ids. No cell hides that.
The honest claim is **blind to the operator's conclusions, to the arm, and to the
other judge; NOT blind to the project's identity.**

One judge also reported a fact worth keeping: *"none of the paths cited by the
subject are openable from this machine; I scored the record as given in the
packet."* Under scoring rule 2, citations were verified as *present and
well-formed*, not as *resolving* — the cell cannot open them by construction.

## Cost

**Not measured.** The four judge dispatches were `claude --safe-mode -p`
processes, which print no cost line; no per-run figure is available and none is
invented here. Wall clock was roughly 5–9 minutes per judge, run concurrently.

---

## Summary

| clause | baseline | measured | verdict |
|---|---|---|---|
| the card runs | no instrument exists | 4 cards from 4 blind judges, 0 failures | **MET** |
| two judges agree within 1 | — | max spread **1** (1 of 10 pairs); 0 elsewhere | **MET** |
| discriminates proposer vs non-proposer | — | **I2 = 2 on all four cards**; only I1 moves, +0.5 | **NOT MET** |

**The goal is NOT MET.** The instrument now exists, runs blind, and two judges
agree — but on this pair it did not separate the subject that proposed from the
one that declared `none met`, and the negative arm was not a clean negative.
