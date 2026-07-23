# ex3 run 4 — scored against PREDICTIONS.md (R4-E3, R4-X1, R4-X2)

Run date 2026-07-22, first run of the COMPOSED surface (post effect-provider
merge). Owner verified: two EFFECT_FUZZ_FAILURE probes in the evidence, the
3,580-point campaign green, descriptors and fitness scan re-read.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| R4-X2 complexity first | **PASS** | Stages walked in the doc's order; refactor decided and validated before any effect work. |
| E3 refactor convergence (4th independent run) | **PASS** | Same canonical call as runs 1/3: write-only-state test applied by name, `mode`/`dirty` deleted, `auditLog` defended — now with a NAMED consumer (the AuditJournalPort itself); bound 8,388,608 → 624; TLC/tests green, assertions byte-identical. |
| R4-E3 effect surface + provider + campaign | **PASS (exceeded)** | Full surface built (manifest commands/results, actions with explicit effect_ports, projections, generated runtime-checkable Protocol, 716 exhaustive transition cases); `on_audit` seam; provider asserts per-entry seq ordering, operation-name content, and exit-count vs modeled auditLog; campaign `--fuzz-runs 5 --seed 20260722` green over 3,580 points. |
| Kill demonstration | **PASS** | Two seeded bugs, both killed with EFFECT_FUZZ_FAILURE: dropped effect (count assertion) and wrong operation name (content assertion). App restored, tests 6/6. |
| R4-X1 docs suffice; no case mutation; replay works | **PARTIAL → findings** | Provider work needed the atomic_publisher example as a template (scaffolding didn't fit the fixture — honest and allowed), and four real findings were filed. Oracle integrity stayed silent throughout. |

## Findings → dispositions

1. **Sequence-item inline mappings broke the whole manifest** (silent
   degradation of budgets/justification/fitness) — a defect in the owner's
   own merge-integration parser extension. **FIXED same-day** (`37c6c65`):
   items opening with `{` route whole to the scalar parser; regression test;
   `effect_providers.md` profile sentence reconciled.
2. Case generation needs a real `tlc2` for DOT dumps — documented in the
   onboarding doc's new calibration notes (same commit).
3. Case-discovery layout mismatch (`--cases-dir` needed for the generator's
   natural layout) — documented; a code-level default reconciliation is a
   candidate post-main ticket.
4. Onboarding-doc single-module/exhaustive-dump assumptions — documented
   (calibration notes: `--target` overrides; the 200-case default is
   scenario-calibrated, and the gate's recorded-rationale accept path is the
   honest response to an exhaustive dump).

## Verdict

The composed value proposition demonstrated end-to-end on a fixture neither
epic ever saw: complexity minimized and locked in first, then the one real
effect boundary fuzzed with content-level assertions that provably kill
content bugs — with exact replay. This is the compounding the two epics were
built for.
