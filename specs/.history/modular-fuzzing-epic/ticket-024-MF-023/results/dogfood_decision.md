# MF-023 — Scanner dogfood on tla-spec-dev, and the refactor decision

## Deliverable 1: scanner run on this repository

`analyze complexity` was run on this repo's own model (the ticket-local
`current/TlaSpecDevCli.tla` + `MC.cfg`, manifest `current/spec_manifest.yaml`).
Full advisory report: `scanner_report_baseline.txt` (text) and
`scanner_report_baseline.json` (machine-readable). Exit code **0** (advisory —
a complex model is a finding, not a failure).

Headline measurements ([MEASURED] from the spec + cfg):

- 9 variables; static state-space upper bound **699,840** (product of 7 bounded
  dimensions; `lastCommand` and `result` are unconstrained by TypeInvariant and
  excluded). Dominant dimension: `ticket_state` (216 = 6^3).
- Graph modularity **Q = 0.012** over the variable-interaction graph — very low,
  i.e. the model does **not** cleanly decompose.
- Near-decomposable clusters found: C1 (6 vars, 14 actions) and C2 (the three
  advisory gate variables `complexity_gate`, `corpus_gate`, `effect_conformance`;
  4 actions). Four actions cross C1<->C2 (`AnalyzeComplexity`, `AnalyzeCorpus`,
  `RunEffectConformance`, `RunSpecUnitTests`).
- Every variable has a recorded justification linkage.
- **Suggested move: ABSTRACT** (not decompose) — project `lastCommand` and
  `result`, which no configured invariant reads.
- One advisory **WARNING**: component C1 is touched by 14 actions, exceeding
  `max_component_actions` 8 — recommends splitting the densest state
  (`lastCommand`, written by all 14 actions) or moving the port-crossing actions
  behind a contract.

## Deliverable 1: refactor decision — NOT TAKEN, and why

The Internal/External (C1/C2) decomposition is a recommendation the scanner may
emit; it is never forced and never a gate. I did **not** take it. The scanner's
own numbers argue against it:

1. **The scanner did not recommend decomposition.** Its suggested move is
   ABSTRACT. The decompose move is only valid when the R/W matrix has real
   modular structure (`architecture_tractability.md`, Move 2). Here modularity is
   **Q = 0.012** — near zero. No clean cut exists.
2. **A C1/C2 split would raise coupling, not lower it.** Four actions already
   cross the C1/C2 boundary. Cutting there forces those actions through a contract
   boundary, adding interface machinery for a partition the graph does not
   support. C2 is just the three advisory-observation variables the scanner/oracle
   actions write; they do not form an independent component.
3. **The one ABSTRACT suggestion yields no bound reduction and cannot be safely
   validated here.** `lastCommand` and `result` are already unconstrained and
   already excluded from the 699,840 bound, so projecting them removes nothing
   from the state-space number — the only gain is representational tidiness. The
   scanner flags that projecting them is legitimate *only if the mutation kill
   rate holds afterwards* — but MF-038 showed the kill test does not catch content
   bugs (0/9, 0.31), and this ticket explicitly forbids running the kill test as
   product validation. So the one move offered cannot be validated the way the
   tool asks, for no state-space payoff.
4. **The C1 warning reflects an irreducible domain shape.** `lastCommand` and
   `result` are written by every action because a CLI records the last command it
   ran and its result — that is what makes C1 dense. This is exactly the "some
   components score badly and still need to exist in that form" case the scanner
   calls out in its own output. It is a finding to surface, not a defect to
   refactor away.
5. The ticket baseline expects **zero TLA+ model delta**.

Decision: record the advisory report, surface the C1 warning and the ABSTRACT
suggestion as findings for the owner, and take no refactor. No before/after scan
is needed because no refactor was taken. This is the "if not, say so and move on"
path the ticket authorizes.

## Deliverable 2 pointer

The scanner is documented as the shipped advisory feature and the
fuzzing/oracle/kill-test machinery is marked EXPERIMENTAL / not-validated-for-
bug-catching (citing 0.31 / 0-of-9 and the Hypothesis stub) in `SKILL.md`,
`references/modular_fuzzing.md`, and `references/architecture_tractability.md`.
No product-validation run of the fuzzing oracles was performed.
