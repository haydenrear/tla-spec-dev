# Case Modules (BDD Slices) — mechanize the option, and fix what the probe found

Status: Open, unscheduled. The **option** shipped as doctrine
(`references/case_modules.md` + `examples/case_modules/`); nothing below is
required to use it.

## What the probe established

One case module EXTENDS a view, declares no state and no actions, and either
restricts `Next` (a slice) or replaces `Init` (a Given). Measured against
`examples/distributed_history`: 732 whole-view cases in 1m23s versus 190 cases
in 4.3s across three aspect modules, with **zero adapter, binding, or
`actions.yml` changes** and channel enforcement passing. Full numbers:
`examples/case_modules/MEASUREMENTS.md`.

The cost is real and stated in the reference: cross-aspect interleavings are
only produced by the whole-view run, and the Given form's reduction is a
modeling claim, not a free lunch.

## Findings filed by the probe

- **CM-F1 (defect, pre-existing, independent of this option).**
  `scripts/spec_evolution.py:find_model_files` picks the alphabetically first
  `*.tla` excluding `MC*` and pairs it with `MC.cfg` or the first `*.cfg`. On
  the accepted three-module baseline that resolves to **`Core.tla` +
  `External.cfg`**, and `complexity_ledger.collect_metrics` returns
  `bound = None`, `modularity = 0.0`. The standing-objective ledger — the thing
  that refuses a close when complexity rises — is measuring a module with no
  variables and no actions on every Core/Internal/External project. It went
  unnoticed because this repository's own baseline is still legacy
  single-module (`tickets/023`). Fix: the measured model is declared, not
  discovered; a mismatched `.tla`/`.cfg` pair is an error, not a silent
  measurement. Interim mitigation for case modules: the `Scenario_` prefix.
- **CM-F2 (usability).** Generation emits one zero-case warning per declared
  view action absent from a slice, diagnosing it as an alias-wrapper problem
  (R4-DF-04's message) when the real cause is that the action is not part of
  this aspect. Needs a per-module action scope so the warning keeps meaning
  what it says.
- **CM-F3 (interpretation).** Dense rows, modularity, and component sizes are
  ratios over the action count, so a slice measures denser than its view (probe:
  Q 0.019 vs 0.047; 6 dense rows vs none; a `max_component_variables` warning
  the view never emits). Descriptors of slices and views are not comparable and
  must not be ledgered against each other.
- **CM-F4 (coupling, arguably correct).** The kill test derives its required
  boundary catalog from the `INVARIANT(S)` of every `*.cfg` in the spec
  directory, so a case module with its own "Then" invariant requires a seeded
  mutant or the run refuses `incomplete_catalog`.

## If it is mechanized

Scope, in the order the probe says matters:

1. Fix CM-F1 — declared model discovery — because it is a live defect on every
   three-module project regardless of this option.
2. A `case_modules:` block in `spec_manifest.yaml`: per module, the view it
   extends, its action subset, and (for a Given) the recorded claim. That block
   is what makes CM-F2 fixable and makes ownership (every view action entered by
   some module or covered by the view's own corpus) checkable instead of
   manual.
3. Corpus aggregation across modules, reported per action against the view's
   action set — a report, not a gate, per "Advisory, Not Blocking".
4. Only then a scaffold template. Templating the shape before the evidence
   would invite projects to slice by default, which is the failure mode: case
   modules are additive to a view's corpus, never a replacement for it.

## Validation this needs before it earns more than "option"

No eval covers it. The three validation examples test the descriptor, the
intuition doc, and the fitness functions; none of them tests whether an agent
handed the case-module option decomposes a program's public surface into
aspects sensibly, or whether it quietly replaces the view's corpus with the
union of its slices. That second one is the prediction worth committing before
any dispatch — it is the degenerate path, and it produces green output.
