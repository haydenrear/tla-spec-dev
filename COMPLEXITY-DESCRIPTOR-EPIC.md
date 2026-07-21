# complexity-descriptor epic — starter for the next epic owner

You are starting a new epic. The previous one (`modular-fuzzing`) is **solid
discovery** — it found what works and what doesn't. Read this before anything.

---

## 1. What the last epic learned (do not re-litigate)

The modular-fuzzing epic tried to build: a complexity analyzer that measures a
program's complexity from its TLA+ model, *gates* on it, and a modular-fuzzing
harness that generates cases and *catches bugs*. Three findings killed most of
that scope, each measured, not asserted:

- **Complexity gates fail every normal program.** A 5-variable, 10-command CLI
  hard-failed promotion (`component touched by 10 actions > 8`). As a hard gate,
  the metric fails in nearly every real project. → **Complexity was made
  advisory** (`references/architecture_tractability.md`, "Advisory, Not
  Blocking"): it warns, never blocks.
- **The fuzzing catches 0 of 9 content bugs.** The kill probe (MF-038) measured
  it: green control, kill rate 0.31, and every subtle content/value/field bug
  survived — the oracles read file *existence and exit codes*, not *content*.
  The Hypothesis random-generation arm was never built (a stub). → **The fuzzing
  is documented EXPERIMENTAL and is not shipped as a bug-finder.**
- **The suggested moves are confidently wrong on standard TLA+.** Validation
  found the scanner's `SUGGESTED MOVE: ABSTRACT` tells a user to project away
  *every* variable whenever the cfg names a composed/aliased invariant
  (`INVARIANT Inv` where `Inv == RealInv`) — a normal pattern the scaffold
  itself ships. → **This epic removes suggestions.**

What survived and is reliable: the **complexity descriptor** — the factual,
TLA+-derived complexity (dimension table, state-space bound, R/W matrix,
modularity + clusters, dense-row/god-state detection, domains). Facts are
trustworthy; judgment (suggestions, gates, bug-catching) was not.

## 2. What this epic ships

The honest product, in three pieces:

1. **CD-01 (#71) — the complexity descriptor.** Remove the suggested-move
   machinery. Present the factual descriptor as a pass-through for TLA+
   complexity. Fix the two accuracy bugs validation found: **F1** (resolve
   invariant aliasing so read-by-invariant analysis is correct) and **F3** (the
   bound degenerates to 1 without a `TypeInvariant` — make it meaningful or
   report it unknown, never a silent 1). Update SKILL.md so the descriptor is
   the surface and no suggestion claims remain.

2. **CD-02 (#72) — complexity intuition.** A doc that teaches an agent to *read*
   a descriptor: what good vs bad complexity shapes look like, framed as
   **"take this complexity descriptor to consider how to refactor complexity out
   of the app."** Intuition for the agent to judge with — not automated moves.

3. **CD-03 (#73) — self-configurable fitness functions.** Composable primitives
   the *project's own agent* uses to write rules over the descriptor (`bound <
   X`, `component_actions <= N`, `no god-state`, composed with and/or/not). They
   persist per-project and, when a rule fires on a scan, **notify future
   agents**. Advisory — report, never block. Ship with **no built-in rules**;
   the project's agent configures them. Quick and dirty, experimental.

Run them in order: CD-01 → CD-02 → CD-03. CD-02 and CD-03 both build on the
descriptor CD-01 produces.

## 3. The roadmap beyond this epic (not tickets yet)

Suggestions may return — but *earned*, not invented. As real apps are onboarded
to the descriptor, observe how descriptors behave in practice, and only then
consider building suggested moves, **possibly as an agent rather than a
function**. Do not build suggestions in this epic.

## 4. How to run it

- **Branch `epic/complexity-descriptor` off the current `epic/modular-fuzzing`
  tip** — you inherit the working advisory scanner, which is the descriptor's
  base. Do NOT branch from `main` (it is `da0a7ff`, pre-everything).
- Scaffold the epic's shared spec workflow with the `git-epic-workflow` skill,
  or continue the existing `specs/` tree — the CD work is mostly in
  `scripts/analyze_complexity.py`, `references/`, and `SKILL.md`, and is largely
  **zero-model-delta** (it does not change this repo's TLA+ model).
- Dispatch one ticket at a time via `git-issue-workflow` in epic mode. Render
  the full assignment block into each issue before dispatching — pin the epic
  tip, include the repository-owner self-merge deviation note. (The three issues
  are intentionally created *without* assignment blocks; you render them.)
- Verify each independently before accepting; hand each to the repository owner
  for review. Do not close issues yourself.

## 5. Standing constraints (unchanged, non-negotiable)

- **Never merge to `main`** (stays at `da0a7ff`) and **never run
  `skill-manager sync`** without explicit owner say-so.
- **Never invoke `tla-spec-dev` from PATH** — it execs a stale installed clone.
  Use `python3 scripts/tla_spec_dev.py --spec-root specs ...`.
- **Run pytest with `--with pyyaml`** or the YAML-validity guard skips silently.
- **Validate `ticket_plan.yaml` after every edit** — it has been broken twice.
- **Carry `max_distinct_states: 500000` and its rationale** through each
  ticket's `desired/` and verify post-promotion (the SF-003 blind spot, #32).
- The tool serves a **constrained v0 TLA+ profile** (SKILL.md "TLA+ Profile"),
  not arbitrary TLA+. The descriptor's accuracy target is that profile plus the
  standard patterns real users write (composed invariants, `TypeOK`) — which is
  exactly what F1/F3 are about.

## 6. Epic-owner discipline that paid off last time

Every substantive finding in the last epic came from an agent measuring, not
from review. The owner made six spec-level errors, all caught by ticket agents.
So: **tell every agent your brief may be wrong and the issue is authoritative**,
verify claims against the code yourself, and treat the self-critical result as
more valuable than the tidy one. The whole reason this epic exists is that a
validation agent was told a low/honest result was a valid outcome — and it
found the suggestions were wrong. Keep that standard.
