# ex2 run 3 — PARTIAL (agent interrupted by session usage limit mid-run)

Run date 2026-07-22, against the main-readiness batch tip. The agent was
terminated by an infrastructure session limit after regeneration; no final
report exists. Everything below is owner-verified directly from the
workspace artifacts, scored only where evidence exists.

| Prediction | Verdict | Evidence (owner-read from workspace) |
| --- | --- | --- |
| R3-E2 pristine regeneration passes out of the box | **PASS (verified)** | Generated case tree exists (`test_graph/build/generated/manual/spec-unit/ecommerce_internal_cases` + validation exports); the agent's last words before termination: "Regeneration is green." No cap refusal, no missing-argument exit — VAL-08/09/10 fixes confirmed on the pristine path. |
| R3-E2 matrix lists true ExternalNext disjuncts | **PASS (verified)** | `descriptor_before.txt` columns include RunFulfillmentWorker / RunFulfillmentWorkerNoop / HiddenInternalProgress; MarkExternal absent; the composed workers now visibly cross C1/C2 — VAL-12/CD-06 confirmed on the real pristine model. |
| E2 semantics convergence (3rd independent run) | **PASS (verified)** | Internal.tla carries the same cancellation window and the textually identical cancelled⇒never-projected invariant as runs 1 and 2. |
| E2-P2 full local path (adapter batches, tests) | **NOT SCORED** | Interrupted before the internal/external adapter batches and descriptor_after. |
| E2-P3/P4, remaining R3-E2/R3-X1 checks | **NOT SCORED** | No final report to score. |

Disposition: resume or re-run ex2 after the session limit resets; the
completed checkpoints above stand as verified evidence regardless.
