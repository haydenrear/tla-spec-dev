# Validation predictions — written BEFORE any agent dispatch

Restart of the MF-037 validation (issue #62), re-aimed at what the
complexity-descriptor epic actually shipped (CD-01 descriptor, CD-02
intuition, CD-03 fitness functions — issues #71/#72/#73). One question,
three shapes: **is the descriptor + intuition + fitness-function surface
useful — does it correctly describe where complexity concentrates, and does
an agent, advised by it, behave correctly?**

Ground rules (MF-037 discipline, unchanged):

- These predictions are committed before any agent starts; "as expected" is a
  prediction, not a post-hoc reading.
- Real agents doing real tickets; transcripts and outputs recorded under
  `examples/validation/runs/`.
- Each example runs at least twice; divergence between runs is itself a
  finding about instruction determinism.
- Findings about the toolchain are FILED, not fixed inline, so the validation
  stays a measurement.
- Agents work in scratch copies; the epic owner collects evidence afterward.
- Agents are NOT shown this file before or during their run.

## Example 1 — scaffold-only (`ex1_scaffold_only/taskq`)

The entry path a new user hits first: onboard a small untouched Python CLI
to a spec workflow, scan it, judge it, configure fitness functions.

- **E1-P1** The agent scaffolds a spec workflow using the documented commands
  (`python3 scripts/tla_spec_dev.py` path, never the PATH wrapper) without
  inventing steps, and reaches a TLC-green model of taskq's behavior
  (pending/running/done lifecycle, running cap 2, duplicate rejection).
- **E1-P2** `analyze complexity` on the scaffolded model reports either
  resolved domains or an explicit `UNKNOWN` bound — never a silent
  `bound = 1` (the F3 fix, on the exact path that used to hit it: scaffolds
  shipping only safety invariants).
- **E1-P3** No suggested-move language appears anywhere (tool output or agent
  writing). The agent's refactor judgment cites descriptor facts plus
  `references/complexity_intuition.md`; for a model this small the honest
  call is "no refactor warranted," with proportionality reasoning.
- **E1-P4** The agent configures at least one composed fitness function that
  persists in the project, and a rescan surfaces it (holds or FIRED — either
  is fine; what matters is the notification surface works from a fresh
  project).
- **E1-P5** The agent treats advisory output as advisory: no budget raised,
  no threshold edited, no gate language.

Watchpoints (candidate findings, not predictions): stale scaffold docs in
SKILL.md after this epic's rewrites; the `does-not-exist` manifest-warning
sentinel (already filed as CD-02-DF-01); the intuition doc lacking guidance
for near-trivial models.

## Example 2 — ticket workflow (`examples/distributed_history`)

The path that was UNUSABLE under the old regime: issue #62 recorded that the
example's External model was refused by the complexity gate (C2 touched by 9
actions). The pivot made complexity advisory; this example must now complete.

- **E2-P1** The agent runs a small real ticket end-to-end (model delta +
  adapters + tests) with NO complexity refusal anywhere; the old C2 finding
  surfaces as an advisory warning only, and nothing in the workflow blocks
  on it.
- **E2-P2** The ticket completes with behavior validated: the example's unit
  and adapter tests pass on the changed model.
- **E2-P3** The descriptor honestly reports the External model's shape —
  pre-dispatch scan shows `bound = 4` with **9 of 10 variables excluded as
  unresolved**. The agent does NOT misread `bound = 4` as "simple model";
  it either notes the exclusions or consults the intuition doc's guidance on
  unknowns. If the doc gives it no footing here, that is a finding about
  CD-02, not about the agent.
- **E2-P4** No gate language, no waivers, no budget edits.

## Example 3 — deliberately over-complex (`ex3_over_complex/order_hub`)

The sharpest, most falsifiable test. Baseline measured before dispatch:
TLC green at 717 distinct / depth 13; descriptor shows `bound = 8,388,608`
(≈11,700× the reachable states — domains far wider than behavior), THREE
dense-row god-state variables (`mode`, `auditLog`, `dirty` touched by 4/4
actions), one monolithic 6-variable cluster, and the advisory
`max_state_space_bound` warning firing.

- **E3-P1** Given the descriptor and the CD-02 framing ("take this complexity
  descriptor to consider how to refactor complexity out of the app"), the
  agent CHOOSES to refactor. An agent that instead raises
  `max_state_space_bound`, edits thresholds to silence the warning, or
  declares the shape fine is a **FAILED VALIDATION of the toolchain** (the
  advice surface did not change behavior), not a failed example.
- **E3-P2** Measured complexity goes DOWN with behavior retained: post-refactor
  bound below 100,000 (honest domain sizing alone reaches ~6,656:
  mode 0..4 × orders 0..3 × shipped 0..3 × retries 0..2 × auditLog 0..12 ×
  dirty 2), and fewer dense rows than baseline's three. Before/after
  descriptors recorded and compared.
- **E3-P3** Validated means validated: TLC green post-refactor AND the
  project's behavior tests pass unmodified (or with changes justified line by
  line as representation-only). A generated-states drop at constant distinct
  states is read as the red flag the ledger doctrine says it is.
- **E3-P4** The agent locks the improvement in: at least one fitness function
  added so a future regression notifies future agents.
- **E3-P5** Run 2 also chooses to refactor. Divergence in WHICH moves is
  acceptable and interesting; divergence in WHETHER to refactor is a finding
  about the intuition doc's strength.

## Cross-cutting predictions

- **X-P1** No agent invokes the PATH `tla-spec-dev` wrapper.
- **X-P2** No agent fixes toolchain defects it trips over; each is reported
  in its run report instead (batch discipline).
- **X-P3** Agent-facing docs (SKILL.md + references) are sufficient to
  complete each task without the agent reading toolchain source as a manual;
  needing to read source to proceed is a docs finding.
