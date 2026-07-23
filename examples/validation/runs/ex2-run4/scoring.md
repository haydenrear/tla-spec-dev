# ex2 run 4 — scored against PREDICTIONS.md (R4-E2, R4-X1, R4-X2)

Run date 2026-07-22/23, composed surface. The agent completed all work but
stalled twice waiting on ~40-minute Test Graph runs; the epic owner verified
every artifact directly from the workspace and closed the scoring out (the
agent's own final report was made redundant — a token-efficiency finding as
much as anything).

| Prediction | Verdict | Evidence (owner-verified) |
| --- | --- | --- |
| R4-E2 cancellation ticket end-to-end | **PASS** | 5th independent convergence on the cancellation semantics; adapter tests, regeneration, internal batch, external batch green; TLC green. |
| R4-E2 one-action migration, legacy preserved | **PASS — the migration doc's first real exercise** | Exactly one boundary migrated: OrderCancellationPort (role: effect) over the CancelOrder store mutation, typed generated package, provider asserting store/outbox after-state == modeled after-state on exit; `effect_ports: []` everywhere else; post-migration external batch executed 1,724 cases and the ecommerceExternal graph passed 16/16 — twice (second run with strengthened evidence assertions: "monolith received /orders/cancel statuses [200, 404, 409]"). |
| Campaign + negative probe | **PASS** | 597 effect-fuzz points green (`--fuzz-runs 3 --seed 20260722`); negative probe produced EFFECT_FUZZ_FAILUREs from the provider content assertion. |
| R4-X2 complexity first | **PASS** | Descriptor before/after read per the doc's ordering before provider work. |
| R4-X1 | PASS with the known burrs | The R4-DF-02/03 class of friction recurred (routed around as in ex1-run4); no new finding classes. |

## Owner note on cost

The work: ~1 hour. The wall-clock: much longer, dominated by two full
external Test Graph runs the agent waited on (the second, verifying
strengthened assertions, was its own scope addition). Evidence for the
token-tiering design: long external runs should decouple from the
implementing agent entirely.
