# ex1 run 2 — scored against PREDICTIONS.md (E1-*), plus run-1 divergence

Run date 2026-07-21. Identical instructions, fresh pristine copy. Owner
re-verified the descriptor (bound 1,152, Q=0.044, no warnings), the fitness
scan (both rules hold), the canary FIRED evidence, and TLC green.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E1-P1 scaffold + TLC green | **PASS** | Internal 139 distinct / External 1,238 distinct, both green; real behavior modeled with the cap exercised. |
| E1-P2 no silent bound = 1 | **PASS** | Bound 1,152 with the two label channels explicit unknowns. Hit the operator-defined-set unknown (VAL-06) first and routed around by inlining literals plus TLC-checked literal-matches invariants — a cleverer route than run 1's. |
| E1-P3 grounded judgment, no suggestion language | **PASS** | "No refactor warranted," argued dimension-by-dimension; dense rows classified as protocol-mandated response channel vs example-3 bookkeeping — explicitly contrasted with order_hub's audit_log. |
| E1-P4 composed fitness rules persist and surface | **PASS (exceeded)** | Two 4-leaf composed rules, both hold; notification path proven end-to-end with a canary rule that FIRED (evidence kept), then removed. |
| E1-P5 advisory treated as advisory | **PASS** | Zero warnings this time (modeling style differs from run 1); budgets at defaults with rationale. |
| X-P1 no PATH wrapper | PASS (per report) |
| X-P2 findings filed, not fixed | **PASS** | 5 findings reported (+1 positive confirmation), none fixed. |
| X-P3 docs suffice without source | **FAIL (→ findings)** | Again needed `analyze_complexity.py` source to diagnose domain resolution (VAL-06/16/17). |

## Run 1 vs run 2 divergence

Convergent on every judgment that matters: both scaffolded successfully,
both reached TLC-green real-behavior models, both ruled "no refactor
warranted" on proportionality grounds, both configured composed JSON fitness
rules that hold, both had to route around VAL-06, both flagged the scaffold's
"hard gates" language (VAL-04) and the helper-as-action artifact (VAL-07).
Divergence is modeling style only: run 2 bounded the CLI observables
(exit/message classes) giving bound 1,152, Q=0.044, three clusters, and zero
warnings, where run 1's lastCli-record style gave bound 64, Q=0.000, one
component, and one component-actions warning. Same shape, different
projection — acceptable under the protocol, and it shows the descriptor's
numbers are sensitive to observable-encoding choices (context for reading
cross-project descriptors).

## New findings filed

- **VAL-16**: `infer_dimensions`' membership regex captures to end-of-line
  only — a multi-line `\in` conjunct (ordinary TLA+ style for a 9-element
  set) silently resolves unknown; single-line requirement documented nowhere.
- **VAL-17**: domain-source precedence (`TypeInvariant` > `TypeOK` > cfg
  invariants) interacts badly with the scaffold's own multi-view layout:
  TLA+ forbids redefining `TypeInvariant` across EXTENDS-ed views, so one
  view's variables always come back unresolved unless the views use
  different names (the run's Internal=`TypeOK` / External=`TypeInvariant`
  trick). Undocumented scaffold/analyzer interaction.
- VAL-06 rediscovered with a sharper diagnosis: `resolve_definition_body`
  has already expanded the operator body; `_set_size` just never consults
  it. VAL-04 and VAL-07 rediscovered verbatim (second sightings). Positive
  confirmation: the documented `fitness_functions.json` fallback works
  exactly as written.
