# Case-module probe — measurements

Run 2026-07-26 against `examples/distributed_history` at `c72d03a`, in a scratch
copy. Same constants (`Clients` 2, `Accounts` 1, `Skus` 2, `Orders` 2), same
projectors, `--dedupe projected` throughout. `tlc2` wrapper on PATH, Java 25.

## Cost

| model | TLC states | cases | wall clock |
|---|---|---|---|
| `External` (whole view) | 49,386 distinct / 632,658 generated, depth 11 | 732 | 1m 22.9s |
| `Scenario_CheckoutHappyPath` | 1,175 | 160 | 2.2s |
| `Scenario_IdempotentResubmit` | 113 | 16 | 1.1s |
| `Scenario_RejectedRequests` | 37 | 14 | 1.0s |
| all three | — | 190 | 4.3s |

## Coverage, per action

| action | whole view | happy | idempotent | rejected |
|---|---|---|---|---|
| SubmitCreateAccount | 2 | 2 | — | 2 |
| SubmitAddCartItem | 40 | 40 | — | — |
| SubmitCheckout | 52 | 52 | — | — |
| RunFulfillmentWorker | 74 | 66 | 2 | — |
| RunFulfillmentWorkerNoop | 48 | — | 2 | — |
| SubmitDuplicateCreateAccount | 120 | — | 4 | — |
| SubmitDuplicateAddCartItem | 200 | — | 4 | — |
| SubmitDuplicateCheckout | 184 | — | 4 | — |
| SubmitAddCartItemMissingAccount | 4 | — | — | 4 |
| SubmitCheckoutMissingAccount | 4 | — | — | 4 |
| SubmitCheckoutEmptyCart | 4 | — | — | 4 |
| **total** | **732** | **160** | **16** | **14** |

`HiddenInternalProgress` is an internal-layer action and generates no external
cases in either configuration.

Readings:

- The slice form is nearly lossless for the actions it keeps: 2 / 40 / 52 match
  the whole view exactly; `RunFulfillmentWorker` loses 8 of 74 (before-states
  reachable only through excluded actions).
- The Given form carries the reduction and the claim: 504 duplicate-command
  cases → 12.
- 190 vs 732 is not "we dropped 542 cases" — it is three different models, each
  exhaustively enumerated. What is genuinely gone is cross-aspect interleaving,
  which only the whole-view run produces.

## Adapter reuse

```
$ run_generated_case_adapters.py <case-module package> \
    --mapping specs/program_model/testgraph_bindings.yml --view external --batch --validate-only
external channel enforcement passed for 4 binding(s); integration rung HistoryPort+OrderPort (real: HistoryPort, OrderPort; double: ClockPort)
validated 11 adapter mappings for 5 labels
```

Zero adapter, binding, or `actions.yml` changes.

## Descriptor comparison (CM-F3)

`analyze complexity`, whole view vs the happy-path slice:

| fact | `External` | `Scenario_CheckoutHappyPath` |
|---|---|---|
| bound | 4 (9 of 10 variables unresolved) | 4 (same — variables are inherited) |
| actions in the matrix | 12 | 4 |
| modularity Q | 0.047 | 0.019 |
| dense rows | none reported | 6 (4/4 and 3/4 rows) |
| threshold warnings | none | `C1 has 7 variables, exceeding max_component_variables 6` |

The slice measures as *denser*, not simpler, because dense-row and component
heuristics are ratios over the action count. Both descriptors are honest; they
are not comparable. Do not put a slice's descriptor in the complexity ledger
next to a view's.

## Friction observed

- 8 `declared external action ... generated ZERO cases` warnings per slice, with
  an alias-wrapper diagnosis that does not apply (CM-F2). Warnings only, exit 0.
- `find_model_files` picks the alphabetically first `*.tla`; on the pristine
  example that is already `Core.tla` paired with `External.cfg`, yielding
  `bound = None`, `modularity = 0.0` from `collect_metrics` (CM-F1).
